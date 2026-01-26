from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.deps import require_roles
from app.models import StudentCourse, StudentUnitProgress, SegmentProgress, Unit, Lesson
from app.schemas import StartCourseRequest, SegmentResponse
from app.enum import ProgressStatus  # assuming you created this enum
from app.crud import progress as crud
from app.log import logger
from datetime import datetime

router = APIRouter()

@router.post("/start-course", response_model=SegmentResponse)
def start_course(
    request: StartCourseRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_roles("student")),
):   
    
    logger.debug("RAW Request Data: %s", request)
    # Check enrollment
    enrollment = db.query(StudentCourse).filter_by(
        student_id=current_user.id,
        course_id=request.course_id
    ).first()

    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course.")

    if enrollment.status == "completed":
        raise HTTPException(status_code=400, detail="Course already completed")

    # Attempt to find an existing unit already in progress
    unit_progress = (
        db.query(StudentUnitProgress)
        .filter_by(student_course_id=enrollment.id, status=ProgressStatus.IN_PROGRESS)
        .first()
    )

    if unit_progress:
        unit = db.get(Unit, unit_progress.unit_id)
    else:
        # No active progress yet – start with the first unit in the course
        unit = (
            db.query(Unit)
            .filter_by(course_id=request.course_id)
            .order_by(Unit.order)
            .first()
        )
        if not unit:
            raise HTTPException(status_code=404, detail="No units found for this course.")

        unit_progress = (
            db.query(StudentUnitProgress)
            .filter_by(student_course_id=enrollment.id, unit_id=unit.id)
            .first()
        )
        if not unit_progress:
            unit_progress = StudentUnitProgress(
                student_course_id=enrollment.id,
                unit_id=unit.id,
                status=ProgressStatus.IN_PROGRESS,
            )
            db.add(unit_progress)
            db.commit()
            db.refresh(unit_progress)

    # Ensure segment progress rows exist for the chosen unit
    lessons = (
        db.query(Lesson)
        .filter_by(unit_id=unit.id)
        .order_by(Lesson.order)
        .all()
    )
    if not lessons:
        raise HTTPException(status_code=404, detail="No lessons found for this unit.")

    for lesson in lessons:
        existing_segment = db.query(SegmentProgress).filter_by(
            student_unit_id=unit_progress.id,
            lesson_id=lesson.id,
        ).first()
        if not existing_segment:
            seg = SegmentProgress(
                student_unit_id=unit_progress.id,
                lesson_id=lesson.id,
                status=ProgressStatus.NOT_STARTED,
            )
            db.add(seg)

    db.commit()

    # Retrieve the current segment for this unit progress
    segment = crud.get_current_segment_for_unit(db, unit_progress.id)
    if not segment:
        raise HTTPException(status_code=404, detail="No segment found.")

    if segment.status == ProgressStatus.NOT_STARTED:
        segment.status = ProgressStatus.IN_PROGRESS
        segment.started_at = datetime.utcnow()
        segment.last_updated = datetime.utcnow()
        unit_progress.status = ProgressStatus.IN_PROGRESS
        if not unit_progress.started_at:
            unit_progress.started_at = datetime.utcnow()
        unit_progress.last_updated = datetime.utcnow()
        enrollment.last_activity_at = datetime.utcnow()
        db.commit()

    return SegmentResponse(
        lesson_id=segment.lesson_id,
        status=segment.status,
        unit_progress_id=unit_progress.id,
    )
