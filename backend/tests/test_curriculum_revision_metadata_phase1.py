from pathlib import Path
import uuid

from app.api.routes.assessments import _serialize_assessment
from app.api.routes.programs import _serialize_course_summary
from app.lesson_governance import serialize_course
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


def test_curriculum_entities_serialize_with_default_revision_metadata(db_session):
    course = Course(title="Versioned Course", description="Course description")
    unit = Unit(course=course, title="Unit One", order=1, content="Unit content")
    lesson = Lesson(
        unit=unit,
        title="Lesson One",
        objective="Objective",
        learning_objectives="Learning objective",
        key_concepts=["concept"],
        teacher_notes="Notes",
        discussion_questions=["What did you learn?"],
        hook="Hook",
        content="Content",
        guided_practice="Guided practice",
        independent_practice="Independent practice",
        assessment="Assessment",
        review_status="approved",
        order=1,
    )
    assessment = Assessment(
        title="Assessment One",
        lesson=lesson,
        course=course,
        assessment_scope="lesson",
    )
    db_session.add_all([course, unit, lesson, assessment])
    db_session.commit()
    db_session.refresh(course)
    db_session.refresh(unit)
    db_session.refresh(lesson)
    db_session.refresh(assessment)

    serialized_course = serialize_course(course, viewer_role="teacher")
    serialized_summary = _serialize_course_summary(course)
    serialized_assessment = _serialize_assessment(assessment, current_user=None)

    assert serialized_course.revision_number == 1
    assert serialized_course.revision_label is None
    assert serialized_course.revision_status == "current"
    assert serialized_course.revision_metadata == {}
    assert serialized_course.published_at is None
    assert serialized_course.deprecated_at is None

    assert serialized_course.units[0].revision_number == 1
    assert serialized_course.units[0].revision_status == "current"
    assert serialized_course.units[0].revision_metadata == {}

    assert serialized_course.units[0].lessons[0].revision_number == 1
    assert serialized_course.units[0].lessons[0].revision_status == "current"
    assert serialized_course.units[0].lessons[0].revision_metadata == {}

    assert serialized_summary.revision_number == 1
    assert serialized_summary.revision_status == "current"
    assert serialized_summary.revision_metadata == {}

    assert serialized_assessment.revision_number == 1
    assert serialized_assessment.revision_status == "current"
    assert serialized_assessment.revision_metadata == {}
    assert serialized_assessment.published_at is None
    assert serialized_assessment.deprecated_at is None


def test_revision_metadata_fields_are_optional_and_additive():
    payload = {
        "id": uuid.uuid4(),
        "title": "Course",
        "description": "Description",
        "learning_objectives": None,
        "skill_tags": [],
        "standards_metadata": {},
        "units": [],
    }

    response = serialize_course.__annotations__  # keep import live for this module
    assert response is not None

    from app.schemas import CourseResponse

    validated = CourseResponse(**payload)
    assert validated.revision_number == 1
    assert validated.revision_label is None
    assert validated.revision_status == "current"
    assert validated.revision_metadata == {}
    assert validated.published_at is None
    assert validated.deprecated_at is None


def test_revision_metadata_serialization_does_not_mutate_progress_or_evidence_records(db_session):
    student = User(
        id=uuid.uuid4(),
        firstname="Student",
        lastname="Learner",
        username=f"student_{uuid.uuid4()}",
        email=f"student_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    course = Course(title="Stable Course", description="Course description")
    unit = Unit(course=course, title="Unit One", order=1, content="Unit content")
    lesson = Lesson(
        unit=unit,
        title="Lesson One",
        objective="Objective",
        learning_objectives="Learning objective",
        key_concepts=["concept"],
        teacher_notes="Notes",
        discussion_questions=["What did you learn?"],
        hook="Hook",
        content="Content",
        guided_practice="Guided practice",
        independent_practice="Independent practice",
        assessment="Assessment",
        review_status="approved",
        order=1,
    )
    assessment = Assessment(
        title="Assessment One",
        lesson=lesson,
        course=course,
        assessment_scope="lesson",
    )
    student_course = StudentCourse(student=student, course=course, status="active")
    db_session.add_all([student, course, unit, lesson, assessment, student_course])
    db_session.commit()

    before_counts = {
        "student_courses": db_session.query(StudentCourse).count(),
        "unit_progress": db_session.query(StudentUnitProgress).count(),
        "assessment_attempts": db_session.query(StudentAssessmentAttempt).count(),
        "program_progress": db_session.query(StudentProgramProgress).count(),
        "certifications": db_session.query(StudentCertification).count(),
        "programs": db_session.query(Program).count(),
    }

    serialize_course(course, viewer_role="student")
    _serialize_course_summary(course)
    _serialize_assessment(assessment, current_user=student)

    after_counts = {
        "student_courses": db_session.query(StudentCourse).count(),
        "unit_progress": db_session.query(StudentUnitProgress).count(),
        "assessment_attempts": db_session.query(StudentAssessmentAttempt).count(),
        "program_progress": db_session.query(StudentProgramProgress).count(),
        "certifications": db_session.query(StudentCertification).count(),
        "programs": db_session.query(Program).count(),
    }

    assert after_counts == before_counts


def test_revision_metadata_migration_is_additive():
    migration_path = Path(__file__).resolve().parents[1] / "alembic/versions/7d3c9a1e5b2f_add_curriculum_revision_metadata.py"
    contents = migration_path.read_text(encoding="utf-8")

    assert 'for table_name in ("courses", "units", "lessons", "assessments")' in contents

    assert 'sa.Column("revision_number"' in contents
    assert 'sa.Column("revision_status"' in contents
    assert 'sa.Column("revision_metadata"' in contents
    assert 'sa.Column("published_at"' in contents
    assert 'sa.Column("deprecated_at"' in contents
    assert "drop_table" not in contents
