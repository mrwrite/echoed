import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import ActiveOrganizationContext, create_access_token
from app.database import get_db
from app.deps import get_current_user
from app.enum import OrganizationType, OrganizationRole
from app.models import Enrollment, Organization, OrganizationMembership, Section, User
from app.schemas import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationMemberResponse,
    OrganizationSectionResponse,
    OrganizationSwitchResponse,
    OrganizationUpdate,
)
from app.deps import require_org_roles

router = APIRouter()


def _require_requested_organization(org_id: str, membership: OrganizationMembership) -> uuid.UUID:
    try:
        org_uuid = uuid.UUID(org_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid organization id") from exc
    if membership.organization_id != org_uuid:
        raise HTTPException(status_code=403, detail="Organization mismatch")
    return org_uuid


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


@router.get("/orgs/{org_id}/members", response_model=list[OrganizationMemberResponse])
def list_org_members(
    org_id: str,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("org_admin")),
):
    org_uuid = _require_requested_organization(org_id, membership)
    rows = (
        db.query(OrganizationMembership, User)
        .join(User, User.id == OrganizationMembership.user_id)
        .filter(OrganizationMembership.organization_id == org_uuid)
        .order_by(User.firstname.asc(), User.lastname.asc(), User.username.asc())
        .all()
    )
    return [
        {
            "id": row.id,
            "user_id": user.id,
            "display_name": f"{user.firstname or ''} {user.lastname or ''}".strip() or user.username,
            "username": user.username,
            "role": row.role.value,
            "status": row.status.value,
            "joined_at": row.created_at,
        }
        for row, user in rows
    ]


@router.get("/orgs/{org_id}/sections", response_model=list[OrganizationSectionResponse])
def list_org_sections(
    org_id: str,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("org_admin")),
):
    org_uuid = _require_requested_organization(org_id, membership)
    sections = (
        db.query(Section)
        .filter(Section.organization_id == org_uuid)
        .order_by(Section.name.asc(), Section.created_at.asc())
        .all()
    )
    results = []
    for section in sections:
        enrollments = db.query(Enrollment).filter(Enrollment.section_id == section.id).all()
        results.append(
            {
                "id": section.id,
                "organization_id": section.organization_id,
                "course_version_id": section.course_version_id,
                "name": section.name,
                "mode": section.mode.value,
                "start_date": section.start_date,
                "end_date": section.end_date,
                "created_by": section.created_by,
                "learner_count": sum(1 for row in enrollments if row.role_in_section == "student"),
                "teacher_count": sum(1 for row in enrollments if row.role_in_section in {"teacher", "instructor"}),
            }
        )
    return results


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


@router.post("/orgs/{org_id}/switch", response_model=OrganizationSwitchResponse)
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

    organization = db.query(Organization).filter(Organization.id == membership.organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")

    active_organization = ActiveOrganizationContext(
        organization_id=organization.id,
        organization_name=organization.name,
        organization_type=organization.type.value,
        organization_role=membership.role.value,
    )

    access_token = create_access_token(
        data={
            "sub": current_user.username,
            "user_id": str(current_user.id),
            "fullname": f"{current_user.firstname} {current_user.lastname}",
            "role": current_user.role,
            "active_org_id": str(active_organization.organization_id),
        }
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "active_org_id": str(active_organization.organization_id),
        "active_org_role": active_organization.organization_role,
        "active_organization": {
            "id": active_organization.organization_id,
            "name": active_organization.organization_name,
            "type": active_organization.organization_type,
            "role": active_organization.organization_role,
        },
    }
