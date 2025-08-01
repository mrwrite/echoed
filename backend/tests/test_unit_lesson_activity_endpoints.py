import os
import uuid
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Course, Unit, Lesson, Activity

client = TestClient(app)

@pytest.fixture
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_course(test_db):
    course = Course(id=uuid.uuid4(), title="T", description="D")
    test_db.add(course)
    test_db.commit()
    return course

@pytest.fixture
def test_unit(test_db, test_course):
    unit = Unit(id=uuid.uuid4(), title="U", course_id=test_course.id)
    test_db.add(unit)
    test_db.commit()
    return unit

@pytest.fixture
def test_lesson(test_db, test_unit):
    lesson = Lesson(id=uuid.uuid4(), title="L", unit_id=test_unit.id)
    test_db.add(lesson)
    test_db.commit()
    return lesson

def test_unit_crud(test_db, test_course):
    resp = client.post(
        "/api/units",
        json={"course_id": str(test_course.id), "title": "Unit1"}
    )
    assert resp.status_code == 200
    unit_id = resp.json()["id"]

    resp = client.get(f"/api/units/{unit_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Unit1"

    resp = client.put(
        f"/api/units/{unit_id}",
        json={"course_id": str(test_course.id), "title": "UnitNew"}
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "UnitNew"

    resp = client.delete(f"/api/units/{unit_id}")
    assert resp.status_code == 200
    assert test_db.query(Unit).filter_by(id=uuid.UUID(unit_id)).first() is None

def test_lesson_crud(test_db, test_unit):
    resp = client.post(
        "/api/lessons",
        json={"unit_id": str(test_unit.id), "title": "Lesson1"}
    )
    assert resp.status_code == 200
    lesson_id = resp.json()["id"]

    resp = client.get(f"/api/lessons/{lesson_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Lesson1"

    resp = client.put(
        f"/api/lessons/{lesson_id}",
        json={"unit_id": str(test_unit.id), "title": "LessonNew"}
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "LessonNew"

    resp = client.delete(f"/api/lessons/{lesson_id}")
    assert resp.status_code == 200
    assert test_db.query(Lesson).filter_by(id=uuid.UUID(lesson_id)).first() is None

def test_activity_crud(test_db, test_lesson):
    resp = client.post(
        "/api/activities",
        json={"lesson_id": str(test_lesson.id), "type": "video", "title": "A", "content": "C"}
    )
    assert resp.status_code == 200
    act_id = resp.json()["id"]

    resp = client.get(f"/api/activities/{act_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "A"

    resp = client.put(
        f"/api/activities/{act_id}",
        json={"lesson_id": str(test_lesson.id), "type": "video", "title": "B", "content": "C"}
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "B"

    resp = client.delete(f"/api/activities/{act_id}")
    assert resp.status_code == 200
    assert test_db.query(Activity).filter_by(id=uuid.UUID(act_id)).first() is None
