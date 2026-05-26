from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.crud.certifications import evaluate_certification
from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import Certification, CertificationRequirement, Program, StudentCertification, User
from app.schemas import (
    CertificationCreateRequest,
    CertificationEvaluationResponse,
    CertificationRequirementResponse,
    CertificationResponse,
    StudentCertificationResponse,
)

router = APIRouter()


def _serialize_certification(certification: Certification) -> CertificationResponse:
    return CertificationResponse(
        id=certification.id,
        program_id=certification.program_id,
        badge_id=certification.badge_id,
        title=certification.title,
        description=certification.description,
        created_at=certification.created_at,
        requirements=[
            CertificationRequirementResponse(
                id=requirement.id,
                requirement_type=requirement.requirement_type,
                course_id=requirement.course_id,
                assessment_id=requirement.assessment_id,
                minimum_score=requirement.minimum_score,
            )
            for requirement in certification.requirements
        ],
    )


def _serialize_student_certification(student_certification: StudentCertification) -> StudentCertificationResponse:
    return StudentCertificationResponse(
        id=student_certification.id,
        student_id=student_certification.student_id,
        certification_id=student_certification.certification_id,
        awarded_at=student_certification.awarded_at,
        score_snapshot=student_certification.score_snapshot,
        certification=_serialize_certification(student_certification.certification),
    )


@router.get("/certifications", response_model=list[CertificationResponse])
def list_certifications(
    program_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Certification).options(joinedload(Certification.requirements))
    if program_id:
        query = query.filter(Certification.program_id == program_id)
    return [_serialize_certification(certification) for certification in query.all()]


@router.post("/certifications", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
def create_certification(
    payload: CertificationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    program = db.get(Program, payload.program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    certification = Certification(
        program_id=payload.program_id,
        badge_id=payload.badge_id,
        title=payload.title,
        description=payload.description,
    )
    db.add(certification)
    db.flush()

    for requirement in payload.requirements:
        db.add(
            CertificationRequirement(
                certification_id=certification.id,
                requirement_type=requirement.requirement_type,
                course_id=requirement.course_id,
                assessment_id=requirement.assessment_id,
                minimum_score=requirement.minimum_score,
            )
        )

    db.commit()
    db.refresh(certification)
    certification = (
        db.query(Certification)
        .options(joinedload(Certification.requirements))
        .filter(Certification.id == certification.id)
        .first()
    )
    return _serialize_certification(certification)


@router.post("/certifications/{certification_id}/evaluate", response_model=CertificationEvaluationResponse)
def evaluate_student_certification(
    certification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student")),
):
    certification = (
        db.query(Certification)
        .options(joinedload(Certification.requirements), joinedload(Certification.program))
        .filter(Certification.id == certification_id)
        .first()
    )
    if not certification:
        raise HTTPException(status_code=404, detail="Certification not found")

    awarded, missing_requirements, student_certification = evaluate_certification(
        db,
        certification,
        current_user.id,
    )
    return CertificationEvaluationResponse(
        certification_id=certification.id,
        awarded=awarded,
        missing_requirements=missing_requirements,
        student_certification=(
            _serialize_student_certification(student_certification)
            if student_certification
            else None
        ),
    )


@router.get("/students/me/certifications", response_model=list[StudentCertificationResponse])
def list_my_certifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student")),
):
    issued = (
        db.query(StudentCertification)
        .options(
            joinedload(StudentCertification.certification).joinedload(Certification.requirements)
        )
        .filter(StudentCertification.student_id == current_user.id)
        .order_by(StudentCertification.awarded_at.desc())
        .all()
    )
    return [_serialize_student_certification(item) for item in issued]
