from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud import progress as crud
from app.models import SegmentProgress, StudentUnitProgress
from app.enum import ProgressStatus
from app.schemas import CompleteSegmentRequest
from uuid import UUID
from app.deps import require_roles, get_current_user
from app.models import StudentCourse, User
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/unit")
def create_unit_progress(
    student_course_id: UUID,
    unit_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    return crud.create_student_unit_progress(db, student_course_id, unit_id)

@router.put("/unit/{progress_id}")
def update_unit_progress(
    progress_id: UUID,
    status: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    return crud.update_student_unit_progress_status(db, progress_id, status)

@router.get("/unit")
def get_unit_progress(
    student_course_id: UUID,
    unit_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    return crud.get_student_unit_progress(db, student_course_id, unit_id)

@router.get("/segment")
def get_segment(
    student_unit_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    segment = crud.get_current_segment_for_unit(db, student_unit_id)
    if not segment:
        raise HTTPException(status_code=404, detail="No segment found.")
    if segment.status == ProgressStatus.NOT_STARTED:
        crud.update_segment_progress_status(db, segment.id, ProgressStatus.IN_PROGRESS)
        segment = crud.get_current_segment_for_unit(db, student_unit_id) or segment
    return segment


@router.post("/segment/complete")
def complete_segment(
    request: CompleteSegmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    segment = db.query(SegmentProgress).filter_by(
        student_unit_id=request.student_unit_id,
        lesson_id=request.lesson_id
    ).first()

    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found.")

    updated = crud.update_segment_progress_status(db, segment.id, ProgressStatus.COMPLETED)

    unit_progress = db.get(StudentUnitProgress, segment.student_unit_id)

    next_segment = crud.get_current_segment_for_unit(db, unit_progress.id)
    next_unit_progress_id = unit_progress.id

    if not next_segment:
        next_unit_progress = (
            db.query(StudentUnitProgress)
            .filter(
                StudentUnitProgress.student_course_id == unit_progress.student_course_id,
                StudentUnitProgress.status == ProgressStatus.IN_PROGRESS,
            )
            .first()
        )
        if next_unit_progress and next_unit_progress.id != unit_progress.id:
            next_segment = crud.get_current_segment_for_unit(db, next_unit_progress.id)
            next_unit_progress_id = next_unit_progress.id

    return {
        "message": "Segment marked as completed.",
        "segment_id": updated.id,
        "next_segment": {
            "lesson_id": next_segment.lesson_id,
            "status": next_segment.status,
            "unit_progress_id": next_unit_progress_id,
        }
        if next_segment
        else None,
    }


@router.get("/streak")
def get_streak(
    user_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if user_id and current_user.role not in {"admin", "teacher"}:
        raise HTTPException(status_code=403, detail="Not authorized")
    target_user_id = user_id or current_user.id

    completed_segments = (
        db.query(SegmentProgress)
        .join(StudentUnitProgress, StudentUnitProgress.id == SegmentProgress.student_unit_id)
        .join(StudentCourse, StudentCourse.id == StudentUnitProgress.student_course_id)
        .filter(
            StudentCourse.student_id == target_user_id,
            SegmentProgress.status == ProgressStatus.COMPLETED,
        )
        .all()
    )

    completed_dates = {
        seg.completed_at.date()
        for seg in completed_segments
        if seg.completed_at is not None
    }

    if not completed_dates:
        return {"streak_days": 0, "last_active": None}

    today = datetime.utcnow().date()
    streak = 0
    day = today
    while day in completed_dates:
        streak += 1
        day = day - timedelta(days=1)

    last_active = max(completed_dates)
    return {"streak_days": streak, "last_active": last_active}
