from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import progress as crud
from app.database import get_db
from app.deps import get_current_user, require_roles
from app.enum import ProgressStatus
from app.models import SegmentProgress, StudentCourse, StudentUnitProgress, User
from app.schemas import CompleteSegmentRequest, SegmentResponse

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


@router.get("/segment", response_model=SegmentResponse)
def get_segment(
    student_unit_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    unit_progress = db.get(StudentUnitProgress, student_unit_id)
    if not unit_progress:
        raise HTTPException(status_code=404, detail="Unit progress not found.")

    current_segment = crud.resolve_governed_segment_for_unit_progress(
        db, student_unit_id
    )
    if current_segment is not None:
        return SegmentResponse(**current_segment)

    progression = crud.resolve_governed_progression(db, unit_progress.student_course_id)
    if progression["delivery_state"] != "governed_available":
        return SegmentResponse(
            unit_progress_id=student_unit_id,
            delivery_state=str(progression["delivery_state"]),
            detail=str(progression.get("detail") or ""),
        )

    return SegmentResponse(**progression)


@router.post("/segment/complete")
def complete_segment(
    request: CompleteSegmentRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    segment = (
        db.query(SegmentProgress)
        .filter_by(
            student_unit_id=request.student_unit_id,
            lesson_id=request.lesson_id,
        )
        .first()
    )

    if not segment:
        raise HTTPException(status_code=404, detail="Segment not found.")

    updated = crud.update_segment_progress_status(db, segment.id, ProgressStatus.COMPLETED)
    unit_progress = db.get(StudentUnitProgress, segment.student_unit_id)
    next_state = crud.resolve_governed_progression(db, unit_progress.student_course_id)

    return {
        "message": "Segment marked as completed.",
        "segment_id": updated.id,
        "next_segment": SegmentResponse(**next_state).model_dump(),
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
