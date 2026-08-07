from datetime import datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.crud import progress as crud
from app.database import get_db
from app.deps import get_current_user, require_roles
from app.enum import ProgressStatus
from app.models import Enrollment, Section, SegmentProgress, StudentCourse, StudentUnitProgress, User
from app.schemas import CompleteSegmentRequest, SegmentResponse

router = APIRouter()


def _can_access_student_course(db: Session, actor: User, student_course: StudentCourse) -> bool:
    if actor.role in {"admin", "super_admin"}:
        return True
    if actor.role == "student":
        return student_course.student_id == actor.id
    if actor.role in {"teacher", "instructor"} and student_course.section_id:
        return (
            db.query(Section)
            .filter(Section.id == student_course.section_id, Section.created_by == actor.id)
            .first()
            is not None
            or db.query(Enrollment)
            .filter(
                Enrollment.section_id == student_course.section_id,
                Enrollment.user_id == actor.id,
                Enrollment.role_in_section.in_(["teacher", "instructor"]),
                Enrollment.status == "active",
            )
            .first()
            is not None
        )
    return False


def _require_student_course(db: Session, actor: User, student_course_id: UUID) -> StudentCourse:
    student_course = db.get(StudentCourse, student_course_id)
    if student_course is None or not _can_access_student_course(db, actor, student_course):
        raise HTTPException(status_code=404, detail="Progress record not found.")
    return student_course


def _require_unit_progress(db: Session, actor: User, progress_id: UUID) -> StudentUnitProgress:
    progress = db.get(StudentUnitProgress, progress_id)
    if progress is None:
        raise HTTPException(status_code=404, detail="Progress record not found.")
    _require_student_course(db, actor, progress.student_course_id)
    return progress


@router.post("/unit")
def create_unit_progress(
    student_course_id: UUID,
    unit_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "teacher", "instructor")),
):
    _require_student_course(db, current_user, student_course_id)
    return crud.create_student_unit_progress(db, student_course_id, unit_id)


@router.put("/unit/{progress_id}")
def update_unit_progress(
    progress_id: UUID,
    status: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "teacher", "instructor")),
):
    _require_unit_progress(db, current_user, progress_id)
    return crud.update_student_unit_progress_status(db, progress_id, status)


@router.get("/unit")
def get_unit_progress(
    student_course_id: UUID,
    unit_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "teacher", "instructor", "student")),
):
    _require_student_course(db, current_user, student_course_id)
    return crud.get_student_unit_progress(db, student_course_id, unit_id)


@router.get("/segment", response_model=SegmentResponse)
def get_segment(
    student_unit_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "super_admin", "teacher", "instructor", "student")),
):
    unit_progress = _require_unit_progress(db, current_user, student_unit_id)

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
    current_user=Depends(require_roles("admin", "super_admin", "teacher", "instructor", "student")),
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
    _require_unit_progress(db, current_user, segment.student_unit_id)

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
    if user_id and current_user.role not in {"admin", "super_admin", "teacher", "instructor"}:
        raise HTTPException(status_code=403, detail="Not authorized")
    target_user_id = user_id or current_user.id

    if target_user_id != current_user.id and current_user.role in {"teacher", "instructor"}:
        visible_learner = (
            db.query(StudentCourse)
            .join(Section, Section.id == StudentCourse.section_id)
            .filter(
                StudentCourse.student_id == target_user_id,
                or_(
                    Section.created_by == current_user.id,
                    Section.enrollments.any(
                        and_(
                            Enrollment.user_id == current_user.id,
                            Enrollment.role_in_section.in_(["teacher", "instructor"]),
                            Enrollment.status == "active",
                        )
                    ),
                ),
            )
            .first()
        )
        if visible_learner is None:
            raise HTTPException(status_code=404, detail="Progress record not found.")

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
