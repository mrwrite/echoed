from __future__ import annotations

import base64
import csv
from datetime import datetime
from io import StringIO
import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import and_, or_
from sqlalchemy.orm import Query as SqlQuery, Session

from app.audit import AUDIT_ACTIONS, append_audit_event, verify_audit_chain
from app.database import get_db
from app.deps import get_active_org_id, get_current_user, require_roles
from app.enum import MembershipStatus, OrganizationRole
from app.models import AuditEvent, OrganizationMembership, User
from app.observability import emit_event, metrics
from app.rate_limit import enforce_rate_limit
from app.schemas import AuditEventPage, AuditEventResponse


router = APIRouter()
MAX_PAGE_SIZE = 100
MAX_EXPORT_ROWS = 5_000
_OUTCOMES = {"succeeded", "failed"}


def _serialize(event: AuditEvent) -> AuditEventResponse:
    return AuditEventResponse(
        id=event.id,
        created_at=event.created_at,
        schema_version=event.schema_version,
        actor_id=event.actor_id,
        actor_role=event.actor_role,
        action=event.action,
        category=event.category,
        outcome=event.outcome,
        target_type=event.target_type,
        target_id=event.target_id,
        organization_id=event.organization_id,
        request_id=event.request_id,
        correlation_id=event.correlation_id,
        reason_code=event.reason_code,
        before_state=event.before_state or {},
        after_state=event.after_state or {},
        integrity_verified=True,
    )


def _encode_cursor(event: AuditEvent) -> str:
    raw = json.dumps(
        {"created_at": event.created_at.isoformat(timespec="microseconds"), "id": str(event.id)},
        separators=(",", ":"),
    ).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_cursor(value: str) -> tuple[datetime, UUID]:
    try:
        padded = value + "=" * (-len(value) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
        return datetime.fromisoformat(payload["created_at"]), UUID(payload["id"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=422, detail="Invalid audit cursor.") from exc


def _filters(
    query: SqlQuery,
    *,
    action: str | None,
    category: str | None,
    outcome: str | None,
    actor_id: UUID | None,
    target_type: str | None,
    target_id: str | None,
    since: datetime | None,
    until: datetime | None,
) -> SqlQuery:
    if action is not None:
        if action not in AUDIT_ACTIONS:
            raise HTTPException(status_code=422, detail="Unsupported audit action filter.")
        query = query.filter(AuditEvent.action == action)
    if category is not None:
        categories = {definition.category for definition in AUDIT_ACTIONS.values()}
        if category not in categories:
            raise HTTPException(status_code=422, detail="Unsupported audit category filter.")
        query = query.filter(AuditEvent.category == category)
    if outcome is not None:
        if outcome not in _OUTCOMES:
            raise HTTPException(status_code=422, detail="Unsupported audit outcome filter.")
        query = query.filter(AuditEvent.outcome == outcome)
    if actor_id is not None:
        query = query.filter(AuditEvent.actor_id == actor_id)
    if target_type is not None:
        query = query.filter(AuditEvent.target_type == target_type)
    if target_id is not None:
        query = query.filter(AuditEvent.target_id == target_id)
    if since is not None:
        query = query.filter(AuditEvent.created_at >= since)
    if until is not None:
        query = query.filter(AuditEvent.created_at <= until)
    if since is not None and until is not None and since > until:
        raise HTTPException(status_code=422, detail="Audit time range is invalid.")
    return query


def _verify_query_scopes(db: Session, events: list[AuditEvent]) -> None:
    organizations = {event.organization_id for event in events}
    scopes = organizations | ({None} if any(event.organization_id is None for event in events) else set())
    for organization_id in scopes:
        result = verify_audit_chain(db, organization_id=organization_id)
        if not result.valid:
            emit_event(
                "audit.integrity.failed",
                level=40,
                component="audit",
                scope="organization" if organization_id else "platform",
                result="failure",
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Audit integrity verification failed. Contact an operator.",
            )


def _page(
    db: Session,
    query: SqlQuery,
    *,
    limit: int,
    cursor: str | None,
) -> AuditEventPage:
    if cursor:
        cursor_time, cursor_id = _decode_cursor(cursor)
        query = query.filter(
            or_(
                AuditEvent.created_at < cursor_time,
                and_(AuditEvent.created_at == cursor_time, AuditEvent.id < cursor_id),
            )
        )
    rows = query.order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc()).limit(limit + 1).all()
    has_more = len(rows) > limit
    rows = rows[:limit]
    _verify_query_scopes(db, rows)
    metrics.increment("echoed_audit_operations_total", operation="read", result="success")
    return AuditEventPage(
        items=[_serialize(row) for row in rows],
        next_cursor=_encode_cursor(rows[-1]) if has_more and rows else None,
    )


def _organization_scope(db: Session, current_user: User, requested: UUID | None) -> UUID:
    if requested is None:
        raise HTTPException(status_code=400, detail="Missing active organization.")
    if current_user.role == "super_admin":
        return requested
    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == requested,
            OrganizationMembership.user_id == current_user.id,
            OrganizationMembership.status == MembershipStatus.ACTIVE,
            OrganizationMembership.role == OrganizationRole.ORG_ADMIN,
        )
        .first()
    )
    if membership is None:
        raise HTTPException(status_code=404, detail="Audit events not found.")
    return requested


