import os
import uuid
import pytest
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app
from app.database import SessionLocal
from app.models import Course, Unit, Lesson, Activity, StorybookPage, User
from app.auth import get_current_user

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def test_db():
    db = SessionLocal()
    from app.models import Base
    Base.metadata.drop_all(bind=db.get_bind())
    Base.metadata.create_all(bind=db.get_bind())
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def test_user(test_db):
    user = User(
        id=uuid.uuid4(),
        firstname="T",
        lastname="U",
        username=f"teacher_{uuid.uuid4()}",
        email=f"teacher_{uuid.uuid4()}@example.com",
        hashed_password="fake",
        role="teacher",
    )
    test_db.add(user)
    test_db.commit()
    return user


def test_update_course_rollback_preserves_storybook_pages(test_db, test_user, monkeypatch):
    # Initial data: course with a storybook activity containing one page
    course = Course(id=uuid.uuid4(), title="C", description="D")
    unit = Unit(id=uuid.uuid4(), title="U", course_id=course.id)
    lesson = Lesson(id=uuid.uuid4(), title="L", unit_id=unit.id)
    activity = Activity(
        id=uuid.uuid4(),
        lesson_id=lesson.id,
        type="storybook",
        title="A",
        content="C",
    )
    page = StorybookPage(
        id=uuid.uuid4(),
        activity_id=activity.id,
        image_url="url",
        order=1,
    )
    test_db.add_all([course, unit, lesson, activity, page])
    test_db.commit()

    assert test_db.query(StorybookPage).count() == 1

    # Patch Session.flush to raise after the first call during update
    from sqlalchemy.orm import Session as SASession

    original_flush = SASession.flush
    call_count = {"count": 0}

    def failing_flush(self, *args, **kwargs):
        call_count["count"] += 1
        if call_count["count"] > 1:
            raise Exception("boom")
        return original_flush(self, *args, **kwargs)

    monkeypatch.setattr(SASession, "flush", failing_flush)

    app.dependency_overrides[get_current_user] = lambda: test_user

    payload = {
        "title": "New",
        "description": "New",
        "units": [
            {
                "title": "U2",
                "order": 1,
                "content": None,
                "lessons": [],
            }
        ],
    }

    response = client.put(f"/api/courses/{course.id}", json=payload)
    assert response.status_code == 500

    # Ensure original storybook page still exists after failed update
    db_check = SessionLocal()
    try:
        assert db_check.query(StorybookPage).count() == 1
    finally:
        db_check.close()

    app.dependency_overrides = {}
