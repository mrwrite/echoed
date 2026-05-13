import uuid

from app.enum import ProgressStatus
from app.lesson_governance import evaluate_assessment_evidence_safety
from app.models import (
    Assessment,
    AssessmentAttemptEvent,
    Badge,
    Certification,
    CertificationRequirement,
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
    StudentProgramProgress,
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
    course_revision_status: str = "current",
    unit_revision_status: str = "current",
    lesson_revision_status: str = "current",
    assessment_revision_status: str = "current",
    assessment_lineage_status: str = "standalone",
    superseded_by_id=None,
):
    course = Course(
        id=uuid.uuid4(),
        title="Evidence Safety Course",
        description="Assessment evidence safety coverage",
        revision_status=course_revision_status,
    )
    unit = Unit(
        id=uuid.uuid4(),
        title="Evidence Safety Unit",
        course_id=course.id,
        order=1,
        content="Unit content",
        revision_status=unit_revision_status,
    )
    lesson = Lesson(
        unit_id=unit.id,
        revision_status=lesson_revision_status,
        **_ready_lesson_kwargs("Evidence Safety Lesson"),
    )
    db_session.add_all([course, unit, lesson])
    db_session.flush()
    assessment = Assessment(
        id=uuid.uuid4(),
        title="Evidence Safety Assessment",
        lesson_id=lesson.id,
        unit_id=unit.id,
        course_id=course.id,
        assessment_scope="lesson",
        revision_status=assessment_revision_status,
        lineage_status=assessment_lineage_status,
        superseded_by_id=superseded_by_id,
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

    db_session.add_all([assessment, student])
    db_session.flush()
    db_session.add(
        Source(
            lesson_id=lesson.id,
            citation="Evidence Safety Source",
            url="https://example.com/source",
        )
    )
    db_session.commit()
    db_session.refresh(assessment)
    db_session.refresh(course)
    db_session.refresh(unit)
    db_session.refresh(lesson)
    db_session.refresh(student)
    return course, unit, lesson, assessment, student


def _add_attempt(db_session, assessment: Assessment, student: User) -> StudentAssessmentAttempt:
    attempt = StudentAssessmentAttempt(
        assessment_id=assessment.id,
        student_id=student.id,
        score=1,
        max_score=1,
        passed=True,
    )
    db_session.add(attempt)
    db_session.commit()
    db_session.refresh(attempt)
    db_session.refresh(assessment)
    return attempt


def _add_attempt_event(
    db_session,
    assessment: Assessment,
    student: User,
    attempt: StudentAssessmentAttempt,
) -> AssessmentAttemptEvent:
    event = AssessmentAttemptEvent(
        assessment_id=assessment.id,
        student_id=student.id,
        attempt_id=attempt.id,
        event_type="submitted",
        score=attempt.score,
        max_score=attempt.max_score,
        passed=attempt.passed,
        event_metadata={"source": "phase4-test"},
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    db_session.refresh(assessment)
    db_session.refresh(attempt)
    return event


def test_deprecated_archived_or_superseded_assessment_with_attempts_produces_issue(db_session):
    _, _, _, assessment, student = _create_assessment_context(
        db_session,
        assessment_revision_status="archived",
        assessment_lineage_status="superseded",
    )
    _add_attempt(db_session, assessment, student)

    result = evaluate_assessment_evidence_safety(assessment)

    assert result.is_safe is False
    assert any(issue.code == "attempts_on_non_current_assessment_revision" for issue in result.blocking_issues)
    assert result.entity_type == "assessment"
    assert result.entity_id == assessment.id
    assert result.entity_title == assessment.title


def test_deprecated_archived_or_superseded_assessment_with_attempt_events_produces_issue(db_session):
    _, _, _, assessment, student = _create_assessment_context(
        db_session,
        assessment_revision_status="current",
        assessment_lineage_status="superseded",
    )
    attempt = _add_attempt(db_session, assessment, student)
    _add_attempt_event(db_session, assessment, student, attempt)

    result = evaluate_assessment_evidence_safety(assessment)

    assert result.is_safe is False
    assert any(issue.code == "attempt_events_on_non_current_assessment_revision" for issue in result.blocking_issues)


def test_historical_assessment_evidence_without_successor_metadata_produces_warning(db_session):
    _, _, _, assessment, student = _create_assessment_context(
        db_session,
        assessment_revision_status="archived",
        assessment_lineage_status="superseded",
        superseded_by_id=None,
    )
    _add_attempt(db_session, assessment, student)

    result = evaluate_assessment_evidence_safety(assessment)

    assert any(
        issue.code == "missing_successor_metadata_with_historical_evidence"
        for issue in result.warnings
    )


def test_archived_assessment_with_historical_evidence_and_no_successor_warns_even_if_lineage_is_standalone(db_session):
    _, _, _, assessment, student = _create_assessment_context(
        db_session,
        assessment_revision_status="archived",
        assessment_lineage_status="standalone",
        superseded_by_id=None,
    )
    _add_attempt(db_session, assessment, student)

    result = evaluate_assessment_evidence_safety(assessment)

    assert any(
        issue.code == "missing_successor_metadata_with_historical_evidence"
        for issue in result.warnings
    )


def test_ambiguous_revision_and_lineage_state_produces_issue(db_session):
    _, _, _, assessment, student = _create_assessment_context(
        db_session,
        assessment_revision_status="current",
        assessment_lineage_status="standalone",
        superseded_by_id=uuid.uuid4(),
    )
    _add_attempt(db_session, assessment, student)

    result = evaluate_assessment_evidence_safety(assessment)

    assert result.is_safe is False
    assert any(issue.code == "ambiguous_evidence_revision_state" for issue in result.blocking_issues)


def test_current_assessment_with_evidence_is_safe(db_session):
    _, _, _, assessment, student = _create_assessment_context(db_session)
    attempt = _add_attempt(db_session, assessment, student)
    _add_attempt_event(db_session, assessment, student, attempt)

    result = evaluate_assessment_evidence_safety(assessment)

    assert result.is_safe is True
    assert result.blocking_issues == []
    assert result.warnings == []


def test_deprecated_curriculum_context_with_assessment_evidence_produces_issue(db_session):
    _, _, lesson, assessment, student = _create_assessment_context(
        db_session,
        lesson_revision_status="deprecated",
    )
    _add_attempt(db_session, assessment, student)

    result = evaluate_assessment_evidence_safety(assessment)

    assert result.is_safe is False
    matching_issues = [
        issue for issue in result.blocking_issues if issue.code == "historical_evidence_on_deprecated_curriculum_context"
    ]
    assert matching_issues
    assert any(issue.entity_type == "lesson" and issue.entity_id == lesson.id for issue in matching_issues)


def test_validation_is_read_only_and_does_not_mutate_attempts_events_certifications_or_progress(db_session):
    course, unit, lesson, assessment, student = _create_assessment_context(db_session)
    attempt = _add_attempt(db_session, assessment, student)
    event = _add_attempt_event(db_session, assessment, student, attempt)
    question = Question(
        assessment_id=assessment.id,
        prompt="What detail supports the answer?",
        question_type="short_answer",
        correct_answer="A cited detail",
        points=1.0,
        order=1,
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    answer = StudentAssessmentAnswer(
        attempt_id=attempt.id,
        question_id=question.id,
        answer="A cited detail",
        is_correct=True,
        awarded_points=1.0,
    )
    db_session.add(answer)
    db_session.commit()
    db_session.refresh(answer)

    successor = Assessment(
        id=uuid.uuid4(),
        title="Evidence Safety Assessment v2",
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
    db_session.add(segment_progress)

    program = Program(id=uuid.uuid4(), title="Evidence Program", description="Program")
    badge = Badge(id=uuid.uuid4(), title="Evidence Badge", description="Badge")
    certification = Certification(
        id=uuid.uuid4(),
        program_id=program.id,
        badge_id=badge.id,
        title="Evidence Certification",
        description="Certification",
    )
    requirement = CertificationRequirement(
        certification_id=certification.id,
        requirement_type="assessment_passed",
        assessment_id=assessment.id,
        minimum_score=100.0,
    )
    issued = StudentCertification(
        student_id=student.id,
        certification_id=certification.id,
        score_snapshot=100.0,
    )
    program_progress = StudentProgramProgress(
        student_id=student.id,
        program_id=program.id,
        status="active",
    )
    db_session.add_all([program, badge, certification, requirement, issued, program_progress, segment_progress])
    db_session.commit()
    db_session.refresh(attempt)
    db_session.refresh(event)
    db_session.refresh(student_course)
    db_session.refresh(unit_progress)
    db_session.refresh(segment_progress)
    db_session.refresh(issued)
    db_session.refresh(program_progress)

    baseline = {
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "certification_count": db_session.query(StudentCertification).count(),
        "student_course_count": db_session.query(StudentCourse).count(),
        "unit_progress_count": db_session.query(StudentUnitProgress).count(),
        "segment_progress_count": db_session.query(SegmentProgress).count(),
        "program_progress_count": db_session.query(StudentProgramProgress).count(),
        "assessment_snapshot": (assessment.id, assessment.superseded_by_id),
        "successor_snapshot": (successor.id, successor.previous_revision_id),
        "attempt_snapshot": (attempt.id, attempt.assessment_id, attempt.score, attempt.max_score, attempt.passed),
        "answer_snapshot": (answer.id, answer.attempt_id, answer.question_id, answer.awarded_points, answer.is_correct),
        "event_snapshot": (event.id, event.assessment_id, event.attempt_id, event.event_type, event.passed),
        "student_course_status": student_course.status,
        "unit_progress_status": unit_progress.status,
        "segment_progress_status": segment_progress.status,
        "certification_snapshot": (issued.id, issued.certification_id, issued.score_snapshot),
    }

    result = evaluate_assessment_evidence_safety(assessment)

    db_session.refresh(assessment)
    db_session.refresh(successor)
    db_session.refresh(attempt)
    db_session.refresh(answer)
    db_session.refresh(event)
    db_session.refresh(student_course)
    db_session.refresh(unit_progress)
    db_session.refresh(segment_progress)
    db_session.refresh(issued)
    after = {
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "certification_count": db_session.query(StudentCertification).count(),
        "student_course_count": db_session.query(StudentCourse).count(),
        "unit_progress_count": db_session.query(StudentUnitProgress).count(),
        "segment_progress_count": db_session.query(SegmentProgress).count(),
        "program_progress_count": db_session.query(StudentProgramProgress).count(),
        "assessment_snapshot": (assessment.id, assessment.superseded_by_id),
        "successor_snapshot": (successor.id, successor.previous_revision_id),
        "attempt_snapshot": (attempt.id, attempt.assessment_id, attempt.score, attempt.max_score, attempt.passed),
        "answer_snapshot": (answer.id, answer.attempt_id, answer.question_id, answer.awarded_points, answer.is_correct),
        "event_snapshot": (event.id, event.assessment_id, event.attempt_id, event.event_type, event.passed),
        "student_course_status": student_course.status,
        "unit_progress_status": unit_progress.status,
        "segment_progress_status": segment_progress.status,
        "certification_snapshot": (issued.id, issued.certification_id, issued.score_snapshot),
    }

    assert result.is_safe is False
    assert any(issue.code == "ambiguous_evidence_revision_state" for issue in result.blocking_issues)
    assert after == baseline
