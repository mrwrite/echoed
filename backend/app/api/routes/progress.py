from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.progress import (
    create_student_unit_progress,
    update_student_unit_progress_status,
    get_student_unit_progress
)
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
