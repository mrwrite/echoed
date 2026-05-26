from app.enum import ProgressStatus
from sqlalchemy.orm import Session
from app.models import StudentUnitProgress, SegmentProgress, Unit, Lesson, StudentCourse, Course
from app.crud.badges import award_badges_for_student
from uuid import UUID
from datetime import datetime
from app.lesson_governance import (
    EMPTY_CONTENT,
    GOVERNED_AVAILABLE,
    governed_lessons_for_unit,
)

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
        .join(Lesson, Lesson.id == SegmentProgress.lesson_id)
        .filter(
            SegmentProgress.student_unit_id == student_unit_id,
            SegmentProgress.status != ProgressStatus.COMPLETED,
        )
        .order_by(Lesson.order.is_(None), Lesson.order, Lesson.id)
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

    if not progress:
        return None

    # Resolve enum safely
    if isinstance(new_status, ProgressStatus):
        status_value = new_status
    else:
        status_value = ProgressStatus(new_status.strip().lower())

    # Update segment status FIRST
    progress.status = status_value

    if status_value == ProgressStatus.IN_PROGRESS and not progress.started_at:
        progress.started_at = datetime.utcnow()

    if status_value in [ProgressStatus.COMPLETED, ProgressStatus.SKIPPED]:
        progress.completed_at = datetime.utcnow()

    progress.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(progress)

    # Update course activity timestamp
    unit_progress = db.get(StudentUnitProgress, progress.student_unit_id)

    if unit_progress:
        student_course = db.get(StudentCourse, unit_progress.student_course_id)

        if student_course:
            student_course.last_activity_at = datetime.utcnow()
            db.commit()

    # Progression logic
    if progress.status in [ProgressStatus.COMPLETED, ProgressStatus.SKIPPED]:
        if unit_progress:
            unit = db.get(Unit, unit_progress.unit_id) if unit_progress else None
            governed_selection = governed_lessons_for_unit(unit) if unit else None
            governed_delivery_active = (
                governed_selection is not None
                and governed_selection.state == GOVERNED_AVAILABLE
            )
            all_segments = (
                db.query(SegmentProgress)
                .filter(SegmentProgress.student_unit_id == unit_progress.id)
                .all()
            )
            relevant_segments = all_segments
            if governed_delivery_active:
                governed_lesson_ids = {
                    lesson.id for lesson in governed_selection.lessons
                }
                relevant_segments = [
                    seg for seg in all_segments if seg.lesson_id in governed_lesson_ids
                ]

            all_complete = all(
                seg.status in [ProgressStatus.COMPLETED, ProgressStatus.SKIPPED]
                for seg in relevant_segments
            )

            if all_complete:
                unit_progress.status = ProgressStatus.COMPLETED
                unit_progress.completed_at = datetime.utcnow()
            else:
                unit_progress.status = ProgressStatus.IN_PROGRESS

            if (
                not all_complete
                and (
                    governed_selection is None
                    or governed_selection.state != GOVERNED_AVAILABLE
                )
            ):
                next_seg = (
                    db.query(SegmentProgress)
                    .filter(
                        SegmentProgress.student_unit_id == unit_progress.id,
                        SegmentProgress.status == ProgressStatus.NOT_STARTED,
                    )
                    .order_by(SegmentProgress.last_updated.asc())
                    .first()
                )

                if next_seg:
                    next_seg.status = ProgressStatus.IN_PROGRESS

                    if not next_seg.started_at:
                        next_seg.started_at = datetime.utcnow()

                    next_seg.last_updated = datetime.utcnow()    

            if not unit_progress.started_at:
                unit_progress.started_at = datetime.utcnow()

            unit_progress.last_updated = datetime.utcnow()

            db.commit()

            student_course = db.get(StudentCourse, unit_progress.student_course_id)

            # Create next unit or complete course
            if all_complete and student_course:
                current_unit = db.get(Unit, unit_progress.unit_id)

                if current_unit and current_unit.order is not None:
                    next_unit = (
                        db.query(Unit)
                        .filter(
                            Unit.course_id == current_unit.course_id,
                            Unit.order > current_unit.order,
                        )
                        .order_by(Unit.order.asc())
                        .first()
                    )
                else:
                    next_unit = None

                if next_unit:
                    if not governed_delivery_active:
                        existing_next = (
                            db.query(StudentUnitProgress)
                            .filter(
                                StudentUnitProgress.student_course_id == student_course.id,
                                StudentUnitProgress.unit_id == next_unit.id,
                            )
                            .first()
                        )

                        if not existing_next:
                            new_progress = create_student_unit_progress(
                                db,
                                student_course.id,
                                next_unit.id,
                            )

                            new_progress.status = ProgressStatus.IN_PROGRESS
                            new_progress.started_at = datetime.utcnow()
                            new_progress.last_updated = datetime.utcnow()
                            next_unit_lessons = (
                                db.query(Lesson)
                                .filter(Lesson.unit_id == next_unit.id)
                                .order_by(Lesson.order.asc())
                                .all()
                            )

                            for lesson in next_unit_lessons:
                                seg = create_segment_progress(
                                    db,
                                    new_progress.id,
                                    lesson.id,
                                )

                                # First lesson becomes active immediately
                                if lesson == next_unit_lessons[0]:
                                    seg.status = ProgressStatus.IN_PROGRESS
                                    seg.started_at = datetime.utcnow()
                                    seg.last_updated = datetime.utcnow()

                            db.commit()

                else:
                    student_course.status = "completed"
                    student_course.completed_at = datetime.utcnow()
                    student_course.last_activity_at = datetime.utcnow()

                db.commit()
            if student_course:
                award_badges_for_student(db, student_course.student_id)

    return progress

