from __future__ import annotations

import argparse
from contextlib import closing
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import time

from fastapi.testclient import TestClient

from app.operational_backup import create_test_backup, restore_test_backup
from app.operational_config import OperationalConfigurationError, load_operational_settings
from scripts.verify_deployment import check_endpoint


@dataclass(frozen=True)
class DrillResult:
    name: str
    passed: bool
    duration_ms: float
    observed: str


def _run(name: str, action) -> DrillResult:
    started = time.perf_counter()
    try:
        observation = action()
        return DrillResult(name, True, round((time.perf_counter() - started) * 1000, 2), observation)
    except Exception as exc:
        return DrillResult(name, False, round((time.perf_counter() - started) * 1000, 2), f"{type(exc).__name__}: safe drill failed")


def _safe_production_values(root: Path, secret: str) -> dict[str, str]:
    return {
        "APP_ENV": "production",
        "DATABASE_URL": "postgresql://echoed:nondefault-credential@database.internal/echoed",
        "JWT_SECRET": secret,
        "ALLOWED_HOSTS": "api.example.edu",
        "FRONTEND_URL": "https://learn.example.edu",
        "EXTERNAL_BASE_URL": "https://api.example.edu",
        "TRUST_PROXY_HEADERS": "false",
        "STORYBOOK_PATH": str(root / "storybook"),
        "COLORINGS_PATH": str(root / "colorings"),
        "BADGES_PATH": str(root / "badges"),
        "PERSISTENT_STORAGE_ACKNOWLEDGED": "true",
        "AUTO_MIGRATE_ON_STARTUP": "false",
        "RELEASE_VERSION": "drill-release",
        "DEPLOYMENT_ID": "drill-deployment",
        "LOG_FORMAT": "json",
        "METRICS_ENABLED": "true",
        "REQUEST_LOGGING_ENABLED": "true",
    }


def invalid_configuration(root: Path) -> str:
    values = _safe_production_values(root, "a-safe-synthetic-secret-at-least-32-bytes")
    values["ALLOWED_HOSTS"] = "*"
    try:
        load_operational_settings(values)
    except OperationalConfigurationError as exc:
        if "ALLOWED_HOSTS" not in str(exc):
            raise RuntimeError("unexpected validation category")
        return "Unsafe production host configuration was rejected without values."
    raise RuntimeError("unsafe configuration was accepted")


def migration_drill(root: Path) -> str:
    backend_root = Path(__file__).resolve().parents[1]
    heads = subprocess.run(
        [sys.executable, "-m", "alembic", "heads"],
        cwd=backend_root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if heads.returncode != 0 or "(head)" not in heads.stdout:
        raise RuntimeError("migration graph head verification failed")
    start_script = (backend_root / "start.sh").read_text(encoding="utf-8")
    if "alembic upgrade" in start_script:
        raise RuntimeError("normal startup still mutates schema")
    migration_script = (backend_root / "migrate.sh").read_text(encoding="utf-8")
    if "alembic upgrade heads" not in migration_script or "verify_migrations" not in migration_script:
        raise RuntimeError("explicit migration gate is incomplete")
    return "Migration graph has a repository head; startup is non-mutating; explicit upgrade and head-verification gates are present."


def lifecycle_and_health() -> str:
    import app.main as main
    from sqlalchemy.exc import SQLAlchemyError

    original_database_ready = main._database_ready

    def unavailable_database() -> None:
        raise SQLAlchemyError("synthetic dependency outage")

    main._database_ready = unavailable_database
    try:
        with TestClient(main.app) as client:
            live = client.get("/health/live")
            ready = client.get("/health/ready")
            if live.status_code != 200 or ready.status_code != 503:
                raise RuntimeError("health separation gate failed")
            if "database" not in ready.json().get("dependencies", {}):
                raise RuntimeError("readiness dependency was not identified")
    finally:
        main._database_ready = original_database_ready
    return "ASGI startup/shutdown completed; liveness stayed healthy while unavailable database failed readiness."


def failed_postdeploy() -> str:
    passed, _ = check_endpoint("http://127.0.0.1:1", "/health/ready", timeout=0.2)
    if passed:
        raise RuntimeError("unavailable deployment passed")
    return "Unavailable readiness target stopped post-deployment verification."


def backup_restore_rollback_storage(root: Path) -> str:
    database = root / "source.sqlite3"
    uploads = root / "uploads"
    uploads.mkdir()
    (uploads / "asset.bin").write_bytes(b"operational-drill-asset")
    with closing(sqlite3.connect(database)) as connection:
        with connection:
            connection.execute("CREATE TABLE release_state (version TEXT NOT NULL)")
            connection.execute("INSERT INTO release_state VALUES ('known-good')")
    bundle = root / "backup"
    create_test_backup(
        database_path=database,
        storage_roots=[("uploads", uploads)],
        output_dir=bundle,
        environment="test",
        acknowledged_test_data=True,
    )
    restored_database = root / "restored.sqlite3"
    restored_storage = root / "restored-storage"
    restore_test_backup(
        bundle=bundle,
        database_target=restored_database,
        storage_target=restored_storage,
        environment="test",
        acknowledged_test_data=True,
    )
    with closing(sqlite3.connect(restored_database)) as connection:
        state = connection.execute("SELECT version FROM release_state").fetchone()[0]
    if state != "known-good" or (restored_storage / "uploads" / "asset.bin").read_bytes() != b"operational-drill-asset":
        raise RuntimeError("restored state unusable")
    return "Backup integrity, isolated restore, known-good data rollback, and upload recovery succeeded."


def rotation_simulation(root: Path) -> str:
    old = load_operational_settings(_safe_production_values(root, "old-synthetic-secret-at-least-32-characters"))
    replacement = load_operational_settings(_safe_production_values(root, "new-synthetic-secret-at-least-32-characters"))
    if old.jwt_secret == replacement.jwt_secret:
        raise RuntimeError("rotation did not change credential")
    return "Old and replacement configurations validated independently; secret values were not emitted."


def main() -> int:
    parser = argparse.ArgumentParser(description="Run isolated EchoEd operational-readiness drills.")
    parser.add_argument("--output", type=Path, help="Optional JSON evidence path outside the temporary drill workspace.")
    args = parser.parse_args()
    if os.getenv("APP_ENV", "development").strip().lower() in {"production", "staging"}:
        print("Operational drills refuse production and staging environments.", file=sys.stderr)
        return 5
    drill_parent = Path(__file__).resolve().parents[1] / ".pytest_tmp"
    drill_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="echoed-operational-drill-", dir=drill_parent) as directory:
        root = Path(directory)
        results = [
            _run("invalid-production-configuration", lambda: invalid_configuration(root)),
            _run("database-migration", lambda: migration_drill(root)),
            _run("startup-health-graceful-shutdown", lifecycle_and_health),
            _run("failed-postdeploy-verification", failed_postdeploy),
            _run("backup-restore-rollback-storage", lambda: backup_restore_rollback_storage(root)),
            _run("secret-configuration-rotation", lambda: rotation_simulation(root)),
        ]
    payload = {
        "environment": "isolated-non-production",
        "results": [asdict(result) for result in results],
        "passed": all(result.passed for result in results),
    }
    rendered = json.dumps(payload, indent=2)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if payload["passed"] else 6


if __name__ == "__main__":
    raise SystemExit(main())
