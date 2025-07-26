import uuid
import pytest
from app.models import (
    User, Course, Unit, Lesson,
    StudentCourse, StudentUnitProgress, SegmentProgress
)
from app.crud import progress as crud
from datetime import datetime


# ---------- Fixtures ----------

@pytest.fixture
def test_user(db_session):
    user = User(
        id=uuid.uuid4(),
        firstname="Progress",
        lastname="Tester",
        username="progress_tester",
        email="progress@example.com",
        hashed_password="hashed"
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def test_course(db_session):
    course = Course(
        id=uuid.uuid4(),
        title="Test Progress Course",
        description="Tracking test course"
    )
    db_session.add(course)
    db_session.commit()
    return course

@pytest.fixture
def test_unit(db_session, test_course):
    unit = Unit(
        id=uuid.uuid4(),
        title="Test Unit",
        course_id=test_course.id
    )
    db_session.add(unit)
    db_session.commit()
    return unit

@pytest.fixture
def test_lesson(db_session, test_unit):
    lesson = Lesson(
        id=uuid.uuid4(),
        title="Test Lesson",
        unit_id=test_unit.id,
        duration_minutes=10
    )
    db_session.add(lesson)
    db_session.commit()
    return lesson

# ---------- Tests ----------

def test_create_student_unit_progress(db_session, test_user, test_course, test_unit):
    student_course = StudentCourse(student_id=test_user.id, course_id=test_course.id)
    db_session.add(student_course)
    db_session.commit()

    unit_progress = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=test_unit.id,
        status="in_progress"
    )
    db_session.add(unit_progress)
    db_session.commit()

    result = db_session.query(StudentUnitProgress).filter_by(unit_id=test_unit.id).first()
    assert result is not None
    assert result.status == "in_progress"
    assert result.unit_id == test_unit.id
    assert result.student_course_id == student_course.id

def test_create_segment_progress(db_session, test_user, test_course, test_unit, test_lesson):
    student_course = StudentCourse(student_id=test_user.id, course_id=test_course.id)
    db_session.add(student_course)
    db_session.commit()

    unit_progress = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=test_unit.id
    )
    db_session.add(unit_progress)
    db_session.commit()

    segment_progress = SegmentProgress(
        student_unit_id=unit_progress.id,
        lesson_id=test_lesson.id,
        status="delivered"
    )
    db_session.add(segment_progress)
    db_session.commit()

    result = db_session.query(SegmentProgress).filter_by(lesson_id=test_lesson.id).first()
    assert result is not None
    assert result.status == "delivered"
    assert result.student_unit_id == unit_progress.id


def test_crud_create_and_get_student_unit_progress(db_session, test_user, test_course, test_unit):
    student_course = StudentCourse(student_id=test_user.id, course_id=test_course.id)
    db_session.add(student_course)
    db_session.commit()

    created = crud.create_student_unit_progress(db_session, student_course.id, test_unit.id)
    assert created is not None
    assert created.status == "not_started"

    retrieved = crud.get_student_unit_progress(db_session, student_course.id, test_unit.id)
    assert retrieved.id == created.id

def test_crud_update_student_unit_progress_status(db_session, test_user, test_course, test_unit):
    student_course = StudentCourse(student_id=test_user.id, course_id=test_course.id)
    db_session.add(student_course)
    db_session.commit()

    progress_obj = crud.create_student_unit_progress(db_session, student_course.id, test_unit.id)
    updated = crud.update_student_unit_progress_status(db_session, progress_obj.id, "completed")

    assert updated.status == "completed"
    assert isinstance(updated.last_updated, datetime)

def test_crud_create_and_get_segment_progress(db_session, test_user, test_course, test_unit, test_lesson):
    student_course = StudentCourse(student_id=test_user.id, course_id=test_course.id)
    db_session.add(student_course)
    db_session.commit()

    unit_progress = crud.create_student_unit_progress(db_session, student_course.id, test_unit.id)

    created = crud.create_segment_progress(db_session, unit_progress.id, test_lesson.id)
    assert created.status == "not_started"

    retrieved = crud.get_segment_progress(db_session, unit_progress.id, test_lesson.id)
    assert retrieved.id == created.id

def test_crud_update_segment_progress_status(db_session, test_user, test_course, test_unit, test_lesson):
    student_course = StudentCourse(student_id=test_user.id, course_id=test_course.id)
    db_session.add(student_course)
    db_session.commit()

    unit_progress = crud.create_student_unit_progress(db_session, student_course.id, test_unit.id)
    segment = crud.create_segment_progress(db_session, unit_progress.id, test_lesson.id)

    updated = crud.update_segment_progress_status(db_session, segment.id, "skipped")
    assert updated.status == "skipped"
    assert isinstance(updated.last_updated, datetime)


def test_delete_lesson_cascades_segment_progress(db_session, test_user, test_course, test_unit):
    lesson = Lesson(
        id=uuid.uuid4(),
        title="Temp Lesson",
        unit_id=test_unit.id,
        duration_minutes=5,
    )
    db_session.add(lesson)
    db_session.commit()

    student_course = StudentCourse(student_id=test_user.id, course_id=test_course.id)
    db_session.add(student_course)
    db_session.commit()

    unit_progress = crud.create_student_unit_progress(db_session, student_course.id, test_unit.id)
    segment = crud.create_segment_progress(db_session, unit_progress.id, lesson.id)

    db_session.delete(lesson)
    db_session.commit()

    result = db_session.query(SegmentProgress).filter_by(id=segment.id).first()
    assert result is None


