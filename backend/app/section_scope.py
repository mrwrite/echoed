from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import CourseVersion, Lesson, OrganizationMembership, Section, Unit


def require_scoped_section(
    db: Session,
    membership: OrganizationMembership,
    section_id: str | UUID,
) -> Section:
    try:
        normalized_id = section_id if isinstance(section_id, UUID) else UUID(section_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid section id") from exc

    section = (
        db.query(Section)
        .filter(
            Section.id == normalized_id,
            Section.organization_id == membership.organization_id,
        )
        .first()
    )
    if section is None:
        raise HTTPException(status_code=404, detail="Section not found")
    return section


def require_section_unit(db: Session, section: Section, unit_id: str | UUID) -> Unit:
    try:
        normalized_id = unit_id if isinstance(unit_id, UUID) else UUID(unit_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid unit id") from exc
    course_version = db.get(CourseVersion, section.course_version_id)
    unit = db.get(Unit, normalized_id)
    if (
        unit is None
        or course_version is None
        or not (
            unit.course_version_id == section.course_version_id
            or (unit.course_version_id is None and unit.course_id == course_version.course_id)
        )
    ):
        raise HTTPException(status_code=404, detail="Unit not found")
    return unit


def require_section_lesson(db: Session, section: Section, lesson_id: str | UUID) -> Lesson:
    try:
        normalized_id = lesson_id if isinstance(lesson_id, UUID) else UUID(lesson_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid lesson id") from exc
    lesson = db.get(Lesson, normalized_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    require_section_unit(db, section, lesson.unit_id)
    return lesson
