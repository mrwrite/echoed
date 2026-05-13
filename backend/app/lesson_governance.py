from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable
from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.enum import MembershipStatus
from app.models import (
    Activity,
    Assessment,
    Course,
    Lesson,
    Media,
    OrganizationMembership,
    Source,
    StorybookPage,
    Unit,
)
from app.schemas import (
    ActivityResponse,
    CourseResponse,
    LessonResponse,
    MediaResponse,
    SourceResponse,
    StorybookPageResponse,
    UnitResponse,
)

VALID_REVIEW_STATUSES = {"draft", "reviewed", "approved"}
VALID_REVISION_STATUSES = {"draft", "current", "deprecated", "archived"}
VALID_LINEAGE_STATUSES = {"standalone", "current", "superseded", "deprecated", "archived"}
REVIEWER_ORG_ROLES = {"content_admin", "org_admin"}
EDUCATOR_VIEWER_ROLES = {
    "admin",
    "teacher",
    "org_admin",
    "content_admin",
    "instructor",
    "super_admin",
}
GOVERNED_AVAILABLE = "governed_available"
GOVERNED_UNAVAILABLE = "governed_unavailable"
PENDING_REVIEW = "pending_review"
NO_APPROVED_CONTENT = "no_approved_content"
EMPTY_CONTENT = "empty_content"


@dataclass
class LessonReadinessResult:
    is_ready: bool
    missing_fields: list[str]


@dataclass
class GovernedUnitSelection:
    state: str
    lessons: list[Lesson]
    detail: str


@dataclass
class GovernedLessonSelection:
    state: str
    lesson: Lesson | None
    detail: str


@dataclass
class PublishReadinessIssue:
    entity_type: str
    entity_id: object | None
    entity_title: str
    code: str
    message: str


@dataclass
class PublishReadinessResult:
    entity_type: str
    entity_id: object | None
    entity_title: str
    is_ready: bool
    blocking_issues: list[PublishReadinessIssue] = field(default_factory=list)
    warnings: list[PublishReadinessIssue] = field(default_factory=list)


@dataclass
class SafePublishValidationResult:
    entity_type: str
    entity_id: object | None
    entity_title: str
    is_safe: bool
    blocking_issues: list[PublishReadinessIssue] = field(default_factory=list)
    warnings: list[PublishReadinessIssue] = field(default_factory=list)


@dataclass
class LineageCoherenceResult:
    entity_type: str
    entity_id: object | None
    entity_title: str
    is_coherent: bool
    blocking_issues: list[PublishReadinessIssue] = field(default_factory=list)
    warnings: list[PublishReadinessIssue] = field(default_factory=list)


@dataclass
class LearnerProgressSafetyResult:
    entity_type: str
    entity_id: object | None
    entity_title: str
    is_safe: bool
    blocking_issues: list[PublishReadinessIssue] = field(default_factory=list)
    warnings: list[PublishReadinessIssue] = field(default_factory=list)


@dataclass
class AssessmentEvidenceSafetyResult:
    entity_type: str
    entity_id: object | None
    entity_title: str
    is_safe: bool
    blocking_issues: list[PublishReadinessIssue] = field(default_factory=list)
    warnings: list[PublishReadinessIssue] = field(default_factory=list)


def _clean_text(value: object | None) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _has_non_empty_items(values: object | None) -> bool:
    if not values:
        return False
    if not isinstance(values, list):
        return False
    return any(_clean_text(value) for value in values)


def _source_is_valid(source: Source | object) -> bool:
    citation = _clean_text(getattr(source, "citation", None))
    if not citation:
        return False
    url = _clean_text(getattr(source, "url", None))
    if not url:
        return True
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _lesson_sources(lesson: Lesson | None, sources: Iterable[Source | object] | None = None) -> list[Source | object]:
    if sources is not None:
        return list(sources)
    if lesson is None:
        return []
    return list(getattr(lesson, "sources", []) or [])


