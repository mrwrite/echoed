import uuid
from datetime import datetime, timedelta

from app.api.routes.analytics import _build_mastery_summary
from app.enum import ProgressStatus
from app.models import (
    Assessment,
    AssessmentAttemptEvent,
    AssessmentCompetencyAlignment,
    Badge,
    Certification,
    Course,
    Lesson,
    Program,
    Question,
    SegmentProgress,
    Source,
    StudentAssessmentAnswer,
    StudentAssessmentAttempt,
    StudentCertification,
    StudentCourse,
    StudentUnitProgress,
    Unit,
    User,
)
from app.runtime_intervention_intelligence import evaluate_runtime_intervention_recommendation


def _ready_lesson_kwargs(title: str) -> dict:
    return {
        "title": title,
        "objective": "Explain the lesson idea clearly.",
        "learning_objectives": "Students will describe a lesson idea using evidence.",
        "key_concepts": ["evidence", "understanding"],
        "teacher_notes": "Prompt students to name one supporting detail.",
        "discussion_questions": ["What helped you understand the idea?"],
        "hook": "Begin with one simple observation.",
        "content": "Explain the main idea with a short example.",
        "guided_practice": "Work through one example together.",
        "independent_practice": "Let students respond on their own.",
        "assessment": "Short oral or written check.",
        "review_status": "approved",
        "order": 1,
    }


