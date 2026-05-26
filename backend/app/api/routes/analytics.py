from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from uuid import UUID

from app.crud.badges import BADGE_RULES, calculate_streak_days, get_or_create_badge
from app.database import get_db
from app.deps import require_roles, require_org_roles
from app.enum import ProgressStatus
from app.models import (
    Assessment,
    StudentAssessmentAttempt,
    Course,
    Lesson,
    SegmentProgress,
    StudentBadge,
    StudentCourse,
    StudentUnitProgress,
    Unit,
    User,
    Enrollment,
)
from app.schemas import (
    AssessmentEvidenceSummaryResponse,
    AssessmentReportingSummaryResponse,
    ContinuationGuidanceResponse,
    EducatorRuntimeSupportSummaryResponse,
    MasteryObjectiveSummaryResponse,
    MasterySummaryResponse,
    ReportingProgressSnapshotResponse,
)

router = APIRouter()

FLAGSHIP_PATHWAY_KEY = "introduction-to-africa"


def _latest_attempt_for_assessment(assessment: Assessment, student_id):
    attempts = [
        attempt
        for attempt in assessment.attempts
        if attempt.student_id == student_id
    ]
    if not attempts:
        return None
    return max(attempts, key=lambda attempt: (attempt.submitted_at, str(attempt.id)))


def _latest_event_metadata(attempt: StudentAssessmentAttempt) -> dict:
    scored_events = [event for event in attempt.events if event.event_type == "attempt_scored"]
    latest_event = scored_events[-1] if scored_events else (attempt.events[-1] if attempt.events else None)
    return dict(latest_event.event_metadata or {}) if latest_event else {}


def _build_mastery_summary(
    assessments: list[Assessment],
    student_id,
    *,
    lesson_id=None,
    unit_id=None,
    course_id=None,
    program_id=None,
) -> MasterySummaryResponse:
    totals: dict[str, dict[str, object]] = {}

    for assessment in assessments:
        if not assessment.competency_alignments:
            continue
        latest_attempt = _latest_attempt_for_assessment(assessment, student_id)
        if latest_attempt is None:
            continue
        evidence_weight = 1.0 if latest_attempt.passed else 0.0
        for alignment in assessment.competency_alignments:
            bucket = totals.setdefault(
                alignment.objective_key,
                {
                    "objective_key": alignment.objective_key,
                    "objective_title": alignment.objective_title,
                    "objective_type": alignment.objective_type,
                    "mastery_threshold": alignment.mastery_threshold,
                    "total_weight": 0.0,
                    "passed_weight": 0.0,
                    "assessments_considered": set(),
                    "attempts_considered": 0,
                    "latest_attempt_at": None,
                },
            )
            bucket["objective_title"] = bucket["objective_title"] or alignment.objective_title
            bucket["objective_type"] = alignment.objective_type
            bucket["mastery_threshold"] = max(float(bucket["mastery_threshold"]), alignment.mastery_threshold)
            bucket["total_weight"] = float(bucket["total_weight"]) + alignment.weight
            bucket["passed_weight"] = float(bucket["passed_weight"]) + (alignment.weight * evidence_weight)
            bucket["assessments_considered"].add(assessment.id)
            bucket["attempts_considered"] = int(bucket["attempts_considered"]) + 1
            latest_attempt_at = bucket["latest_attempt_at"]
            if latest_attempt_at is None or latest_attempt.submitted_at > latest_attempt_at:
                bucket["latest_attempt_at"] = latest_attempt.submitted_at

    objective_rows = []
    for bucket in sorted(totals.values(), key=lambda item: item["objective_key"]):
        total_weight = float(bucket["total_weight"])
        passed_weight = float(bucket["passed_weight"])
        mastery_percentage = round((passed_weight / total_weight) * 100, 1) if total_weight else 0.0
        mastery_threshold = float(bucket["mastery_threshold"])
        objective_rows.append(
            MasteryObjectiveSummaryResponse(
                objective_key=bucket["objective_key"],
                objective_title=bucket["objective_title"],
                objective_type=bucket["objective_type"],
                mastery_threshold=mastery_threshold,
                total_weight=total_weight,
                passed_weight=passed_weight,
                mastery_percentage=mastery_percentage,
                mastered=mastery_percentage >= mastery_threshold,
                assessments_considered=len(bucket["assessments_considered"]),
                attempts_considered=int(bucket["attempts_considered"]),
                latest_attempt_at=bucket["latest_attempt_at"],
            )
        )

    return MasterySummaryResponse(
        student_id=student_id,
        lesson_id=lesson_id,
        unit_id=unit_id,
        course_id=course_id,
        program_id=program_id,
        objectives=objective_rows,
    )


