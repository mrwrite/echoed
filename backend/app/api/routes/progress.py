from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.progress import (
    create_student_unit_progress,
    update_student_unit_progress_status,
    get_student_unit_progress,
    get_current_segment_for_unit
)
from app.models import SegmentProgress
from app.enum import ProgressStatus
from app.schemas import CompleteSegmentRequest
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()

@router.post("/unit")
def create_unit_progress(student_course_id: UUID, unit_id: UUID, db: Session = Depends(get_db)):
    return create_student_unit_progress(db, student_course_id, unit_id)

@router.put("/unit/{progress_id}")
def update_unit_progress(progress_id: UUID, status: str, db: Session = Depends(get_db)):
    return update_student_unit_progress_status(db, progress_id, status)

@router.get("/unit")
def get_unit_progress(student_course_id: UUID, unit_id: UUID, db: Session = Depends(get_db)):
    return get_student_unit_progress(db, student_course_id, unit_id)

@router.get("/segment")
def get_segment(student_unit_id: UUID, db: Session = Depends(get_db)):
    segment = get_current_segment_for_unit(db, student_unit_id)
    if not segment:
        raise HTTPException(status_code=404, detail="No segment found.")
    return segment


@router.post("/segment/complete")
def complete_segment(
    request: CompleteSegmentRequest,
    db: Session = Depends(get_db)
):
    segment = db.query(SegmentProgress).filter_by(
        student_unit_id=request.student_unit_id,
        lesson_id=request.lesson_id
    ).first()

    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found.")

    segment.status = ProgressStatus.COMPLETED
    db.commit()
    db.refresh(segment)

    return {"message": "Segment marked as completed.", "segment_id": segment.id}
