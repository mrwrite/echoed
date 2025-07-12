from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.auth import get_current_user
from app.models import StudentCourse, StudentUnitProgress, SegmentProgress, Course, Unit, Lesson
from app.schemas import StartCourseRequest, SegmentResponse
from app.enum import ProgressStatus  # assuming you created this enum

router = APIRouter()

@router.post("/start-course", response_model=SegmentResponse)
def start_course(
    request: StartCourseRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):   
    
    print("RAW Request Data:", request)    
    # Check enrollment
    enrollment = db.query(StudentCourse).filter_by(
        student_id=current_user.id,
        course_id=request.course_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course.")

    # Get first unit in course
    unit = db.query(Unit).filter_by(course_id=request.course_id).order_by(Unit.order).first()
    if not unit:
        raise HTTPException(status_code=404, detail="No units found for this course.")

    # Create StudentUnitProgress if it doesn’t exist
    unit_progress = db.query(StudentUnitProgress).filter_by(
        student_course_id=enrollment.id,
        unit_id=unit.id
    ).first()

    if not unit_progress:
        unit_progress = StudentUnitProgress(
            student_course_id=enrollment.id,
            unit_id=unit.id,
            status=ProgressStatus.IN_PROGRESS
        )
        db.add(unit_progress)
        db.commit()
        db.refresh(unit_progress)

    # Get all lessons in unit
    lessons = db.query(Lesson).filter_by(unit_id=unit.id).order_by(Lesson.order).all()
    if not lessons:
        raise HTTPException(status_code=404, detail="No lessons found for this unit.")

    # Create SegmentProgress rows if they don’t exist
    segment_progress_list = []
    for idx, lesson in enumerate(lessons):
        existing_segment = db.query(SegmentProgress).filter_by(
            student_unit_id=unit_progress.id,
            lesson_id=lesson.id
        ).first()

        if not existing_segment:
            segment = SegmentProgress(
                student_unit_id=unit_progress.id,
                lesson_id=lesson.id,
                status=ProgressStatus.NOT_STARTED
            )
            db.add(segment)
            segment_progress_list.append(segment)
        else:
            segment_progress_list.append(existing_segment)

    db.commit()

    # Return the first segment to begin course flow
    first_segment = segment_progress_list[0]
    return SegmentResponse(
        lesson_id=first_segment.lesson_id,
        status=first_segment.status,
        unit_progress_id=unit_progress.id
    )