def _build_progress_snapshot(db: Session, student_id: UUID) -> ReportingProgressSnapshotResponse:
    lessons_completed = (
        db.query(SegmentProgress)
        .join(StudentUnitProgress, StudentUnitProgress.id == SegmentProgress.student_unit_id)
        .join(StudentCourse, StudentCourse.id == StudentUnitProgress.student_course_id)
        .filter(
            StudentCourse.student_id == student_id,
            SegmentProgress.status == ProgressStatus.COMPLETED,
        )
        .count()
    )
    units_completed = (
        db.query(StudentUnitProgress)
        .join(StudentCourse, StudentCourse.id == StudentUnitProgress.student_course_id)
        .filter(
            StudentCourse.student_id == student_id,
            StudentUnitProgress.status == ProgressStatus.COMPLETED,
        )
        .count()
    )
    courses_completed = (
        db.query(StudentCourse)
        .filter(StudentCourse.student_id == student_id, StudentCourse.status == "completed")
        .count()
    )
    last_activity_at = (
        db.query(StudentCourse.last_activity_at)
        .filter(StudentCourse.student_id == student_id)
        .order_by(StudentCourse.last_activity_at.desc())
        .first()
    )
    return ReportingProgressSnapshotResponse(
        lessons_completed=lessons_completed,
        units_completed=units_completed,
        courses_completed=courses_completed,
        last_activity_at=last_activity_at[0] if last_activity_at else None,
    )


def _is_flagship_course(course: Course | None) -> bool:
    if course is None:
        return False
    metadata = course.standards_metadata or {}
    return bool(metadata.get("flagship")) and metadata.get("pathway_key") == FLAGSHIP_PATHWAY_KEY


def _ordered_course_lessons(course: Course | None) -> list[Lesson]:
    if course is None:
        return []

    ordered_lessons: list[Lesson] = []
    for unit in sorted(
        course.units or [],
        key=lambda row: (row.order is None, row.order if row.order is not None else 0, str(row.id)),
    ):
        ordered_lessons.extend(
            sorted(
                unit.lessons or [],
                key=lambda row: (row.order is None, row.order if row.order is not None else 0, str(row.id)),
            )
        )
    return ordered_lessons


def _metadata_string_list(metadata: dict | None, key: str) -> list[str]:
    raw_values = (metadata or {}).get(key, [])
    if not isinstance(raw_values, list):
        return []
    return [str(value) for value in raw_values if value]


def _resolve_remediation_review_lesson(course: Course | None, assessment: Assessment) -> Lesson | None:
    lessons = _ordered_course_lessons(course)
    if not lessons:
        return None

    if assessment.lesson_id is not None:
        for lesson in lessons:
            if lesson.id == assessment.lesson_id:
                return lesson

    if assessment.unit_id is not None:
        for unit in course.units or []:
            if unit.id == assessment.unit_id:
                ordered_unit_lessons = sorted(
                    unit.lessons or [],
                    key=lambda row: (row.order is None, row.order if row.order is not None else 0, str(row.id)),
                )
                if ordered_unit_lessons:
                    return ordered_unit_lessons[0]

    return lessons[0]


def _build_remediation_review_prompts(lesson: Lesson | None) -> list[str]:
    if lesson is None:
        return []

    prompts = _metadata_string_list(lesson.standards_metadata, "remediation_review_prompts")
    if prompts:
        return prompts[:2]

    discussion_questions = [str(question) for question in (lesson.discussion_questions or []) if question]
    if discussion_questions:
        return discussion_questions[:2]

    key_concepts = [str(concept) for concept in (lesson.key_concepts or []) if concept]
    if key_concepts:
        return [f"Explain what {key_concepts[0]} means in this lesson."]

    return []


