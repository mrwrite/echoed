from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import uuid

from app.auth import get_current_user as auth_get_current_user
from app.database import SessionLocal
from app.enum import MembershipStatus
from app.models import User, OrganizationMembership


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


get_current_user = auth_get_current_user


def require_roles(*roles: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
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
    def org_role_checker(
        active_org_id: str | None = Depends(get_active_org_id),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> OrganizationMembership:
        if current_user.role == "super_admin":
            membership = (
                db.query(OrganizationMembership)
                .filter(OrganizationMembership.organization_id == active_org_id)
                .first()
            )
            if membership:
                return membership
        if not active_org_id:
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
        if not membership or membership.role.value not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return membership

    return org_role_checker
