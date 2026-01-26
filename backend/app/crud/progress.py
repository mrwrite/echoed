from app.enum import ProgressStatus
from sqlalchemy.orm import Session
from app.models import StudentUnitProgress, SegmentProgress, Unit, Lesson, StudentCourse
from app.crud.badges import award_badges_for_student
from uuid import UUID
from datetime import datetime

# ---------- StudentUnitProgress ----------


def create_student_unit_progress(
    db: Session, student_course_id: UUID, unit_id: UUID
) -> StudentUnitProgress:
    progress = StudentUnitProgress(
        student_course_id=student_course_id,
        unit_id=unit_id,
        status=ProgressStatus.NOT_STARTED,
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


def update_student_unit_progress_status(
    db: Session, progress_id: UUID, new_status: str
):
    progress = db.get(StudentUnitProgress, progress_id)
    if progress:
        if isinstance(new_status, ProgressStatus):
            status_value = new_status
        else:
            status_value = ProgressStatus[new_status.upper()]
        progress.status = status_value
        if status_value == ProgressStatus.IN_PROGRESS and not progress.started_at:
            progress.started_at = datetime.utcnow()
        if status_value == ProgressStatus.COMPLETED:
            progress.completed_at = datetime.utcnow()
        progress.last_updated = datetime.utcnow()
        db.commit()
    return progress


def get_current_segment_for_unit(db: Session, student_unit_id: UUID):
    """Return the next segment that has not been completed for a unit."""
    return (
        db.query(SegmentProgress)
        .filter(
            SegmentProgress.student_unit_id == student_unit_id,
            SegmentProgress.status != ProgressStatus.COMPLETED,
        )
        .order_by(SegmentProgress.id)
        .first()
    )


def get_student_unit_progress(db: Session, student_course_id: UUID, unit_id: UUID):
    return (
        db.query(StudentUnitProgress)
        .filter_by(student_course_id=student_course_id, unit_id=unit_id)
        .first()
    )


# ---------- SegmentProgress ----------


def create_segment_progress(
    db: Session, student_unit_id: UUID, lesson_id: UUID
) -> SegmentProgress:
    progress = SegmentProgress(
        student_unit_id=student_unit_id,
        lesson_id=lesson_id,
        status=ProgressStatus.NOT_STARTED,
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


def update_segment_progress_status(db: Session, progress_id: UUID, new_status: str):
    progress = db.get(SegmentProgress, progress_id)
    if progress:
        if isinstance(new_status, ProgressStatus):
            status_value = new_status
        else:
            status_value = ProgressStatus[new_status.upper()]
        progress.status = status_value
        if status_value == ProgressStatus.IN_PROGRESS and not progress.started_at:
            progress.started_at = datetime.utcnow()
        if status_value == ProgressStatus.COMPLETED:
            progress.completed_at = datetime.utcnow()
        progress.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(progress)

        if progress.status == ProgressStatus.IN_PROGRESS:
            unit_progress = db.get(StudentUnitProgress, progress.student_unit_id)
            if unit_progress:
                student_course = db.get(StudentCourse, unit_progress.student_course_id)
                if student_course:
                    student_course.last_activity_at = datetime.utcnow()
                    db.commit()

        # If the segment was completed, advance progress within the unit or to the
        # next unit as needed.
        if progress.status == ProgressStatus.COMPLETED:
            # Look for the next segment in the same unit that has not been completed
            next_seg = (
                db.query(SegmentProgress)
                .filter(
                    SegmentProgress.student_unit_id == progress.student_unit_id,
                    SegmentProgress.status != ProgressStatus.COMPLETED,
                )
                .order_by(SegmentProgress.id)
                .first()
            )

            if next_seg:
                # Move to the next lesson within the unit
                next_seg.status = ProgressStatus.IN_PROGRESS
                next_seg.last_updated = datetime.utcnow()
                unit_progress = db.get(StudentUnitProgress, progress.student_unit_id)
                if unit_progress and unit_progress.status != ProgressStatus.COMPLETED:
                    unit_progress.status = ProgressStatus.IN_PROGRESS
                    if not unit_progress.started_at:
                        unit_progress.started_at = datetime.utcnow()
                    unit_progress.last_updated = datetime.utcnow()
                student_course = db.get(StudentCourse, unit_progress.student_course_id) if unit_progress else None
                if student_course:
                    student_course.last_activity_at = datetime.utcnow()
                db.commit()
            else:
                # All lessons in the unit are complete; mark unit complete and
                # advance to the next unit if available
                unit_progress = db.get(StudentUnitProgress, progress.student_unit_id)
                if unit_progress:
                    unit_progress.status = ProgressStatus.COMPLETED
                    unit_progress.completed_at = datetime.utcnow()
                    unit_progress.last_updated = datetime.utcnow()
                    db.commit()

                    # Find the next unit in the course based on order
                    next_unit = (
                        db.query(Unit)
                        .filter(
                            Unit.course_id == unit_progress.unit.course_id,
                            Unit.order > (unit_progress.unit.order or 0),
                        )
                        .order_by(Unit.order)
                        .first()
                    )

                    if next_unit:
                        # Create or update progress for the next unit
                        next_progress = (
                            db.query(StudentUnitProgress)
                            .filter_by(
                                student_course_id=unit_progress.student_course_id,
                                unit_id=next_unit.id,
                            )
                            .first()
                        )

                        if not next_progress:
                            next_progress = StudentUnitProgress(
                                student_course_id=unit_progress.student_course_id,
                                unit_id=next_unit.id,
                                status=ProgressStatus.IN_PROGRESS,
                            )
                            next_progress.started_at = datetime.utcnow()
                            db.add(next_progress)
                            db.commit()
                        else:
                            next_progress.status = ProgressStatus.IN_PROGRESS
                            if not next_progress.started_at:
                                next_progress.started_at = datetime.utcnow()
                            next_progress.last_updated = datetime.utcnow()
                            db.commit()

                        # Ensure segment progress records exist for the new unit
                        existing = (
                            db.query(SegmentProgress)
                            .filter_by(student_unit_id=next_progress.id)
                            .count()
                        )
                        if existing == 0:
                            lessons = (
                                db.query(Lesson)
                                .filter_by(unit_id=next_unit.id)
                                .order_by(Lesson.order)
                                .all()
                            )
                            for idx, lesson in enumerate(lessons):
                                seg_status = (
                                    ProgressStatus.IN_PROGRESS
                                    if idx == 0
                                    else ProgressStatus.NOT_STARTED
                                )
                                seg = SegmentProgress(
                                    student_unit_id=next_progress.id,
                                    lesson_id=lesson.id,
                                    status=seg_status,
                                )
                                if seg_status == ProgressStatus.IN_PROGRESS:
                                    seg.started_at = datetime.utcnow()
                                db.add(seg)
                            db.commit()
                        else:
                            # If segments already exist, mark the first incomplete as in progress
                            next_seg = (
                                db.query(SegmentProgress)
                                .filter(
                                    SegmentProgress.student_unit_id == next_progress.id,
                                    SegmentProgress.status != ProgressStatus.COMPLETED,
                                )
                                .order_by(SegmentProgress.id)
                                .first()
                            )
                            if next_seg and next_seg.status == ProgressStatus.NOT_STARTED:
                                next_seg.status = ProgressStatus.IN_PROGRESS
                                next_seg.started_at = datetime.utcnow()
                                next_seg.last_updated = datetime.utcnow()
                                db.commit()
                    else:
                        # No more units left; mark entire course as completed
                        student_course = db.get(
                            StudentCourse, unit_progress.student_course_id
                        )
                        if student_course:
                            student_course.status = "completed"
                            student_course.completed_at = datetime.utcnow()
                            student_course.last_activity_at = datetime.utcnow()
                            db.commit()
            if unit_progress:
                student_course = db.get(StudentCourse, unit_progress.student_course_id)
                if student_course:
                    award_badges_for_student(db, student_course.student_id)
    return progress


def get_segment_progress(db: Session, student_unit_id: UUID, lesson_id: UUID):
    return (
        db.query(SegmentProgress)
        .filter_by(student_unit_id=student_unit_id, lesson_id=lesson_id)
        .first()
    )