def _build_enrichment_extension_prompts(lesson: Lesson | None) -> list[str]:
    if lesson is None:
        return []

    prompts = _metadata_string_list(lesson.standards_metadata, "enrichment_extensions")
    if prompts:
        return prompts[:2]

    community_extensions = _metadata_string_list(lesson.standards_metadata, "community_extensions")
    if community_extensions:
        return community_extensions[:2]

    discussion_questions = [str(question) for question in (lesson.discussion_questions or []) if question]
    if discussion_questions:
        return discussion_questions[:2]

    return []


def _course_assessments_with_evidence(db: Session, course: Course | None) -> list[Assessment]:
    if course is None:
        return []

    unit_ids = [unit.id for unit in course.units or []]
    lesson_ids = [
        lesson.id
        for unit in course.units or []
        for lesson in unit.lessons or []
    ]
    filters = [Assessment.course_id == course.id]
    if unit_ids:
        filters.append(Assessment.unit_id.in_(unit_ids))
    if lesson_ids:
        filters.append(Assessment.lesson_id.in_(lesson_ids))

    return (
        db.query(Assessment)
        .options(
            selectinload(Assessment.attempts).selectinload(StudentAssessmentAttempt.events),
            selectinload(Assessment.competency_alignments),
        )
        .filter(or_(*filters))
        .all()
    )


def _latest_attempt_with_assessment(
    assessments: list[Assessment], student_id: UUID
) -> tuple[Assessment, StudentAssessmentAttempt] | None:
    latest: tuple[Assessment, StudentAssessmentAttempt] | None = None
    for assessment in assessments:
        if assessment.assessment_state != "published" or assessment.availability_state != "available":
            continue
        attempt = _latest_attempt_for_assessment(assessment, student_id)
        if attempt is None:
            continue
        if latest is None or (attempt.submitted_at, str(attempt.id)) > (
            latest[1].submitted_at,
            str(latest[1].id),
        ):
            latest = (assessment, attempt)
    return latest


def _display_name(user: User | None) -> str:
    if user is None:
        return "Unknown learner"
    full_name = f"{user.firstname} {user.lastname}".strip()
    return full_name or user.username or "Unknown learner"


def build_course_continuation_guidance(
    db: Session,
    course: Course | None,
    student_id: UUID,
    *,
    educator_visible: bool = False,
) -> ContinuationGuidanceResponse | None:
    if not _is_flagship_course(course):
        return None

    assessments = _course_assessments_with_evidence(db, course)
    mastery_summary = _build_mastery_summary(assessments, student_id, course_id=course.id if course else None)
    latest = _latest_attempt_with_assessment(assessments, student_id)

    if latest is None:
        return ContinuationGuidanceResponse(
            support_state="normal",
            learner_title="Your next lesson is ready",
            learner_message="Continue with your next governed lesson. Short checks along the way will help you notice what is sticking.",
            reinforcement_title="Steady start",
            reinforcement_message="You do not need to rush. Each lesson is another chance to notice, question, and grow your understanding.",
            recommended_action="continue",
            evidence_source="no_recent_assessment",
            educator_note=(
                "No recent flagship assessment evidence yet. Continue with the governed lesson path and watch for the learner's first check-for-understanding."
                if educator_visible
                else None
            ),
        )

    latest_assessment, latest_attempt = latest
    latest_percentage = (latest_attempt.score / latest_attempt.max_score * 100) if latest_attempt.max_score else 0.0
    mastered_objectives = mastery_summary.objectives and all(objective.mastered for objective in mastery_summary.objectives)
    review_lesson = _resolve_remediation_review_lesson(course, latest_assessment)
    review_lesson_title = review_lesson.title if review_lesson is not None else None
    review_prompts = _build_remediation_review_prompts(review_lesson)
    review_key_concepts = [str(concept) for concept in (review_lesson.key_concepts or []) if concept][:3] if review_lesson else []
    extension_lesson = review_lesson
    extension_lesson_title = extension_lesson.title if extension_lesson is not None else None
    extension_prompts = _build_enrichment_extension_prompts(extension_lesson)
    extension_key_concepts = (
        [str(concept) for concept in (extension_lesson.key_concepts or []) if concept][:3]
        if extension_lesson
        else []
    )
    educator_intervention_hint = (
        _metadata_string_list(review_lesson.standards_metadata if review_lesson else None, "intervention_hints")[0]
        if review_lesson is not None and _metadata_string_list(review_lesson.standards_metadata, "intervention_hints")
        else None
    )

    if not latest_attempt.passed:
        return ContinuationGuidanceResponse(
            support_state="remediation",
            learner_title="Take your next step with support",
            learner_message=(
                f"Your next lesson is still ready. Before or after you continue, revisit {review_lesson_title or latest_assessment.title} "
                "and use these review prompts to rebuild confidence one idea at a time."
            ),
            reinforcement_title="Learning can be rebuilt",
            reinforcement_message="A hard moment does not erase your progress. Review one idea at a time, then keep moving with support.",
            recommended_action="review-and-continue",
            evidence_source="recent_assessment_retry",
            review_lesson_id=review_lesson.id if review_lesson is not None else None,
            review_lesson_title=review_lesson_title,
            review_key_concepts=review_key_concepts,
            review_prompts=review_prompts,
            educator_note=(
                f"Recent evidence from {latest_assessment.title} suggests the learner may benefit from brief review in {review_lesson_title or latest_assessment.title}, confidence-preserving pacing, and targeted discussion support."
                if educator_visible
                else None
            ),
            educator_intervention_hint=educator_intervention_hint if educator_visible else None,
        )

    if mastered_objectives and latest_percentage >= 90.0:
        return ContinuationGuidanceResponse(
            support_state="enrichment",
            learner_title="You are ready for a deeper challenge",
            learner_message=(
                f"Continue with your next governed lesson and, if you want an extra stretch, revisit "
                f"{extension_lesson_title or latest_assessment.title} for optional extension prompts that deepen your thinking."
            ),
            reinforcement_title="Your understanding is growing strong",
            reinforcement_message="You have earned an optional deeper look. Follow your curiosity without leaving your steady learning path.",
            recommended_action="continue-with-enrichment",
            evidence_source="strong_mastery_signal",
            extension_lesson_id=extension_lesson.id if extension_lesson is not None else None,
            extension_lesson_title=extension_lesson_title,
            extension_key_concepts=extension_key_concepts,
            extension_prompts=extension_prompts,
            educator_note=(
                f"Recent mastery evidence is strong enough to support optional enrichment through {extension_lesson_title or latest_assessment.title} while keeping the learner on the governed pathway."
                if educator_visible
                else None
            ),
        )

    return ContinuationGuidanceResponse(
        support_state="normal",
        learner_title="Your next lesson is ready",
        learner_message="Keep your momentum with the next governed lesson. You are building understanding one steady step at a time.",
        reinforcement_title="Steady progress matters",
        reinforcement_message="Your effort is adding up. Keep going with care, and let each lesson strengthen what you know.",
        recommended_action="continue",
        evidence_source="governed_continuation",
        educator_note=(
            "Current evidence supports a normal governed continuation with no special runtime support state."
            if educator_visible
            else None
        ),
    )


def build_educator_runtime_support_summary(
    db: Session,
    student_course: StudentCourse,
    *,
    guidance: ContinuationGuidanceResponse | None = None,
) -> EducatorRuntimeSupportSummaryResponse | None:
    course = student_course.course
    if course is None or not _is_flagship_course(course):
        return None

    guidance = guidance or build_course_continuation_guidance(
        db,
        course,
        student_course.student_id,
        educator_visible=True,
    )
    latest = _latest_attempt_with_assessment(_course_assessments_with_evidence(db, course), student_course.student_id)
    last_evidence_at = latest[1].submitted_at if latest is not None else student_course.last_activity_at

    support_state = guidance.support_state if guidance is not None else "unknown"
    support_summary = guidance.educator_note if guidance and guidance.educator_note else (
        "No flagship runtime support summary is available for this learner yet."
    )
    evidence_source = guidance.evidence_source if guidance is not None else "no_flagship_guidance"
    recommended_action = guidance.recommended_action if guidance is not None else "continue"
    context_lesson_id = None
    context_lesson_title = None
    context_key_concepts: list[str] = []
    context_prompts: list[str] = []
    educator_intervention_hint = guidance.educator_intervention_hint if guidance is not None else None

    if student_course.status == "completed":
        support_state = "completed"
        support_summary = (
            "The learner has completed the current flagship pathway. Recognize the progress and invite reflective extension only if it feels useful."
        )
        evidence_source = "course_completed"
        recommended_action = "celebrate-and-reflect"
        educator_intervention_hint = None
    elif guidance is not None and guidance.support_state == "remediation":
        context_lesson_id = guidance.review_lesson_id
        context_lesson_title = guidance.review_lesson_title
        context_key_concepts = list(guidance.review_key_concepts or [])
        context_prompts = list(guidance.review_prompts or [])
    elif guidance is not None and guidance.support_state == "enrichment":
        context_lesson_id = guidance.extension_lesson_id
        context_lesson_title = guidance.extension_lesson_title
        context_key_concepts = list(guidance.extension_key_concepts or [])
        context_prompts = list(guidance.extension_prompts or [])
    elif guidance is not None and guidance.support_state == "normal":
        if guidance.evidence_source == "no_recent_assessment":
            support_summary = (
                "Normal continuation with limited flagship evidence so far. Continue with the governed lesson path and watch for the learner's first check-for-understanding."
            )
        elif guidance.evidence_source == "governed_continuation":
            support_summary = (
                "Current evidence supports a normal governed continuation with no special runtime support state."
            )

    return EducatorRuntimeSupportSummaryResponse(
        student_id=student_course.student_id,
        student_name=_display_name(student_course.student),
        student_course_id=student_course.id,
        course_id=course.id,
        course_title=course.title,
        support_state=support_state,
        support_summary=support_summary,
        evidence_source=evidence_source,
        recommended_action=recommended_action,
        last_evidence_at=last_evidence_at,
        context_lesson_id=context_lesson_id,
        context_lesson_title=context_lesson_title,
        context_key_concepts=context_key_concepts,
        context_prompts=context_prompts,
        educator_intervention_hint=educator_intervention_hint,
    )


def _build_assessment_evidence_summary(
    assessments: list[Assessment],
    student_id: UUID,
) -> list[AssessmentEvidenceSummaryResponse]:
    rows: list[AssessmentEvidenceSummaryResponse] = []
    for assessment in assessments:
        if assessment.assessment_state != "published" or assessment.availability_state != "available":
            continue
        attempts = sorted(
            [attempt for attempt in assessment.attempts if attempt.student_id == student_id],
            key=lambda attempt: (attempt.submitted_at, str(attempt.id)),
        )
        if not attempts:
            continue

        latest_attempt = attempts[-1]
        latest_event_metadata = _latest_event_metadata(latest_attempt)
        submitted_event_count = sum(
            1 for attempt in attempts for event in attempt.events if event.event_type == "attempt_submitted"
        )
        scored_event_count = sum(
            1 for attempt in attempts for event in attempt.events if event.event_type == "attempt_scored"
        )
        rows.append(
            AssessmentEvidenceSummaryResponse(
                assessment_id=assessment.id,
                assessment_title=assessment.title,
                assessment_scope=assessment.assessment_scope or (
                    "unit"
                    if assessment.unit_id
                    else "lesson"
                    if assessment.lesson_id
                    else "course"
                    if assessment.course_id
                    else "program"
                ),
                assessment_state=assessment.assessment_state or "published",
                availability_state=assessment.availability_state or "available",
                question_count=len(assessment.questions or []),
                attempt_count=len(attempts),
                passed_attempt_count=sum(1 for attempt in attempts if attempt.passed),
                latest_attempt_id=latest_attempt.id,
                latest_attempt_at=latest_attempt.submitted_at,
                latest_score=latest_attempt.score,
                latest_max_score=latest_attempt.max_score,
                latest_percentage=(latest_attempt.score / latest_attempt.max_score * 100) if latest_attempt.max_score else 0.0,
                latest_passed=latest_attempt.passed,
                submitted_event_count=submitted_event_count,
                scored_event_count=scored_event_count,
                latest_event_metadata=latest_event_metadata,
            )
        )
    rows.sort(key=lambda row: (row.latest_attempt_at or row.assessment_title, row.assessment_title))
    return rows


@router.get("/analytics/overview")
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    total_students = db.query(User).filter(User.role == "student").count()
    total_teachers = db.query(User).filter(User.role == "teacher").count()
    total_courses = db.query(Course).count()
    total_enrollments = db.query(StudentCourse).count()
    active_students = db.query(StudentCourse.student_id).distinct().count()
    lessons_completed = db.query(SegmentProgress).filter(
        SegmentProgress.status == ProgressStatus.COMPLETED
    ).count()
    units_completed = db.query(StudentUnitProgress).filter(
        StudentUnitProgress.status == ProgressStatus.COMPLETED
    ).count()
    courses_completed = db.query(StudentCourse).filter(
        StudentCourse.status == "completed"
    ).count()
    completion_rate = (
        round((courses_completed / total_enrollments) * 100, 1)
        if total_enrollments
        else 0
    )
    pending_enrollments = total_enrollments - courses_completed

    return {
        "totals": {
            "students": total_students,
            "teachers": total_teachers,
            "courses": total_courses,
            "active_students": active_students,
            "total_enrollments": total_enrollments,
            "pending_enrollments": pending_enrollments,
        },
        "progress": {
            "lessons_completed": lessons_completed,
            "units_completed": units_completed,
            "courses_completed": courses_completed,
            "course_completion_rate": completion_rate,
        },
    }


@router.get("/analytics/teacher-summary")
def get_teacher_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    courses = db.query(Course).all()
    course_lesson_counts = {}
    for course in courses:
        lesson_count = (
            db.query(Lesson)
            .join(Unit, Unit.id == Lesson.unit_id)
            .filter(Unit.course_id == course.id)
            .count()
        )
        course_lesson_counts[course.id] = lesson_count

    enrollments = (
        db.query(StudentCourse)
        .join(User, User.id == StudentCourse.student_id)
        .all()
    )
    results = []
    for enrollment in enrollments:
        completed_lessons = (
            db.query(SegmentProgress)
            .join(StudentUnitProgress, StudentUnitProgress.id == SegmentProgress.student_unit_id)
            .filter(
                StudentUnitProgress.student_course_id == enrollment.id,
                SegmentProgress.status == ProgressStatus.COMPLETED,
            )
            .count()
        )
        total_lessons = course_lesson_counts.get(enrollment.course_id, 0)
        progress = round((completed_lessons / total_lessons) * 100, 1) if total_lessons else 0
        results.append(
            {
                "student_name": f"{enrollment.student.firstname} {enrollment.student.lastname}",
                "course_title": enrollment.course.title,
                "progress": progress,
                "last_active": enrollment.last_activity_at,
                "status": enrollment.status,
            }
        )
    return results


