from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_org_roles
from app.models import Assignment, AssignmentSubmission
from app.enum import AssignmentTargetType, AssignmentSubmissionStatus
from app.schemas import (
    AssignmentCreateRequest,
    AssignmentResponse,
    AssignmentSubmissionRequest,
    AssignmentSubmissionResponse,
)

router = APIRouter()


@router.post("/sections/{section_id}/assignments", response_model=AssignmentResponse)
def create_assignment(
    section_id: str,
    payload: AssignmentCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_org_roles("teacher", "org_admin", "instructor")),
):
    assignment = Assignment(
        section_id=section_id,
        target_type=AssignmentTargetType(payload.target_type),
        target_id=payload.target_id,
        due_at=payload.due_at,
        instructions=payload.instructions,
        created_by=current_user.id,
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.get("/sections/{section_id}/assignments", response_model=list[AssignmentResponse])
def list_assignments(
    section_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return db.query(Assignment).filter(Assignment.section_id == section_id).all()


@router.post("/assignments/{assignment_id}/submit", response_model=AssignmentSubmissionResponse)
def submit_assignment(
    assignment_id: str,
    payload: AssignmentSubmissionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    submission = (
        db.query(AssignmentSubmission)
        .filter(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.user_id == current_user.id,
        )
        .first()
    )
    if not submission:
        submission = AssignmentSubmission(
            assignment_id=assignment_id,
            user_id=current_user.id,
        )
        db.add(submission)

    submission.status = AssignmentSubmissionStatus(payload.status)
    submission.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(submission)
    return submission
