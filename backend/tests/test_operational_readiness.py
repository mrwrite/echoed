from __future__ import annotations

import json
from pathlib import Path
import sqlite3

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import pytest

from app.network_trust import resolve_network_context
from app.operational_backup import BackupSafetyError, create_test_backup, restore_test_backup, verify_backup
from app.operational_config import OperationalConfigurationError, load_operational_settings


def production_environment(tmp_path: Path) -> dict[str, str]:
    return {
        "APP_ENV": "production",
        "DATABASE_URL": "postgresql://echoed:nondefault-credential@database.internal/echoed",
        "JWT_SECRET": "a-production-secret-with-at-least-32-characters",
        "ALLOWED_HOSTS": "learn.example.edu,api.example.edu",
        "FRONTEND_URL": "https://learn.example.edu",
        "EXTERNAL_BASE_URL": "https://api.example.edu",
        "TRUST_PROXY_HEADERS": "true",
        "TRUSTED_PROXY_IPS": "10.20.0.0/16,2001:db8::1",
        "STORYBOOK_PATH": str(tmp_path / "storybook"),
        "COLORINGS_PATH": str(tmp_path / "colorings"),
        "BADGES_PATH": str(tmp_path / "badges"),
        "PERSISTENT_STORAGE_ACKNOWLEDGED": "true",
        "AUTO_MIGRATE_ON_STARTUP": "false",
        "RELEASE_VERSION": "sha-0123456789ab",
        "DEPLOYMENT_ID": "production-us-test-1",
        "LOG_FORMAT": "json",
        "METRICS_ENABLED": "true",
        "REQUEST_LOGGING_ENABLED": "true",
        "METRICS_ENDPOINT_ENABLED": "false",
    }


def test_valid_production_configuration_is_explicit(tmp_path):
    settings = load_operational_settings(production_environment(tmp_path))
    assert settings.environment == "production"
    assert settings.allowed_hosts == ("learn.example.edu", "api.example.edu")
    assert not settings.auto_migrate_on_startup


@pytest.mark.parametrize(
    ("name", "value", "expected_category"),
    [
        ("JWT_SECRET", "changeme", "JWT_SECRET"),
        ("DATABASE_URL", "sqlite:///production.db", "DATABASE_URL"),
        ("ALLOWED_HOSTS", "*", "ALLOWED_HOSTS"),
        ("FRONTEND_URL", "http://learn.example.edu", "FRONTEND_URL"),
        ("TRUSTED_PROXY_IPS", "not-a-network", "TRUSTED_PROXY_IPS"),
        ("AUTO_MIGRATE_ON_STARTUP", "true", "AUTO_MIGRATE_ON_STARTUP"),
        ("PERSISTENT_STORAGE_ACKNOWLEDGED", "false", "PERSISTENT_STORAGE_ACKNOWLEDGED"),
        ("LOG_FORMAT", "developer", "LOG_FORMAT"),
    ],
)
def test_unsafe_production_configuration_fails_closed(tmp_path, name, value, expected_category):
    values = production_environment(tmp_path)
    values[name] = value
    with pytest.raises(OperationalConfigurationError, match=expected_category):
        load_operational_settings(values)


def test_missing_production_release_identity_fails_without_secret_value(tmp_path):
    values = production_environment(tmp_path)
    del values["DEPLOYMENT_ID"]
    with pytest.raises(OperationalConfigurationError) as error:
        load_operational_settings(values)
    assert "RELEASE_IDENTITY" in str(error.value)
    assert values["JWT_SECRET"] not in str(error.value)


def test_development_and_test_configuration_remain_usable(tmp_path):
    for environment in ("development", "test"):
        settings = load_operational_settings({
            "APP_ENV": environment,
            "JWT_SECRET": "testsecret",
            "DATABASE_URL": "sqlite:///./test.db",
            "STORYBOOK_PATH": str(tmp_path / environment / "storybook"),
        })
        assert settings.environment == environment
        assert "testserver" in settings.allowed_hosts


def _network_app(settings):
    application = FastAPI()

    @application.get("/")
    def context(request: Request):
        return resolve_network_context(request, settings).__dict__

    return application


def test_untrusted_forwarded_headers_are_not_authoritative(tmp_path):
    settings = load_operational_settings({
        "APP_ENV": "test",
        "JWT_SECRET": "testsecret",
        "DATABASE_URL": "sqlite:///./test.db",
        "TRUST_PROXY_HEADERS": "true",
        "TRUSTED_PROXY_IPS": "10.0.0.0/8",
    })
    with TestClient(_network_app(settings), client=("192.0.2.4", 50000)) as client:
        response = client.get("/", headers={
            "X-Forwarded-For": "203.0.113.44",
            "X-Forwarded-Proto": "https",
            "X-Forwarded-Host": "spoof.example",
        })
    assert response.json() == {
        "client_ip": "192.0.2.4",
        "scheme": "http",
        "host": "testserver",
        "proxy_trusted": False,
    }