def evaluate_lesson_readiness(
    lesson: Lesson | None = None,
    *,
    title: str | None = None,
    objective: str | None = None,
    learning_objectives: str | None = None,
    key_concepts: list[str] | None = None,
    hook: str | None = None,
    content: str | None = None,
    guided_practice: str | None = None,
    independent_practice: str | None = None,
    assessment: str | None = None,
    sources: Iterable[Source | object] | None = None,
) -> LessonReadinessResult:
    title_value = _clean_text(title if title is not None else getattr(lesson, "title", None))
    objective_value = _clean_text(
        objective if objective is not None else getattr(lesson, "objective", None)
    )
    learning_objectives_value = _clean_text(
        learning_objectives
        if learning_objectives is not None
        else getattr(lesson, "learning_objectives", None)
    )
    key_concepts_value = key_concepts if key_concepts is not None else getattr(lesson, "key_concepts", None)
    hook_value = _clean_text(hook if hook is not None else getattr(lesson, "hook", None))
    content_value = _clean_text(content if content is not None else getattr(lesson, "content", None))
    guided_practice_value = _clean_text(
        guided_practice
        if guided_practice is not None
        else getattr(lesson, "guided_practice", None)
    )
    independent_practice_value = _clean_text(
        independent_practice
        if independent_practice is not None
        else getattr(lesson, "independent_practice", None)
    )
    assessment_value = _clean_text(
        assessment if assessment is not None else getattr(lesson, "assessment", None)
    )
    lesson_sources = _lesson_sources(lesson, sources)

    missing_fields: list[str] = []

    if not title_value:
        missing_fields.append("title")
    if not (objective_value or learning_objectives_value):
        missing_fields.append("objective_or_learning_objectives")
    if not _has_non_empty_items(key_concepts_value):
        missing_fields.append("key_concepts")
    if not hook_value:
        missing_fields.append("hook")
    if not content_value:
        missing_fields.append("content")
    if not guided_practice_value:
        missing_fields.append("guided_practice")
    if not independent_practice_value:
        missing_fields.append("independent_practice")
    if not assessment_value:
        missing_fields.append("assessment")
    if not lesson_sources:
        missing_fields.append("sources")
    elif not any(_source_is_valid(source) for source in lesson_sources):
        missing_fields.append("sources")

    for index, source in enumerate(lesson_sources):
        citation = _clean_text(getattr(source, "citation", None))
        if not citation:
            missing_fields.append(f"sources[{index}].citation")
        url = _clean_text(getattr(source, "url", None))
        if url and not _source_is_valid(source):
            missing_fields.append(f"sources[{index}].url")

    deduped_missing_fields = list(dict.fromkeys(missing_fields))
    return LessonReadinessResult(
        is_ready=not deduped_missing_fields,
        missing_fields=deduped_missing_fields,
    )


def validate_review_status(review_status: str) -> str:
    if review_status not in VALID_REVIEW_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid review status.")
    return review_status


def _membership_value(value: object | None) -> str | None:
    if value is None:
        return None
    return getattr(value, "value", value)


def _get_course_for_unit(db: Session, unit_id) -> Course | None:
    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if not unit:
        return None
    return db.query(Course).filter(Course.id == unit.course_id).first()


def can_manage_lesson_review(
    db: Session,
    current_user,
    *,
    lesson: Lesson | None = None,
    unit_id=None,
) -> bool:
    if current_user.role == "admin":
        return True

    course: Course | None = None
    if lesson is not None:
        course = lesson.unit.course if lesson.unit else None
        if course is None:
            course = _get_course_for_unit(db, lesson.unit_id)
    elif unit_id is not None:
        course = _get_course_for_unit(db, unit_id)

    if course is None or course.organization_id is None:
        return False

    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == course.organization_id,
            OrganizationMembership.user_id == current_user.id,
        )
        .first()
    )
    if membership is None:
        return False

    membership_role = _membership_value(membership.role)
    membership_status = _membership_value(membership.status)
    return membership_role in REVIEWER_ORG_ROLES and membership_status == MembershipStatus.ACTIVE.value


def resolve_review_fields(
    *,
    db: Session,
    current_user,
    requested_status: str,
    unit_id,
    lesson: Lesson | None = None,
    readiness: LessonReadinessResult,
) -> tuple[str, object | None]:
    review_status = validate_review_status(requested_status)

    if review_status in {"reviewed", "approved"} and not can_manage_lesson_review(
        db,
        current_user,
        lesson=lesson,
        unit_id=unit_id,
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to update lesson review fields.",
        )

    if review_status == "approved" and not readiness.is_ready:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Lesson is not ready for approval.",
                "missing_readiness_fields": readiness.missing_fields,
            },
        )

    if review_status == "draft":
        return review_status, None

    return review_status, current_user.id


def is_lesson_approved_and_ready(lesson: Lesson) -> bool:
    return lesson.review_status == "approved" and evaluate_lesson_readiness(lesson).is_ready


def _sort_lessons_for_delivery(lessons: Iterable[Lesson]) -> list[Lesson]:
    return sorted(
        list(lessons),
        key=lambda lesson: (
            lesson.order is None,
            lesson.order if lesson.order is not None else 0,
            str(lesson.id),
        ),
    )


def _sort_units_for_governance(units: Iterable[Unit]) -> list[Unit]:
    return sorted(
        list(units),
        key=lambda unit: (
            unit.order is None,
            unit.order if unit.order is not None else 0,
            str(unit.id),
        ),
    )


def _issue_for_entity(
    *,
    entity_type: str,
    entity,
    code: str,
    message: str,
) -> PublishReadinessIssue:
    return PublishReadinessIssue(
        entity_type=entity_type,
        entity_id=getattr(entity, "id", None),
        entity_title=_clean_text(getattr(entity, "title", None)) or entity_type.title(),
        code=code,
        message=message,
    )


