import uuid

from app.api.routes.analytics import _build_mastery_summary
from app.crud.progress import resolve_governed_progression
from app.enum import ProgressStatus
from app.lesson_governance import evaluate_course_competency_evidence_integrity
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
        event_metadata={"source": "phase2-test"},
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


def _create_scoped_assessment(
    db_session,
    *,
    course,
    unit,
    lesson,
    scope: str,
    title: str,
    revision_status: str = "current",
    lineage_status: str = "standalone",
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


def test_course_with_explainable_aligned_assessments_is_valid(db_session):
    course, unit, lesson, lesson_assessment, lesson_question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=lesson_assessment, question=lesson_question, objective_key="lesson-evidence")
    lesson_attempt = _add_attempt(db_session, assessment=lesson_assessment, question=lesson_question, student=student)
    _add_attempt_event(db_session, assessment=lesson_assessment, attempt=lesson_attempt, student=student, event_type="attempt_scored")

    unit_assessment, unit_question = _create_scoped_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        scope="unit",
        title="Unit Competency Integrity Assessment",
    )
    _add_alignment(db_session, assessment=unit_assessment, question=unit_question, objective_key="unit-evidence")
    unit_attempt = _add_attempt(db_session, assessment=unit_assessment, question=unit_question, student=student)
    _add_attempt_event(db_session, assessment=unit_assessment, attempt=unit_attempt, student=student, event_type="attempt_scored")

    course_assessment, course_question = _create_scoped_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        scope="course",
        title="Course Competency Integrity Assessment",
    )
    _add_alignment(db_session, assessment=course_assessment, question=course_question, objective_key="course-evidence")
    course_attempt = _add_attempt(db_session, assessment=course_assessment, question=course_question, student=student)
    _add_attempt_event(db_session, assessment=course_assessment, attempt=course_attempt, student=student, event_type="attempt_submitted")

    result = evaluate_course_competency_evidence_integrity(course)

    assert result.is_valid is True
    assert result.is_explainable is True
    assert result.blocking_issue_count == 0
    assert result.warning_count == 0
    assert result.blocking_issues == []
    assert result.warnings == []
    assert result.affected_assessments == []
    assert result.affected_competency_identifiers == []


def test_course_with_unaligned_assessment_evidence_returns_warning(db_session):
    course, unit, lesson, assessment, question, student = _create_assessment_context(db_session)
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student)
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student, event_type="attempt_scored")

    result = evaluate_course_competency_evidence_integrity(course)

    assert result.is_valid is True
    assert result.is_explainable is False
    assert result.blocking_issue_count == 0
    assert result.warning_count == 1
    assert any(issue.code == "unaligned_assessment_mastery_evidence" for issue in result.warnings)
    assert result.affected_assessments[0].assessment_id == assessment.id
    assert result.affected_assessments[0].assessment_title == assessment.title
    assert result.affected_assessments[0].competency_identifiers == []
    assert result.affected_competency_identifiers == []


def test_course_with_missing_attempt_event_returns_issue(db_session):
    course, _unit, _lesson, assessment, question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="geometry")
    _add_attempt(db_session, assessment=assessment, question=question, student=student)

    result = evaluate_course_competency_evidence_integrity(course)

    assert result.is_valid is False
    assert result.is_explainable is False
    assert result.blocking_issue_count == 1
    assert any(issue.code == "missing_attempt_event_for_mastery_evidence" for issue in result.blocking_issues)
    assert result.affected_assessments[0].competency_identifiers == ["geometry"]
    assert result.affected_competency_identifiers == ["geometry"]


def test_course_with_deprecated_or_superseded_assessment_evidence_returns_issue(db_session):
    course, _unit, _lesson, assessment, question, student = _create_assessment_context(
        db_session,
        assessment_revision_status="archived",
        assessment_lineage_status="superseded",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="history")
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student)
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student, event_type="attempt_scored")

    result = evaluate_course_competency_evidence_integrity(course)

    assert result.is_valid is False
    assert result.blocking_issue_count >= 1
    assert any(
        issue.code in {
            "attempts_on_non_current_assessment_revision",
            "attempt_events_on_non_current_assessment_revision",
            "ambiguous_evidence_revision_state",
        }
        for issue in result.blocking_issues
    )
    assert result.affected_assessments[0].assessment_id == assessment.id
    assert result.affected_competency_identifiers == ["history"]


def test_aggregation_includes_affected_assessment_and_competency_context(db_session):
    course, unit, lesson, aligned_assessment, aligned_question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=aligned_assessment, question=aligned_question, objective_key="algebra", objective_title="Algebra")
    _add_attempt(db_session, assessment=aligned_assessment, question=aligned_question, student=student)

    unaligned_assessment, unaligned_question = _create_scoped_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        scope="course",
        title="Unaligned Course Assessment",
    )
    unaligned_attempt = _add_attempt(db_session, assessment=unaligned_assessment, question=unaligned_question, student=student)
    _add_attempt_event(db_session, assessment=unaligned_assessment, attempt=unaligned_attempt, student=student, event_type="attempt_scored")

    result = evaluate_course_competency_evidence_integrity(course)

    assert result.is_valid is False
    assert result.warning_count == 1
    assert {context.assessment_title for context in result.affected_assessments} == {
        aligned_assessment.title,
        unaligned_assessment.title,
    }
    affected_by_id = {context.assessment_id: context for context in result.affected_assessments}
    assert affected_by_id[aligned_assessment.id].competency_identifiers == ["algebra"]
    assert affected_by_id[unaligned_assessment.id].competency_identifiers == []
    assert result.affected_competency_identifiers == ["algebra"]


