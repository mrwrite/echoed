import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import activities, lessons, units
from app.database import get_db
from app.deps import get_current_user
from app.models import Activity, Course, Lesson, Source, Unit, User


@pytest.fixture
def api_client(db_session):
    test_app = FastAPI()
    test_app.include_router(units.router, prefix="/api")
    test_app.include_router(lessons.router, prefix="/api")
    test_app.include_router(activities.router, prefix="/api")

    current_user = {"value": None}

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return current_user["value"]

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = override_get_current_user

    return TestClient(test_app), current_user


@pytest.fixture
def admin_user(db_session):
    user = User(
        id=uuid.uuid4(),
        firstname="Admin",
        lastname="User",
        username=f"admin_{uuid.uuid4().hex[:8]}",
        email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        role="admin",
    )
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def test_course(db_session):
    course = Course(id=uuid.uuid4(), title="T", description="D")
    db_session.add(course)
    db_session.commit()
    return course


@pytest.fixture
def test_unit(db_session, test_course):
    unit = Unit(id=uuid.uuid4(), title="U", course_id=test_course.id)
    db_session.add(unit)
    db_session.commit()
    return unit


@pytest.fixture
def test_lesson(db_session, test_unit):
    lesson = Lesson(id=uuid.uuid4(), title="L", unit_id=test_unit.id)
    db_session.add(lesson)
    db_session.commit()
    return lesson


def test_unit_crud(api_client, admin_user, db_session, test_course):
    client, current_user = api_client
    current_user["value"] = admin_user

    resp = client.post(
        "/api/units",
        json={"course_id": str(test_course.id), "title": "Unit1"},
    )
    assert resp.status_code == 200
    unit_id = resp.json()["id"]

    resp = client.get(f"/api/units/{unit_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Unit1"

    resp = client.put(
        f"/api/units/{unit_id}",
        json={"course_id": str(test_course.id), "title": "UnitNew"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "UnitNew"

    resp = client.delete(f"/api/units/{unit_id}")
    assert resp.status_code == 200
    assert db_session.query(Unit).filter_by(id=uuid.UUID(unit_id)).first() is None


def test_lesson_crud(api_client, admin_user, db_session, test_unit):
    client, current_user = api_client
    current_user["value"] = admin_user

    resp = client.post(
        "/api/lessons",
        json={
            "unit_id": str(test_unit.id),
            "title": "Lesson1",
            "learning_objectives": "Understand how evidence strengthens a lesson.",
            "key_concepts": ["evidence", "citation"],
            "teacher_notes": "Model source evaluation before discussion.",
            "discussion_questions": ["Why do historians cite sources?"],
            "hook": "Ask students whether every website should be trusted equally.",
            "content": "Introduce source credibility and historical citation practices.",
            "guided_practice": "Review one primary and one secondary source together.",
            "independent_practice": "Students annotate a source and explain its value.",
            "assessment": "Exit ticket on identifying a strong citation.",
            "review_status": "reviewed",
            "sources": [
                {
                    "citation": "Example Source, 2024",
                    "url": "https://example.com/source",
                }
            ],
        },
    )
    assert resp.status_code == 200
    lesson_id = resp.json()["id"]
    assert resp.json()["learning_objectives"] == "Understand how evidence strengthens a lesson."
    assert resp.json()["review_status"] == "reviewed"
    assert resp.json()["sources"][0]["citation"] == "Example Source, 2024"

    resp = client.get(f"/api/lessons/{lesson_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Lesson1"
    assert resp.json()["key_concepts"] == ["evidence", "citation"]
    assert resp.json()["discussion_questions"] == ["Why do historians cite sources?"]

    resp = client.put(
        f"/api/lessons/{lesson_id}",
        json={
            "unit_id": str(test_unit.id),
            "title": "LessonNew",
            "learning_objectives": "Understand how evidence strengthens a lesson.",
            "key_concepts": ["evidence", "citation"],
            "teacher_notes": "Model source evaluation before discussion.",
            "discussion_questions": ["Why do historians cite sources?"],
            "hook": "Ask students whether every website should be trusted equally.",
            "content": "Introduce source credibility and historical citation practices.",
            "guided_practice": "Review one primary and one secondary source together.",
            "independent_practice": "Students annotate a source and explain its value.",
            "assessment": "Exit ticket on identifying a strong citation.",
            "review_status": "approved",
            "sources": [
                {
                    "citation": "Updated Source, 2025",
                    "url": "https://example.com/updated-source",
                }
            ],
        },
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "LessonNew"
    assert resp.json()["review_status"] == "approved"
    assert resp.json()["sources"][0]["citation"] == "Updated Source, 2025"
    assert db_session.query(Source).filter_by(lesson_id=uuid.UUID(lesson_id)).count() == 1

    resp = client.delete(f"/api/lessons/{lesson_id}")
    assert resp.status_code == 200
    assert db_session.query(Lesson).filter_by(id=uuid.UUID(lesson_id)).first() is None
    assert db_session.query(Source).filter_by(lesson_id=uuid.UUID(lesson_id)).count() == 0


def test_activity_crud(api_client, admin_user, db_session, test_lesson):
    client, current_user = api_client
    current_user["value"] = admin_user

    resp = client.post(
        "/api/activities",
        json={"lesson_id": str(test_lesson.id), "type": "video", "title": "A", "content": "C"},
    )
    assert resp.status_code == 200
    act_id = resp.json()["id"]

    resp = client.get(f"/api/activities/{act_id}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "A"

    resp = client.put(
        f"/api/activities/{act_id}",
        json={"lesson_id": str(test_lesson.id), "type": "video", "title": "B", "content": "C"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "B"

    resp = client.delete(f"/api/activities/{act_id}")
    assert resp.status_code == 200
    assert db_session.query(Activity).filter_by(id=uuid.UUID(act_id)).first() is None
