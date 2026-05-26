import uuid

from app.api.routes.analytics import _build_mastery_summary
from app.crud.progress import resolve_governed_progression
from app.enum import ProgressStatus
from app.lesson_governance import evaluate_competency_evidence_integrity
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


def _create_assessment_context(
    db_session,
    *,
    assessment_revision_status: str = "current",
    assessment_lineage_status: str = "standalone",
    superseded_by_id=None,
):
    course = Course(
        id=uuid.uuid4(),
        title="Competency Integrity Course",
        description="Competency evidence integrity coverage",
        revision_status="current",
    )
    unit = Unit(
        id=uuid.uuid4(),
        title="Competency Integrity Unit",
        course_id=course.id,
        order=1,
        content="Unit content",
        revision_status="current",
    )
    lesson = Lesson(
        unit_id=unit.id,
        revision_status="current",
        **_ready_lesson_kwargs("Competency Integrity Lesson"),
    )
    db_session.add_all([course, unit, lesson])
    db_session.flush()

    assessment = Assessment(
        id=uuid.uuid4(),
        title="Competency Integrity Assessment",
        lesson_id=lesson.id,
        unit_id=unit.id,
        course_id=course.id,
        assessment_scope="lesson",
        revision_status=assessment_revision_status,
        lineage_status=assessment_lineage_status,
        superseded_by_id=superseded_by_id,
    )
    question = Question(
        id=uuid.uuid4(),
        assessment_id=assessment.id,
        prompt="What detail supports the answer?",
        question_type="short_answer",
        correct_answer="A cited detail",
        points=1.0,
        order=1,
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

    db_session.add_all([assessment, question, student])
    db_session.flush()
    db_session.add(
        Source(
            lesson_id=lesson.id,
            citation="Competency Integrity Source",
            url="https://example.com/source",
        )
    )
    db_session.commit()
    db_session.refresh(course)
    db_session.refresh(unit)
    db_session.refresh(lesson)
    db_session.refresh(assessment)
    db_session.refresh(question)
    db_session.refresh(student)
    return course, unit, lesson, assessment, question, student


def _add_alignment(
    db_session,
    *,
    assessment: Assessment,
    question: Question,
    objective_key: str = "evidence",
    objective_title: str = "Evidence",
) -> AssessmentCompetencyAlignment:
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
    passed: bool = True,
) -> StudentAssessmentAttempt:
    attempt = StudentAssessmentAttempt(
        assessment_id=assessment.id,
        student_id=student.id,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        passed=passed,
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
    event_type: str = "submitted",
) -> AssessmentAttemptEvent:
    event = AssessmentAttemptEvent(
        assessment_id=assessment.id,
        student_id=student.id,
        attempt_id=attempt.id,
        event_type=event_type,
        score=attempt.score,
        max_score=attempt.max_score,
        passed=attempt.passed,
        event_metadata={"source": "phase1-test"},
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    db_session.refresh(attempt)
    db_session.refresh(assessment)
    return event


def _summary_payload(summary):
    if hasattr(summary, "model_dump"):
        return summary.model_dump()
    return summary.dict()


def test_aligned_assessment_attempt_is_explainable(db_session):
    _course, _unit, _lesson, assessment, question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=assessment, question=question)
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student)
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student, event_type="attempt_scored")

    result = evaluate_competency_evidence_integrity(assessment)

    assert result.is_valid is True
    assert result.is_explainable is True
    assert result.blocking_issues == []
    assert result.warnings == []


def test_attempt_submitted_event_is_explainable(db_session):
    _course, _unit, _lesson, assessment, question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=assessment, question=question)
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student)
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student, event_type="attempt_submitted")

    result = evaluate_competency_evidence_integrity(assessment)

    assert result.is_valid is True
    assert result.is_explainable is True
    assert result.blocking_issues == []
    assert result.warnings == []


def test_unaligned_assessment_evidence_produces_warning(db_session):
    _course, _unit, _lesson, assessment, question, student = _create_assessment_context(db_session)
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student)
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student)

    result = evaluate_competency_evidence_integrity(assessment)

    assert result.is_valid is True
    assert result.is_explainable is False
    assert any(issue.code == "unaligned_assessment_mastery_evidence" for issue in result.warnings)


