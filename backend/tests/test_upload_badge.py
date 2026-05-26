import os
import uuid

from fastapi.testclient import TestClient

from app.api.routes import uploads
from app.deps import get_current_user
from app.main import app
from app.models import User

client = TestClient(app)


def test_upload_badge_image(db_session, tmp_path, monkeypatch):
    admin_user = User(
        id=uuid.uuid4(),
        firstname="Badge",
        lastname="Uploader",
        username=f"badge_{uuid.uuid4().hex[:8]}",
        email=f"badge_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="fake",
        role="admin",
    )
    db_session.add(admin_user)
    db_session.commit()

    badges_path = tmp_path / "badges"
    badges_path.mkdir()
    monkeypatch.setattr(uploads, "BADGES_PATH", str(badges_path))
    app.dependency_overrides[get_current_user] = lambda: admin_user

    try:
        content = b"\x89PNG\r\n\x1a\n"
        files = {"file": ("badge.png", content, "image/png")}
        response = client.post("/api/upload/badge", files=files)
        assert response.status_code == 200

        data = response.json()
        assert "file_path" in data

        filename = data["file_path"].rstrip("/").split("/")[-1]
        file_path = os.path.join(uploads.BADGES_PATH, filename)
        assert os.path.exists(file_path)
    finally:
        app.dependency_overrides = {}
