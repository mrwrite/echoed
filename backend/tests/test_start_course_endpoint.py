import os
import uuid
import pytest

# Use a file-based SQLite database for tests
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes import start_course
from app.auth import get_current_user
from app.database import SessionLocal
from app.models import (
    User,
    Course,
    Unit,
    Lesson,
    StudentCourse,
    StudentUnitProgress,
    SegmentProgress,
)
from app.enum import ProgressStatus


@pytest.fixture
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_student(test_db):
    student = User(
        id=uuid.uuid4(),
        firstname="Start",
        lastname="User",
        username=f"start_user_{uuid.uuid4()}",
        email=f"start_{uuid.uuid4()}@example.com",
        hashed_password="fake",
        role="student"
    )
    test_db.add(student)
    test_db.commit()
    test_db.refresh(student)
    return student


@pytest.fixture
def test_course_and_unit_and_lesson(test_db):
    course = Course(id=uuid.uuid4(), title="Course A", description="Test")
    unit = Unit(id=uuid.uuid4(), title="Unit A", course_id=course.id, order=1)
    lesson = Lesson(id=uuid.uuid4(), title="Lesson A", unit_id=unit.id, duration_minutes=10, order=1)

    test_db.add_all([course, unit, lesson])
    test_db.commit()
    return course, unit, lesson


def override_get_current_user(user):
    return lambda: user


def test_student_can_start_course(test_db, test_student, test_course_and_unit_and_lesson):
    course, unit, lesson = test_course_and_unit_and_lesson

    # Enroll the student
    student_course = StudentCourse(student_id=test_student.id, course_id=course.id)
    test_db.add(student_course)
    test_db.commit()
    test_db.refresh(student_course)

    # Override and isolate router
    test_app = FastAPI()
    test_app.include_router(start_course.router, prefix="/api")
    test_app.dependency_overrides[get_current_user] = override_get_current_user(test_student)
    client = TestClient(test_app)

    response = client.post("/api/start-course", json={"course_id": str(course.id)})

    assert response.status_code == 200
    data = response.json()
    assert data["lesson_id"] == str(lesson.id)
    assert data["status"] == ProgressStatus.NOT_STARTED.value

    # Verify unit progress
    unit_progress = test_db.query(StudentUnitProgress).filter_by(
        student_course_id=student_course.id,
        unit_id=unit.id
    ).first()
    assert unit_progress is not None
    assert unit_progress.status == ProgressStatus.IN_PROGRESS

    # Verify segment progress
    segment_progress = test_db.query(SegmentProgress).filter_by(
        student_unit_id=unit_progress.id,
        lesson_id=lesson.id
    ).first()
    assert segment_progress is not None
    assert segment_progress.status == ProgressStatus.NOT_STARTED


def test_start_course_requires_enrollment(test_db, test_student, test_course_and_unit_and_lesson):
    course, _, _ = test_course_and_unit_and_lesson

    test_app = FastAPI()
    test_app.include_router(start_course.router, prefix="/api")
    test_app.dependency_overrides[get_current_user] = override_get_current_user(test_student)
    client = TestClient(test_app)

    response = client.post("/api/start-course", json={"course_id": str(course.id)})

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enrolled in this course."
