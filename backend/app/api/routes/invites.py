from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_org_roles
from app.enum import OrganizationRole
from app.models import OrganizationInvite, OrganizationMembership, Organization
from app.schemas import (
    OrganizationInviteCreate,
    OrganizationInviteResponse,
    InviteAcceptRequest,
)

router = APIRouter()


@router.post("/orgs/{org_id}/invites", response_model=OrganizationInviteResponse)
def create_invite(
    org_id: str,
    payload: OrganizationInviteCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_org_roles("org_admin")),
):
    try:
        org_uuid = uuid.UUID(org_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid organization id") from exc
    organization = db.query(Organization).filter(Organization.id == org_uuid).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if str(membership.organization_id) != str(org_id):
        raise HTTPException(status_code=403, detail="Organization mismatch")

    expires_at = payload.expires_at or (datetime.utcnow() + timedelta(days=7))
    invite = OrganizationInvite(
        organization_id=org_uuid,
        email=payload.email,
        role=OrganizationRole(payload.role),
        token=str(uuid.uuid4()),
        expires_at=expires_at,
        invited_by_user_id=current_user.id,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.get("/orgs/{org_id}/invites", response_model=list[OrganizationInviteResponse])
def list_invites(
    org_id: str,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("org_admin")),
):
    try:
        org_uuid = uuid.UUID(org_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid organization id") from exc
    if str(membership.organization_id) != str(org_id):
        raise HTTPException(status_code=403, detail="Organization mismatch")
    return (
        db.query(OrganizationInvite)
        .filter(OrganizationInvite.organization_id == org_uuid)
        .all()
    )


@router.post("/invites/accept")
def accept_invite(
    payload: InviteAcceptRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    invite = (
        db.query(OrganizationInvite)
        .filter(OrganizationInvite.token == payload.token)
        .first()
    )
    if not invite:
        raise HTTPException(status_code=404, detail="Invite not found")
    if invite.accepted_at:
        raise HTTPException(status_code=400, detail="Invite already accepted")
    if invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invite expired")

    membership = OrganizationMembership(
        organization_id=invite.organization_id,
        user_id=current_user.id,
        role=invite.role,
    )
    invite.accepted_at = datetime.utcnow()
    db.add(membership)
    db.commit()
    return {"message": "Invite accepted"}