def _create_runtime_context(
    db_session,
    *,
    course_title: str = "Runtime Intervention Course",
):
    course = Course(
        id=uuid.uuid4(),
        title=course_title,
        description="Runtime intervention intelligence coverage",
        revision_status="current",
    )
    unit = Unit(
        id=uuid.uuid4(),
        title="Runtime Intervention Unit",
        course_id=course.id,
        order=1,
        content="Unit content",
        revision_status="current",
    )
    lesson = Lesson(
        unit_id=unit.id,
        revision_status="current",
        **_ready_lesson_kwargs("Runtime Intervention Lesson"),
    )
    student = User(
        id=uuid.uuid4(),
        firstname="Student",
        lastname="Learner",
        username=f"student_{uuid.uuid4()}",
        email=f"student_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    db_session.add_all([course, unit, lesson, student])
    db_session.flush()

    student_course = StudentCourse(student_id=student.id, course_id=course.id, status="active")
    db_session.add(student_course)
    db_session.flush()

    unit_progress = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=unit.id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add(unit_progress)
    db_session.flush()

    segment_progress = SegmentProgress(
        student_unit_id=unit_progress.id,
        lesson_id=lesson.id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add(segment_progress)
    db_session.flush()

    source = Source(
        lesson_id=lesson.id,
        citation="Runtime Intervention Source",
        url="https://example.com/source",
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(course)
    db_session.refresh(unit)
    db_session.refresh(lesson)
    db_session.refresh(student)
    db_session.refresh(student_course)
    return course, unit, lesson, student, student_course


def _create_assessment(
    db_session,
    *,
    course: Course,
    unit: Unit,
    lesson: Lesson,
    title: str,
    scope: str = "lesson",
    revision_status: str = "current",
    lineage_status: str = "standalone",
    superseded_by_id=None,
):
    assessment = Assessment(
        id=uuid.uuid4(),
        title=title,
        course_id=course.id,
        unit_id=unit.id if scope in {"unit", "lesson"} else None,
        lesson_id=lesson.id if scope == "lesson" else None,
        assessment_scope=scope,
        revision_status=revision_status,
        lineage_status=lineage_status,
        superseded_by_id=superseded_by_id,
    )
    question = Question(
        id=uuid.uuid4(),
        assessment_id=assessment.id,
        prompt=f"{title} prompt",
        question_type="short_answer",
        correct_answer="A cited detail",
        points=1.0,
        order=1,
    )
    db_session.add_all([assessment, question])
    db_session.commit()
    db_session.refresh(assessment)
    db_session.refresh(question)
    return assessment, question


def _add_alignment(
    db_session,
    *,
    assessment: Assessment,
    question: Question,
    objective_key: str,
    objective_title: str = "Evidence",
):
    alignment = AssessmentCompetencyAlignment(
        assessment_id=assessment.id,
        question_id=question.id,
        objective_key=objective_key,
        objective_title=objective_title,
        objective_type="competency",
        weight=1.0,
        mastery_threshold=80.0,
    )
    db_session.add(alignment)
    db_session.commit()
    db_session.refresh(alignment)
    db_session.refresh(assessment)
    return alignment


def _add_attempt(
    db_session,
    *,
    assessment: Assessment,
    question: Question,
    student: User,
    passed: bool,
    submitted_at: datetime,
):
    attempt = StudentAssessmentAttempt(
        assessment_id=assessment.id,
        student_id=student.id,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        passed=passed,
        submitted_at=submitted_at,
    )
    db_session.add(attempt)
    db_session.flush()
    answer = StudentAssessmentAnswer(
        attempt_id=attempt.id,
        question_id=question.id,
        answer="A cited detail" if passed else "Wrong detail",
        is_correct=passed,
        awarded_points=1.0 if passed else 0.0,
    )
    db_session.add(answer)
    db_session.commit()
    db_session.refresh(attempt)
    db_session.refresh(answer)
    db_session.refresh(assessment)
    return attempt


def _add_attempt_event(
    db_session,
    *,
    assessment: Assessment,
    attempt: StudentAssessmentAttempt,
    student: User,
    event_type: str = "attempt_scored",
):
    event = AssessmentAttemptEvent(
        assessment_id=assessment.id,
        student_id=student.id,
        attempt_id=attempt.id,
        event_type=event_type,
        score=attempt.score,
        max_score=attempt.max_score,
        passed=attempt.passed,
        event_metadata={"source": "runtime-intervention-phase1"},
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    db_session.refresh(attempt)
    return event


def _summary_payload(summary):
    if hasattr(summary, "model_dump"):
        return summary.model_dump()
    return summary.dict()


def _now():
    return datetime.now()


def test_enrichment_recommendation_from_strong_valid_mastery_evidence(db_session):
    course, unit, lesson, student, student_course = _create_runtime_context(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        title="Strong Mastery Check",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="evidence")
    attempt = _add_attempt(
        db_session,
        assessment=assessment,
        question=question,
        student=student,
        passed=True,
        submitted_at=_now(),
    )
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student)

    result = evaluate_runtime_intervention_recommendation(db_session, student_course)

    assert result.recommendation_state == "enrichment"
    assert result.educator_attention_level == "low"
    assert result.confidence_level == "high"
    assert "Strong valid mastery evidence" in result.summary
    assert result.caution_flags == []
    assert any(basis.source == "mastery_summary" for basis in result.evidence_basis)


def test_review_recommendation_from_moderate_uncertain_evidence(db_session):
    course, unit, lesson, student, student_course = _create_runtime_context(db_session)
    first_assessment, first_question = _create_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        title="Earlier Check",
    )
    second_assessment, second_question = _create_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        title="Latest Check",
        scope="unit",
    )
    _add_alignment(db_session, assessment=first_assessment, question=first_question, objective_key="evidence")
    _add_alignment(db_session, assessment=second_assessment, question=second_question, objective_key="evidence")
    first_attempt = _add_attempt(
        db_session,
        assessment=first_assessment,
        question=first_question,
        student=student,
        passed=False,
        submitted_at=_now() - timedelta(minutes=5),
    )
    second_attempt = _add_attempt(
        db_session,
        assessment=second_assessment,
        question=second_question,
        student=student,
        passed=True,
        submitted_at=_now(),
    )
    _add_attempt_event(db_session, assessment=first_assessment, attempt=first_attempt, student=student)
    _add_attempt_event(db_session, assessment=second_assessment, attempt=second_attempt, student=student)

    result = evaluate_runtime_intervention_recommendation(db_session, student_course)

    assert result.recommendation_state == "review"
    assert result.educator_attention_level == "medium"
    assert result.confidence_level == "medium"
    assert "short review" in result.summary.lower()
    assert any("50.0%" in basis.detail for basis in result.evidence_basis if basis.source == "mastery_summary")


def test_reteach_recommendation_from_weak_evidence(db_session):
    course, unit, lesson, student, student_course = _create_runtime_context(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        title="Weak Evidence Check",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="evidence")
    attempt = _add_attempt(
        db_session,
        assessment=assessment,
        question=question,
        student=student,
        passed=False,
        submitted_at=_now(),
    )
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student)

    result = evaluate_runtime_intervention_recommendation(db_session, student_course)

    assert result.recommendation_state == "reteach"
    assert result.educator_attention_level == "high"
    assert result.confidence_level == "high"
    assert "targeted reteach" in result.summary.lower()


