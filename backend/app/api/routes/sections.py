from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_org_roles
from app.models import Section, Enrollment, OrganizationMembership, User
from app.enum import SectionMode
from app.schemas import SectionCreateRequest, SectionResponse, EnrollmentCreateRequest, EnrollmentResponse
from app.section_scope import require_scoped_section

router = APIRouter()


@router.post("/sections", response_model=SectionResponse)
def create_section(
    payload: SectionCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_org_roles("teacher", "org_admin", "instructor")),
):
    section = Section(
        organization_id=membership.organization_id,
        course_version_id=payload.course_version_id,
        name=payload.name,
        mode=SectionMode(payload.mode),
        start_date=payload.start_date,
        end_date=payload.end_date,
        created_by=current_user.id,
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    return section


@router.get("/sections", response_model=list[SectionResponse])
def list_sections(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    created_sections = (
        db.query(Section).filter(Section.created_by == current_user.id).all()
    )
    enrolled_sections = (
        db.query(Section)
        .join(Enrollment, Enrollment.section_id == Section.id)
        .filter(Enrollment.user_id == current_user.id)
        .all()
    )
    section_map = {section.id: section for section in created_sections + enrolled_sections}
    return list(section_map.values())


@router.get("/sections/{section_id}/roster", response_model=list[EnrollmentResponse])
def section_roster(
    section_id: str,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("teacher", "org_admin", "instructor")),
):
    section = require_scoped_section(db, membership, section_id)
    return db.query(Enrollment).filter(Enrollment.section_id == section.id).all()


@router.post("/sections/{section_id}/enrollments", response_model=EnrollmentResponse)
def add_enrollment(
    section_id: str,
    payload: EnrollmentCreateRequest,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("teacher", "org_admin", "instructor")),
):
    section = require_scoped_section(db, membership, section_id)
    if not payload.user_id and not payload.email:
        raise HTTPException(status_code=400, detail="Provide a user_id or email")

    user = None
    if payload.user_id:
        user = db.query(User).filter(User.id == payload.user_id).first()
    elif payload.email:
        user = db.query(User).filter(User.email == payload.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    active_membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == membership.organization_id,
            OrganizationMembership.user_id == user.id,
            OrganizationMembership.status == "active",
        )
        .first()
    )
    if active_membership is None:
        raise HTTPException(status_code=400, detail="User is not an active member of this organization")

    enrollment = Enrollment(section_id=section.id, user_id=user.id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment
