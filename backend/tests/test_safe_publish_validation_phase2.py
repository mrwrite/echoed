import uuid

from app.enum import ProgressStatus
from app.lesson_governance import evaluate_course_safe_publish
from app.models import (
    Assessment,
    Course,
    Lesson,
    SegmentProgress,
    Source,
    StudentAssessmentAttempt,
    StudentCertification,
    StudentCourse,
    StudentProgramProgress,
    StudentUnitProgress,
    Unit,
    User,
)


def _ready_lesson_kwargs(title: str, *, order: int | None = 1, review_status: str = "approved") -> dict:
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
        "review_status": review_status,
        "order": order,
    }


def _add_source(db_session, lesson: Lesson, citation: str | None = None):
    db_session.add(
        Source(
            lesson_id=lesson.id,
            citation=citation or f"{lesson.title} source",
            url="https://example.com/source",
        )
    )


def _create_publish_ready_course(db_session, *, revision_status: str = "current") -> Course:
    course = Course(
        id=uuid.uuid4(),
        title="Safe Publish Course",
        description="Course ready for safe publish validation",
        revision_status=revision_status,
    )
    unit = Unit(
        id=uuid.uuid4(),
        title="Unit One",
        course_id=course.id,
        order=1,
        revision_status=revision_status,
    )
    db_session.add_all([course, unit])
    db_session.flush()

    lesson = Lesson(
        unit_id=unit.id,
        revision_status=revision_status,
        **_ready_lesson_kwargs("Lesson One", order=1),
    )
    db_session.add(lesson)
    db_session.flush()
    _add_source(db_session, lesson)

    db_session.commit()
    db_session.refresh(course)
    return course


def test_current_publish_ready_course_is_safe(db_session):
    course = _create_publish_ready_course(db_session, revision_status="current")

    result = evaluate_course_safe_publish(course)

    assert result.is_safe is True
    assert result.blocking_issues == []


def test_draft_publish_ready_course_is_safe_if_readiness_passes(db_session):
    course = _create_publish_ready_course(db_session, revision_status="draft")

    result = evaluate_course_safe_publish(course)

    assert result.is_safe is True
    assert result.blocking_issues == []


def test_deprecated_or_archived_course_is_blocked(db_session):
    deprecated_course = _create_publish_ready_course(db_session, revision_status="deprecated")
    archived_course = _create_publish_ready_course(db_session, revision_status="archived")

    deprecated_result = evaluate_course_safe_publish(deprecated_course)
    archived_result = evaluate_course_safe_publish(archived_course)

    assert deprecated_result.is_safe is False
    assert archived_result.is_safe is False
    assert any(issue.code == "blocked_revision_status" for issue in deprecated_result.blocking_issues)
    assert any(issue.code == "blocked_revision_status" for issue in archived_result.blocking_issues)


def test_incomplete_course_is_blocked_through_publish_readiness_dependency(db_session):
    course = Course(id=uuid.uuid4(), title="Blocked Course", description="Missing readiness")
    unit = Unit(id=uuid.uuid4(), title="Unit One", course_id=course.id, order=1)
    db_session.add_all([course, unit])
    db_session.flush()
    lesson = Lesson(unit_id=unit.id, **_ready_lesson_kwargs("Draft Lesson", review_status="draft"))
    db_session.add(lesson)
    db_session.flush()
    _add_source(db_session, lesson)
    db_session.commit()
    db_session.refresh(course)

    result = evaluate_course_safe_publish(course)

    assert result.is_safe is False
    assert any(issue.code == "review_status_not_approved" for issue in result.blocking_issues)


def test_inconsistent_revision_metadata_produces_warnings_or_blocking_issues(db_session):
    course = _create_publish_ready_course(db_session, revision_status="current")
    course.revision_number = 0
    course.deprecated_at = course.created_at
    db_session.commit()
    db_session.refresh(course)

    result = evaluate_course_safe_publish(course)

    assert result.is_safe is False
    assert any(issue.code == "invalid_revision_number" for issue in result.blocking_issues)
    assert any(issue.code == "current_has_deprecated_at" for issue in result.warnings)


def test_unsafe_assessment_evidence_status_is_blocked(db_session):
    course = _create_publish_ready_course(db_session, revision_status="current")
    student = User(
        id=uuid.uuid4(),
        firstname="Student",
        lastname="Learner",
        username=f"student_{uuid.uuid4()}",
        email=f"student_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    lesson = course.units[0].lessons[0]
    assessment = Assessment(
        title="Archived Assessment",
        lesson_id=lesson.id,
        course_id=course.id,
        assessment_scope="lesson",
        revision_status="archived",
    )
    db_session.add_all([student, assessment])
    db_session.flush()
    db_session.add(
        StudentAssessmentAttempt(
            assessment_id=assessment.id,
            student_id=student.id,
            score=0,
            max_score=1,
            passed=False,
        )
    )
    db_session.commit()
    db_session.refresh(course)

    result = evaluate_course_safe_publish(course)

    assert result.is_safe is False
    assert any(issue.code == "assessment_evidence_safety_risk" for issue in result.blocking_issues)


def test_safe_publish_validation_is_read_only_for_progress_and_evidence_state(db_session):
    course = _create_publish_ready_course(db_session, revision_status="current")
    student = User(
        id=uuid.uuid4(),
        firstname="Learner",
        lastname="State",
        username=f"learner_{uuid.uuid4()}",
        email=f"learner_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(course)

    first_unit = course.units[0]
    first_lesson = first_unit.lessons[0]
    student_course = StudentCourse(student_id=student.id, course_id=course.id, status="in_progress")
    db_session.add(student_course)
    db_session.commit()
    db_session.refresh(student_course)

    unit_progress = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=first_unit.id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add(unit_progress)
    db_session.commit()
    db_session.refresh(unit_progress)

    segment_progress = SegmentProgress(
        student_unit_id=unit_progress.id,
        lesson_id=first_lesson.id,
        status=ProgressStatus.NOT_STARTED,
    )
    db_session.add(segment_progress)
    db_session.commit()
    db_session.refresh(segment_progress)

    baseline = (
        student_course.status,
        unit_progress.status,
        segment_progress.status,
        db_session.query(StudentCourse).count(),
        db_session.query(StudentUnitProgress).count(),
        db_session.query(SegmentProgress).count(),
        db_session.query(StudentAssessmentAttempt).count(),
        db_session.query(StudentProgramProgress).count(),
        db_session.query(StudentCertification).count(),
    )

    result = evaluate_course_safe_publish(course)

    db_session.refresh(student_course)
    db_session.refresh(unit_progress)
    db_session.refresh(segment_progress)
    after = (
        student_course.status,
        unit_progress.status,
        segment_progress.status,
        db_session.query(StudentCourse).count(),
        db_session.query(StudentUnitProgress).count(),
        db_session.query(SegmentProgress).count(),
        db_session.query(StudentAssessmentAttempt).count(),
        db_session.query(StudentProgramProgress).count(),
        db_session.query(StudentCertification).count(),
    )

    assert result.is_safe is True
    assert after == baseline