def test_missing_attempt_event_produces_issue(db_session):
    _course, _unit, _lesson, assessment, question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=assessment, question=question)
    _add_attempt(db_session, assessment=assessment, question=question, student=student)

    result = evaluate_competency_evidence_integrity(assessment)

    assert result.is_valid is False
    assert result.is_explainable is False
    assert any(issue.code == "missing_attempt_event_for_mastery_evidence" for issue in result.blocking_issues)


def test_deprecated_or_superseded_assessment_evidence_produces_integrity_issue(db_session):
    _course, _unit, _lesson, assessment, question, student = _create_assessment_context(
        db_session,
        assessment_revision_status="archived",
        assessment_lineage_status="superseded",
    )
    _add_alignment(db_session, assessment=assessment, question=question)
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student)
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student)

    result = evaluate_competency_evidence_integrity(assessment)

    assert result.is_valid is False
    assert any(
        issue.code in {
            "attempts_on_non_current_assessment_revision",
            "attempt_events_on_non_current_assessment_revision",
            "ambiguous_evidence_revision_state",
        }
        for issue in result.blocking_issues
    )


def test_current_mastery_summary_behavior_remains_unchanged(db_session):
    course, _unit, _lesson, assessment, question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="algebra", objective_title="Algebra")
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student, passed=True)
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student, event_type="attempt_scored")

    db_session.refresh(assessment)
    summary_before = _summary_payload(_build_mastery_summary([assessment], student.id, course_id=course.id))
    result = evaluate_competency_evidence_integrity(assessment)
    db_session.refresh(assessment)
    summary_after = _summary_payload(_build_mastery_summary([assessment], student.id, course_id=course.id))

    assert result.is_valid is True
    assert summary_before == summary_after
    assert summary_after["objectives"][0]["objective_key"] == "algebra"
    assert summary_after["objectives"][0]["mastered"] is True


def test_validation_is_read_only_and_does_not_mutate_evidence_or_progress(db_session):
    course, unit, lesson, assessment, question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=assessment, question=question)
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student)
    event = _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student)

    successor = Assessment(
        id=uuid.uuid4(),
        title="Competency Integrity Assessment v2",
        lesson_id=lesson.id,
        unit_id=unit.id,
        course_id=course.id,
        assessment_scope="lesson",
        revision_status="current",
        lineage_status="current",
        previous_revision_id=assessment.id,
    )
    assessment.superseded_by_id = successor.id
    db_session.add(successor)
    db_session.commit()
    db_session.refresh(assessment)
    db_session.refresh(successor)

    student_course = StudentCourse(student_id=student.id, course_id=course.id, status="in_progress")
    db_session.add(student_course)
    db_session.commit()
    db_session.refresh(student_course)

    unit_progress = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=unit.id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add(unit_progress)
    db_session.commit()
    db_session.refresh(unit_progress)

    segment_progress = SegmentProgress(
        student_unit_id=unit_progress.id,
        lesson_id=lesson.id,
        status=ProgressStatus.NOT_STARTED,
    )
    program = Program(id=uuid.uuid4(), title="Integrity Program", description="Program")
    badge = Badge(id=uuid.uuid4(), title="Integrity Badge", description="Badge")
    certification_record = Certification(
        id=uuid.uuid4(),
        program_id=program.id,
        badge_id=badge.id,
        title="Integrity Certification",
        description="Certification",
    )
    certification = StudentCertification(
        student_id=student.id,
        certification_id=certification_record.id,
        score_snapshot=100.0,
    )
    db_session.add_all([program, badge, certification_record, segment_progress, certification])
    db_session.commit()
    db_session.refresh(segment_progress)
    db_session.refresh(certification)

    baseline = {
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "alignment_count": db_session.query(AssessmentCompetencyAlignment).count(),
        "student_course_count": db_session.query(StudentCourse).count(),
        "unit_progress_count": db_session.query(StudentUnitProgress).count(),
        "segment_progress_count": db_session.query(SegmentProgress).count(),
        "certification_count": db_session.query(StudentCertification).count(),
        "assessment_snapshot": (assessment.id, assessment.superseded_by_id),
        "successor_snapshot": (successor.id, successor.previous_revision_id),
        "attempt_snapshot": (attempt.id, attempt.assessment_id, attempt.score, attempt.max_score, attempt.passed),
        "event_snapshot": (event.id, event.assessment_id, event.attempt_id, event.event_type, event.passed),
        "student_course_status": student_course.status,
        "unit_progress_status": unit_progress.status,
        "segment_progress_status": segment_progress.status,
        "certification_snapshot": (certification.id, certification.student_id, certification.score_snapshot),
    }

    result = evaluate_competency_evidence_integrity(assessment)

    db_session.refresh(assessment)
    db_session.refresh(successor)
    db_session.refresh(attempt)
    db_session.refresh(event)
    db_session.refresh(student_course)
    db_session.refresh(unit_progress)
    db_session.refresh(segment_progress)
    db_session.refresh(certification)
    after = {
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "alignment_count": db_session.query(AssessmentCompetencyAlignment).count(),
        "student_course_count": db_session.query(StudentCourse).count(),
        "unit_progress_count": db_session.query(StudentUnitProgress).count(),
        "segment_progress_count": db_session.query(SegmentProgress).count(),
        "certification_count": db_session.query(StudentCertification).count(),
        "assessment_snapshot": (assessment.id, assessment.superseded_by_id),
        "successor_snapshot": (successor.id, successor.previous_revision_id),
        "attempt_snapshot": (attempt.id, attempt.assessment_id, attempt.score, attempt.max_score, attempt.passed),
        "event_snapshot": (event.id, event.assessment_id, event.attempt_id, event.event_type, event.passed),
        "student_course_status": student_course.status,
        "unit_progress_status": unit_progress.status,
        "segment_progress_status": segment_progress.status,
        "certification_snapshot": (certification.id, certification.student_id, certification.score_snapshot),
    }

    assert result.is_valid is False
    assert any(issue.code == "ambiguous_evidence_revision_state" for issue in result.blocking_issues)
    assert after == baseline


