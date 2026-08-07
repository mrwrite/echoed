from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import uuid

from app.auth import get_current_user as auth_get_current_user
from app.database import SessionLocal
from app.enum import MembershipStatus
from app.models import User, OrganizationMembership
from app.security import ORGANIZATION_ROLES, PLATFORM_ROLES, validate_role_allowlist
from app.observability import emit_event, metrics


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError:
        db.rollback()
        metrics.increment("echoed_database_operations_total", operation="authorization_session", result="failure")
        emit_event("database.operation_failed", level=40, component="database", operation="authorization_session", result="failure")
        raise
    finally:
        db.close()


get_current_user = auth_get_current_user


def require_roles(*roles: str):
    allowed_roles = validate_role_allowlist(roles, PLATFORM_ROLES, scope="platform")

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            metrics.increment("echoed_authorization_denials_total", scope="platform", reason="role")
            emit_event(
                "authorization.denied",
                level=30,
                component="authorization",
                actor_id=current_user.id,
                actor_role=current_user.role,
                scope="platform",
                reason="role_not_allowed",
                result="denied",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_user

    return role_checker


def get_active_org_id(
    x_org_id: str | None = Header(default=None, alias="X-Org-Id"),
) -> uuid.UUID | None:
    if not x_org_id:
        return None
    try:
        return uuid.UUID(x_org_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid organization id.",
        ) from exc


def require_org_roles(*roles: str):
    allowed_roles = validate_role_allowlist(roles, ORGANIZATION_ROLES, scope="organization")

    def org_role_checker(
        active_org_id: str | None = Depends(get_active_org_id),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> OrganizationMembership:
        if not active_org_id:
            metrics.increment("echoed_authorization_denials_total", scope="organization", reason="missing_context")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing active organization.",
            )
        membership = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.organization_id == active_org_id,
                OrganizationMembership.user_id == current_user.id,
                OrganizationMembership.status == MembershipStatus.ACTIVE,
            )
            .first()
        )
        if current_user.role == "super_admin":
            return membership or OrganizationMembership(
                organization_id=active_org_id,
                user_id=current_user.id,
                role="super_admin",
                status=MembershipStatus.ACTIVE,
            )
        if not membership or membership.role.value not in allowed_roles:
            reason = "inactive_or_cross_organization" if not membership else "role"
            metrics.increment("echoed_authorization_denials_total", scope="organization", reason=reason)
            emit_event(
                "authorization.denied",
                level=30,
                component="authorization",
                actor_id=current_user.id,
                actor_role=current_user.role,
                scope="organization",
                reason=reason,
                result="denied",
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return membership

    return org_role_checker