def get_segment_progress(db: Session, student_unit_id: UUID, lesson_id: UUID):
    return (
        db.query(SegmentProgress)
        .filter_by(student_unit_id=student_unit_id, lesson_id=lesson_id)
        .first()
    )


def _sorted_units_for_course(course: Course) -> list[Unit]:
    return sorted(
        list(course.units or []),
        key=lambda unit: (
            unit.order is None,
            unit.order if unit.order is not None else 0,
            str(unit.id),
        ),
    )


def _lesson_ids(lessons: list[Lesson]) -> list[UUID]:
    return [lesson.id for lesson in lessons]


def _existing_segments_by_lesson(
    db: Session, student_unit_id: UUID, lesson_ids: list[UUID]
) -> dict[UUID, SegmentProgress]:
    if not lesson_ids:
        return {}
    return {
        segment.lesson_id: segment
        for segment in (
            db.query(SegmentProgress)
            .filter(
                SegmentProgress.student_unit_id == student_unit_id,
                SegmentProgress.lesson_id.in_(lesson_ids),
            )
            .all()
        )
    }


def _ensure_unit_progress(
    db: Session, student_course_id: UUID, unit: Unit
) -> StudentUnitProgress:
    progress = (
        db.query(StudentUnitProgress)
        .filter_by(student_course_id=student_course_id, unit_id=unit.id)
        .first()
    )
    if progress is None:
        progress = StudentUnitProgress(
            student_course_id=student_course_id,
            unit_id=unit.id,
            status=ProgressStatus.IN_PROGRESS,
            started_at=datetime.utcnow(),
            last_updated=datetime.utcnow(),
        )
        db.add(progress)
        db.commit()
        db.refresh(progress)
        return progress

    if progress.status != ProgressStatus.COMPLETED:
        progress.status = ProgressStatus.IN_PROGRESS
        if not progress.started_at:
            progress.started_at = datetime.utcnow()
        progress.last_updated = datetime.utcnow()
        db.commit()
        db.refresh(progress)
    return progress


