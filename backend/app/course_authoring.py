from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.course_authoring_permissions import CourseAuthoringCapabilities
from app.enum import CourseVersionStatus
from app.models import Activity, Assessment, Course, CourseVersion, Lesson, Source, StorybookPage, Unit


class CourseAuthoringValidationError(Exception):
    def __init__(self, issues: list[dict]):
        super().__init__("Course authoring validation failed")
        self.issues = issues


class CourseAuthoringConflictError(Exception):
    def __init__(self, course: Course):
        super().__init__("Course draft revision conflict")
        self.course_id = course.id
        self.current_revision = course.revision_number
        self.updated_at = course.updated_at


def _value(payload, name: str, default=None):
    return getattr(payload, name, default)


def _issue(entity_type: str, field: str, message: str, corrective_context: str, entity_id=None):
    return {
        "severity": "blocking",
        "entity_type": entity_type,
        "entity_id": entity_id,
        "field": field,
        "message": message,
        "corrective_context": corrective_context,
    }


def validate_authoring_graph(payload) -> None:
    issues: list[dict] = []
    if not (_value(payload, "title", "") or "").strip():
        issues.append(_issue("course", "title", "Course title is required.", "Add a concise course title."))
    age_min = _value(payload, "age_band_min")
    age_max = _value(payload, "age_band_max")
    if age_min is not None and age_max is not None and age_min > age_max:
        issues.append(
            _issue(
                "course",
                "age_band_max",
                "Maximum age cannot be lower than minimum age.",
                "Increase the maximum age or lower the minimum age.",
            )
        )
    for unit in _value(payload, "units", []) or []:
        if not (_value(unit, "title", "") or "").strip():
            issues.append(_issue("unit", "title", "Unit title is required.", "Name the unit.", _value(unit, "id")))
        for lesson in _value(unit, "lessons", []) or []:
            if not (_value(lesson, "title", "") or "").strip():
                issues.append(
                    _issue("lesson", "title", "Lesson title is required.", "Name the lesson.", _value(lesson, "id"))
                )
            duration = _value(lesson, "duration_minutes")
            if duration is not None and duration < 1:
                issues.append(
                    _issue(
                        "lesson",
                        "duration_minutes",
                        "Lesson duration must be at least one minute.",
                        "Enter a positive duration.",
                        _value(lesson, "id"),
                    )
                )
            for activity in _value(lesson, "activities", []) or []:
                if not (_value(activity, "title", "") or "").strip():
                    issues.append(
                        _issue(
                            "activity",
                            "title",
                            "Activity title is required.",
                            "Name the activity.",
                            _value(activity, "id"),
                        )
                    )
                if not (_value(activity, "type", "") or "").strip():
                    issues.append(
                        _issue(
                            "activity",
                            "type",
                            "Activity type is required.",
                            "Choose a supported activity type.",
                            _value(activity, "id"),
                        )
                    )
    if issues:
        raise CourseAuthoringValidationError(issues)


def _owned(existing: dict[UUID, object], requested_id: UUID | None):
    return existing.get(requested_id) if requested_id else None


def _sync_assessment_refs(db: Session, owner, requested_ids, scope: str, course_id: UUID) -> None:
    requested = set(requested_ids or [])
    current_rows = list(getattr(owner, "assessments", []))
    if scope == "course":
        current_rows = [assessment for assessment in current_rows if assessment.unit_id is None and assessment.lesson_id is None]
    current = {assessment.id: assessment for assessment in current_rows}
    found = db.query(Assessment).filter(Assessment.id.in_(requested)).all() if requested else []
    if len(found) != len(requested):
        raise CourseAuthoringValidationError([_issue(scope, "assessment_ids", "One or more assessment references do not exist.", "Remove unavailable assessment references.", owner.id)])
    for assessment in found:
        if assessment.course_id not in {None, course_id}:
            raise CourseAuthoringValidationError([_issue(scope, "assessment_ids", "An assessment belongs to another course.", "Choose an assessment from this course.", owner.id)])
        assessment.course_id = course_id
        if scope == "course":
            assessment.unit_id = None
            assessment.lesson_id = None
        if scope == "unit":
            assessment.unit_id = owner.id
            assessment.lesson_id = None
        if scope == "lesson": assessment.lesson_id = owner.id
    for assessment_id, assessment in current.items():
        if assessment_id not in requested:
            if scope == "course": assessment.course_id = None
            if scope == "unit": assessment.unit_id = None
            if scope == "lesson": assessment.lesson_id = None


