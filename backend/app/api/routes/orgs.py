import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import create_access_token
from app.database import get_db
from app.deps import get_current_user
from app.enum import OrganizationType, OrganizationRole
from app.models import Organization, OrganizationMembership
from app.schemas import OrganizationCreate, OrganizationResponse, OrganizationUpdate

router = APIRouter()


@router.get("/orgs", response_model=list[OrganizationResponse])
def list_orgs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    memberships = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.user_id == current_user.id)
        .all()
    )
    org_ids = [membership.organization_id for membership in memberships]
    organizations = db.query(Organization).filter(Organization.id.in_(org_ids)).all()
    role_by_org = {membership.organization_id: membership.role.value for membership in memberships}
    return [
        {
            "id": org.id,
            "name": org.name,
            "type": org.type.value,
            "country": org.country,
            "timezone": org.timezone,
            "created_at": org.created_at,
            "role": role_by_org.get(org.id),
        }
        for org in organizations
    ]


@router.post("/orgs", response_model=OrganizationResponse)
def create_org(
    payload: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    organization = Organization(
        name=payload.name,
        type=OrganizationType(payload.type),
        country=payload.country,
        timezone=payload.timezone,
    )
    db.add(organization)
    db.flush()

    membership = OrganizationMembership(
        organization_id=organization.id,
        user_id=current_user.id,
        role=OrganizationRole.ORG_ADMIN,
    )
    db.add(membership)
    db.commit()
    db.refresh(organization)
    return organization


@router.patch("/orgs/{org_id}", response_model=OrganizationResponse)
def update_org(
    org_id: str,
    payload: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        org_uuid = uuid.UUID(org_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid organization id") from exc

    organization = db.query(Organization).filter(Organization.id == org_uuid).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    if current_user.role != "super_admin":
        membership = (
            db.query(OrganizationMembership)
            .filter(
                OrganizationMembership.organization_id == org_uuid,
                OrganizationMembership.user_id == current_user.id,
            )
            .first()
        )
        allowed_roles = {
            OrganizationRole.ORG_ADMIN.value,
            OrganizationRole.CONTENT_ADMIN.value,
        }
        if not membership or membership.role.value not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to update this organization.",
            )

    organization.name = payload.name
    db.commit()
    db.refresh(organization)
    return organization


@router.post("/orgs/{org_id}/switch")
def switch_org(
    org_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        org_uuid = uuid.UUID(org_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid organization id") from exc
    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == org_uuid,
            OrganizationMembership.user_id == current_user.id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=404, detail="Organization not found")

    access_token = create_access_token(
        data={
            "sub": current_user.username,
            "user_id": str(current_user.id),
            "fullname": f"{current_user.firstname} {current_user.lastname}",
            "role": current_user.role,
            "active_org_id": str(membership.organization_id),
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}