def _ensure_governed_segments(
    db: Session, unit_progress: StudentUnitProgress, lessons: list[Lesson]
) -> list[SegmentProgress]:
    lesson_ids = _lesson_ids(lessons)
    existing_by_lesson = _existing_segments_by_lesson(db, unit_progress.id, lesson_ids)
    created = False

    for lesson in lessons:
        if lesson.id in existing_by_lesson:
            continue
        db.add(
            SegmentProgress(
                student_unit_id=unit_progress.id,
                lesson_id=lesson.id,
                status=ProgressStatus.NOT_STARTED,
            )
        )
        created = True

    if created:
        db.commit()

    return [
        existing_by_lesson.get(lesson.id)
        or db.query(SegmentProgress)
        .filter_by(student_unit_id=unit_progress.id, lesson_id=lesson.id)
        .first()
        for lesson in lessons
    ]


def _governed_current_segment_for_unit_progress(
    db: Session, unit_progress: StudentUnitProgress, lessons: list[Lesson]
) -> SegmentProgress | None:
    lesson_ids = _lesson_ids(lessons)
    segments = (
        db.query(SegmentProgress)
        .join(Lesson, Lesson.id == SegmentProgress.lesson_id)
        .filter(
            SegmentProgress.student_unit_id == unit_progress.id,
            SegmentProgress.lesson_id.in_(lesson_ids),
            SegmentProgress.status != ProgressStatus.COMPLETED,
        )
        .order_by(Lesson.order.is_(None), Lesson.order, Lesson.id)
        .all()
    )
    return segments[0] if segments else None


def resolve_governed_progression(
    db: Session, student_course_id: UUID | str
) -> dict[str, object]:
    student_course = db.get(StudentCourse, student_course_id)
    if student_course is None:
        return {
            "delivery_state": "governed_unavailable",
            "detail": "Student course enrollment was not found.",
        }

    course = (
        db.query(Course)
        .filter(Course.id == student_course.course_id)
        .first()
    )
    if course is None:
        return {
            "delivery_state": "empty_course",
            "detail": "The requested course does not exist.",
        }

    units = _sorted_units_for_course(course)
    if not units:
        return {
            "delivery_state": "empty_course",
            "detail": "This course does not contain any instructional units.",
        }

    completed_unit_ids = {
        progress.unit_id
        for progress in (
            db.query(StudentUnitProgress)
            .filter_by(student_course_id=student_course.id, status=ProgressStatus.COMPLETED)
            .all()
        )
    }

    for unit in units:
        if unit.id in completed_unit_ids:
            continue

        selection = governed_lessons_for_unit(unit)
        if selection.state == GOVERNED_AVAILABLE:
            unit_progress = _ensure_unit_progress(db, student_course.id, unit)
            _ensure_governed_segments(db, unit_progress, selection.lessons)
            segment = _governed_current_segment_for_unit_progress(
                db, unit_progress, selection.lessons
            )
            if segment is None:
                unit_progress.status = ProgressStatus.COMPLETED
                unit_progress.completed_at = unit_progress.completed_at or datetime.utcnow()
                unit_progress.last_updated = datetime.utcnow()
                db.commit()
                completed_unit_ids.add(unit.id)
                continue

            if segment.status == ProgressStatus.NOT_STARTED:
                segment.status = ProgressStatus.IN_PROGRESS
                segment.started_at = segment.started_at or datetime.utcnow()
                segment.last_updated = datetime.utcnow()
                unit_progress.status = ProgressStatus.IN_PROGRESS
                unit_progress.started_at = unit_progress.started_at or datetime.utcnow()
                unit_progress.last_updated = datetime.utcnow()
                student_course.last_activity_at = datetime.utcnow()
                db.commit()
                db.refresh(segment)
                db.refresh(unit_progress)

            return {
                "delivery_state": GOVERNED_AVAILABLE,
                "detail": selection.detail,
                "lesson_id": segment.lesson_id,
                "status": segment.status,
                "unit_progress_id": unit_progress.id,
            }

        delivery_state = "empty_unit" if selection.state == EMPTY_CONTENT else selection.state
        return {
            "delivery_state": delivery_state,
            "detail": selection.detail,
        }

    student_course.status = "completed"
    student_course.completed_at = student_course.completed_at or datetime.utcnow()
    student_course.last_activity_at = datetime.utcnow()
    db.commit()
    return {
        "delivery_state": "completed",
        "detail": "All governed instructional content in this course has been completed.",
    }