def _deterministic_order_issues(
    items: Iterable[object],
    *,
    entity_type: str,
) -> list[PublishReadinessIssue]:
    issues: list[PublishReadinessIssue] = []
    seen_orders: dict[int, object] = {}

    for item in items:
        order = getattr(item, "order", None)
        if order is None:
            issues.append(
                _issue_for_entity(
                    entity_type=entity_type,
                    entity=item,
                    code="missing_order",
                    message=f"{entity_type.title()} is missing an explicit order value.",
                )
            )
            continue

        if order in seen_orders:
            issues.append(
                _issue_for_entity(
                    entity_type=entity_type,
                    entity=item,
                    code="duplicate_order",
                    message=(
                        f"{entity_type.title()} order {order} is duplicated and must be unique "
                        "for deterministic publishing."
                    ),
                )
            )
            original = seen_orders[order]
            if not any(
                existing.code == "duplicate_order" and existing.entity_id == getattr(original, "id", None)
                for existing in issues
            ):
                issues.append(
                    _issue_for_entity(
                        entity_type=entity_type,
                        entity=original,
                        code="duplicate_order",
                        message=(
                            f"{entity_type.title()} order {order} is duplicated and must be unique "
                            "for deterministic publishing."
                        ),
                    )
                )
            continue

        seen_orders[order] = item

    return issues


def evaluate_lesson_publish_readiness(lesson: Lesson) -> PublishReadinessResult:
    blocking_issues: list[PublishReadinessIssue] = []
    readiness = evaluate_lesson_readiness(lesson)

    if getattr(lesson, "review_status", None) != "approved":
        blocking_issues.append(
            _issue_for_entity(
                entity_type="lesson",
                entity=lesson,
                code="review_status_not_approved",
                message="Lesson must be approved before it is publish-ready for learners.",
            )
        )

    if not readiness.is_ready:
        for missing_field in readiness.missing_fields:
            blocking_issues.append(
                _issue_for_entity(
                    entity_type="lesson",
                    entity=lesson,
                    code="missing_readiness_field",
                    message=f"Lesson is missing required publish-readiness field: {missing_field}.",
                )
            )

    if getattr(lesson, "order", None) is None:
        blocking_issues.append(
            _issue_for_entity(
                entity_type="lesson",
                entity=lesson,
                code="missing_order",
                message="Lesson is missing an explicit order value.",
            )
        )

    return PublishReadinessResult(
        entity_type="lesson",
        entity_id=lesson.id,
        entity_title=lesson.title,
        is_ready=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=[],
    )


def evaluate_unit_publish_readiness(unit: Unit) -> PublishReadinessResult:
    blocking_issues: list[PublishReadinessIssue] = []
    warnings: list[PublishReadinessIssue] = []

    if getattr(unit, "order", None) is None:
        blocking_issues.append(
            _issue_for_entity(
                entity_type="unit",
                entity=unit,
                code="missing_order",
                message="Unit is missing an explicit order value.",
            )
        )

    unit_lessons = _sort_lessons_for_delivery(unit.lessons or [])
    if not unit_lessons:
        warnings.append(
            _issue_for_entity(
                entity_type="unit",
                entity=unit,
                code="empty_unit",
                message="Unit does not contain any lessons yet.",
            )
        )

    blocking_issues.extend(_deterministic_order_issues(unit_lessons, entity_type="lesson"))
    for lesson in unit_lessons:
        blocking_issues.extend(evaluate_lesson_publish_readiness(lesson).blocking_issues)

    return PublishReadinessResult(
        entity_type="unit",
        entity_id=unit.id,
        entity_title=unit.title,
        is_ready=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def evaluate_course_publish_readiness(course: Course) -> PublishReadinessResult:
    blocking_issues: list[PublishReadinessIssue] = []
    warnings: list[PublishReadinessIssue] = []

    course_units = _sort_units_for_governance(course.units or [])
    if not course_units:
        warnings.append(
            _issue_for_entity(
                entity_type="course",
                entity=course,
                code="empty_course",
                message="Course does not contain any units yet.",
            )
        )

    blocking_issues.extend(_deterministic_order_issues(course_units, entity_type="unit"))
    for unit in course_units:
        unit_readiness = evaluate_unit_publish_readiness(unit)
        blocking_issues.extend(unit_readiness.blocking_issues)
        warnings.extend(unit_readiness.warnings)

    return PublishReadinessResult(
        entity_type="course",
        entity_id=course.id,
        entity_title=course.title,
        is_ready=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def _revision_metadata_issues(
    *,
    entity_type: str,
    entity,
) -> tuple[list[PublishReadinessIssue], list[PublishReadinessIssue]]:
    blocking_issues: list[PublishReadinessIssue] = []
    warnings: list[PublishReadinessIssue] = []

    revision_number = getattr(entity, "revision_number", None)
    revision_status = _clean_text(getattr(entity, "revision_status", None)) or "current"
    published_at = getattr(entity, "published_at", None)
    deprecated_at = getattr(entity, "deprecated_at", None)

    if revision_number is None or revision_number < 1:
        blocking_issues.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="invalid_revision_number",
                message=f"{entity_type.title()} revision number must be greater than or equal to 1.",
            )
        )

    if revision_status not in VALID_REVISION_STATUSES:
        blocking_issues.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="invalid_revision_status",
                message=(
                    f"{entity_type.title()} revision status '{revision_status}' is not supported for "
                    "safe publish validation."
                ),
            )
        )
        return blocking_issues, warnings

    if revision_status in {"deprecated", "archived"}:
        blocking_issues.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="blocked_revision_status",
                message=(
                    f"{entity_type.title()} with revision status '{revision_status}' cannot be safely "
                    "published or republished."
                ),
            )
        )
        if deprecated_at is None:
            warnings.append(
                _issue_for_entity(
                    entity_type=entity_type,
                    entity=entity,
                    code="missing_deprecated_at",
                    message=(
                        f"{entity_type.title()} is marked '{revision_status}' but has no deprecated_at timestamp."
                    ),
                )
            )

    if revision_status == "draft" and published_at is not None:
        warnings.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="draft_has_published_at",
                message="Draft revision metadata already contains a published_at timestamp.",
            )
        )

    if revision_status == "current" and deprecated_at is not None:
        warnings.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="current_has_deprecated_at",
                message="Current revision metadata should not already carry deprecated_at.",
            )
        )

    if revision_status in {"draft", "current"} and deprecated_at is not None and published_at and deprecated_at < published_at:
        warnings.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="deprecated_before_published",
                message="Revision metadata contains deprecated_at earlier than published_at.",
            )
        )

    return blocking_issues, warnings


