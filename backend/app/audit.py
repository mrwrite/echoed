from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import re
from typing import Mapping
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models import AuditEvent
from app.observability import correlation_id_context, emit_event, metrics, request_id_context


AUDIT_SCHEMA_VERSION = 1
GENESIS_HASH = "0" * 64
_SAFE_CODE = re.compile(r"^[a-z][a-z0-9_.-]{0,99}$")
_SENSITIVE_PARTS = (
    "password",
    "secret",
    "token",
    "authorization",
    "cookie",
    "email",
    "name",
    "content",
    "answer",
    "filename",
    "body",
)


@dataclass(frozen=True)
class AuditAction:
    category: str
    state_keys: frozenset[str]


AUDIT_ACTIONS: dict[str, AuditAction] = {
    "platform.role.changed": AuditAction("access", frozenset({"role"})),
    "platform.user.deleted": AuditAction("identity", frozenset({"role"})),
    "organization.invite.created": AuditAction("membership", frozenset({"role", "status"})),
    "organization.invite.accepted": AuditAction("membership", frozenset({"role", "status"})),
    "forum.post.moderated": AuditAction("moderation", frozenset({"moderator_override"})),
    "forum.thread.moderated": AuditAction("moderation", frozenset({"moderator_override"})),
    "course.review.changed": AuditAction("content_governance", frozenset({"review_state"})),
    "course.version.published": AuditAction("content_governance", frozenset({"version_status"})),
    "product.review.changed": AuditAction("content_governance", frozenset({"review_state"})),
    "product.published": AuditAction("content_governance", frozenset({"status", "visibility"})),
    "audit.exported": AuditAction("audit", frozenset({"row_count"})),
    "audit.retention.performed": AuditAction("audit", frozenset({"deleted_count", "cutoff"})),
}


class AuditPayloadError(ValueError):
    pass


def _safe_state(action: str, state: Mapping[str, object] | None) -> dict[str, str | int | float | bool | None]:
    values = dict(state or {})
    definition = AUDIT_ACTIONS[action]
    if len(values) > 16 or set(values) - definition.state_keys:
        raise AuditPayloadError("Audit state contains unsupported fields")
    result: dict[str, str | int | float | bool | None] = {}
    for key, value in values.items():
        normalized = key.lower().replace("-", "_")
        if any(part in normalized for part in _SENSITIVE_PARTS):
            raise AuditPayloadError("Audit state contains a sensitive field")
        if value is not None and not isinstance(value, (str, int, float, bool)):
            raise AuditPayloadError("Audit state values must be primitive")
        if isinstance(value, str) and len(value) > 160:
            raise AuditPayloadError("Audit state value is too long")
        result[key] = value
    return result


