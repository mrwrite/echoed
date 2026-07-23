import uuid

from fastapi.testclient import TestClient

from app.api.routes import uploads
from app.deps import get_current_user, require_org_roles
from app.enum import MembershipStatus, OrganizationRole, OrganizationType
from app.main import app
from app.models import Organization, OrganizationMembership, User


client = TestClient(app)


def _user(db_session, role: str = "admin") -> User:
    user = User(
        id=uuid.uuid4(),
        firstname="Platform",
        lastname="Tester",
        username=f"platform_{uuid.uuid4().hex}",
        email=f"platform_{uuid.uuid4().hex}@example.com",
        hashed_password="fake",
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_protected_auth_route_requires_a_token():
    response = client.get("/api/auth/protected")

    assert response.status_code == 401


def test_health_and_security_headers_are_available():
    response = client.get("/health/live", headers={"X-Request-ID": "phase-7-check"})

    assert response.status_code == 200
    assert response.json() == {"status": "live"}
    assert response.headers["x-request-id"] == "phase-7-check"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"


def test_upload_rejects_mismatched_content_type(db_session, tmp_path, monkeypatch):
    admin_user = _user(db_session)
    badge_path = tmp_path / "badges"
    badge_path.mkdir()
    monkeypatch.setattr(uploads, "BADGES_PATH", str(badge_path))
    app.dependency_overrides[get_current_user] = lambda: admin_user

    try:
        response = client.post(
            "/api/upload/badge",
            files={"file": ("badge.png", b"not an image", "text/plain")},
        )
    finally:
        app.dependency_overrides = {}

    assert response.status_code == 415
    assert list(badge_path.iterdir()) == []


def test_upload_rejects_files_over_limit(db_session, tmp_path, monkeypatch):
    admin_user = _user(db_session)
    badge_path = tmp_path / "badges"
    badge_path.mkdir()
    monkeypatch.setattr(uploads, "BADGES_PATH", str(badge_path))
    app.dependency_overrides[get_current_user] = lambda: admin_user

    try:
        response = client.post(
            "/api/upload/badge",
            files={
                "file": (
                    "badge.png",
                    b"\x89PNG\r\n\x1a\n" + b"x" * uploads.MAX_IMAGE_UPLOAD_BYTES,
                    "image/png",
                )
            },
        )
    finally:
        app.dependency_overrides = {}

    assert response.status_code == 413
    assert list(badge_path.iterdir()) == []


def test_inactive_organization_membership_cannot_authorize(db_session):
    user = _user(db_session, role="teacher")
    organization = Organization(
        id=uuid.uuid4(),
        name="Inactive Membership School",
        type=OrganizationType.SCHOOL,
    )
    db_session.add(organization)
    db_session.flush()
    db_session.add(
        OrganizationMembership(
            id=uuid.uuid4(),
            organization_id=organization.id,
            user_id=user.id,
            role=OrganizationRole.TEACHER,
            status=MembershipStatus.INACTIVE,
        )
    )
    db_session.commit()

    checker = require_org_roles("teacher")
    try:
        checker(active_org_id=organization.id, current_user=user, db=db_session)
        denied = False
    except Exception as exc:
        denied = getattr(exc, "status_code", None) == 403

    assert denied is True
