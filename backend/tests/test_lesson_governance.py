import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import courses, lessons
from app.auth import get_current_user
from app.database import get_db
from app.models import Course, Lesson, Source, Unit, User


def _ready_lesson_kwargs(title: str) -> dict:
    return {
        "title": title,
        "objective": "Evaluate claims with evidence.",
        "learning_objectives": "Students will compare cited and uncited claims.",
        "key_concepts": ["citation", "credibility"],
        "teacher_notes": "Use the sample text to model the comparison.",
        "discussion_questions": ["Which source is more credible?"],
        "hook": "Show two conflicting claims.",
        "content": "Explain how to inspect source credibility.",
        "guided_practice": "Work through one cited article together.",
        "independent_practice": "Students review one source on their own.",
        "assessment": "Short written credibility comparison.",
    }


@pytest.fixture
def governance_app(db_session):
    app = FastAPI()
    app.include_router(lessons.router, prefix="/api")
    app.include_router(courses.router, prefix="/api")

    admin = User(
        id=uuid.uuid4(),
        firstname="Admin",
        lastname="Reviewer",
        username=f"admin_{uuid.uuid4()}",
        email=f"admin_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="admin",
    )
    teacher = User(
        id=uuid.uuid4(),
        firstname="Teacher",
        lastname="Author",
        username=f"teacher_{uuid.uuid4()}",
        email=f"teacher_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="teacher",
    )
    student = User(
        id=uuid.uuid4(),
        firstname="Student",
        lastname="Learner",
        username=f"student_{uuid.uuid4()}",
        email=f"student_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    db_session.add_all([admin, teacher, student])
    db_session.commit()

    course = Course(id=uuid.uuid4(), title="Governed Content", description="Course with governance rules")
    db_session.add(course)
    db_session.commit()

    approved_unit = Unit(id=uuid.uuid4(), title="Approved Unit", course_id=course.id, order=1)
    fallback_unit = Unit(id=uuid.uuid4(), title="Fallback Unit", course_id=course.id, order=2)
    db_session.add_all([approved_unit, fallback_unit])
    db_session.commit()

    current_user_holder = {"user": admin}

    def override_get_current_user():
        return current_user_holder["user"]

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    return {
        "client": TestClient(app),
        "db_session": db_session,
        "admin": admin,
        "teacher": teacher,
        "student": student,
        "course": course,
        "approved_unit": approved_unit,
        "fallback_unit": fallback_unit,
        "current_user_holder": current_user_holder,
    }


def _add_lesson(db_session, unit: Unit, *, review_status: str, title: str, reviewed_by=None) -> Lesson:
    lesson = Lesson(
        unit_id=unit.id,
        review_status=review_status,
        reviewed_by=reviewed_by,
        **_ready_lesson_kwargs(title),
    )
    db_session.add(lesson)
    db_session.flush()
    db_session.add(
        Source(
            lesson_id=lesson.id,
            citation=f"{title} source",
            url="https://example.com/source",
        )
    )
    db_session.commit()
    db_session.refresh(lesson)
    return lesson


def test_approval_requires_readiness(governance_app):
    client = governance_app["client"]
    approved_unit = governance_app["approved_unit"]

    response = client.post(
        "/api/lessons",
        json={
            "unit_id": str(approved_unit.id),
            "title": "Incomplete Lesson",
            "review_status": "approved",
            "sources": [],
        },
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert detail["message"] == "Lesson is not ready for approval."
    assert "key_concepts" in detail["missing_readiness_fields"]
    assert "sources" in detail["missing_readiness_fields"]


def test_only_reviewers_can_set_review_status_and_reviewer_is_system_managed(governance_app):
    client = governance_app["client"]
    approved_unit = governance_app["approved_unit"]
    current_user_holder = governance_app["current_user_holder"]
    teacher = governance_app["teacher"]
    admin = governance_app["admin"]

    current_user_holder["user"] = teacher
    forbidden = client.post(
        "/api/lessons",
        json={
            "unit_id": str(approved_unit.id),
            "review_status": "reviewed",
            "sources": [{"citation": "Teacher source", "url": "https://example.com/teacher"}],
            **_ready_lesson_kwargs("Teacher Review Attempt"),
        },
    )
    assert forbidden.status_code == 403

    current_user_holder["user"] = admin
    response = client.post(
        "/api/lessons",
        json={
            "unit_id": str(approved_unit.id),
            "review_status": "approved",
            "reviewed_by": str(uuid.uuid4()),
            "sources": [{"citation": "Admin source", "url": "https://example.com/admin"}],
            **_ready_lesson_kwargs("Admin Approval"),
        },
    )

    assert response.status_code == 200
    created = response.json()
    assert created["review_status"] == "approved"
    assert created["reviewed_by"] == str(admin.id)
    assert created["is_ready_for_approval"] is True


def test_student_direct_lesson_access_remains_available_but_filters_staff_fields(governance_app):
    db_session = governance_app["db_session"]
    current_user_holder = governance_app["current_user_holder"]
    student = governance_app["student"]
    approved_unit = governance_app["approved_unit"]
    client = governance_app["client"]

    legacy_lesson = Lesson(
        unit_id=approved_unit.id,
        title="Legacy Lesson",
        objective="Legacy objective",
        teacher_notes="Teacher-only note",
        discussion_questions=["Private discussion prompt"],
        review_status="draft",
    )
    db_session.add(legacy_lesson)
    db_session.commit()
    db_session.refresh(legacy_lesson)

    current_user_holder["user"] = student
    response = client.get(f"/api/lessons/{legacy_lesson.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Legacy Lesson"
    assert payload["teacher_notes"] is None
    assert payload["discussion_questions"] == []
    assert payload["is_ready_for_approval"] is False


def test_student_direct_lesson_access_prefers_approved_ready_sibling(governance_app):
    db_session = governance_app["db_session"]
    current_user_holder = governance_app["current_user_holder"]
    student = governance_app["student"]
    admin = governance_app["admin"]
    approved_unit = governance_app["approved_unit"]
    client = governance_app["client"]

    approved_lesson = _add_lesson(
        db_session,
        approved_unit,
        review_status="approved",
        title="Approved Lesson",
        reviewed_by=admin.id,
    )
    draft_lesson = Lesson(
        unit_id=approved_unit.id,
        title="Requested Draft Lesson",
        objective="Legacy objective",
        teacher_notes="Teacher-only note",
        discussion_questions=["Private discussion prompt"],
        review_status="draft",
        order=99,
    )
    db_session.add(draft_lesson)
    db_session.commit()
    db_session.refresh(draft_lesson)

    current_user_holder["user"] = student
    response = client.get(f"/api/lessons/{draft_lesson.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(approved_lesson.id)
    assert payload["title"] == "Approved Lesson"
    assert payload["teacher_notes"] is None
    assert payload["discussion_questions"] == []


def test_course_endpoint_prefers_approved_lessons_but_falls_back_when_needed(governance_app):
    db_session = governance_app["db_session"]
    current_user_holder = governance_app["current_user_holder"]
    student = governance_app["student"]
    admin = governance_app["admin"]
    course = governance_app["course"]
    approved_unit = governance_app["approved_unit"]
    fallback_unit = governance_app["fallback_unit"]
    client = governance_app["client"]

    _add_lesson(
        db_session,
        approved_unit,
        review_status="approved",
        title="Approved Lesson",
        reviewed_by=admin.id,
    )
    draft_lesson = _add_lesson(
        db_session,
        approved_unit,
        review_status="draft",
        title="Draft Lesson",
    )
    fallback_lesson = Lesson(
        unit_id=fallback_unit.id,
        title="Fallback Lesson",
        objective="Legacy objective",
        teacher_notes="Fallback note",
        discussion_questions=["Fallback prompt"],
        review_status="draft",
    )
    db_session.add(fallback_lesson)
    db_session.commit()

    current_user_holder["user"] = student
    response = client.get(f"/api/courses/{course.id}")

    assert response.status_code == 200
    payload = response.json()

    approved_unit_payload = payload["units"][0]
    assert [lesson["title"] for lesson in approved_unit_payload["lessons"]] == ["Approved Lesson"]

    fallback_unit_payload = payload["units"][1]
    assert [lesson["title"] for lesson in fallback_unit_payload["lessons"]] == ["Fallback Lesson"]
    assert fallback_unit_payload["lessons"][0]["teacher_notes"] is None
    assert fallback_unit_payload["lessons"][0]["discussion_questions"] == []

    assert draft_lesson.title not in [lesson["title"] for lesson in approved_unit_payload["lessons"]]


def test_editing_approved_lesson_can_explicitly_revert_to_draft(governance_app):
    db_session = governance_app["db_session"]
    current_user_holder = governance_app["current_user_holder"]
    teacher = governance_app["teacher"]
    admin = governance_app["admin"]
    approved_unit = governance_app["approved_unit"]
    client = governance_app["client"]

    approved_lesson = _add_lesson(
        db_session,
        approved_unit,
        review_status="approved",
        title="Approved Lesson",
        reviewed_by=admin.id,
    )

    current_user_holder["user"] = teacher
    response = client.put(
        f"/api/lessons/{approved_lesson.id}",
        json={
            "unit_id": str(approved_unit.id),
            "review_status": "draft",
            "sources": [{"citation": "Teacher source", "url": "https://example.com/teacher"}],
            **_ready_lesson_kwargs("Approved Lesson Revised"),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["review_status"] == "draft"
    assert payload["reviewed_by"] is None
