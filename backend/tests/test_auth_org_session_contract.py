from datetime import datetime, timedelta, timezone
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

from app.api.routes import auth as auth_routes
from app.api.routes import orgs as org_routes
from app.auth import SECRET_KEY, ALGORITHM, hash_password
from app.database import get_db as route_get_db
from app.auth import get_db as auth_get_db
from app.enum import MembershipStatus, OrganizationRole, OrganizationType
from app.models import Organization, OrganizationMembership, User


def build_client(db_session):
    app = FastAPI()
    app.include_router(auth_routes.router, prefix="/api")
    app.include_router(org_routes.router, prefix="/api")

    def override_get_db():
        yield db_session

    app.dependency_overrides[route_get_db] = override_get_db
    app.dependency_overrides[auth_get_db] = override_get_db
    return TestClient(app)


def create_user(db_session, username: str, password: str = "secret", role: str = "teacher") -> User:
    suffix = uuid.uuid4().hex[:8]
    user = User(
        id=uuid.uuid4(),
        firstname="Test",
        lastname="User",
        username=f"{username}_{suffix}",
        email=f"{username}_{suffix}@example.com",
        hashed_password=hash_password(password),
        role=role,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def create_org(
    db_session,
    name: str,
    org_type: OrganizationType,
    created_at: datetime,
) -> Organization:
    org = Organization(
        id=uuid.uuid4(),
        name=name,
        type=org_type,
        created_at=created_at,
    )
    db_session.add(org)
    db_session.commit()
    db_session.refresh(org)
    return org


def create_membership(
    db_session,
    user: User,
    org: Organization,
    role: OrganizationRole,
    status: MembershipStatus = MembershipStatus.ACTIVE,
) -> OrganizationMembership:
    membership = OrganizationMembership(
        id=uuid.uuid4(),
        user_id=user.id,
        organization_id=org.id,
        role=role,
        status=status,
    )
    db_session.add(membership)
    db_session.commit()
    db_session.refresh(membership)
    return membership


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def test_single_org_login_returns_authoritative_active_org_context(db_session):
    client = build_client(db_session)
    user = create_user(db_session, "single_org")
    org = create_org(
        db_session,
        "Single Org Academy",
        OrganizationType.SCHOOL,
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    create_membership(db_session, user, org, OrganizationRole.TEACHER)

    response = client.post(
        "/api/auth/token",
        data={"username": user.username, "password": "secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["active_org_id"] == str(org.id)
    assert payload["active_org_role"] == OrganizationRole.TEACHER.value
    assert payload["active_organization"] == {
        "id": str(org.id),
        "name": "Single Org Academy",
        "type": OrganizationType.SCHOOL.value,
        "role": OrganizationRole.TEACHER.value,
    }
    assert payload["organizations"] == [
        {"id": str(org.id), "role": OrganizationRole.TEACHER.value}
    ]

    token_payload = decode_access_token(payload["access_token"])
    assert token_payload["active_org_id"] == str(org.id)


def test_multi_org_login_uses_deterministic_non_personal_order(db_session):
    client = build_client(db_session)
    user = create_user(db_session, "multi_org")
    later_org = create_org(
        db_session,
        "Later School",
        OrganizationType.SCHOOL,
        datetime(2026, 2, 1, tzinfo=timezone.utc),
    )
    earlier_org = create_org(
        db_session,
        "Earlier School",
        OrganizationType.SCHOOL,
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    create_membership(db_session, user, later_org, OrganizationRole.CONTENT_ADMIN)
    create_membership(db_session, user, earlier_org, OrganizationRole.TEACHER)

    response = client.post(
        "/api/auth/token",
        data={"username": user.username, "password": "secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_org_id"] == str(earlier_org.id)
    assert payload["active_org_role"] == OrganizationRole.TEACHER.value
    assert payload["active_organization"]["id"] == str(earlier_org.id)
    assert payload["active_organization"]["role"] == OrganizationRole.TEACHER.value


def test_login_prefers_institutional_org_over_personal_org(db_session):
    client = build_client(db_session)
    user = create_user(db_session, "personal_and_school")
    personal_org = create_org(
        db_session,
        "Personal Workspace",
        OrganizationType.PERSONAL,
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    school_org = create_org(
        db_session,
        "Institutional School",
        OrganizationType.SCHOOL,
        datetime(2026, 2, 1, tzinfo=timezone.utc),
    )
    create_membership(db_session, user, personal_org, OrganizationRole.ORG_ADMIN)
    create_membership(db_session, user, school_org, OrganizationRole.TEACHER)

    response = client.post(
        "/api/auth/token",
        data={"username": user.username, "password": "secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["active_org_id"] == str(school_org.id)
    assert payload["active_org_role"] == OrganizationRole.TEACHER.value
    assert payload["active_organization"]["type"] == OrganizationType.SCHOOL.value


def test_no_org_login_preserves_compatible_null_active_org_fields(db_session):
    client = build_client(db_session)
    user = create_user(db_session, "no_org")

    response = client.post(
        "/api/auth/token",
        data={"username": user.username, "password": "secret"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["organizations"] == []
    assert payload["active_org_id"] is None
    assert payload["active_org_role"] is None
    assert payload["active_organization"] is None

    token_payload = decode_access_token(payload["access_token"])
    assert token_payload["active_org_id"] is None


def test_org_switch_returns_authoritative_active_org_context(db_session):
    client = build_client(db_session)
    user = create_user(db_session, "switch_org")
    school_org = create_org(
        db_session,
        "Switch School",
        OrganizationType.SCHOOL,
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    personal_org = create_org(
        db_session,
        "Switch Personal",
        OrganizationType.PERSONAL,
        datetime(2026, 2, 1, tzinfo=timezone.utc),
    )
    create_membership(db_session, user, school_org, OrganizationRole.TEACHER)
    create_membership(db_session, user, personal_org, OrganizationRole.ORG_ADMIN)

    login_response = client.post(
        "/api/auth/token",
        data={"username": user.username, "password": "secret"},
    )
    login_payload = login_response.json()

    switch_response = client.post(
        f"/api/orgs/{personal_org.id}/switch",
        headers={"Authorization": f"Bearer {login_payload['access_token']}"},
    )

    assert switch_response.status_code == 200
    payload = switch_response.json()
    assert payload["token_type"] == "bearer"
    assert payload["active_org_id"] == str(personal_org.id)
    assert payload["active_org_role"] == OrganizationRole.ORG_ADMIN.value
    assert payload["active_organization"] == {
        "id": str(personal_org.id),
        "name": "Switch Personal",
        "type": OrganizationType.PERSONAL.value,
        "role": OrganizationRole.ORG_ADMIN.value,
    }

    token_payload = decode_access_token(payload["access_token"])
    assert token_payload["active_org_id"] == str(personal_org.id)


def test_org_switch_failure_for_non_member_preserves_endpoint_contract(db_session):
    client = build_client(db_session)
    user = create_user(db_session, "switch_failure")
    member_org = create_org(
        db_session,
        "Member Org",
        OrganizationType.SCHOOL,
        datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    outsider_org = create_org(
        db_session,
        "Outsider Org",
        OrganizationType.SCHOOL,
        datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    create_membership(db_session, user, member_org, OrganizationRole.TEACHER)

    login_response = client.post(
        "/api/auth/token",
        data={"username": user.username, "password": "secret"},
    )
    login_payload = login_response.json()

    switch_response = client.post(
        f"/api/orgs/{outsider_org.id}/switch",
        headers={"Authorization": f"Bearer {login_payload['access_token']}"},
    )

    assert switch_response.status_code == 404
    assert switch_response.json()["detail"] == "Organization not found"