def _lineage_metadata_issues(
    *,
    entity_type: str,
    entity,
) -> tuple[list[PublishReadinessIssue], list[PublishReadinessIssue]]:
    blocking_issues: list[PublishReadinessIssue] = []
    warnings: list[PublishReadinessIssue] = []

    entity_id = getattr(entity, "id", None)
    revision_status = _clean_text(getattr(entity, "revision_status", None)) or "current"
    lineage_status = _clean_text(getattr(entity, "lineage_status", None)) or "standalone"
    previous_revision_id = getattr(entity, "previous_revision_id", None)
    superseded_by_id = getattr(entity, "superseded_by_id", None)

    if lineage_status not in VALID_LINEAGE_STATUSES:
        blocking_issues.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="invalid_lineage_status",
                message=(
                    f"{entity_type.title()} lineage status '{lineage_status}' is not supported for "
                    "historical lineage validation."
                ),
            )
        )
        return blocking_issues, warnings

    if previous_revision_id is not None and previous_revision_id == entity_id:
        blocking_issues.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="self_referential_previous_revision",
                message=f"{entity_type.title()} cannot reference itself as previous revision.",
            )
        )

    if superseded_by_id is not None and superseded_by_id == entity_id:
        blocking_issues.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="self_referential_successor_revision",
                message=f"{entity_type.title()} cannot reference itself as successor revision.",
            )
        )

    if (
        previous_revision_id is not None
        and superseded_by_id is not None
        and previous_revision_id == superseded_by_id
    ):
        blocking_issues.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="previous_and_successor_match",
                message=(
                    f"{entity_type.title()} previous_revision_id and superseded_by_id cannot point "
                    "to the same revision."
                ),
            )
        )

    if revision_status == "current" and lineage_status in {"superseded", "deprecated", "archived"}:
        blocking_issues.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="current_revision_inconsistent_lineage_status",
                message=(
                    f"{entity_type.title()} is a current revision but lineage status is "
                    f"'{lineage_status}'."
                ),
            )
        )

    if revision_status in {"deprecated", "archived"} and lineage_status in {"standalone", "current"}:
        warnings.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="deprecated_revision_missing_lineage_status",
                message=(
                    f"{entity_type.title()} revision status '{revision_status}' should usually carry "
                    "deprecated, archived, or superseded lineage context."
                ),
            )
        )

    if lineage_status == "standalone" and (previous_revision_id is not None or superseded_by_id is not None):
        warnings.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="standalone_has_lineage_references",
                message=(
                    f"{entity_type.title()} is marked standalone but still carries predecessor or "
                    "successor references."
                ),
            )
        )

    if lineage_status == "current" and superseded_by_id is not None:
        warnings.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="current_has_successor_reference",
                message=(
                    f"{entity_type.title()} is marked current while also carrying a successor reference."
                ),
            )
        )

    if lineage_status in {"superseded", "deprecated", "archived"} and superseded_by_id is None:
        warnings.append(
            _issue_for_entity(
                entity_type=entity_type,
                entity=entity,
                code="missing_successor_reference",
                message=(
                    f"{entity_type.title()} is marked '{lineage_status}' but has no successor revision "
                    "reference."
                ),
            )
        )

    return blocking_issues, warnings


