import uuid

from app.enum import ProgressStatus
from app.lesson_governance import (
    evaluate_course_learner_progress_safety,
    evaluate_lesson_learner_progress_safety,
    evaluate_unit_learner_progress_safety,
)
from app.models import (
    Course,
    Lesson,
    Program,
    SegmentProgress,
    StudentAssessmentAttempt,
    StudentCertification,
    StudentCourse,
    StudentProgramProgress,
    StudentUnitProgress,
    Unit,
    User,
)


def _lesson_kwargs(title: str) -> dict:
    return {
        "title": title,
        "objective": "Objective",
        "learning_objectives": "Learning objective",
        "key_concepts": ["concept"],
        "teacher_notes": "Notes",
        "discussion_questions": ["What did you learn?"],
        "hook": "Hook",
        "content": "Content",
        "guided_practice": "Guided practice",
        "independent_practice": "Independent practice",
        "assessment": "Assessment",
        "review_status": "approved",
        "order": 1,
    }


def _seed_progress_chain(db_session, *, course_revision_status="current", course_lineage_status="standalone", unit_revision_status="current", unit_lineage_status="standalone", lesson_revision_status="current", lesson_lineage_status="standalone", course_superseded_by_id=None, unit_superseded_by_id=None, lesson_superseded_by_id=None):
    student = User(
        id=uuid.uuid4(),
        firstname="Student",
        lastname="Learner",
        username=f"student_{uuid.uuid4()}",
        email=f"student_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    course = Course(
        title="Course",
        description="Description",
        revision_status=course_revision_status,
        lineage_status=course_lineage_status,
        superseded_by_id=course_superseded_by_id,
    )
    unit = Unit(
        course=course,
        title="Unit",
        order=1,
        content="Content",
        revision_status=unit_revision_status,
        lineage_status=unit_lineage_status,
        superseded_by_id=unit_superseded_by_id,
    )
    lesson = Lesson(
        unit=unit,
        revision_status=lesson_revision_status,
        lineage_status=lesson_lineage_status,
        superseded_by_id=lesson_superseded_by_id,
        **_lesson_kwargs("Lesson"),
    )
    student_course = StudentCourse(student=student, course=course, status="active")
    db_session.add_all([student, course, unit, lesson, student_course])
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

    segment = SegmentProgress(
        student_unit_id=unit_progress.id,
        lesson_id=lesson.id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add(segment)
    db_session.commit()
    db_session.refresh(course)
    db_session.refresh(unit)
    db_session.refresh(lesson)
    return course, unit, lesson, student_course, unit_progress, segment


def test_active_course_progress_against_deprecated_or_archived_course_produces_issue(db_session):
    deprecated_course, _, _, _, _, _ = _seed_progress_chain(
        db_session,
        course_revision_status="deprecated",
        course_lineage_status="deprecated",
    )
    archived_course, _, _, _, _, _ = _seed_progress_chain(
        db_session,
        course_revision_status="archived",
        course_lineage_status="archived",
    )

    deprecated_result = evaluate_course_learner_progress_safety(deprecated_course)
    archived_result = evaluate_course_learner_progress_safety(archived_course)

    assert any(issue.code == "active_course_progress_on_deprecated_revision" for issue in deprecated_result.blocking_issues)
    assert any(issue.code == "active_course_progress_on_deprecated_revision" for issue in archived_result.blocking_issues)


def test_unit_progress_against_deprecated_or_archived_unit_produces_issue(db_session):
    _, deprecated_unit, _, _, _, _ = _seed_progress_chain(
        db_session,
        unit_revision_status="deprecated",
        unit_lineage_status="deprecated",
    )
    _, archived_unit, _, _, _, _ = _seed_progress_chain(
        db_session,
        unit_revision_status="archived",
        unit_lineage_status="archived",
    )

    deprecated_result = evaluate_unit_learner_progress_safety(deprecated_unit)
    archived_result = evaluate_unit_learner_progress_safety(archived_unit)

    assert any(issue.code == "active_unit_progress_on_deprecated_revision" for issue in deprecated_result.blocking_issues)
    assert any(issue.code == "active_unit_progress_on_deprecated_revision" for issue in archived_result.blocking_issues)


def test_segment_progress_against_deprecated_archived_or_superseded_lesson_produces_issue(db_session):
    _, _, deprecated_lesson, _, _, _ = _seed_progress_chain(
        db_session,
        lesson_revision_status="deprecated",
        lesson_lineage_status="deprecated",
    )
    _, _, archived_lesson, _, _, _ = _seed_progress_chain(
        db_session,
        lesson_revision_status="archived",
        lesson_lineage_status="archived",
    )
    _, _, superseded_lesson, _, _, _ = _seed_progress_chain(
        db_session,
        lesson_revision_status="deprecated",
        lesson_lineage_status="superseded",
    )

    deprecated_result = evaluate_lesson_learner_progress_safety(deprecated_lesson)
    archived_result = evaluate_lesson_learner_progress_safety(archived_lesson)
    superseded_result = evaluate_lesson_learner_progress_safety(superseded_lesson)

    assert any(issue.code == "segment_progress_on_deprecated_revision" for issue in deprecated_result.blocking_issues)
    assert any(issue.code == "segment_progress_on_deprecated_revision" for issue in archived_result.blocking_issues)
    assert any(issue.code == "segment_progress_on_superseded_revision" for issue in superseded_result.blocking_issues)


def test_current_content_with_progress_is_safe(db_session):
    course, unit, lesson, _, _, _ = _seed_progress_chain(db_session)

    assert evaluate_course_learner_progress_safety(course).is_safe is True
    assert evaluate_unit_learner_progress_safety(unit).is_safe is True
    assert evaluate_lesson_learner_progress_safety(lesson).is_safe is True


def test_missing_successor_metadata_produces_warning_when_progress_exists(db_session):
    course, unit, lesson, _, _, _ = _seed_progress_chain(
        db_session,
        course_revision_status="deprecated",
        course_lineage_status="deprecated",
        unit_revision_status="deprecated",
        unit_lineage_status="deprecated",
        lesson_revision_status="deprecated",
        lesson_lineage_status="superseded",
    )

    course_result = evaluate_course_learner_progress_safety(course)
    unit_result = evaluate_unit_learner_progress_safety(unit)
    lesson_result = evaluate_lesson_learner_progress_safety(lesson)

    assert any(issue.code == "missing_successor_metadata_with_active_course_progress" for issue in course_result.warnings)
    assert any(issue.code == "missing_successor_metadata_with_active_unit_progress" for issue in unit_result.warnings)
    assert any(issue.code == "missing_successor_metadata_with_segment_progress" for issue in lesson_result.warnings)


def test_progress_safety_validation_is_read_only_and_does_not_mutate_progress(db_session):
    course, unit, lesson, student_course, unit_progress, segment = _seed_progress_chain(
        db_session,
        course_revision_status="deprecated",
        course_lineage_status="deprecated",
        unit_revision_status="deprecated",
        unit_lineage_status="deprecated",
        lesson_revision_status="deprecated",
        lesson_lineage_status="superseded",
    )

    baseline = {
        "student_course_status": student_course.status,
        "unit_progress_status": unit_progress.status,
        "segment_status": segment.status,
        "student_courses": db_session.query(StudentCourse).count(),
        "unit_progress": db_session.query(StudentUnitProgress).count(),
        "segments": db_session.query(SegmentProgress).count(),
        "assessment_attempts": db_session.query(StudentAssessmentAttempt).count(),
        "program_progress": db_session.query(StudentProgramProgress).count(),
        "certifications": db_session.query(StudentCertification).count(),
        "programs": db_session.query(Program).count(),
    }

    evaluate_course_learner_progress_safety(course)
    evaluate_unit_learner_progress_safety(unit)
    evaluate_lesson_learner_progress_safety(lesson)

    db_session.refresh(student_course)
    db_session.refresh(unit_progress)
    db_session.refresh(segment)

    after = {
        "student_course_status": student_course.status,
        "unit_progress_status": unit_progress.status,
        "segment_status": segment.status,
        "student_courses": db_session.query(StudentCourse).count(),
        "unit_progress": db_session.query(StudentUnitProgress).count(),
        "segments": db_session.query(SegmentProgress).count(),
        "assessment_attempts": db_session.query(StudentAssessmentAttempt).count(),
        "program_progress": db_session.query(StudentProgramProgress).count(),
        "certifications": db_session.query(StudentCertification).count(),
        "programs": db_session.query(Program).count(),
    }

    assert after == baseline