def _sync_pages(db: Session, activity: Activity, payloads) -> None:
    existing = {page.id: page for page in activity.storybook_pages}
    retained: set[UUID] = set()
    for index, payload in enumerate(payloads or [], start=1):
        page = _owned(existing, _value(payload, "id"))
        if page is None:
            page = StorybookPage(activity_id=activity.id)
            db.add(page)
        page.image_url = (_value(payload, "image_url", "") or "").strip()
        page.order = index
        db.flush()
        retained.add(page.id)
    for page_id, page in existing.items():
        if page_id not in retained:
            db.delete(page)


def _sync_activities(db: Session, lesson: Lesson, payloads) -> None:
    existing = {activity.id: activity for activity in lesson.activities}
    retained: set[UUID] = set()
    for index, payload in enumerate(payloads or [], start=1):
        activity = _owned(existing, _value(payload, "id"))
        if activity is None:
            activity = Activity(lesson_id=lesson.id)
            db.add(activity)
        activity.type = (_value(payload, "type", "") or "").strip()
        activity.title = (_value(payload, "title", "") or "").strip()
        activity.content = _value(payload, "content", "") or ""
        activity.media_id = _value(payload, "media_id")
        activity.order = index
        db.flush()
        retained.add(activity.id)
        _sync_pages(db, activity, _value(payload, "pages", []))
    for activity_id, activity in existing.items():
        if activity_id not in retained:
            db.delete(activity)


def _sync_sources(db: Session, lesson: Lesson, payloads) -> None:
    existing = {source.id: source for source in lesson.sources}
    retained: set[UUID] = set()
    for payload in payloads or []:
        source = _owned(existing, _value(payload, "id"))
        if source is None:
            source = Source(lesson_id=lesson.id)
            db.add(source)
        source.citation = (_value(payload, "citation", "") or "").strip()
        source.url = _value(payload, "url")
        db.flush()
        retained.add(source.id)
    for source_id, source in existing.items():
        if source_id not in retained:
            db.delete(source)


def _sync_lessons(db: Session, unit: Unit, payloads) -> None:
    existing = {lesson.id: lesson for lesson in unit.lessons}
    retained: set[UUID] = set()
    fields = (
        "objective",
        "learning_objectives",
        "teacher_notes",
        "hook",
        "content",
        "guided_practice",
        "independent_practice",
        "assessment",
        "duration_minutes",
    )
    for index, payload in enumerate(payloads or [], start=1):
        lesson = _owned(existing, _value(payload, "id"))
        if lesson is None:
            lesson = Lesson(unit_id=unit.id, review_status="draft")
            db.add(lesson)
        lesson.title = (_value(payload, "title", "") or "").strip()
        lesson.order = index
        for field in fields:
            setattr(lesson, field, _value(payload, field))
        lesson.key_concepts = list(_value(payload, "key_concepts", []) or [])
        lesson.discussion_questions = list(_value(payload, "discussion_questions", []) or [])
        lesson.skill_tags = list(_value(payload, "skill_tags", []) or [])
        lesson.standards_metadata = dict(_value(payload, "standards_metadata", {}) or {})
        db.flush()
        retained.add(lesson.id)
        _sync_sources(db, lesson, _value(payload, "sources", []))
        _sync_activities(db, lesson, _value(payload, "activities", []))
        _sync_assessment_refs(db, lesson, _value(payload, "assessment_ids", []), "lesson", unit.course_id)
    for lesson_id, lesson in existing.items():
        if lesson_id not in retained:
            db.delete(lesson)


def _sync_units(db: Session, course: Course, version: CourseVersion, payloads) -> None:
    existing = {unit.id: unit for unit in course.units if unit.course_version_id == version.id}
    retained: set[UUID] = set()
    for index, payload in enumerate(payloads or [], start=1):
        unit = _owned(existing, _value(payload, "id"))
        if unit is None:
            unit = Unit(course_id=course.id)
            db.add(unit)
        unit.course_version_id = version.id
        unit.title = (_value(payload, "title", "") or "").strip()
        unit.content = _value(payload, "content")
        unit.order = index
        db.flush()
        retained.add(unit.id)
        _sync_lessons(db, unit, _value(payload, "lessons", []))
        _sync_assessment_refs(db, unit, _value(payload, "assessment_ids", []), "unit", course.id)
    for unit_id, unit in existing.items():
        if unit_id not in retained:
            db.delete(unit)


def _current_draft_version(db: Session, course: Course) -> CourseVersion:
    version = (
        db.query(CourseVersion)
        .filter(
            CourseVersion.course_id == course.id,
            CourseVersion.status == CourseVersionStatus.DRAFT,
        )
        .order_by(CourseVersion.version_number.desc())
        .first()
    )
    if version is None:
        latest = (
            db.query(CourseVersion)
            .filter(CourseVersion.course_id == course.id)
            .order_by(CourseVersion.version_number.desc())
            .first()
        )
        version = CourseVersion(
            course_id=course.id,
            version_number=1 if latest is None else latest.version_number + 1,
            status=CourseVersionStatus.DRAFT,
            changelog="Authoring draft",
        )
        db.add(version)
        db.flush()
    return version


