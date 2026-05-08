from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.enum import MembershipStatus
from app.models import (
    Activity,
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
        units=[
            UnitResponse(
                id=unit.id,
                title=unit.title,
                content=unit.content,
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