def test_course_aggregation_is_read_only_and_does_not_mutate_evidence_or_progress(db_session):
    course, unit, lesson, assessment, question, student = _create_assessment_context(db_session)
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="science")
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=student)
    event = _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=student, event_type="attempt_scored")

    archived_assessment, archived_question = _create_scoped_assessment(
        db_session,
        course=course,
        unit=unit,
        lesson=lesson,
        scope="course",
        title="Archived Course Assessment",
        revision_status="archived",
        lineage_status="superseded",
    )
    _add_alignment(db_session, assessment=archived_assessment, question=archived_question, objective_key="science-archive")
    archived_attempt = _add_attempt(db_session, assessment=archived_assessment, question=archived_question, student=student)
    archived_event = _add_attempt_event(
        db_session,
        assessment=archived_assessment,
        attempt=archived_attempt,
        student=student,
        event_type="attempt_scored",
    )

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
    program = Program(id=uuid.uuid4(), title="Phase2 Integrity Program", description="Program")
    badge = Badge(id=uuid.uuid4(), title="Phase2 Integrity Badge", description="Badge")
    certification_record = Certification(
        id=uuid.uuid4(),
        program_id=program.id,
        badge_id=badge.id,
        title="Phase2 Integrity Certification",
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

    summary_before = _summary_payload(_build_mastery_summary([assessment], student.id, course_id=course.id))
    progression_before = dict(resolve_governed_progression(db_session, student_course.id))
    baseline = {
        "assessment_count": db_session.query(Assessment).count(),
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "alignment_count": db_session.query(AssessmentCompetencyAlignment).count(),
        "student_course_count": db_session.query(StudentCourse).count(),
        "unit_progress_count": db_session.query(StudentUnitProgress).count(),
        "segment_progress_count": db_session.query(SegmentProgress).count(),
        "certification_count": db_session.query(StudentCertification).count(),
        "attempt_snapshot": (attempt.id, attempt.assessment_id, attempt.score, attempt.max_score, attempt.passed),
        "event_snapshot": (event.id, event.assessment_id, event.attempt_id, event.event_type),
        "archived_attempt_snapshot": (
            archived_attempt.id,
            archived_attempt.assessment_id,
            archived_attempt.score,
            archived_attempt.max_score,
            archived_attempt.passed,
        ),
        "archived_event_snapshot": (
            archived_event.id,
            archived_event.assessment_id,
            archived_event.attempt_id,
            archived_event.event_type,
        ),
        "student_course_status": student_course.status,
        "unit_progress_status": unit_progress.status,
        "segment_progress_status": segment_progress.status,
        "certification_snapshot": (certification.id, certification.student_id, certification.score_snapshot),
    }

    result = evaluate_course_competency_evidence_integrity(course)

    db_session.refresh(assessment)
    db_session.refresh(attempt)
    db_session.refresh(event)
    db_session.refresh(archived_assessment)
    db_session.refresh(archived_attempt)
    db_session.refresh(archived_event)
    db_session.refresh(student_course)
    db_session.refresh(unit_progress)
    db_session.refresh(segment_progress)
    db_session.refresh(certification)
    summary_after = _summary_payload(_build_mastery_summary([assessment], student.id, course_id=course.id))
    progression_after = dict(resolve_governed_progression(db_session, student_course.id))
    after = {
        "assessment_count": db_session.query(Assessment).count(),
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "alignment_count": db_session.query(AssessmentCompetencyAlignment).count(),
        "student_course_count": db_session.query(StudentCourse).count(),
        "unit_progress_count": db_session.query(StudentUnitProgress).count(),
        "segment_progress_count": db_session.query(SegmentProgress).count(),
        "certification_count": db_session.query(StudentCertification).count(),
        "attempt_snapshot": (attempt.id, attempt.assessment_id, attempt.score, attempt.max_score, attempt.passed),
        "event_snapshot": (event.id, event.assessment_id, event.attempt_id, event.event_type),
        "archived_attempt_snapshot": (
            archived_attempt.id,
            archived_attempt.assessment_id,
            archived_attempt.score,
            archived_attempt.max_score,
            archived_attempt.passed,
        ),
        "archived_event_snapshot": (
            archived_event.id,
            archived_event.assessment_id,
            archived_event.attempt_id,
            archived_event.event_type,
        ),
        "student_course_status": student_course.status,
        "unit_progress_status": unit_progress.status,
        "segment_progress_status": segment_progress.status,
        "certification_snapshot": (certification.id, certification.student_id, certification.score_snapshot),
    }

    assert result.is_valid is False
    assert any(
        issue.code in {
            "attempts_on_non_current_assessment_revision",
            "attempt_events_on_non_current_assessment_revision",
            "ambiguous_evidence_revision_state",
        }
        for issue in result.blocking_issues
    )
    assert baseline == after
    assert summary_before == summary_after
    assert progression_before == progression_after
