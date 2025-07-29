import os
import uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app, STORYBOOK_PATH
from app.models import User
from app.database import SessionLocal
from app import deps

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
        firstname="Story",
        lastname="Tester",
        username=f"story_{uuid.uuid4()}",
        email=f"story_{uuid.uuid4()}@example.com",
        hashed_password="fake",
        role="teacher",
    )
    test_db.add(user)
    test_db.commit()
    return user


def test_upload_storybook_page(test_db, test_user):
    app.dependency_overrides[deps.get_current_user] = lambda: test_user
    content = b"\x89PNG\r\n\x1a\n"
    files = {"file": ("page.png", content, "image/png")}
    response = client.post("/api/upload/storybook", files=files)
    assert response.status_code == 200
    data = response.json()
    assert "file_path" in data

    filename = data["file_path"].split("/")[-1]
    file_path = os.path.join(STORYBOOK_PATH, filename)
    assert os.path.exists(file_path)

    os.remove(file_path)
    app.dependency_overrides = {}
