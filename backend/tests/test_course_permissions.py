import os
import uuid
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import User, Course
from app.auth import get_current_user

client = TestClient(app)


@pytest.fixture
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def teacher_user(test_db):
    user = User(
        id=uuid.uuid4(),
        firstname="Teach",
        lastname="User",
        username=f"teacher_{uuid.uuid4()}",
        email=f"teacher_{uuid.uuid4()}@example.com",
        hashed_password="fake",
        role="teacher",
    )
    test_db.add(user)
    test_db.commit()
    return user


@pytest.fixture
def student_user(test_db):
    user = User(
        id=uuid.uuid4(),
        firstname="Stud",
        lastname="User",
        username=f"student_{uuid.uuid4()}",
        email=f"student_{uuid.uuid4()}@example.com",
        hashed_password="fake",
        role="student",
    )
    test_db.add(user)
    test_db.commit()
    return user


def test_teacher_can_create_course(test_db, teacher_user):
    app.dependency_overrides[get_current_user] = lambda: teacher_user

    resp = client.post(
        "/api/courses",
        json={"title": "Course A", "description": "Desc", "units": []},
    )

    assert resp.status_code == 200
    assert test_db.query(Course).filter_by(title="Course A").first() is not None

    app.dependency_overrides = {}


def test_student_cannot_create_course(test_db, student_user):
    app.dependency_overrides[get_current_user] = lambda: student_user

    resp = client.post(
        "/api/courses",
        json={"title": "Course B", "description": "Desc", "units": []},
    )

    assert resp.status_code == 403
    assert test_db.query(Course).filter_by(title="Course B").first() is None

    app.dependency_overrides = {}


def test_teacher_can_update_course(test_db, teacher_user):
    course = Course(id=uuid.uuid4(), title="Old", description="Old")
    test_db.add(course)
    test_db.commit()

    app.dependency_overrides[get_current_user] = lambda: teacher_user

    resp = client.put(
        f"/api/courses/{course.id}",
        json={"title": "New", "description": "New", "units": []},
    )

    assert resp.status_code == 200
    test_db.expire_all()
    updated = test_db.query(Course).filter_by(id=course.id).first()
    assert updated.title == "New"

    app.dependency_overrides = {}


def test_student_cannot_update_course(test_db, student_user):
    course = Course(id=uuid.uuid4(), title="Old2", description="Old")
    test_db.add(course)
    test_db.commit()

    app.dependency_overrides[get_current_user] = lambda: student_user

    resp = client.put(
        f"/api/courses/{course.id}",
        json={"title": "Fail", "description": "Fail", "units": []},
    )

    assert resp.status_code == 403
    unchanged = test_db.query(Course).filter_by(id=course.id).first()
    assert unchanged.title == "Old2"

    app.dependency_overrides = {}


def test_student_cannot_delete_course(test_db, student_user):
    course = Course(id=uuid.uuid4(), title="Del", description="Del")
    test_db.add(course)
    test_db.commit()

    app.dependency_overrides[get_current_user] = lambda: student_user

    resp = client.delete(f"/api/courses/{course.id}")

    assert resp.status_code == 403
    assert test_db.query(Course).filter_by(id=course.id).first() is not None

    app.dependency_overrides = {}