def test_monitor_recommendation_from_ambiguous_competency_integrity(db_session):
    course, unit, lesson, student, student_course = _create_runtime_context(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        title="Unaligned Check",
    )
    attempt = _add_attempt(
        db_session,
        assessment=assessment,
        question=question,
        student=student,
        passed=True,
        submitted_at=_now(),
    )
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student)

    result = evaluate_runtime_intervention_recommendation(db_session, student_course)

    assert result.recommendation_state == "monitor"
    assert result.confidence_level == "low"
    assert "ambiguous" in result.summary.lower()
    assert "ambiguous_competency_evidence" in result.caution_flags


def test_normal_recommendation_when_no_concern_is_detected(db_session):
    course, _unit, _lesson, _student, student_course = _create_runtime_context(db_session)

    result = evaluate_runtime_intervention_recommendation(db_session, student_course)

    assert result.recommendation_state == "normal"
    assert result.educator_attention_level == "low"
    assert "normal continuation" in result.summary.lower()
    assert "limited_mastery_evidence" in result.caution_flags


def test_caution_flags_appear_for_incomplete_and_unsafe_evidence(db_session):
    course, unit, lesson, student, student_course = _create_runtime_context(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        title="Deprecated Evidence Check",
        revision_status="deprecated",
        lineage_status="superseded",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="evidence")
    _add_attempt(
        db_session,
        assessment=assessment,
        question=question,
        student=student,
        passed=True,
        submitted_at=_now(),
    )

    result = evaluate_runtime_intervention_recommendation(db_session, student_course)

    assert result.recommendation_state == "monitor"
    assert "incomplete_attempt_event_history" in result.caution_flags
    assert "deprecated_evidence_revision" in result.caution_flags
    assert "superseded_evidence_revision" in result.caution_flags
    assert "unsafe_historical_evidence" in result.caution_flags


def test_helper_is_read_only_and_does_not_mutate_progress_or_certification_state(db_session):
    course, unit, lesson, student, student_course = _create_runtime_context(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        title="Read Only Check",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="evidence")
    attempt = _add_attempt(
        db_session,
        assessment=assessment,
        question=question,
        student=student,
        passed=True,
        submitted_at=_now(),
    )
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student)

    program = Program(
        id=uuid.uuid4(),
        title="Runtime Program",
        description="Program for read-only verification",
    )
    badge = Badge(
        id=uuid.uuid4(),
        title="Runtime Badge",
        description="Badge for read-only verification",
    )
    db_session.add_all([program, badge])
    db_session.flush()
    certification = Certification(
        id=uuid.uuid4(),
        program_id=program.id,
        badge_id=badge.id,
        title="Runtime Certification",
    )
    db_session.add(certification)
    db_session.flush()
    student_certification = StudentCertification(
        student_id=student.id,
        certification_id=certification.id,
    )
    db_session.add(student_certification)
    db_session.commit()

    mastery_before = _summary_payload(_build_mastery_summary([assessment], student.id, course_id=course.id))
    snapshot_before = {
        "student_course_status": student_course.status,
        "student_course_completed_at": student_course.completed_at,
        "unit_progress_statuses": [
            getattr(progress.status, "value", str(progress.status))
            for progress in student_course.unit_progress
        ],
        "segment_statuses": [
            getattr(segment.status, "value", str(segment.status))
            for progress in student_course.unit_progress
            for segment in progress.segments
        ],
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "student_certification_count": db_session.query(StudentCertification).count(),
    }

    result = evaluate_runtime_intervention_recommendation(db_session, student_course)

    db_session.refresh(student_course)
    for progress in student_course.unit_progress:
        db_session.refresh(progress)
        for segment in progress.segments:
            db_session.refresh(segment)

    mastery_after = _summary_payload(_build_mastery_summary([assessment], student.id, course_id=course.id))
    snapshot_after = {
        "student_course_status": student_course.status,
        "student_course_completed_at": student_course.completed_at,
        "unit_progress_statuses": [
            getattr(progress.status, "value", str(progress.status))
            for progress in student_course.unit_progress
        ],
        "segment_statuses": [
            getattr(segment.status, "value", str(segment.status))
            for progress in student_course.unit_progress
            for segment in progress.segments
        ],
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "student_certification_count": db_session.query(StudentCertification).count(),
    }

    assert result.recommendation_state == "enrichment"
    assert mastery_before == mastery_after
    assert snapshot_before == snapshot_after
