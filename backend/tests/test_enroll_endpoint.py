import os
import uuid
import pytest

# Use an in-memory SQLite database for tests
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from app.main import app
from app.models import User, Course, StudentCourse
from app.database import SessionLocal
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
def student_user(test_db):
    user = User(
        id=uuid.uuid4(),
        firstname="Enroll",
        lastname="Tester",
        username=f"enroll_tester_{uuid.uuid4()}",
        email=f"enroll_{uuid.uuid4()}@example.com",
        hashed_password="test123",
        role="student"
    )
    test_db.add(user)
    test_db.commit()
    return user

@pytest.fixture
def test_course(test_db):
    course = Course(
        id=uuid.uuid4(),
        title="Enroll Test Course",
        description="For enrollment testing"
    )
    test_db.add(course)
    test_db.commit()
    return course

def test_student_can_enroll_in_course(test_db, student_user, test_course):
    app.dependency_overrides[get_current_user] = lambda: student_user

    # re-import after override is applied
    from app.api.routes import enroll
    app.include_router(enroll.router, prefix="/api", tags=["Enrollment"])

    response = client.post("/api/enroll", json={"course_id": str(test_course.id)})
    assert response.status_code == 200

    enrolled = test_db.query(StudentCourse).filter_by(
        student_id=student_user.id,
        course_id=test_course.id
    ).first()

    assert enrolled is not None
    assert enrolled.status == "active"
    app.dependency_overrides = {}


