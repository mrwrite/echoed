import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import lessons
from app.auth import get_current_user
from app.database import get_db
from app.models import Course, Lesson, Source, Unit, User


@pytest.fixture
def test_app(db_session):
    app = FastAPI()
    app.include_router(lessons.router, prefix="/api")

    admin = User(
        id=uuid.uuid4(),
        firstname="Lesson",
        lastname="Reviewer",
        username=f"lesson_reviewer_{uuid.uuid4()}",
        email=f"lesson_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="admin",
    )
    db_session.add(admin)
    db_session.commit()

    course = Course(id=uuid.uuid4(), title="Academic Quality", description="Test course")
    db_session.add(course)
    db_session.commit()

    unit = Unit(id=uuid.uuid4(), title="Lesson Design", course_id=course.id, order=1)
    db_session.add(unit)
    db_session.commit()

    def override_get_current_user():
        return admin

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    return TestClient(app), db_session, unit, admin


def test_lesson_quality_fields_and_sources_round_trip(test_app):
    client, db_session, unit, admin = test_app

    create_response = client.post(
        "/api/lessons",
        json={
            "unit_id": str(unit.id),
            "title": "Source Credibility",
            "objective": "Evaluate claims with evidence.",
            "learning_objectives": "Students will distinguish strong and weak citations.",
            "key_concepts": ["primary source", "citation"],
            "teacher_notes": "Pause after the hook and ask for predictions.",
            "discussion_questions": [
                "What makes a source trustworthy?",
                "Why should academic claims be cited?",
            ],
            "hook": "Display two conflicting online claims and ask which one students trust.",
            "content": "Model how to inspect author, date, and citation quality.",
            "guided_practice": "Walk through a source evaluation together.",
            "independent_practice": "Students annotate one source on their own.",
            "assessment": "Exit ticket on identifying the strongest citation.",
            "review_status": "reviewed",
            "reviewed_by": str(admin.id),
            "sources": [
                {
                    "citation": "National Museum of African American History and Culture, 2024",
                    "url": "https://example.com/nmaahc"
                }
            ],
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    assert created["learning_objectives"] == "Students will distinguish strong and weak citations."
    assert created["key_concepts"] == ["primary source", "citation"]
    assert created["review_status"] == "reviewed"
    assert created["sources"][0]["citation"].startswith("National Museum")

    lesson_id = created["id"]
    fetch_response = client.get(f"/api/lessons/{lesson_id}")
    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert fetched["discussion_questions"][0] == "What makes a source trustworthy?"
    assert fetched["hook"].startswith("Display two conflicting")
    assert fetched["sources"][0]["url"] == "https://example.com/nmaahc"

    update_response = client.put(
        f"/api/lessons/{lesson_id}",
        json={
            "unit_id": str(unit.id),
            "title": "Source Credibility Revised",
            "objective": "Evaluate claims with evidence.",
            "learning_objectives": "Students will distinguish strong and weak citations.",
            "key_concepts": ["primary source", "citation"],
            "teacher_notes": "Pause after the hook and ask for predictions.",
            "discussion_questions": [
                "What makes a source trustworthy?",
                "Why should academic claims be cited?",
            ],
            "hook": "Display two conflicting online claims and ask which one students trust.",
            "content": "Model how to inspect author, date, and citation quality.",
            "guided_practice": "Walk through a source evaluation together.",
            "independent_practice": "Students annotate one source on their own.",
            "assessment": "Exit ticket on identifying the strongest citation.",
            "review_status": "approved",
            "sources": [
                {
                    "citation": "Library of Congress, 2025",
                    "url": "https://example.com/loc"
                }
            ],
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["title"] == "Source Credibility Revised"
    assert updated["review_status"] == "approved"
    assert updated["sources"][0]["citation"] == "Library of Congress, 2025"

    stored_lesson = db_session.query(Lesson).filter(Lesson.id == uuid.UUID(lesson_id)).first()
    assert stored_lesson is not None
    assert stored_lesson.review_status == "approved"
    stored_sources = db_session.query(Source).filter(Source.lesson_id == stored_lesson.id).all()
    assert len(stored_sources) == 1
    assert stored_sources[0].citation == "Library of Congress, 2025"
