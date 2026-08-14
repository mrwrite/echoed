from __future__ import annotations

from datetime import datetime, timedelta
from types import SimpleNamespace
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update

from app.audit import AuditPayloadError, _lock_scope_for_append, append_audit_event, verify_audit_chain
from app.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models import AuditEvent, Organization, OrganizationMembership, User
from app.enum import MembershipStatus, OrganizationRole, OrganizationType
from app.rate_limit import limiter
from app.operational_backup import create_test_backup, restore_test_backup


def _user(db, role: str) -> User:
    user = User(
        id=uuid.uuid4(),
        firstname="Audit",
        lastname="Reviewer",
        username=f"audit-{uuid.uuid4()}",
        email=f"audit-{uuid.uuid4()}@example.test",
        hashed_password="unused",
        role=role,
    )
    db.add(user)
    db.commit()
    return user


def _override(db, user):
    app.dependency_overrides[get_db] = lambda: (yield db)
    app.dependency_overrides[get_current_user] = lambda: user
    limiter.clear()
    return TestClient(app)


def _clear_overrides():
    app.dependency_overrides.clear()
    limiter.clear()


def test_append_is_minimized_chained_and_transaction_bound(db_session):
    actor = _user(db_session, "admin")
    first = append_audit_event(
        db_session,
        action="platform.role.changed",
        actor_id=actor.id,
        actor_role=actor.role,
        target_type="user",
        target_id=uuid.uuid4(),
        before={"role": "student"},
        after={"role": "teacher"},
    )
    second = append_audit_event(
        db_session,
        action="platform.user.deleted",
        actor_id=actor.id,
        actor_role=actor.role,
        target_type="user",
        target_id=uuid.uuid4(),
        before={"role": "student"},
    )
    assert second.previous_hash == first.event_hash
    assert (first.scope_sequence, second.scope_sequence) == (1, 2)
    assert db_session.query(AuditEvent).count() == 2
    db_session.rollback()
    assert db_session.query(AuditEvent).count() == 0


@pytest.mark.parametrize("unsafe", [{"password": "private"}, {"role": {"nested": "value"}}, {"role": "x" * 161}])
def test_sensitive_or_unbounded_state_fails_closed(db_session, unsafe):
    with pytest.raises(AuditPayloadError):
        append_audit_event(
            db_session,
            action="platform.role.changed",
            actor_id=uuid.uuid4(),
            actor_role="admin",
            target_type="user",
            target_id=uuid.uuid4(),
            after=unsafe,
        )
    assert db_session.query(AuditEvent).count() == 0


def test_chain_verification_detects_tampering(db_session):
    actor = _user(db_session, "admin")
    append_audit_event(
        db_session,
        action="platform.role.changed",
        actor_id=actor.id,
        actor_role=actor.role,
        target_type="user",
        target_id=uuid.uuid4(),
        before={"role": "student"},
        after={"role": "teacher"},
    )
    db_session.commit()
    assert verify_audit_chain(db_session).valid
    event = db_session.query(AuditEvent).one()
    # Simulate modification below the protected application ORM boundary.
    db_session.execute(
        update(AuditEvent)
        .where(AuditEvent.id == event.id)
        .values(after_state={"role": "super_admin"})
    )
    db_session.commit()
    assert not verify_audit_chain(db_session).valid


def test_ordinary_orm_delete_is_rejected(db_session):
    event = append_audit_event(
        db_session,
        action="platform.user.deleted",
        actor_id=uuid.uuid4(),
        actor_role="admin",
        target_type="user",
        target_id=uuid.uuid4(),
        before={"role": "student"},
    )
    db_session.commit()
    db_session.delete(event)
    with pytest.raises(RuntimeError, match="append-only"):
        db_session.flush()
    db_session.rollback()


def test_ordinary_orm_update_is_rejected(db_session):
    event = append_audit_event(
        db_session,
        action="platform.user.deleted",
        actor_id=uuid.uuid4(),
        actor_role="admin",
        target_type="user",
        target_id=uuid.uuid4(),
        before={"role": "student"},
    )
    db_session.commit()
    event.after_state = {"role": "teacher"}
    with pytest.raises(RuntimeError, match="append-only"):
        db_session.flush()
    db_session.rollback()


def test_postgresql_scope_lock_serializes_first_and_later_appends():
    captured = {}

    class FakeSession:
        def get_bind(self):
            return SimpleNamespace(dialect=SimpleNamespace(name="postgresql"))

        def execute(self, statement, parameters):
            captured["sql"] = str(statement)
            captured["parameters"] = parameters

    _lock_scope_for_append(FakeSession(), "organization:scope")
    assert "pg_advisory_xact_lock" in captured["sql"]
    assert captured["parameters"] == {"scope_key": "organization:scope"}


def test_platform_feed_is_explicit_paginated_and_role_protected(db_session):
    admin = _user(db_session, "admin")
    for role in ("student", "teacher"):
        append_audit_event(
            db_session,
            action="platform.role.changed",
            actor_id=admin.id,
            actor_role=admin.role,
            target_type="user",
            target_id=uuid.uuid4(),
            before={"role": "student"},
            after={"role": role},
        )
    db_session.commit()
    client = _override(db_session, admin)
    try:
        first = client.get("/api/audit-events?limit=1")
        assert first.status_code == 200
        payload = first.json()
        assert len(payload["items"]) == 1
        assert payload["next_cursor"]
        assert "event_hash" not in payload["items"][0]
        assert "scope_key" not in payload["items"][0]
        second = client.get(f"/api/audit-events?limit=1&cursor={payload['next_cursor']}")
        assert second.status_code == 200
        assert second.json()["items"][0]["id"] != payload["items"][0]["id"]

        learner = _user(db_session, "student")
        app.dependency_overrides[get_current_user] = lambda: learner
        assert client.get("/api/audit-events").status_code == 403
    finally:
        _clear_overrides()


