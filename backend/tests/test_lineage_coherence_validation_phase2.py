import uuid

from app.lesson_governance import (
    evaluate_assessment_lineage_coherence,
    evaluate_course_lineage_coherence,
    evaluate_lesson_lineage_coherence,
    evaluate_unit_lineage_coherence,
)
from app.models import (
    Assessment,
    Course,
    Lesson,
    Program,
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


def test_default_lineage_metadata_is_coherent_for_curriculum_and_assessment_entities(db_session):
    course = Course(title="Course", description="Description")
    unit = Unit(course=course, title="Unit", order=1, content="Content")
    lesson = Lesson(unit=unit, **_lesson_kwargs("Lesson"))
    assessment = Assessment(title="Assessment", lesson=lesson, course=course, assessment_scope="lesson")
    db_session.add_all([course, unit, lesson, assessment])
    db_session.commit()

    assert evaluate_course_lineage_coherence(course).is_coherent is True
    assert evaluate_unit_lineage_coherence(unit).is_coherent is True
    assert evaluate_lesson_lineage_coherence(lesson).is_coherent is True
    assert evaluate_assessment_lineage_coherence(assessment).is_coherent is True


def test_invalid_lineage_status_produces_blocking_issue(db_session):
    course = Course(title="Course", description="Description", lineage_status="broken")
    db_session.add(course)
    db_session.commit()

    result = evaluate_course_lineage_coherence(course)

    assert result.is_coherent is False
    assert any(issue.code == "invalid_lineage_status" for issue in result.blocking_issues)


def test_self_referential_previous_revision_is_blocked(db_session):
    course = Course(id=uuid.uuid4(), title="Course", description="Description")
    course.previous_revision_id = course.id
    db_session.add(course)
    db_session.commit()

    result = evaluate_course_lineage_coherence(course)

    assert result.is_coherent is False
    assert any(issue.code == "self_referential_previous_revision" for issue in result.blocking_issues)


def test_self_referential_successor_revision_is_blocked(db_session):
    assessment = Assessment(
        id=uuid.uuid4(),
        title="Assessment",
        assessment_scope="course",
        superseded_by_id=None,
    )
    assessment.superseded_by_id = assessment.id
    db_session.add(assessment)
    db_session.commit()

    result = evaluate_assessment_lineage_coherence(assessment)

    assert result.is_coherent is False
    assert any(issue.code == "self_referential_successor_revision" for issue in result.blocking_issues)


def test_matching_previous_and_successor_references_are_blocked(db_session):
    shared_id = uuid.uuid4()
    course = Course(title="Course", description="Description")
    db_session.add(course)
    db_session.flush()
    unit = Unit(
        title="Unit",
        course_id=course.id,
        order=1,
        previous_revision_id=shared_id,
        superseded_by_id=shared_id,
        content="Content",
    )
    db_session.add(unit)
    db_session.commit()

    result = evaluate_unit_lineage_coherence(unit)

    assert result.is_coherent is False
    assert any(issue.code == "previous_and_successor_match" for issue in result.blocking_issues)


def test_superseded_or_deprecated_entities_without_successor_produce_warning(db_session):
    course = Course(title="Course", description="Description")
    unit = Unit(course=course, title="Unit", order=1, content="Content")
    db_session.add_all([course, unit])
    db_session.flush()
    lesson = Lesson(
        unit_id=unit.id,
        revision_status="deprecated",
        lineage_status="superseded",
        **_lesson_kwargs("Lesson"),
    )
    db_session.add(lesson)
    db_session.commit()

    result = evaluate_lesson_lineage_coherence(lesson)

    assert result.is_coherent is True
    assert any(issue.code == "missing_successor_reference" for issue in result.warnings)


def test_inconsistent_current_or_standalone_lineage_metadata_produces_issues(db_session):
    course = Course(
        title="Course",
        description="Description",
        revision_status="current",
        lineage_status="superseded",
    )
    successor_id = uuid.uuid4()
    unit = Unit(
        course=course,
        title="Unit",
        order=1,
        content="Content",
        lineage_status="standalone",
        previous_revision_id=uuid.uuid4(),
        superseded_by_id=successor_id,
    )
    db_session.add_all([course, unit])
    db_session.commit()

    course_result = evaluate_course_lineage_coherence(course)
    unit_result = evaluate_unit_lineage_coherence(unit)

    assert any(issue.code == "current_revision_inconsistent_lineage_status" for issue in course_result.blocking_issues)
    assert any(issue.code == "standalone_has_lineage_references" for issue in unit_result.warnings)


def test_lineage_coherence_validation_is_read_only_for_progress_and_evidence_state(db_session):
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
        revision_status="deprecated",
        lineage_status="deprecated",
    )
    unit = Unit(course=course, title="Unit", order=1, content="Content")
    lesson = Lesson(unit=unit, **_lesson_kwargs("Lesson"))
    assessment = Assessment(
        title="Assessment",
        lesson=lesson,
        course=course,
        assessment_scope="lesson",
        revision_status="deprecated",
        lineage_status="deprecated",
    )
    student_course = StudentCourse(student=student, course=course, status="active")
    db_session.add_all([student, course, unit, lesson, assessment, student_course])
    db_session.commit()

    baseline = {
        "student_courses": db_session.query(StudentCourse).count(),
        "unit_progress": db_session.query(StudentUnitProgress).count(),
        "assessment_attempts": db_session.query(StudentAssessmentAttempt).count(),
        "program_progress": db_session.query(StudentProgramProgress).count(),
        "certifications": db_session.query(StudentCertification).count(),
        "programs": db_session.query(Program).count(),
    }

    course_result = evaluate_course_lineage_coherence(course)
    unit_result = evaluate_unit_lineage_coherence(unit)
    lesson_result = evaluate_lesson_lineage_coherence(lesson)
    assessment_result = evaluate_assessment_lineage_coherence(assessment)

    after = {
        "student_courses": db_session.query(StudentCourse).count(),
        "unit_progress": db_session.query(StudentUnitProgress).count(),
        "assessment_attempts": db_session.query(StudentAssessmentAttempt).count(),
        "program_progress": db_session.query(StudentProgramProgress).count(),
        "certifications": db_session.query(StudentCertification).count(),
        "programs": db_session.query(Program).count(),
    }

    assert any(issue.code == "missing_successor_reference" for issue in course_result.warnings)
    assert unit_result.is_coherent is True
    assert lesson_result.is_coherent is True
    assert any(issue.code == "missing_successor_reference" for issue in assessment_result.warnings)
    assert after == baseline