def _canonical_payload(event: AuditEvent) -> bytes:
    payload = {
        "action": event.action,
        "actor_id": str(event.actor_id) if event.actor_id else None,
        "actor_role": event.actor_role,
        "after": event.after_state or {},
        "before": event.before_state or {},
        "category": event.category,
        "correlation_id": event.correlation_id,
        "created_at": event.created_at.isoformat(timespec="microseconds"),
        "id": str(event.id),
        "organization_id": str(event.organization_id) if event.organization_id else None,
        "outcome": event.outcome,
        "previous_hash": event.previous_hash,
        "reason_code": event.reason_code,
        "request_id": event.request_id,
        "schema_version": event.schema_version,
        "scope_key": event.scope_key,
        "scope_sequence": event.scope_sequence,
        "target_id": event.target_id,
        "target_type": event.target_type,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def compute_event_hash(event: AuditEvent) -> str:
    return hashlib.sha256(_canonical_payload(event)).hexdigest()


def _lock_scope_for_append(db: Session, scope_key: str) -> None:
    if db.get_bind().dialect.name == "postgresql":
        db.execute(text("SELECT pg_advisory_xact_lock(hashtext(:scope_key))"), {"scope_key": scope_key})


def append_audit_event(
    db: Session,
    *,
    action: str,
    actor_id: UUID | None,
    actor_role: str,
    target_type: str,
    target_id: UUID | str,
    organization_id: UUID | None = None,
    before: Mapping[str, object] | None = None,
    after: Mapping[str, object] | None = None,
    outcome: str = "succeeded",
    reason_code: str | None = None,
    request_id: str | None = None,
    correlation_id: str | None = None,
) -> AuditEvent:
    if action not in AUDIT_ACTIONS:
        raise AuditPayloadError("Unknown audit action")
    if outcome not in {"succeeded", "failed"}:
        raise AuditPayloadError("Unsupported audit outcome")
    if not _SAFE_CODE.fullmatch(target_type) or not _SAFE_CODE.fullmatch(actor_role):
        raise AuditPayloadError("Invalid audit attribution")
    if reason_code is not None and not _SAFE_CODE.fullmatch(reason_code):
        raise AuditPayloadError("Invalid audit reason code")
    target_text = str(target_id)
    if not target_text or len(target_text) > 100:
        raise AuditPayloadError("Invalid audit target")

    scope_key = f"organization:{organization_id}" if organization_id else "platform"
    # A row lock cannot serialize two concurrent first events because no row
    # exists yet. PostgreSQL's transaction-scoped advisory lock closes that gap.
    _lock_scope_for_append(db, scope_key)
    latest = (
        db.query(AuditEvent)
        .filter(AuditEvent.scope_key == scope_key)
        .order_by(AuditEvent.scope_sequence.desc())
        .with_for_update()
        .first()
    )
    event = AuditEvent(
        id=uuid4(),
        created_at=datetime.utcnow(),
        schema_version=AUDIT_SCHEMA_VERSION,
        scope_key=scope_key,
        scope_sequence=(latest.scope_sequence + 1) if latest else 1,
        organization_id=organization_id,
        actor_id=actor_id,
        actor_role=actor_role,
        action=action,
        category=AUDIT_ACTIONS[action].category,
        outcome=outcome,
        target_type=target_type,
        target_id=target_text,
        request_id=(request_id or request_id_context.get()),
        correlation_id=(correlation_id or correlation_id_context.get()),
        reason_code=reason_code,
        before_state=_safe_state(action, before),
        after_state=_safe_state(action, after),
        previous_hash=latest.event_hash if latest else GENESIS_HASH,
        event_hash="",
    )
    event.event_hash = compute_event_hash(event)
    try:
        db.add(event)
        db.flush()
    except Exception as exc:
        metrics.increment("echoed_audit_operations_total", operation="capture", result="failure")
        emit_event(
            "audit.capture.failed",
            level=40,
            component="audit",
            category=AUDIT_ACTIONS[action].category,
            result="failure",
            exc_info=exc,
        )
        raise
    metrics.increment("echoed_audit_operations_total", operation="capture", result="success")
    emit_event(
        "audit.capture.succeeded",
        component="audit",
        category=event.category,
        result="success",
    )
    return event


@dataclass(frozen=True)
class IntegrityResult:
    valid: bool
    checked: int
    scope_key: str
    first_event_id: str | None = None
    last_event_id: str | None = None
    error_event_id: str | None = None


def verify_audit_chain(db: Session, *, organization_id: UUID | None = None) -> IntegrityResult:
    scope_key = f"organization:{organization_id}" if organization_id else "platform"
    events = (
        db.query(AuditEvent)
        .filter(AuditEvent.scope_key == scope_key)
        .order_by(AuditEvent.scope_sequence.asc())
        .all()
    )
    previous = events[0].previous_hash if events else GENESIS_HASH
    for event in events:
        if event.previous_hash != previous or event.event_hash != compute_event_hash(event):
            metrics.increment("echoed_audit_operations_total", operation="verify", result="failure")
            return IntegrityResult(
                False,
                len(events),
                scope_key,
                str(events[0].id),
                str(events[-1].id),
                str(event.id),
            )
        previous = event.event_hash
    metrics.increment("echoed_audit_operations_total", operation="verify", result="success")
    return IntegrityResult(
        True,
        len(events),
        scope_key,
        str(events[0].id) if events else None,
        str(events[-1].id) if events else None,
    )
