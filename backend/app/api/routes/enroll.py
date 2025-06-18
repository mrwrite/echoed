from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import StudentCourse
from app.database import SessionLocal
from app.deps import get_db, get_current_user
from app.schemas import EnrollRequest

router = APIRouter()

@router.post("/enroll")
def enroll_in_course(
    request: EnrollRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Only students can enroll in courses.")

    existing = db.query(StudentCourse).filter_by(
        student_id=current_user.id,
        course_id=request.course_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already enrolled in this course.")

    enrollment = StudentCourse(student_id=current_user.id, course_id=request.course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment
