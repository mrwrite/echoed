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


def test_curriculum_entities_serialize_with_default_lineage_metadata(db_session):
    course = Course(title="Lineage Course", description="Course description")
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

    serialized_course = serialize_course(course, viewer_role="teacher")
    serialized_summary = _serialize_course_summary(course)
    serialized_assessment = _serialize_assessment(assessment, current_user=None)

    assert serialized_course.previous_revision_id is None
    assert serialized_course.superseded_by_id is None
    assert serialized_course.lineage_status == "standalone"
    assert serialized_course.lineage_metadata == {}

    assert serialized_course.units[0].previous_revision_id is None
    assert serialized_course.units[0].superseded_by_id is None
    assert serialized_course.units[0].lineage_status == "standalone"
    assert serialized_course.units[0].lineage_metadata == {}

    assert serialized_course.units[0].lessons[0].previous_revision_id is None
    assert serialized_course.units[0].lessons[0].superseded_by_id is None
    assert serialized_course.units[0].lessons[0].lineage_status == "standalone"
    assert serialized_course.units[0].lessons[0].lineage_metadata == {}

    assert serialized_summary.previous_revision_id is None
    assert serialized_summary.superseded_by_id is None
    assert serialized_summary.lineage_status == "standalone"
    assert serialized_summary.lineage_metadata == {}

    assert serialized_assessment.previous_revision_id is None
    assert serialized_assessment.superseded_by_id is None
    assert serialized_assessment.lineage_status == "standalone"
    assert serialized_assessment.lineage_metadata == {}


def test_lineage_metadata_fields_are_optional_and_additive():
    payload = {
        "id": uuid.uuid4(),
        "title": "Course",
        "description": "Description",
        "learning_objectives": None,
        "skill_tags": [],
        "standards_metadata": {},
        "units": [],
    }

    from app.schemas import CourseResponse

    validated = CourseResponse(**payload)
    assert validated.previous_revision_id is None
    assert validated.superseded_by_id is None
    assert validated.lineage_status == "standalone"
    assert validated.lineage_metadata == {}


def test_lineage_metadata_serialization_does_not_mutate_progress_or_evidence_records(db_session):
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


def test_lineage_metadata_migration_is_additive():
    migration_path = Path("alembic/versions/9f1c2d3e4a5b_add_curriculum_lineage_metadata.py")
    contents = migration_path.read_text(encoding="utf-8")

    assert 'for table_name in ("courses", "units", "lessons", "assessments")' in contents
    assert 'sa.Column("previous_revision_id"' in contents
    assert 'sa.Column("superseded_by_id"' in contents
    assert 'sa.Column("lineage_status"' in contents
    assert 'sa.Column("lineage_metadata"' in contents
    assert "drop_table" not in contents