def test_trusted_proxy_applies_only_valid_forwarding_metadata(tmp_path):
    settings = load_operational_settings({
        "APP_ENV": "test",
        "JWT_SECRET": "testsecret",
        "DATABASE_URL": "sqlite:///./test.db",
        "TRUST_PROXY_HEADERS": "true",
        "TRUSTED_PROXY_IPS": "10.0.0.0/8",
    })
    with TestClient(_network_app(settings), client=("10.1.2.3", 50000)) as client:
        response = client.get("/", headers={
            "X-Forwarded-For": "203.0.113.44, 10.1.2.3",
            "X-Forwarded-Proto": "https",
            "X-Forwarded-Host": "api.example.edu",
        })
    assert response.json() == {
        "client_ip": "203.0.113.44",
        "scheme": "https",
        "host": "api.example.edu",
        "proxy_trusted": True,
    }


def test_main_app_enforces_allowed_and_rejected_hosts():
    from app.main import app

    with TestClient(app) as client:
        assert client.get("/health/live", headers={"Host": "testserver"}).status_code == 200
        assert client.get("/health/live", headers={"Host": "unexpected.invalid"}).status_code == 400


def _sample_state(root: Path) -> tuple[Path, list[tuple[str, Path]]]:
    database = root / "source.sqlite3"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE evidence (id INTEGER PRIMARY KEY, value TEXT NOT NULL)")
        connection.execute("INSERT INTO evidence(value) VALUES ('operational-drill')")
    badges = root / "badges"
    storybook = root / "storybook"
    badges.mkdir()
    storybook.mkdir()
    (badges / "badge.png").write_bytes(b"safe-image-fixture")
    (storybook / "page.jpg").write_bytes(b"safe-story-fixture")
    return database, [("badges", badges), ("storybook", storybook)]


def test_backup_integrity_and_restore_usability(tmp_path):
    database, storage = _sample_state(tmp_path)
    bundle = tmp_path / "bundle"
    result = create_test_backup(
        database_path=database,
        storage_roots=storage,
        output_dir=bundle,
        environment="test",
        acknowledged_test_data=True,
    )
    assert result.files == 3
    assert verify_backup(bundle)["format_version"] == 1
    restored_db = tmp_path / "restored" / "database.sqlite3"
    restored_uploads = tmp_path / "restored-uploads"
    restore_test_backup(
        bundle=bundle,
        database_target=restored_db,
        storage_target=restored_uploads,
        environment="test",
        acknowledged_test_data=True,
    )
    with sqlite3.connect(restored_db) as connection:
        assert connection.execute("SELECT value FROM evidence").fetchone()[0] == "operational-drill"
    assert (restored_uploads / "badges" / "badge.png").read_bytes() == b"safe-image-fixture"


def test_corrupt_backup_fails_before_restore_targets_exist(tmp_path):
    database, storage = _sample_state(tmp_path)
    bundle = tmp_path / "bundle"
    create_test_backup(
        database_path=database,
        storage_roots=storage,
        output_dir=bundle,
        environment="test",
        acknowledged_test_data=True,
    )
    (bundle / "database.sqlite3").write_bytes(b"corrupt")
    target = tmp_path / "target.sqlite3"
    with pytest.raises(BackupSafetyError, match="integrity"):
        restore_test_backup(
            bundle=bundle,
            database_target=target,
            storage_target=tmp_path / "uploads-restored",
            environment="test",
            acknowledged_test_data=True,
        )
    assert not target.exists()


def test_backup_tool_refuses_production_and_existing_targets(tmp_path):
    database, storage = _sample_state(tmp_path)
    with pytest.raises(BackupSafetyError, match="restricted"):
        create_test_backup(
            database_path=database,
            storage_roots=storage,
            output_dir=tmp_path / "bundle",
            environment="production",
            acknowledged_test_data=True,
        )


def test_manifest_path_traversal_is_rejected(tmp_path):
    database, storage = _sample_state(tmp_path)
    bundle = tmp_path / "bundle"
    create_test_backup(
        database_path=database,
        storage_roots=storage,
        output_dir=bundle,
        environment="test",
        acknowledged_test_data=True,
    )
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"][0]["path"] = "../outside"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(BackupSafetyError, match="unsafe"):
        verify_backup(bundle)


def test_lifespan_disposes_database_resources(monkeypatch):
    from app.main import app, engine

    calls = []
    monkeypatch.setattr(engine, "dispose", lambda: calls.append("disposed"))
    with TestClient(app) as client:
        assert client.get("/health/live").json() == {"status": "live"}
    assert calls == ["disposed"]