def evaluate_course_lineage_coherence(course: Course) -> LineageCoherenceResult:
    blocking_issues, warnings = _lineage_metadata_issues(entity_type="course", entity=course)
    return LineageCoherenceResult(
        entity_type="course",
        entity_id=course.id,
        entity_title=course.title,
        is_coherent=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def evaluate_unit_lineage_coherence(unit: Unit) -> LineageCoherenceResult:
    blocking_issues, warnings = _lineage_metadata_issues(entity_type="unit", entity=unit)
    return LineageCoherenceResult(
        entity_type="unit",
        entity_id=unit.id,
        entity_title=unit.title,
        is_coherent=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def evaluate_lesson_lineage_coherence(lesson: Lesson) -> LineageCoherenceResult:
    blocking_issues, warnings = _lineage_metadata_issues(entity_type="lesson", entity=lesson)
    return LineageCoherenceResult(
        entity_type="lesson",
        entity_id=lesson.id,
        entity_title=lesson.title,
        is_coherent=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def evaluate_assessment_lineage_coherence(assessment) -> LineageCoherenceResult:
    blocking_issues, warnings = _lineage_metadata_issues(entity_type="assessment", entity=assessment)
    return LineageCoherenceResult(
        entity_type="assessment",
        entity_id=assessment.id,
        entity_title=assessment.title,
        is_coherent=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def _student_course_is_active(student_course) -> bool:
    return _clean_text(getattr(student_course, "status", None)).lower() not in {"", "completed", "withdrawn"}


def _unit_progress_is_active(unit_progress) -> bool:
    status = getattr(unit_progress, "status", None)
    status_value = _clean_text(getattr(status, "value", status)).lower()
    return status_value not in {"", "completed"}


def _segment_progress_exists(segment_progress) -> bool:
    return getattr(segment_progress, "id", None) is not None


def evaluate_course_learner_progress_safety(course: Course) -> LearnerProgressSafetyResult:
    blocking_issues: list[PublishReadinessIssue] = []
    warnings: list[PublishReadinessIssue] = []

    revision_status = _clean_text(getattr(course, "revision_status", None)) or "current"
    lineage_status = _clean_text(getattr(course, "lineage_status", None)) or "standalone"
    active_student_courses = [student_course for student_course in (course.student_courses or []) if _student_course_is_active(student_course)]

    if revision_status in {"deprecated", "archived"} and active_student_courses:
        blocking_issues.append(
            _issue_for_entity(
                entity_type="course",
                entity=course,
                code="active_course_progress_on_deprecated_revision",
                message=(
                    "Active learner course progress exists for a deprecated or archived course revision. "
                    "Historical learner continuity would be at risk."
                ),
            )
        )

    if (
        active_student_courses
        and lineage_status in {"superseded", "deprecated", "archived"}
        and getattr(course, "superseded_by_id", None) is None
    ):
        warnings.append(
            _issue_for_entity(
                entity_type="course",
                entity=course,
                code="missing_successor_metadata_with_active_course_progress",
                message=(
                    "Learner course progress exists, but the historical course revision has no successor "
                    "metadata for staff interpretation."
                ),
            )
        )

    return LearnerProgressSafetyResult(
        entity_type="course",
        entity_id=course.id,
        entity_title=course.title,
        is_safe=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def evaluate_unit_learner_progress_safety(unit: Unit) -> LearnerProgressSafetyResult:
    blocking_issues: list[PublishReadinessIssue] = []
    warnings: list[PublishReadinessIssue] = []

    revision_status = _clean_text(getattr(unit, "revision_status", None)) or "current"
    lineage_status = _clean_text(getattr(unit, "lineage_status", None)) or "standalone"
    active_unit_progress = [progress for progress in (unit.student_progress or []) if _unit_progress_is_active(progress)]

    if revision_status in {"deprecated", "archived"} and active_unit_progress:
        blocking_issues.append(
            _issue_for_entity(
                entity_type="unit",
                entity=unit,
                code="active_unit_progress_on_deprecated_revision",
                message=(
                    "Active learner unit progress exists for a deprecated or archived unit revision. "
                    "Historical unit continuity would be at risk."
                ),
            )
        )

    if (
        active_unit_progress
        and lineage_status in {"superseded", "deprecated", "archived"}
        and getattr(unit, "superseded_by_id", None) is None
    ):
        warnings.append(
            _issue_for_entity(
                entity_type="unit",
                entity=unit,
                code="missing_successor_metadata_with_active_unit_progress",
                message=(
                    "Learner unit progress exists, but the historical unit revision has no successor "
                    "metadata for staff interpretation."
                ),
            )
        )

    return LearnerProgressSafetyResult(
        entity_type="unit",
        entity_id=unit.id,
        entity_title=unit.title,
        is_safe=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def evaluate_lesson_learner_progress_safety(lesson: Lesson) -> LearnerProgressSafetyResult:
    blocking_issues: list[PublishReadinessIssue] = []
    warnings: list[PublishReadinessIssue] = []

    revision_status = _clean_text(getattr(lesson, "revision_status", None)) or "current"
    lineage_status = _clean_text(getattr(lesson, "lineage_status", None)) or "standalone"

    segment_references = []
    student_progress = getattr(getattr(lesson, "unit", None), "student_progress", None) or []
    for unit_progress in student_progress:
        for segment in getattr(unit_progress, "segments", None) or []:
            if getattr(segment, "lesson_id", None) == lesson.id and _segment_progress_exists(segment):
                segment_references.append(segment)

    if revision_status in {"deprecated", "archived"} and segment_references:
        blocking_issues.append(
            _issue_for_entity(
                entity_type="lesson",
                entity=lesson,
                code="segment_progress_on_deprecated_revision",
                message=(
                    "Learner segment progress exists for a deprecated or archived lesson revision. "
                    "Historical lesson continuity would be at risk."
                ),
            )
        )

    if lineage_status == "superseded" and segment_references:
        blocking_issues.append(
            _issue_for_entity(
                entity_type="lesson",
                entity=lesson,
                code="segment_progress_on_superseded_revision",
                message=(
                    "Learner segment progress still references a superseded lesson revision. "
                    "Historical segment references must remain explicit and protected."
                ),
            )
        )

    if (
        segment_references
        and lineage_status in {"superseded", "deprecated", "archived"}
        and getattr(lesson, "superseded_by_id", None) is None
    ):
        warnings.append(
            _issue_for_entity(
                entity_type="lesson",
                entity=lesson,
                code="missing_successor_metadata_with_segment_progress",
                message=(
                    "Learner segment progress exists, but the historical lesson revision has no successor "
                    "metadata for staff interpretation."
                ),
            )
        )

    return LearnerProgressSafetyResult(
        entity_type="lesson",
        entity_id=lesson.id,
        entity_title=lesson.title,
        is_safe=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def _assessment_attempt_events(assessment: Assessment) -> list[object]:
    events_by_id: dict[object, object] = {}

    for event in getattr(assessment, "events", None) or []:
        events_by_id[getattr(event, "id", id(event))] = event

    for attempt in getattr(assessment, "attempts", None) or []:
        for event in getattr(attempt, "events", None) or []:
            events_by_id[getattr(event, "id", id(event))] = event

    return list(events_by_id.values())


def _assessment_curriculum_contexts(assessment: Assessment) -> list[tuple[str, object]]:
    contexts: list[tuple[str, object]] = []
    seen_ids: set[object] = set()

    lesson = getattr(assessment, "lesson", None)
    unit = getattr(assessment, "unit", None) or getattr(lesson, "unit", None)
    course = (
        getattr(assessment, "course", None)
        or getattr(unit, "course", None)
        or getattr(getattr(lesson, "unit", None), "course", None)
    )

    for entity_type, entity in (
        ("lesson", lesson),
        ("unit", unit),
        ("course", course),
    ):
        entity_id = getattr(entity, "id", None)
        if entity is None or entity_id in seen_ids:
            continue
        seen_ids.add(entity_id)
        contexts.append((entity_type, entity))

    return contexts


def _assessment_evidence_state_is_ambiguous(*, revision_status: str, lineage_status: str, has_successor: bool) -> bool:
    if revision_status == "draft":
        return True
    if revision_status == "current" and lineage_status in {"superseded", "deprecated", "archived"}:
        return True
    if revision_status in {"deprecated", "archived"} and lineage_status in {"current", "standalone"}:
        return True
    if has_successor and revision_status == "current":
        return True
    return False


def evaluate_assessment_evidence_safety(assessment: Assessment) -> AssessmentEvidenceSafetyResult:
    blocking_issues: list[PublishReadinessIssue] = []
    warnings: list[PublishReadinessIssue] = []

    revision_status = _clean_text(getattr(assessment, "revision_status", None)) or "current"
    lineage_status = _clean_text(getattr(assessment, "lineage_status", None)) or "standalone"
    attempts = list(getattr(assessment, "attempts", None) or [])
    attempt_events = _assessment_attempt_events(assessment)
    has_attempts = bool(attempts)
    has_attempt_events = bool(attempt_events)
    has_historical_evidence = has_attempts or has_attempt_events
    non_current_history_state = (
        revision_status in {"deprecated", "archived"}
        or lineage_status in {"superseded", "deprecated", "archived"}
    )
    has_successor = getattr(assessment, "superseded_by_id", None) is not None

    if has_attempts and non_current_history_state:
        blocking_issues.append(
            _issue_for_entity(
                entity_type="assessment",
                entity=assessment,
                code="attempts_on_non_current_assessment_revision",
                message=(
                    "Assessment has historical attempt records while marked deprecated, archived, "
                    "or superseded. Historical evidence must remain anchored to the original "
                    "revision without introducing grading ambiguity."
                ),
            )
        )

    if has_attempt_events and non_current_history_state:
        blocking_issues.append(
            _issue_for_entity(
                entity_type="assessment",
                entity=assessment,
                code="attempt_events_on_non_current_assessment_revision",
                message=(
                    "Assessment has historical attempt-event records while marked deprecated, "
                    "archived, or superseded. Historical event evidence must remain explicit."
                ),
            )
        )

    if has_historical_evidence and not has_successor and non_current_history_state:
        warnings.append(
            _issue_for_entity(
                entity_type="assessment",
                entity=assessment,
                code="missing_successor_metadata_with_historical_evidence",
                message=(
                    "Assessment has historical evidence but no successor metadata for staff, mastery, "
                    "or reporting interpretation."
                ),
            )
        )

    if has_historical_evidence and _assessment_evidence_state_is_ambiguous(
        revision_status=revision_status,
        lineage_status=lineage_status,
        has_successor=has_successor,
    ):
        blocking_issues.append(
            _issue_for_entity(
                entity_type="assessment",
                entity=assessment,
                code="ambiguous_evidence_revision_state",
                message=(
                    "Assessment revision and lineage metadata would make historical mastery or "
                    "reporting interpretation ambiguous."
                ),
            )
        )

    if has_historical_evidence:
        for entity_type, entity in _assessment_curriculum_contexts(assessment):
            context_revision_status = _clean_text(getattr(entity, "revision_status", None)) or "current"
            if context_revision_status not in {"deprecated", "archived"}:
                continue
            blocking_issues.append(
                _issue_for_entity(
                    entity_type=entity_type,
                    entity=entity,
                    code="historical_evidence_on_deprecated_curriculum_context",
                    message=(
                        "Historical assessment evidence exists while the surrounding curriculum "
                        "context is deprecated or archived, which risks ambiguous interpretation."
                    ),
                )
            )

    return AssessmentEvidenceSafetyResult(
        entity_type="assessment",
        entity_id=assessment.id,
        entity_title=assessment.title,
        is_safe=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def _collect_course_assessments(course: Course) -> list[object]:
    assessments_by_id: dict[object, object] = {}

    for assessment in course.assessments or []:
        assessments_by_id[assessment.id] = assessment
    for unit in course.units or []:
        for assessment in unit.assessments or []:
            assessments_by_id[assessment.id] = assessment
        for lesson in unit.lessons or []:
            for assessment in lesson.assessments or []:
                assessments_by_id[assessment.id] = assessment

    return list(assessments_by_id.values())


def evaluate_course_safe_publish(course: Course) -> SafePublishValidationResult:
    blocking_issues: list[PublishReadinessIssue] = []
    warnings: list[PublishReadinessIssue] = []

    readiness = evaluate_course_publish_readiness(course)
    blocking_issues.extend(readiness.blocking_issues)
    warnings.extend(readiness.warnings)

    course_blockers, course_warnings = _revision_metadata_issues(entity_type="course", entity=course)
    blocking_issues.extend(course_blockers)
    warnings.extend(course_warnings)

    for unit in _sort_units_for_governance(course.units or []):
        unit_blockers, unit_warnings = _revision_metadata_issues(entity_type="unit", entity=unit)
        blocking_issues.extend(unit_blockers)
        warnings.extend(unit_warnings)

        for lesson in _sort_lessons_for_delivery(unit.lessons or []):
            lesson_blockers, lesson_warnings = _revision_metadata_issues(entity_type="lesson", entity=lesson)
            blocking_issues.extend(lesson_blockers)
            warnings.extend(lesson_warnings)

            if getattr(lesson, "revision_status", "current") in {"deprecated", "archived"} and course.student_courses:
                blocking_issues.append(
                    _issue_for_entity(
                        entity_type="lesson",
                        entity=lesson,
                        code="learner_progress_safety_risk",
                        message=(
                            "Learner course progress exists for a lesson marked deprecated or archived. "
                            "Republish would risk historical learner continuity."
                        ),
                    )
                )

    for assessment in _collect_course_assessments(course):
        assessment_blockers, assessment_warnings = _revision_metadata_issues(
            entity_type="assessment",
            entity=assessment,
        )
        blocking_issues.extend(assessment_blockers)
        warnings.extend(assessment_warnings)

        assessment_evidence_safety = evaluate_assessment_evidence_safety(assessment)
        blocking_issues.extend(assessment_evidence_safety.blocking_issues)
        warnings.extend(assessment_evidence_safety.warnings)

        if assessment_evidence_safety.blocking_issues:
            blocking_issues.append(
                _issue_for_entity(
                    entity_type="assessment",
                    entity=assessment,
                    code="assessment_evidence_safety_risk",
                    message=(
                        "Assessment has historical attempt or evidence records while marked deprecated or archived. "
                        "Republish would risk evidence continuity."
                    ),
                )
            )

    return SafePublishValidationResult(
        entity_type="course",
        entity_id=course.id,
        entity_title=course.title,
        is_safe=not blocking_issues,
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def governed_lessons_for_unit(unit: Unit | None) -> GovernedUnitSelection:
    if unit is None:
        return GovernedUnitSelection(
            state=EMPTY_CONTENT,
            lessons=[],
            detail="The requested instructional unit does not exist.",
        )

    unit_lessons = _sort_lessons_for_delivery(unit.lessons or [])
    if not unit_lessons:
        return GovernedUnitSelection(
            state=EMPTY_CONTENT,
            lessons=[],
            detail="This instructional unit does not contain any lessons.",
        )

    approved_ready = [
        lesson for lesson in unit_lessons if is_lesson_approved_and_ready(lesson)
    ]
    if approved_ready:
        return GovernedUnitSelection(
            state=GOVERNED_AVAILABLE,
            lessons=approved_ready,
            detail="Governed instructional content is available.",
        )

    if any(lesson.review_status == "reviewed" for lesson in unit_lessons):
        return GovernedUnitSelection(
            state=PENDING_REVIEW,
            lessons=[],
            detail="Instruction for this unit is pending governance review.",
        )

    return GovernedUnitSelection(
        state=NO_APPROVED_CONTENT,
        lessons=[],
        detail="No approved learner-ready lessons are available for this unit.",
    )


def governed_lesson_for_student(lesson: Lesson) -> GovernedLessonSelection:
    if is_lesson_approved_and_ready(lesson):
        return GovernedLessonSelection(
            state=GOVERNED_AVAILABLE,
            lesson=lesson,
            detail="Governed instructional content is available.",
        )

    unit_selection = governed_lessons_for_unit(lesson.unit if lesson.unit else None)
    if lesson.review_status == "reviewed":
        return GovernedLessonSelection(
            state=PENDING_REVIEW,
            lesson=None,
            detail="This lesson is pending governance review.",
        )

    if unit_selection.state == GOVERNED_AVAILABLE:
        return GovernedLessonSelection(
            state=GOVERNED_UNAVAILABLE,
            lesson=None,
            detail="This lesson is not learner-eligible.",
        )

    return GovernedLessonSelection(
        state=unit_selection.state,
        lesson=None,
        detail=unit_selection.detail,
    )


def raise_governed_unavailable(selection: GovernedLessonSelection, *, lesson_id) -> None:
    raise HTTPException(
        status_code=409,
        detail={
            "delivery_state": selection.state,
            "lesson_id": str(lesson_id),
            "message": selection.detail,
        },
    )


def serialize_lesson(lesson: Lesson, *, viewer_role: str) -> LessonResponse:
    readiness = evaluate_lesson_readiness(lesson)
    show_staff_fields = viewer_role in EDUCATOR_VIEWER_ROLES
    teacher_notes = lesson.teacher_notes if show_staff_fields else None
    discussion_questions = lesson.discussion_questions or []
    review_status = lesson.review_status if show_staff_fields else None
    reviewed_by = lesson.reviewed_by if show_staff_fields else None
    is_ready_for_approval = readiness.is_ready if show_staff_fields else None
    missing_readiness_fields = readiness.missing_fields if show_staff_fields else []

    return LessonResponse(
        id=lesson.id,
        title=lesson.title,
        objective=lesson.objective,
        learning_objectives=lesson.learning_objectives,
        key_concepts=lesson.key_concepts or [],
        teacher_notes=teacher_notes,
        discussion_questions=discussion_questions,
        hook=lesson.hook,
        content=lesson.content,
        guided_practice=lesson.guided_practice,
        independent_practice=lesson.independent_practice,
        assessment=lesson.assessment,
        review_status=review_status,
        reviewed_by=reviewed_by,
        skill_tags=lesson.skill_tags or [],
        standards_metadata=lesson.standards_metadata or {},
        revision_number=lesson.revision_number,
        revision_label=lesson.revision_label,
        revision_status=lesson.revision_status,
        revision_metadata=lesson.revision_metadata or {},
        previous_revision_id=lesson.previous_revision_id,
        superseded_by_id=lesson.superseded_by_id,
        lineage_status=lesson.lineage_status,
        lineage_metadata=lesson.lineage_metadata or {},
        published_at=lesson.published_at,
        deprecated_at=lesson.deprecated_at,
        order=lesson.order,
        duration_minutes=lesson.duration_minutes,
        activities=[
            ActivityResponse(
                id=activity.id,
                type=activity.type,
                title=activity.title,
                content=activity.content,
                order=activity.order,
                media=_serialize_media(activity.media),
                pages=[
                    StorybookPageResponse.from_orm(page)
                    for page in activity.storybook_pages or []
                ],
            )
            for activity in lesson.activities or []
        ],
        sources=[
            SourceResponse(
                id=source.id,
                citation=source.citation,
                url=source.url,
                created_at=source.created_at,
            )
            for source in lesson.sources or []
        ],
        is_ready_for_approval=is_ready_for_approval,
        missing_readiness_fields=missing_readiness_fields,
    )


def _serialize_media(media: Media | None) -> MediaResponse | None:
    if media is None:
        return None
    return MediaResponse(
        id=media.id,
        type=media.type,
        title=media.title,
        url=media.url,
        description=media.description,
    )


def serialize_course(course: Course, *, viewer_role: str) -> CourseResponse:
    learner_view = viewer_role == "student"
    return CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        learning_objectives=course.learning_objectives,
        skill_tags=course.skill_tags or [],
        standards_metadata=course.standards_metadata or {},
        revision_number=course.revision_number,
        revision_label=course.revision_label,
        revision_status=course.revision_status,
        revision_metadata=course.revision_metadata or {},
        previous_revision_id=course.previous_revision_id,
        superseded_by_id=course.superseded_by_id,
        lineage_status=course.lineage_status,
        lineage_metadata=course.lineage_metadata or {},
        published_at=course.published_at,
        deprecated_at=course.deprecated_at,
        units=[
            UnitResponse(
                id=unit.id,
                title=unit.title,
                content=unit.content,
                revision_number=unit.revision_number,
                revision_label=unit.revision_label,
                revision_status=unit.revision_status,
                revision_metadata=unit.revision_metadata or {},
                previous_revision_id=unit.previous_revision_id,
                superseded_by_id=unit.superseded_by_id,
                lineage_status=unit.lineage_status,
                lineage_metadata=unit.lineage_metadata or {},
                published_at=unit.published_at,
                deprecated_at=unit.deprecated_at,
                order=unit.order,
                lessons=[
                    serialize_lesson(lesson, viewer_role=viewer_role)
                    for lesson in (
                        governed_lessons_for_unit(unit).lessons
                        if learner_view
                        else _sort_lessons_for_delivery(unit.lessons or [])
                    )
                ],
                learner_availability=(
                    governed_lessons_for_unit(unit).state if learner_view else None
                ),
                learner_availability_detail=(
                    governed_lessons_for_unit(unit).detail if learner_view else None
                ),
            )
            for unit in course.units or []
        ],
    )