@router.get("/analytics/student-progress")
def get_student_progress(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    student_id = current_user.id

    lessons_completed = (
        db.query(SegmentProgress)
        .join(StudentUnitProgress, StudentUnitProgress.id == SegmentProgress.student_unit_id)
        .join(StudentCourse, StudentCourse.id == StudentUnitProgress.student_course_id)
        .filter(
            StudentCourse.student_id == student_id,
            SegmentProgress.status == ProgressStatus.COMPLETED,
        )
        .count()
    )
    units_completed = (
        db.query(StudentUnitProgress)
        .join(StudentCourse, StudentCourse.id == StudentUnitProgress.student_course_id)
        .filter(
            StudentCourse.student_id == student_id,
            StudentUnitProgress.status == ProgressStatus.COMPLETED,
        )
        .count()
    )
    courses_completed = (
        db.query(StudentCourse)
        .filter(StudentCourse.student_id == student_id, StudentCourse.status == "completed")
        .count()
    )
    streak_days = calculate_streak_days(db, student_id)

    progress_cards = []
    for rule in BADGE_RULES:
        badge = get_or_create_badge(db, rule["title"], rule["description"])
        current_value = {
            "lessons_completed": lessons_completed,
            "units_completed": units_completed,
            "courses_completed": courses_completed,
            "streak_days": streak_days,
        }.get(rule["metric"], 0)
        progress_cards.append(
            {
                "title": rule["title"],
                "description": rule["description"],
                "current": current_value,
                "target": rule["threshold"],
                "earned": bool(
                    db.query(StudentBadge)
                    .filter_by(student_id=student_id, badge_id=badge.id)
                    .first()
                ),
            }
        )

    return {
        "metrics": {
            "lessons_completed": lessons_completed,
            "units_completed": units_completed,
            "courses_completed": courses_completed,
            "streak_days": streak_days,
        },
        "badge_progress": progress_cards,
    }


@router.get("/sections/{section_id}/analytics/summary")
def get_section_summary(
    section_id: str,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("teacher", "org_admin", "instructor")),
):
    total_enrolled = (
        db.query(Enrollment)
        .filter(Enrollment.section_id == section_id)
        .count()
    )
    completed_lessons = (
        db.query(SegmentProgress)
        .filter(
            SegmentProgress.section_id == section_id,
            SegmentProgress.status == ProgressStatus.COMPLETED,
        )
        .count()
    )
    completed_units = (
        db.query(StudentUnitProgress)
        .filter(
            StudentUnitProgress.section_id == section_id,
            StudentUnitProgress.status == ProgressStatus.COMPLETED,
        )
        .count()
    )
    return {
        "section_id": section_id,
        "totals": {
            "enrolled": total_enrolled,
            "lessons_completed": completed_lessons,
            "units_completed": completed_units,
        },
    }


@router.get("/analytics/mastery-summary", response_model=MasterySummaryResponse)
def get_mastery_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
    student_id: UUID | None = None,
    lesson_id: UUID | None = None,
    unit_id: UUID | None = None,
    course_id: UUID | None = None,
    program_id: UUID | None = None,
):
    scope_count = sum(value is not None for value in (lesson_id, unit_id, course_id, program_id))
    if scope_count != 1:
        raise HTTPException(status_code=400, detail="Mastery summary must target exactly one of lesson, unit, course, or program.")

    target_student_id = current_user.id
    if student_id is not None:
        if current_user.role not in {"admin", "teacher"}:
            raise HTTPException(status_code=403, detail="Only educators can request mastery summaries for other students.")
        target_student_id = student_id

    query = db.query(Assessment).options(
        selectinload(Assessment.competency_alignments),
        selectinload(Assessment.attempts),
    )
    if lesson_id is not None:
        query = query.filter(Assessment.lesson_id == lesson_id)
    if unit_id is not None:
        query = query.filter(Assessment.unit_id == unit_id)
    if course_id is not None:
        query = query.filter(Assessment.course_id == course_id)
    if program_id is not None:
        query = query.filter(Assessment.program_id == program_id)

    assessments = query.all()
    return _build_mastery_summary(
        assessments,
        target_student_id,
        lesson_id=lesson_id,
        unit_id=unit_id,
        course_id=course_id,
        program_id=program_id,
    )


