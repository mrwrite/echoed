from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.course_authoring_permissions import (
    require_course_authoring_capability,
    resolve_course_authoring_capabilities,
)
from app.models import Activity, Course, Lesson, Unit, User


def course_for_unit(db: Session, unit_id: UUID) -> Course:
    course = db.query(Course).join(Unit, Unit.course_id == Course.id).filter(Unit.id == unit_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return course


def course_for_lesson(db: Session, lesson_id: UUID) -> Course:
    course = (
        db.query(Course)
        .join(Unit, Unit.course_id == Course.id)
        .join(Lesson, Lesson.unit_id == Unit.id)
        .filter(Lesson.id == lesson_id)
        .first()
    )
    if course is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return course


def course_for_activity(db: Session, activity_id: UUID) -> Course:
    course = (
        db.query(Course)
        .join(Unit, Unit.course_id == Course.id)
        .join(Lesson, Lesson.unit_id == Unit.id)
        .join(Activity, Activity.lesson_id == Lesson.id)
        .filter(Activity.id == activity_id)
        .first()
    )
    if course is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return course


def require_course_edit(db: Session, current_user: User, course: Course) -> None:
    require_course_authoring_capability(
        resolve_course_authoring_capabilities(db, current_user, course=course),
        "edit",
    )
