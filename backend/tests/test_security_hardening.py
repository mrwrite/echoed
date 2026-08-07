import uuid

from fastapi import Request
from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.database import get_db
from app.deps import get_db as deps_get_db
from app.enum import OrganizationRole, OrganizationType
from app.main import app
from app.models import Course, Organization, OrganizationMembership, StudentCourse, StudentUnitProgress, Unit, User
from app.rate_limit import FixedWindowRateLimiter, direct_peer_key, get_policy, limiter


def _user(role: str, prefix: str) -> User:
    suffix = uuid.uuid4().hex[:8]
    return User(
        id=uuid.uuid4(), firstname=prefix.title(), lastname="Security",
        username=f"{prefix}_{suffix}", email=f"{prefix}_{suffix}@example.test",
        hashed_password="not-a-public-field", role=role,
    )


def _client(db_session, actor: User | None = None) -> TestClient:
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[deps_get_db] = lambda: db_session
    if actor is not None:
        app.dependency_overrides[get_current_user] = lambda: actor
    return TestClient(app)


def _clear() -> None:
    app.dependency_overrides.clear()
    limiter.clear()


def test_admin_user_responses_are_explicit_and_minimized(db_session):
    admin = _user("admin", "admin")
    student = _user("student", "student")
    db_session.add_all([admin, student])
    db_session.commit()
    client = _client(db_session, admin)
    try:
        response = client.get("/api/users")
    finally:
        _clear()

    assert response.status_code == 200
    assert set(response.json()[0]) == {"id", "firstname", "lastname", "username", "email", "role", "created_at"}
    assert all("hashed_password" not in item and "updated_at" not in item for item in response.json())


def test_user_role_update_rejects_mass_assignment_and_platform_grant(db_session):
    admin = _user("admin", "admin")
    student = _user("student", "student")
    db_session.add_all([admin, student])
    db_session.commit()
    client = _client(db_session, admin)
    try:
        mass = client.put(
            f"/api/users/{student.id}",
            json={"role": "teacher", "hashed_password": "replace-me"},
        )
        escalation = client.put(f"/api/users/{student.id}", json={"role": "super_admin"})
    finally:
        _clear()

    db_session.refresh(student)
    assert mass.status_code == 422
    assert escalation.status_code == 403
    assert student.role == "student"
    assert student.hashed_password == "not-a-public-field"


def test_administrator_cannot_change_or_delete_self(db_session):
    admin = _user("admin", "admin")
    db_session.add(admin)
    db_session.commit()
    client = _client(db_session, admin)
    try:
        role_response = client.put(f"/api/users/{admin.id}", json={"role": "student"})
        delete_response = client.delete(f"/api/users/{admin.id}")
    finally:
        _clear()

    assert role_response.status_code == 409
    assert delete_response.status_code == 409
    assert db_session.query(User).filter(User.id == admin.id).first() is not None


def test_final_super_admin_cannot_be_demoted_or_deleted(db_session):
    actor = _user("super_admin", "external_super")
    final_admin = _user("super_admin", "final_super")
    db_session.add(final_admin)
    db_session.commit()
    client = _client(db_session, actor)
    try:
        demote = client.put(f"/api/users/{final_admin.id}", json={"role": "admin"})
        delete = client.delete(f"/api/users/{final_admin.id}")
    finally:
        _clear()

    db_session.refresh(final_admin)
    assert demote.status_code == 409
    assert delete.status_code == 409
    assert final_admin.role == "super_admin"


def test_super_admin_can_remove_another_when_multiple_remain(db_session):
    actor = _user("super_admin", "actor_super")
    target = _user("super_admin", "target_super")
    db_session.add_all([actor, target])
    db_session.commit()
    client = _client(db_session, actor)
    try:
        response = client.put(f"/api/users/{target.id}", json={"role": "admin"})
    finally:
        _clear()

    db_session.refresh(target)
    assert response.status_code == 200
    assert target.role == "admin"


def test_registration_ignores_requested_privileged_role(db_session):
    client = _client(db_session)
    suffix = uuid.uuid4().hex[:8]
    try:
        response = client.post(
            "/api/auth/register",
            json={
                "firstname": "Public", "lastname": "Registrant",
                "username": f"register_{suffix}", "email": f"register_{suffix}@example.test",
                "password": "secret", "role": "super_admin",
            },
        )
    finally:
        _clear()

    created = db_session.query(User).filter(User.username == f"register_{suffix}").one()
    assert response.status_code == 200
    assert created.role == "student"


