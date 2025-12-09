import os
import uuid
import shutil
import pytest

# Use an in-memory SQLite database for tests and a temp directory for uploads
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["BADGES_PATH"] = "./test_badges"

from fastapi.testclient import TestClient
from app import main as app_main
from app.main import app

BADGES_PATH = os.environ["BADGES_PATH"]
app_main.BADGES_PATH = BADGES_PATH
from app.models import User
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
def test_user(test_db):
    user = User(
        id=uuid.uuid4(),
        firstname="Badge",
        lastname="Uploader",
        username=f"badge_{uuid.uuid4()}",
        email=f"badge_{uuid.uuid4()}@example.com",
        hashed_password="fake",
        role="teacher",
    )
    test_db.add(user)
    test_db.commit()
    return user


def test_upload_badge_image(test_db, test_user):
    app.dependency_overrides[get_current_user] = lambda: test_user
    os.makedirs(BADGES_PATH, exist_ok=True)
    content = b"\x89PNG\r\n\x1a\n"
    files = {"file": ("badge.png", content, "image/png")}
    response = client.post("/api/upload/badge", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "file_path" in data

    filename = data["file_path"].split("/")[-1]
    file_path = os.path.join(BADGES_PATH, filename)
    assert os.path.exists(file_path)

    os.remove(file_path)
    if os.path.exists(BADGES_PATH):
        shutil.rmtree(BADGES_PATH)
    app.dependency_overrides = {}