def _draft_or_latest_version(db: Session, course: Course) -> CourseVersion:
    version = (
        db.query(CourseVersion)
        .filter(CourseVersion.course_id == course.id, CourseVersion.status == CourseVersionStatus.DRAFT)
        .order_by(CourseVersion.version_number.desc())
        .first()
    )
    if version is not None:
        return version
    version = (
        db.query(CourseVersion)
        .filter(CourseVersion.course_id == course.id)
        .order_by(CourseVersion.version_number.desc())
        .first()
    )
    if version is None:
        return _current_draft_version(db, course)
    return version


def _apply_course_fields(course: Course, payload) -> None:
    course.title = (_value(payload, "title", "") or "").strip()
    course.description = _value(payload, "description", "") or ""
    course.subject = _value(payload, "subject")
    course.age_band_min = _value(payload, "age_band_min")
    course.age_band_max = _value(payload, "age_band_max")
    course.default_locale = _value(payload, "default_locale", "en") or "en"
    course.learning_objectives = _value(payload, "learning_objectives")
    course.skill_tags = list(_value(payload, "skill_tags", []) or [])
    course.standards_metadata = dict(_value(payload, "standards_metadata", {}) or {})


def find_idempotent_course(
    db: Session,
    *,
    created_by: UUID,
    organization_id: UUID | None,
    idempotency_key: str,
) -> Course | None:
    candidates = db.query(Course).filter(Course.created_by == created_by)
    candidates = candidates.filter(Course.organization_id == organization_id)
    for course in candidates.all():
        if (course.revision_metadata or {}).get("idempotency_key") == idempotency_key:
            return course
    return None


def create_course_draft(
    db: Session,
    payload,
    *,
    current_user_id: UUID,
    organization_id: UUID | None,
    idempotency_key: str,
) -> Course:
    validate_authoring_graph(payload)
    existing = find_idempotent_course(
        db,
        created_by=current_user_id,
        organization_id=organization_id,
        idempotency_key=idempotency_key,
    )
    if existing is not None:
        return existing
    metadata = {"idempotency_key": idempotency_key}
    metadata["authoring_state"] = "draft"
    template_id = _value(payload, "template_id")
    if template_id:
        metadata["template_id"] = template_id
    course = Course(
        title="",
        description="",
        created_by=current_user_id,
        organization_id=organization_id,
        revision_number=1,
        revision_status="draft",
        revision_metadata=metadata,
        updated_at=datetime.utcnow(),
    )
    _apply_course_fields(course, payload)
    db.add(course)
    db.flush()
    version = _current_draft_version(db, course)
    _sync_units(db, course, version, _value(payload, "units", []))
    _sync_assessment_refs(db, course, _value(payload, "assessment_ids", []), "course", course.id)
    return course


def update_course_draft(db: Session, course: Course, payload) -> Course:
    validate_authoring_graph(payload)
    expected_revision = _value(payload, "revision_number")
    if expected_revision is not None and expected_revision != course.revision_number:
        raise CourseAuthoringConflictError(course)
    _apply_course_fields(course, payload)
    metadata = dict(course.revision_metadata or {})
    if metadata.get("authoring_state") in {"approved", "published"}:
        metadata["authoring_state"] = "draft"
        metadata.pop("review_feedback", None)
    course.revision_metadata = metadata
    course.revision_number += 1
    course.updated_at = datetime.utcnow()
    version = _current_draft_version(db, course)
    _sync_units(db, course, version, _value(payload, "units", []))
    _sync_assessment_refs(db, course, _value(payload, "assessment_ids", []), "course", course.id)
    db.flush()
    return course


