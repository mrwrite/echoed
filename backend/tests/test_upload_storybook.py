import os
import uuid

from fastapi.testclient import TestClient

from app.api.routes import uploads
from app.deps import get_current_user
from app.main import app
from app.models import User

client = TestClient(app)


def test_upload_storybook_page(db_session, tmp_path, monkeypatch):
    teacher_user = User(
        id=uuid.uuid4(),
        firstname="Story",
        lastname="Tester",
        username=f"story_{uuid.uuid4().hex[:8]}",
        email=f"story_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="fake",
        role="teacher",
    )
    db_session.add(teacher_user)
    db_session.commit()

    storybook_path = tmp_path / "storybook"
    storybook_path.mkdir()
    monkeypatch.setattr(uploads, "STORYBOOK_PATH", str(storybook_path))
    app.dependency_overrides[get_current_user] = lambda: teacher_user

    try:
        content = b"\x89PNG\r\n\x1a\n"
        files = {"file": ("page.png", content, "image/png")}
        response = client.post("/api/upload/storybook", files=files)
        assert response.status_code == 200

        data = response.json()
        assert "file_path" in data

        filename = data["file_path"].rstrip("/").split("/")[-1]
        file_path = os.path.join(uploads.STORYBOOK_PATH, filename)
        assert os.path.exists(file_path)
    finally:
        app.dependency_overrides = {}