def test_historical_mastery_evidence_remains_anchored_to_original_revision(db_session):
    course, unit, lesson, assessment, question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="anchor", objective_title="Anchored")
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student)
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student, event_type="attempt_scored")

    successor = Assessment(
        id=uuid.uuid4(),
        title="Competency Integrity Assessment v2",
        lesson_id=lesson.id,
        unit_id=unit.id,
        course_id=course.id,
        assessment_scope="lesson",
        revision_status="current",
        lineage_status="current",
        previous_revision_id=assessment.id,
    )
    db_session.add(successor)
    db_session.flush()
    assessment.superseded_by_id = successor.id
    db_session.commit()
    db_session.refresh(assessment)
    db_session.refresh(successor)

    original_before = _summary_payload(_build_mastery_summary([assessment], student.id, course_id=course.id))
    successor_before = _summary_payload(_build_mastery_summary([successor], student.id, course_id=course.id))

    result = evaluate_competency_evidence_integrity(assessment)

    original_after = _summary_payload(_build_mastery_summary([assessment], student.id, course_id=course.id))
    successor_after = _summary_payload(_build_mastery_summary([successor], student.id, course_id=course.id))

    assert result.is_valid is False
    assert any(issue.code == "ambiguous_evidence_revision_state" for issue in result.blocking_issues)
    assert original_before == original_after
    assert successor_before == successor_after
    assert original_after["objectives"][0]["objective_key"] == "anchor"
    assert original_after["objectives"][0]["mastered"] is True
    assert successor_after["objectives"] == []


def test_validation_does_not_change_governed_delivery_resolution(db_session):
    course, unit, lesson, assessment, question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=assessment, question=question)
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student)
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student, event_type="attempt_scored")

    student_course = StudentCourse(student_id=student.id, course_id=course.id, status="in_progress")
    db_session.add(student_course)
    db_session.commit()
    db_session.refresh(student_course)

    before = dict(resolve_governed_progression(db_session, student_course.id))
    result = evaluate_competency_evidence_integrity(assessment)
    after = dict(resolve_governed_progression(db_session, student_course.id))

    assert result.is_valid is True
    assert before == after
    assert after["delivery_state"] == "governed_available"
    assert after["lesson_id"] == lesson.id
