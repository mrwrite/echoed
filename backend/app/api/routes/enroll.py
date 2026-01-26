from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models import StudentCourse
from app.deps import require_roles
from app.database import get_db
from app.schemas import EnrollRequest, AssignCourseRequest

router = APIRouter()

@router.post("/enroll")
def enroll_in_course(
    request: EnrollRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("student")),
):
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


@router.post("/assign-course")
def assign_course_to_student(
    request: AssignCourseRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    existing = db.query(StudentCourse).filter_by(
        student_id=request.student_id,
        course_id=request.course_id,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Student already enrolled in this course.")

    enrollment = StudentCourse(student_id=request.student_id, course_id=request.course_id)
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    return enrollment
