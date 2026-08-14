from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.audit import append_audit_event
from app.deps import get_current_user, require_org_roles
from app.enum import MembershipStatus, OrganizationRole
from app.models import OrganizationInvite, OrganizationMembership, Organization
from app.schemas import (
    OrganizationInviteCreate,
    OrganizationInviteCreatedResponse,
    OrganizationInviteResponse,
    InviteAcceptRequest,
)

router = APIRouter()

from app.rate_limit import enforce_rate_limit
from app.security import ORG_ADMIN_GRANTABLE_ROLES, security_event


@router.post("/orgs/{org_id}/invites", response_model=OrganizationInviteCreatedResponse)
def create_invite(
    org_id: str,
    payload: OrganizationInviteCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_org_roles("org_admin")),
):
    enforce_rate_limit(request, "invite_manage", actor_id=current_user.id)
    try:
        org_uuid = uuid.UUID(org_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid organization id") from exc
    organization = db.query(Organization).filter(Organization.id == org_uuid).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    if str(membership.organization_id) != str(org_id):
        raise HTTPException(status_code=403, detail="Organization mismatch")

    if payload.role not in ORG_ADMIN_GRANTABLE_ROLES:
        raise HTTPException(
            status_code=403,
            detail="This organization role cannot be granted through invitations.",
        )
    expires_at = payload.expires_at or (datetime.utcnow() + timedelta(days=7))
    invite = OrganizationInvite(
        id=uuid.uuid4(),
        organization_id=org_uuid,
        email=payload.email,
        role=OrganizationRole(payload.role),
        token=str(uuid.uuid4()),
        expires_at=expires_at,
        invited_by_user_id=current_user.id,
    )
    db.add(invite)
    append_audit_event(
        db,
        action="organization.invite.created",
        actor_id=current_user.id,
        actor_role=current_user.role,
        target_type="organization_invite",
        target_id=invite.id,
        organization_id=org_uuid,
        after={"role": payload.role, "status": "pending"},
        request_id=getattr(request.state, "request_id", None),
    )
    db.commit()
    db.refresh(invite)
    security_event(
        action="organization_invite_create",
        result="allowed",
        actor_id=current_user.id,
        target_type="organization",
        target_id=org_uuid,
        reason=f"role_{payload.role}",
        request_id=getattr(request.state, "request_id", None),
    )
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
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    enforce_rate_limit(request, "invite_accept", actor_id=current_user.id)
    invite = (
        db.query(OrganizationInvite)
        .filter(OrganizationInvite.token == payload.token)
        .first()
    )
    if not invite:
        raise HTTPException(status_code=404, detail="Invitation is invalid or unavailable")
    if invite.accepted_at:
        raise HTTPException(status_code=409, detail="Invitation is invalid or unavailable")
    if invite.expires_at < datetime.utcnow():
        raise HTTPException(status_code=409, detail="Invitation is invalid or unavailable")

    existing_membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == invite.organization_id,
            OrganizationMembership.user_id == current_user.id,
        )
        .first()
    )
    previous_role = existing_membership.role.value if existing_membership else None
    previous_status = existing_membership.status.value if existing_membership else None
    if existing_membership:
        existing_membership.role = invite.role
        existing_membership.status = MembershipStatus.ACTIVE
        membership = existing_membership
    else:
        membership = OrganizationMembership(
            id=uuid.uuid4(),
            organization_id=invite.organization_id,
            user_id=current_user.id,
            role=invite.role,
            status=MembershipStatus.ACTIVE,
        )

    invite.accepted_at = datetime.utcnow()
    if not existing_membership:
        db.add(membership)
    append_audit_event(
        db,
        action="organization.invite.accepted",
        actor_id=current_user.id,
        actor_role=current_user.role,
        target_type="organization_membership",
        target_id=membership.id,
        organization_id=invite.organization_id,
        before={"role": previous_role, "status": previous_status},
        after={"role": invite.role.value, "status": MembershipStatus.ACTIVE.value},
        request_id=getattr(request.state, "request_id", None),
    )
    db.commit()
    return {"message": "Invite accepted"}