def test_invite_response_omits_token_and_org_admin_cannot_grant_super_admin(db_session):
    admin = _user("admin", "org_admin")
    organization = Organization(id=uuid.uuid4(), name="Safe Org", type=OrganizationType.SCHOOL)
    db_session.add_all([admin, organization])
    db_session.flush()
    db_session.add(
        OrganizationMembership(
            id=uuid.uuid4(), organization_id=organization.id, user_id=admin.id,
            role=OrganizationRole.ORG_ADMIN,
        )
    )
    db_session.commit()
    client = _client(db_session, admin)
    headers = {"X-Org-Id": str(organization.id)}
    try:
        allowed = client.post(
            f"/api/orgs/{organization.id}/invites", headers=headers,
            json={"email": "teacher@example.test", "role": "teacher"},
        )
        denied = client.post(
            f"/api/orgs/{organization.id}/invites", headers=headers,
            json={"email": "super@example.test", "role": "super_admin"},
        )
    finally:
        _clear()

    assert allowed.status_code == 200, allowed.text
    assert "token" in allowed.json()
    listed = _client(db_session, admin).get(
        f"/api/orgs/{organization.id}/invites", headers=headers
    )
    _clear()
    assert "token" not in listed.json()[0]
    assert denied.status_code == 403


def test_fixed_window_rate_limiter_has_independent_keys_and_resets(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_AUTH_LOGIN_LIMIT", "2")
    monkeypatch.setenv("RATE_LIMIT_AUTH_LOGIN_WINDOW_SECONDS", "10")
    test_limiter = FixedWindowRateLimiter()

    assert test_limiter.check("auth_login", "a", now=100) is None
    assert test_limiter.check("auth_login", "a", now=101) is None
    assert test_limiter.check("auth_login", "b", now=102) is None
    assert test_limiter.check("auth_login", "a", now=102) == 8
    assert test_limiter.check("auth_login", "a", now=110) is None


def test_rate_limit_proxy_key_ignores_untrusted_forwarded_header():
    request = Request({
        "type": "http", "method": "GET", "path": "/", "query_string": b"",
        "headers": [(b"x-forwarded-for", b"203.0.113.10")],
        "client": ("127.0.0.9", 12345), "server": ("test", 80), "scheme": "http",
    })
    assert direct_peer_key(request) == "127.0.0.9"


def test_rate_limit_configuration_rejects_non_positive_values(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_AUTH_LOGIN_LIMIT", "0")
    try:
        get_policy("auth_login")
        raised = False
    except RuntimeError:
        raised = True
    assert raised is True


def test_authentication_rate_limit_returns_429_and_retry_after(db_session, monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_AUTH_LOGIN_LIMIT", "1")
    monkeypatch.setenv("RATE_LIMIT_AUTH_LOGIN_WINDOW_SECONDS", "60")
    client = _client(db_session)
    try:
        first = client.post("/api/auth/token", data={"username": "missing", "password": "bad"})
        limited = client.post("/api/auth/token", data={"username": "missing", "password": "bad"})
    finally:
        _clear()

    assert first.status_code == 401
    assert limited.status_code == 429
    assert int(limited.headers["Retry-After"]) >= 1
    assert limited.json()["detail"] == "Too many requests. Please try again later."


def test_inactive_membership_cannot_switch_organization(db_session):
    from app.enum import MembershipStatus
    user = _user("teacher", "inactive")
    organization = Organization(id=uuid.uuid4(), name="Inactive Org", type=OrganizationType.SCHOOL)
    db_session.add_all([user, organization])
    db_session.flush()
    db_session.add(
        OrganizationMembership(
            id=uuid.uuid4(), organization_id=organization.id, user_id=user.id,
            role=OrganizationRole.TEACHER, status=MembershipStatus.INACTIVE,
        )
    )
    db_session.commit()
    client = _client(db_session, user)
    try:
        response = client.post(f"/api/orgs/{organization.id}/switch")
    finally:
        _clear()

    assert response.status_code == 404


def test_sensitive_user_mutation_rate_limit_returns_429(db_session, monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_USER_MANAGEMENT_LIMIT", "1")
    monkeypatch.setenv("RATE_LIMIT_USER_MANAGEMENT_WINDOW_SECONDS", "60")
    actor = _user("super_admin", "rate_super")
    first_target = _user("student", "rate_first")
    second_target = _user("student", "rate_second")
    db_session.add_all([actor, first_target, second_target])
    db_session.commit()
    client = _client(db_session, actor)
    try:
        first = client.put(f"/api/users/{first_target.id}", json={"role": "teacher"})
        limited = client.put(f"/api/users/{second_target.id}", json={"role": "teacher"})
    finally:
        _clear()

    assert first.status_code == 200
    assert limited.status_code == 429


def test_learner_cannot_read_another_learners_progress_by_direct_id(db_session):
    learner_a = _user("student", "learner_a")
    learner_b = _user("student", "learner_b")
    course = Course(id=uuid.uuid4(), title="Protected Course", description="Scope")
    unit = Unit(id=uuid.uuid4(), course_id=course.id, title="Protected Unit")
    db_session.add_all([learner_a, learner_b, course, unit])
    db_session.flush()
    enrollment = StudentCourse(id=uuid.uuid4(), student_id=learner_b.id, course_id=course.id)
    db_session.add(enrollment)
    db_session.flush()
    progress = StudentUnitProgress(
        id=uuid.uuid4(), student_course_id=enrollment.id, unit_id=unit.id,
    )
    db_session.add(progress)
    db_session.commit()
    client = _client(db_session, learner_a)
    try:
        response = client.get(f"/api/progress/segment?student_unit_id={progress.id}")
    finally:
        _clear()

    assert response.status_code == 404


def test_upload_signature_traversal_authorization_and_limit(db_session, tmp_path, monkeypatch):
    from app.api.routes import uploads

    admin = _user("admin", "upload_admin")
    student = _user("student", "upload_student")
    db_session.add_all([admin, student])
    db_session.commit()
    destination = tmp_path / "badges"
    destination.mkdir()
    monkeypatch.setattr(uploads, "BADGES_PATH", str(destination))
    valid_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR\x00\x00\x00\x01\x00\x00\x00\x01"

    student_client = _client(db_session, student)
    unauthorized = student_client.post(
        "/api/upload/badge", files={"file": ("badge.png", valid_png, "image/png")}
    )
    _clear()

    admin_client = _client(db_session, admin)
    mismatch = admin_client.post(
        "/api/upload/badge", files={"file": ("badge.png", b"not-png", "image/png")}
    )
    traversal = admin_client.post(
        "/api/upload/badge", files={"file": ("../../badge.png", valid_png, "image/png")}
    )
    _clear()

    assert unauthorized.status_code == 403
    assert mismatch.status_code == 415
    assert traversal.status_code == 200
    stored = list(destination.iterdir())
    assert len(stored) == 1
    assert stored[0].parent == destination
    assert ".." not in stored[0].name


def test_upload_rate_limit_is_per_authenticated_user(db_session, tmp_path, monkeypatch):
    from app.api.routes import uploads

    monkeypatch.setenv("RATE_LIMIT_UPLOAD_LIMIT", "1")
    monkeypatch.setenv("RATE_LIMIT_UPLOAD_WINDOW_SECONDS", "60")
    first_admin = _user("admin", "first_upload")
    second_admin = _user("admin", "second_upload")
    db_session.add_all([first_admin, second_admin])
    db_session.commit()
    destination = tmp_path / "badges"
    destination.mkdir()
    monkeypatch.setattr(uploads, "BADGES_PATH", str(destination))
    image = b"\x89PNG\r\n\x1a\n\x00\x00\x00\x0dIHDR\x00\x00\x00\x01\x00\x00\x00\x01"

    first_client = _client(db_session, first_admin)
    first = first_client.post("/api/upload/badge", files={"file": ("one.png", image, "image/png")})
    limited = first_client.post("/api/upload/badge", files={"file": ("two.png", image, "image/png")})
    _clear()
    second_client = _client(db_session, second_admin)
    independent = second_client.post("/api/upload/badge", files={"file": ("three.png", image, "image/png")})
    _clear()

    assert first.status_code == 200
    assert limited.status_code == 429
    assert "Retry-After" in limited.headers
    assert independent.status_code == 200


def test_content_administrator_cannot_mutate_another_organizations_unit(db_session):
    actor = _user("content_admin", "content_admin")
    organization_a = Organization(id=uuid.uuid4(), name="Org A", type=OrganizationType.SCHOOL)
    organization_b = Organization(id=uuid.uuid4(), name="Org B", type=OrganizationType.SCHOOL)
    course_b = Course(
        id=uuid.uuid4(), organization_id=organization_b.id,
        title="Org B Course", description="Protected",
    )
    unit_b = Unit(id=uuid.uuid4(), course_id=course_b.id, title="Org B Unit")
    db_session.add_all([actor, organization_a, organization_b, course_b, unit_b])
    db_session.flush()
    db_session.add(
        OrganizationMembership(
            id=uuid.uuid4(), organization_id=organization_a.id, user_id=actor.id,
            role=OrganizationRole.CONTENT_ADMIN,
        )
    )
    db_session.commit()
    client = _client(db_session, actor)
    try:
        response = client.put(
            f"/api/units/{unit_b.id}",
            json={
                "course_id": str(course_b.id), "title": "Stolen",
                "content": None, "order": 1,
            },
        )
    finally:
        _clear()

    db_session.refresh(unit_b)
    assert response.status_code == 403
    assert unit_b.title == "Org B Unit"
