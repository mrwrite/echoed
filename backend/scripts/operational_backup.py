from __future__ import annotations

import argparse
import os
from pathlib import Path

from app.operational_backup import create_test_backup, restore_test_backup, verify_backup


def main() -> int:
    parser = argparse.ArgumentParser(description="Safe EchoEd non-production backup/restore drill tool.")
    subparsers = parser.add_subparsers(dest="operation", required=True)
    backup = subparsers.add_parser("backup")
    backup.add_argument("--database", type=Path, required=True)
    backup.add_argument("--storage", action="append", default=[], metavar="CATEGORY=PATH")
    backup.add_argument("--output", type=Path, required=True)
    backup.add_argument("--acknowledge-test-data", action="store_true")
    verify = subparsers.add_parser("verify")
    verify.add_argument("--bundle", type=Path, required=True)
    restore = subparsers.add_parser("restore")
    restore.add_argument("--bundle", type=Path, required=True)
    restore.add_argument("--database-target", type=Path, required=True)
    restore.add_argument("--storage-target", type=Path, required=True)
    restore.add_argument("--acknowledge-test-data", action="store_true")
    args = parser.parse_args()
    environment = os.getenv("APP_ENV", "development")
    if args.operation == "verify":
        manifest = verify_backup(args.bundle)
        print(f"Backup integrity verified ({len(manifest['files'])} file(s)).")
    elif args.operation == "backup":
        roots = []
        for item in args.storage:
            category, separator, path = item.partition("=")
            if not separator:
                parser.error("--storage values must use CATEGORY=PATH")
            roots.append((category, Path(path)))
        result = create_test_backup(
            database_path=args.database,
            storage_roots=roots,
            output_dir=args.output,
            environment=environment,
            acknowledged_test_data=args.acknowledge_test_data,
        )
        print(f"Backup created and verified ({result.files} file(s), {result.bytes} bytes).")
    else:
        result = restore_test_backup(
            bundle=args.bundle,
            database_target=args.database_target,
            storage_target=args.storage_target,
            environment=environment,
            acknowledged_test_data=args.acknowledge_test_data,
        )
        print(f"Backup restored and verified ({result.files} file(s), {result.bytes} bytes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