def _formula_safe(value: object) -> str:
    text = "" if value is None else str(value)
    return f"'{text}" if text.lstrip().startswith(("=", "+", "-", "@")) else text


@router.get("/audit-events", response_model=AuditEventPage)
def list_platform_audit_events(
    action: str | None = None,
    category: str | None = None,
    outcome: str | None = None,
    actor_id: UUID | None = None,
    target_type: str | None = Query(default=None, min_length=1, max_length=60),
    target_id: str | None = Query(default=None, min_length=1, max_length=100),
    since: datetime | None = None,
    until: datetime | None = None,
    cursor: str | None = Query(default=None, max_length=512),
    limit: int = Query(default=50, ge=1, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "super_admin")),
):
    query = _filters(
        db.query(AuditEvent),
        action=action,
        category=category,
        outcome=outcome,
        actor_id=actor_id,
        target_type=target_type,
        target_id=target_id,
        since=since,
        until=until,
    )
    return _page(db, query, limit=limit, cursor=cursor)


@router.get("/orgs/{org_id}/audit-events", response_model=AuditEventPage)
def list_organization_audit_events(
    org_id: UUID,
    action: str | None = None,
    category: str | None = None,
    outcome: str | None = None,
    actor_id: UUID | None = None,
    target_type: str | None = Query(default=None, min_length=1, max_length=60),
    target_id: str | None = Query(default=None, min_length=1, max_length=100),
    since: datetime | None = None,
    until: datetime | None = None,
    cursor: str | None = Query(default=None, max_length=512),
    limit: int = Query(default=50, ge=1, le=MAX_PAGE_SIZE),
    active_org_id: UUID | None = Depends(get_active_org_id),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if active_org_id != org_id:
        raise HTTPException(status_code=404, detail="Audit events not found.")
    scope = _organization_scope(db, current_user, active_org_id)
    query = _filters(
        db.query(AuditEvent).filter(AuditEvent.organization_id == scope),
        action=action,
        category=category,
        outcome=outcome,
        actor_id=actor_id,
        target_type=target_type,
        target_id=target_id,
        since=since,
        until=until,
    )
    return _page(db, query, limit=limit, cursor=cursor)


@router.get("/audit-events/export.csv")
def export_platform_audit_events(
    request: Request,
    action: str | None = None,
    category: str | None = None,
    outcome: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "super_admin")),
):
    enforce_rate_limit(request, "audit_export", actor_id=current_user.id)
    query = _filters(
        db.query(AuditEvent),
        action=action,
        category=category,
        outcome=outcome,
        actor_id=None,
        target_type=None,
        target_id=None,
        since=None,
        until=None,
    )
    rows = query.order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc()).limit(MAX_EXPORT_ROWS).all()
    _verify_query_scopes(db, rows)
    output = StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(
        [
            "event_id",
            "created_at",
            "action",
            "category",
            "outcome",
            "actor_id",
            "actor_role",
            "organization_id",
            "target_type",
            "target_id",
            "reason_code",
            "request_id",
            "correlation_id",
            "before_state",
            "after_state",
        ]
    )
    for event in rows:
        writer.writerow(
            [
                _formula_safe(event.id),
                event.created_at.isoformat(),
                event.action,
                event.category,
                event.outcome,
                _formula_safe(event.actor_id),
                event.actor_role,
                _formula_safe(event.organization_id),
                event.target_type,
                _formula_safe(event.target_id),
                event.reason_code or "",
                _formula_safe(event.request_id),
                _formula_safe(event.correlation_id),
                json.dumps(event.before_state or {}, sort_keys=True, separators=(",", ":")),
                json.dumps(event.after_state or {}, sort_keys=True, separators=(",", ":")),
            ]
        )
    append_audit_event(
        db,
        action="audit.exported",
        actor_id=current_user.id,
        actor_role=current_user.role,
        target_type="audit_event_set",
        target_id="platform",
        after={"row_count": len(rows)},
    )
    db.commit()
    metrics.increment("echoed_audit_operations_total", operation="export", result="success")
    return Response(
        content=output.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="echoed-audit-events.csv"'},
    )


@router.get("/audit-events/{event_id}", response_model=AuditEventResponse)
def get_platform_audit_event(
    event_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "super_admin")),
):
    event = db.query(AuditEvent).filter(AuditEvent.id == event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Audit event not found.")
    _verify_query_scopes(db, [event])
    return _serialize(event)