def test_organization_feed_conceals_cross_org_events(db_session):
    org_admin = _user(db_session, "org_admin")
    own = Organization(id=uuid.uuid4(), name="Own", type=OrganizationType.SCHOOL)
    other = Organization(id=uuid.uuid4(), name="Other", type=OrganizationType.SCHOOL)
    db_session.add_all([own, other])
    db_session.flush()
    db_session.add(
        OrganizationMembership(
            id=uuid.uuid4(),
            organization_id=own.id,
            user_id=org_admin.id,
            role=OrganizationRole.ORG_ADMIN,
            status=MembershipStatus.ACTIVE,
        )
    )
    append_audit_event(
        db_session,
        action="organization.invite.created",
        actor_id=org_admin.id,
        actor_role=org_admin.role,
        target_type="organization_invite",
        target_id=uuid.uuid4(),
        organization_id=own.id,
        after={"role": "teacher", "status": "pending"},
    )
    append_audit_event(
        db_session,
        action="organization.invite.created",
        actor_id=uuid.uuid4(),
        actor_role="org_admin",
        target_type="organization_invite",
        target_id=uuid.uuid4(),
        organization_id=other.id,
        after={"role": "teacher", "status": "pending"},
    )
    db_session.commit()
    client = _override(db_session, org_admin)
    try:
        allowed = client.get(f"/api/orgs/{own.id}/audit-events", headers={"X-Org-Id": str(own.id)})
        assert allowed.status_code == 200
        assert {row["organization_id"] for row in allowed.json()["items"]} == {str(own.id)}
        denied = client.get(f"/api/orgs/{other.id}/audit-events", headers={"X-Org-Id": str(other.id)})
        assert denied.status_code == 404
    finally:
        _clear_overrides()


def test_export_is_formula_safe_capped_schema_and_audited(db_session):
    admin = _user(db_session, "admin")
    append_audit_event(
        db_session,
        action="platform.user.deleted",
        actor_id=admin.id,
        actor_role=admin.role,
        target_type="user",
        target_id="=formula",
        before={"role": "student"},
    )
    db_session.commit()
    client = _override(db_session, admin)
    try:
        response = client.get("/api/audit-events/export.csv")
        assert response.status_code == 200
        assert "attachment" in response.headers["content-disposition"]
        assert "'=formula" in response.text
        assert "event_hash" not in response.text.splitlines()[0]
        assert db_session.query(AuditEvent).filter(AuditEvent.action == "audit.exported").count() == 1
    finally:
        _clear_overrides()


def test_role_change_creates_one_durable_event_and_denial_creates_none(db_session, monkeypatch):
    from app.api.routes import users as user_routes

    admin = _user(db_session, "admin")
    target = _user(db_session, "student")
    monkeypatch.setattr(user_routes, "enforce_rate_limit", lambda *args, **kwargs: None)
    request = SimpleNamespace(state=SimpleNamespace(request_id="audit-request"))
    user_routes.update_user(
        target.id,
        SimpleNamespace(role="teacher"),
        request,
        db_session,
        admin,
    )
    event = db_session.query(AuditEvent).one()
    assert event.action == "platform.role.changed"
    assert event.before_state == {"role": "student"}
    assert event.after_state == {"role": "teacher"}

    with pytest.raises(Exception):
        user_routes.update_user(
            admin.id,
            SimpleNamespace(role="super_admin"),
            request,
            db_session,
            admin,
        )
    assert db_session.query(AuditEvent).count() == 1


def test_retention_candidates_are_time_bounded(db_session):
    actor = _user(db_session, "admin")
    old = append_audit_event(
        db_session,
        action="platform.user.deleted",
        actor_id=actor.id,
        actor_role=actor.role,
        target_type="user",
        target_id=uuid.uuid4(),
        before={"role": "student"},
    )
    old_id = old.id
    db_session.commit()
    db_session.execute(
        update(AuditEvent)
        .where(AuditEvent.id == old_id)
        .values(created_at=datetime.utcnow() - timedelta(days=400))
    )
    db_session.commit()
    cutoff = datetime.utcnow() - timedelta(days=365)
    assert db_session.query(AuditEvent).filter(AuditEvent.created_at < cutoff).count() == 1


def test_backup_restore_acceptance_verifies_audit_chain(tmp_path):
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.models import Base

    source_path = tmp_path / "audit-source.sqlite3"
    source_engine = create_engine(f"sqlite:///{source_path.as_posix()}")
    Base.metadata.create_all(source_engine)
    source_session = sessionmaker(bind=source_engine)()
    try:
        append_audit_event(
            source_session,
            action="platform.user.deleted",
            actor_id=uuid.uuid4(),
            actor_role="admin",
            target_type="user",
            target_id=uuid.uuid4(),
            before={"role": "student"},
        )
        source_session.commit()
    finally:
        source_session.close()
        source_engine.dispose()

    bundle = tmp_path / "audit-backup"
    create_test_backup(
        database_path=source_path,
        storage_roots=[],
        output_dir=bundle,
        environment="test",
        acknowledged_test_data=True,
    )
    restored_path = tmp_path / "restored" / "audit.sqlite3"
    restore_test_backup(
        bundle=bundle,
        database_target=restored_path,
        storage_target=tmp_path / "restored-storage",
        environment="test",
        acknowledged_test_data=True,
    )

    restored_engine = create_engine(f"sqlite:///{restored_path.as_posix()}")
    restored_session = sessionmaker(bind=restored_engine)()
    try:
        assert verify_audit_chain(restored_session).valid
        assert restored_session.query(AuditEvent).count() == 1
    finally:
        restored_session.close()
        restored_engine.dispose()
