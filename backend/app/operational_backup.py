from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from contextlib import closing
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
from typing import Iterable


FORMAT_VERSION = 1


class BackupSafetyError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _assert_test_boundary(environment: str, acknowledged_test_data: bool) -> None:
    if environment.lower() in {"production", "staging"} or not acknowledged_test_data:
        raise BackupSafetyError("Repository backup tooling is restricted to explicitly acknowledged development/test data")


def _safe_relative(path: Path) -> str:
    value = path.as_posix()
    if path.is_absolute() or ".." in path.parts:
        raise BackupSafetyError("Backup manifest contains an unsafe path")
    return value


@dataclass(frozen=True)
class BackupResult:
    bundle: Path
    files: int
    bytes: int


def create_test_backup(
    *,
    database_path: Path,
    storage_roots: Iterable[tuple[str, Path]],
    output_dir: Path,
    environment: str,
    acknowledged_test_data: bool,
) -> BackupResult:
    _assert_test_boundary(environment, acknowledged_test_data)
    if output_dir.exists():
        raise BackupSafetyError("Backup output must not already exist")
    if not database_path.is_file():
        raise BackupSafetyError("SQLite source database is unavailable")
    output_dir.mkdir(parents=True)
    database_output = output_dir / "database.sqlite3"
    with closing(sqlite3.connect(database_path)) as source, closing(sqlite3.connect(database_output)) as target:
        with target:
            source.backup(target)
            integrity = target.execute("PRAGMA integrity_check").fetchone()
            if not integrity or integrity[0] != "ok":
                raise BackupSafetyError("SQLite backup integrity verification failed")

    files: list[dict[str, object]] = []
    assets_root = output_dir / "uploads"
    for category, root in storage_roots:
        if not re_safe_category(category):
            raise BackupSafetyError("Storage category is invalid")
        if not root.exists():
            continue
        for source_file in sorted(path for path in root.rglob("*") if path.is_file()):
            relative = source_file.relative_to(root)
            destination = assets_root / category / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, destination)
            bundle_relative = destination.relative_to(output_dir)
            files.append({
                "path": _safe_relative(bundle_relative),
                "sha256": _sha256(destination),
                "bytes": destination.stat().st_size,
            })
    files.insert(0, {
        "path": "database.sqlite3",
        "sha256": _sha256(database_output),
        "bytes": database_output.stat().st_size,
    })
    manifest = {
        "format_version": FORMAT_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "data_class": "non-production-operational-drill",
        "files": files,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    verify_backup(output_dir)
    return BackupResult(output_dir, len(files), sum(int(item["bytes"]) for item in files))


def re_safe_category(value: str) -> bool:
    return bool(value) and all(character.isalnum() or character in {"-", "_"} for character in value)


def verify_backup(bundle: Path) -> dict[str, object]:
    manifest_path = bundle / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise BackupSafetyError("Backup manifest is unavailable or invalid") from exc
    if manifest.get("format_version") != FORMAT_VERSION or manifest.get("data_class") != "non-production-operational-drill":
        raise BackupSafetyError("Backup manifest format or data class is unsupported")
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        raise BackupSafetyError("Backup manifest has no files")
    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise BackupSafetyError("Backup manifest file entry is invalid")
        relative = Path(_safe_relative(Path(entry["path"])))
        source = bundle / relative
        if not source.is_file() or _sha256(source) != entry.get("sha256") or source.stat().st_size != entry.get("bytes"):
            raise BackupSafetyError("Backup integrity verification failed")
    return manifest


def restore_test_backup(
    *,
    bundle: Path,
    database_target: Path,
    storage_target: Path,
    environment: str,
    acknowledged_test_data: bool,
) -> BackupResult:
    _assert_test_boundary(environment, acknowledged_test_data)
    manifest = verify_backup(bundle)
    if database_target.exists() or storage_target.exists():
        raise BackupSafetyError("Restore targets must not already exist")
    database_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bundle / "database.sqlite3", database_target)
    uploads = bundle / "uploads"
    if uploads.exists():
        shutil.copytree(uploads, storage_target)
    else:
        storage_target.mkdir(parents=True)
    with closing(sqlite3.connect(database_target)) as restored:
        integrity = restored.execute("PRAGMA integrity_check").fetchone()
        if not integrity or integrity[0] != "ok":
            raise BackupSafetyError("Restored SQLite database failed integrity verification")
        table_exists = restored.execute(
            "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'audit_events'"
        ).fetchone()
    if table_exists:
        _verify_restored_audit_chains(database_target)
    files = manifest["files"]
    return BackupResult(bundle, len(files), sum(int(item["bytes"]) for item in files))


def _verify_restored_audit_chains(database_path: Path) -> None:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.audit import verify_audit_chain
    from app.models import AuditEvent

    engine = create_engine(f"sqlite:///{database_path.as_posix()}")
    restored_session = sessionmaker(bind=engine)()
    try:
        organization_ids = [
            row[0]
            for row in restored_session.query(AuditEvent.organization_id)
            .filter(AuditEvent.organization_id.isnot(None))
            .distinct()
            .all()
        ]
        scopes = [None, *organization_ids]
        for organization_id in scopes:
            result = verify_audit_chain(restored_session, organization_id=organization_id)
            if not result.valid:
                raise BackupSafetyError("Restored audit-event integrity verification failed")
    finally:
        restored_session.close()
        engine.dispose()
