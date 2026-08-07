from __future__ import annotations

from collections.abc import Iterable
from typing import Final
from uuid import UUID

from fastapi import HTTPException, status

from app.observability import emit_event, metrics

PLATFORM_ROLES: Final[frozenset[str]] = frozenset(
    {"student", "teacher", "instructor", "parent", "content_admin", "org_admin", "admin", "super_admin"}
)
PLATFORM_ADMIN_ROLES: Final[frozenset[str]] = frozenset({"admin", "super_admin"})
HIGHEST_PLATFORM_ROLE: Final[str] = "super_admin"
FORUM_MODERATOR_ROLES: Final[frozenset[str]] = PLATFORM_ADMIN_ROLES
ORGANIZATION_ROLES: Final[frozenset[str]] = frozenset(
    {"org_admin", "content_admin", "teacher", "parent", "student", "instructor", "viewer", "super_admin"}
)
ORG_ADMIN_GRANTABLE_ROLES: Final[frozenset[str]] = frozenset(
    {"org_admin", "content_admin", "teacher", "parent", "student", "instructor", "viewer"}
)
PUBLIC_REGISTRATION_ROLES: Final[frozenset[str]] = frozenset(
    {"student", "teacher", "instructor", "parent"}
)


def validate_role_allowlist(requested: Iterable[str], canonical: frozenset[str], *, scope: str) -> tuple[str, ...]:
    roles = tuple(dict.fromkeys(requested))
    unknown = set(roles) - canonical
    if unknown:
        raise RuntimeError(f"Unknown {scope} role(s) in authorization policy: {sorted(unknown)}")
    if not roles:
        raise RuntimeError(f"At least one {scope} role is required")
    return roles


def normalize_platform_role(role: str) -> str:
    normalized = role.strip().lower()
    if normalized not in PLATFORM_ROLES:
        raise ValueError("Unsupported platform role")
    return normalized


def can_manage_platform_target(actor_role: str, target_role: str, requested_role: str | None = None) -> bool:
    if actor_role == "super_admin":
        return True
    if actor_role != "admin":
        return False
    if target_role in PLATFORM_ADMIN_ROLES:
        return False
    return requested_role is None or requested_role not in PLATFORM_ADMIN_ROLES


def require_owner_or_forum_moderator(*, actor_id: UUID, actor_role: str, owner_id: UUID) -> None:
    if actor_id != owner_id and actor_role not in FORUM_MODERATOR_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this forum content.",
        )


def security_event(
    *,
    action: str,
    result: str,
    actor_id: UUID | str | None = None,
    target_type: str | None = None,
    target_id: UUID | str | None = None,
    reason: str | None = None,
    request_id: str | None = None,
) -> None:
    event_names = {
        "authentication": "auth.login.failed" if result == "denied" else "auth.login.succeeded",
        "rate_limit": "rate_limit.triggered",
        "upload_rejection": "upload.rejected",
    }
    metrics.increment("echoed_security_events_total", action=action, result=result)
    emit_event(
        event_names.get(action, f"security.{action}.{result}"),
        component="security",
        request_id=request_id,
        actor_id=actor_id or "anonymous",
        action=action,
        target_type=target_type or "none",
        target_id=target_id or "none",
        result=result,
        reason=reason or "none",
    )