def serialize_course_draft(
    db: Session,
    course: Course,
    capabilities: CourseAuthoringCapabilities,
) -> dict:
    version = _draft_or_latest_version(db, course)
    units = []
    version_units = [unit for unit in course.units if unit.course_version_id == version.id]
    for unit in sorted(version_units, key=lambda item: (item.order or 0, str(item.id))):
        lessons = []
        for lesson in sorted(unit.lessons, key=lambda item: (item.order or 0, str(item.id))):
            activities = []
            for activity in sorted(lesson.activities, key=lambda item: (item.order or 0, str(item.id))):
                activities.append(
                    {
                        "id": activity.id,
                        "type": activity.type,
                        "title": activity.title,
                        "content": activity.content or "",
                        "order": activity.order,
                        "media_id": activity.media_id,
                        "pages": [
                            {"id": page.id, "image_url": page.image_url, "order": page.order}
                            for page in sorted(
                                activity.storybook_pages,
                                key=lambda item: (item.order or 0, str(item.id)),
                            )
                        ],
                    }
                )
            lessons.append(
                {
                    "id": lesson.id,
                    "title": lesson.title,
                    "objective": lesson.objective,
                    "learning_objectives": lesson.learning_objectives,
                    "key_concepts": lesson.key_concepts or [],
                    "teacher_notes": lesson.teacher_notes,
                    "discussion_questions": lesson.discussion_questions or [],
                    "hook": lesson.hook,
                    "content": lesson.content,
                    "guided_practice": lesson.guided_practice,
                    "independent_practice": lesson.independent_practice,
                    "assessment": lesson.assessment,
                    "review_status": lesson.review_status,
                    "skill_tags": lesson.skill_tags or [],
                    "standards_metadata": lesson.standards_metadata or {},
                    "order": lesson.order,
                    "duration_minutes": lesson.duration_minutes,
                    "sources": [
                        {"id": source.id, "citation": source.citation, "url": source.url}
                        for source in lesson.sources
                    ],
                    "activities": activities,
                    "assessment_ids": [assessment.id for assessment in lesson.assessments],
                }
            )
        units.append(
            {
                "id": unit.id,
                "title": unit.title,
                "content": unit.content,
                "order": unit.order,
                "lessons": lessons,
                "assessment_ids": [assessment.id for assessment in unit.assessments],
            }
        )
    return {
        "id": course.id,
        "title": course.title,
        "description": course.description,
        "subject": course.subject,
        "age_band_min": course.age_band_min,
        "age_band_max": course.age_band_max,
        "default_locale": course.default_locale,
        "learning_objectives": course.learning_objectives,
        "skill_tags": course.skill_tags or [],
        "standards_metadata": course.standards_metadata or {},
        "organization_id": course.organization_id,
        "created_by": course.created_by,
        "revision_number": course.revision_number,
        "revision_status": (course.revision_metadata or {}).get("authoring_state", course.revision_status),
        "revision_metadata": course.revision_metadata or {},
        "updated_at": course.updated_at or course.created_at or datetime.utcnow(),
        "current_version_id": version.id,
        "units": units,
        "assessment_ids": [assessment.id for assessment in course.assessments],
        "capabilities": capabilities.model_payload(),
    }


def build_course_duplicate_payload(course: Course) -> dict:
    units: list[dict] = []
    draft_versions = [version for version in course.versions if version.status == CourseVersionStatus.DRAFT]
    selected_version = max(draft_versions or list(course.versions), key=lambda item: item.version_number, default=None)
    selected_units = [unit for unit in course.units if selected_version is None or unit.course_version_id == selected_version.id]
    for unit in sorted(selected_units, key=lambda item: (item.order or 0, str(item.id))):
        lessons: list[dict] = []
        for lesson in sorted(unit.lessons, key=lambda item: (item.order or 0, str(item.id))):
            activities: list[dict] = []
            for activity in sorted(lesson.activities, key=lambda item: (item.order or 0, str(item.id))):
                activities.append(
                    {
                        "type": activity.type,
                        "title": activity.title,
                        "content": activity.content or "",
                        "media_id": activity.media_id,
                        "pages": [
                            {"image_url": page.image_url}
                            for page in sorted(
                                activity.storybook_pages,
                                key=lambda item: (item.order or 0, str(item.id)),
                            )
                        ],
                    }
                )
            lessons.append(
                {
                    "title": lesson.title,
                    "objective": lesson.objective,
                    "learning_objectives": lesson.learning_objectives,
                    "key_concepts": lesson.key_concepts or [],
                    "teacher_notes": lesson.teacher_notes,
                    "discussion_questions": lesson.discussion_questions or [],
                    "hook": lesson.hook,
                    "content": lesson.content,
                    "guided_practice": lesson.guided_practice,
                    "independent_practice": lesson.independent_practice,
                    "assessment": lesson.assessment,
                    "skill_tags": lesson.skill_tags or [],
                    "standards_metadata": lesson.standards_metadata or {},
                    "duration_minutes": lesson.duration_minutes,
                    "sources": [
                        {"citation": source.citation, "url": source.url}
                        for source in lesson.sources
                    ],
                    "activities": activities,
                }
            )
        units.append({"title": unit.title, "content": unit.content, "lessons": lessons})
    return {
        "title": f"Copy of {course.title}",
        "description": course.description,
        "subject": course.subject,
        "age_band_min": course.age_band_min,
        "age_band_max": course.age_band_max,
        "default_locale": course.default_locale,
        "learning_objectives": course.learning_objectives,
        "skill_tags": course.skill_tags or [],
        "standards_metadata": course.standards_metadata or {},
        "units": units,
    }
