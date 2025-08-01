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
def admin_user(test_db):
    user = User(
        id=uuid.uuid4(),
        firstname="Admin",
        lastname="User",
        username=f"admin_{uuid.uuid4()}",
        email=f"admin_{uuid.uuid4()}@example.com",
        hashed_password="fake",
        role="admin",
    )
    test_db.add(user)
    test_db.commit()
    return user


def test_delete_course_endpoint(test_db, admin_user):
    course = Course(id=uuid.uuid4(), title="Delete Me", description="Temp")
    test_db.add(course)
    test_db.commit()

    app.dependency_overrides[get_current_user] = lambda: admin_user

    resp = client.delete(f"/api/courses/{course.id}")
    assert resp.status_code == 200
    assert test_db.query(Course).filter_by(id=course.id).first() is None

    app.dependency_overrides = {}


def test_delete_user_endpoint(test_db, admin_user):
    user = User(
        id=uuid.uuid4(),
        firstname="Delete",
        lastname="User",
        username=f"del_{uuid.uuid4()}",
        email="del@example.com",
        hashed_password="fake",
        role="student",
    )
    test_db.add(user)
    test_db.commit()

    app.dependency_overrides[get_current_user] = lambda: admin_user

    resp = client.delete(f"/api/users/{user.id}")
    assert resp.status_code == 200
    assert test_db.query(User).filter_by(id=user.id).first() is None

    app.dependency_overrides = {}
