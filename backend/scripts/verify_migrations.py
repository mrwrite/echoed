from __future__ import annotations

import sys

from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory

from app.database import engine


def verify_migration_heads() -> tuple[set[str], set[str]]:
    config = Config("alembic.ini")
    script = ScriptDirectory.from_config(config)
    expected = set(script.get_heads())
    with engine.connect() as connection:
        actual = set(MigrationContext.configure(connection).get_current_heads())
    return expected, actual


def main() -> int:
    expected, actual = verify_migration_heads()
    if actual != expected:
        print("Database migration state does not match repository heads.", file=sys.stderr)
        return 3
    print(f"Database migration state verified ({len(actual)} head(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
