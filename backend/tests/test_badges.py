import os
import uuid
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes import badges as badges_router
from app.auth import get_current_user
from app.database import SessionLocal
from app.models import User

app = FastAPI()
app.include_router(badges_router.router, prefix="/api")

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
        email="admin@example.com",
        hashed_password="fake",
        role="admin",
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
        email="student@example.com",
        hashed_password="fake",
        role="student",
    )
    test_db.add(user)
    test_db.commit()
    return user


def override_current(user):
    return lambda: user


def test_create_and_assign_badge(test_db, admin_user, student_user):
    client = TestClient(app)
    app.dependency_overrides[get_current_user] = override_current(admin_user)
    resp = client.post(
        "/api/badges",
        json={"title": "Great", "description": "Well done", "image_url": "http://x"}
    )
    assert resp.status_code == 200
    badge_id = resp.json()["id"]

    resp = client.post(f"/api/students/{student_user.id}/badges/{badge_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["student_id"] == str(student_user.id)
    assert data["badge_id"] == badge_id

    app.dependency_overrides[get_current_user] = override_current(student_user)
    resp = client.get(f"/api/students/{student_user.id}/badges")
    assert resp.status_code == 200
    badges = resp.json()
    assert len(badges) == 1
    assert badges[0]["badge_id"] == badge_id
    app.dependency_overrides = {}