@router.get("/analytics/reporting-summary", response_model=AssessmentReportingSummaryResponse)
def get_reporting_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
    student_id: UUID | None = None,
    lesson_id: UUID | None = None,
    unit_id: UUID | None = None,
    course_id: UUID | None = None,
    program_id: UUID | None = None,
):
    scope_count = sum(value is not None for value in (lesson_id, unit_id, course_id, program_id))
    if scope_count != 1:
        raise HTTPException(status_code=400, detail="Reporting summary must target exactly one of lesson, unit, course, or program.")

    target_student_id = current_user.id
    if student_id is not None:
        if current_user.role not in {"admin", "teacher"}:
            raise HTTPException(status_code=403, detail="Only educators can request reporting summaries for other students.")
        target_student_id = student_id

    query = db.query(Assessment).options(
        selectinload(Assessment.questions),
        selectinload(Assessment.attempts).selectinload(StudentAssessmentAttempt.events),
        selectinload(Assessment.competency_alignments),
    )
    if lesson_id is not None:
        query = query.filter(Assessment.lesson_id == lesson_id)
    if unit_id is not None:
        query = query.filter(Assessment.unit_id == unit_id)
    if course_id is not None:
        query = query.filter(Assessment.course_id == course_id)
    if program_id is not None:
        query = query.filter(Assessment.program_id == program_id)

    assessments = query.all()
    continuation_course: Course | None = None
    if course_id is not None:
        continuation_course = (
            db.query(Course)
            .options(selectinload(Course.units).selectinload(Unit.lessons))
            .filter(Course.id == course_id)
            .first()
        )
    elif unit_id is not None:
        unit = (
            db.query(Unit)
            .options(selectinload(Unit.course).selectinload(Course.units).selectinload(Unit.lessons))
            .filter(Unit.id == unit_id)
            .first()
        )
        continuation_course = unit.course if unit else None
    elif lesson_id is not None:
        lesson = (
            db.query(Lesson)
            .options(selectinload(Lesson.unit).selectinload(Unit.course).selectinload(Course.units).selectinload(Unit.lessons))
            .filter(Lesson.id == lesson_id)
            .first()
        )
        continuation_course = lesson.unit.course if lesson and lesson.unit else None

    continuation_guidance = build_course_continuation_guidance(
        db,
        continuation_course,
        target_student_id,
        educator_visible=current_user.role in {"admin", "teacher"},
    )
    educator_runtime_support_summary = None
    if current_user.role in {"admin", "teacher"} and continuation_course is not None:
        student_course = (
            db.query(StudentCourse)
            .options(selectinload(StudentCourse.student), selectinload(StudentCourse.course))
            .filter(
                StudentCourse.student_id == target_student_id,
                StudentCourse.course_id == continuation_course.id,
            )
            .first()
        )
        if student_course is not None:
            educator_runtime_support_summary = build_educator_runtime_support_summary(
                db,
                student_course,
                guidance=continuation_guidance,
            )

    return AssessmentReportingSummaryResponse(
        student_id=target_student_id,
        lesson_id=lesson_id,
        unit_id=unit_id,
        course_id=course_id,
        program_id=program_id,
        progress=_build_progress_snapshot(db, target_student_id),
        assessment_evidence=_build_assessment_evidence_summary(assessments, target_student_id),
        mastery_summary=_build_mastery_summary(
            assessments,
            target_student_id,
            lesson_id=lesson_id,
            unit_id=unit_id,
            course_id=course_id,
            program_id=program_id,
        ),
        continuation_guidance=continuation_guidance,
        educator_runtime_support_summary=educator_runtime_support_summary,
    )


@router.get(
    "/analytics/educator-runtime-support",
    response_model=list[EducatorRuntimeSupportSummaryResponse],
)
def get_educator_runtime_support(
    course_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    course = (
        db.query(Course)
        .options(
            selectinload(Course.units).selectinload(Unit.lessons),
            selectinload(Course.student_courses).selectinload(StudentCourse.student),
        )
        .filter(Course.id == course_id)
        .first()
    )
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    if not _is_flagship_course(course):
        return []

    summaries: list[EducatorRuntimeSupportSummaryResponse] = []
    for student_course in sorted(
        course.student_courses or [],
        key=lambda row: (
            _display_name(row.student).lower(),
            row.enrolled_on,
            str(row.id),
        ),
    ):
        guidance = build_course_continuation_guidance(
            db,
            course,
            student_course.student_id,
            educator_visible=True,
        )
        summary = build_educator_runtime_support_summary(
            db,
            student_course,
            guidance=guidance,
        )
        if summary is not None:
            summaries.append(summary)

    return summaries
