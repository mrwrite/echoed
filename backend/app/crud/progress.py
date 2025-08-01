from app.enum import ProgressStatus
from sqlalchemy.orm import Session
from app.models import StudentUnitProgress, SegmentProgress, Unit, Lesson, StudentCourse
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
        progress.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(progress)

        # If the segment was completed, check if the unit is finished
        if progress.status == ProgressStatus.COMPLETED:
            remaining = (
                db.query(SegmentProgress)
                .filter(
                    SegmentProgress.student_unit_id == progress.student_unit_id,
                    SegmentProgress.status != ProgressStatus.COMPLETED,
                )
                .first()
            )

            if not remaining:
                unit_progress = db.get(StudentUnitProgress, progress.student_unit_id)
                if unit_progress:
                    unit_progress.status = ProgressStatus.COMPLETED
                    unit_progress.last_updated = datetime.utcnow()
                    db.commit()

                    # Attempt to create progress for the next unit in the course
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
                        exists = (
                            db.query(StudentUnitProgress)
                            .filter_by(
                                student_course_id=unit_progress.student_course_id,
                                unit_id=next_unit.id,
                            )
                            .first()
                        )
                        if not exists:
                            next_progress = StudentUnitProgress(
                                student_course_id=unit_progress.student_course_id,
                                unit_id=next_unit.id,
                                status=ProgressStatus.NOT_STARTED,
                            )
                            db.add(next_progress)
                            db.commit()

                            # create segment progress records for the lessons in the new unit
                            lessons = (
                                db.query(Lesson)
                                .filter_by(unit_id=next_unit.id)
                                .order_by(Lesson.order)
                                .all()
                            )
                            for lesson in lessons:
                                seg = SegmentProgress(
                                    student_unit_id=next_progress.id,
                                    lesson_id=lesson.id,
                                    status=ProgressStatus.NOT_STARTED,
                                )
                                db.add(seg)
                            db.commit()
                    else:
                        # No more units left; mark entire course as completed
                        student_course = db.get(
                            StudentCourse, unit_progress.student_course_id
                        )
                        if student_course:
                            student_course.status = "completed"
                            db.commit()
    return progress


def get_segment_progress(db: Session, student_unit_id: UUID, lesson_id: UUID):
    return (
        db.query(SegmentProgress)
        .filter_by(student_unit_id=student_unit_id, lesson_id=lesson_id)
        .first()
    )
