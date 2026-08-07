from __future__ import annotations

import sys

from app.operational_config import OperationalConfigurationError, load_operational_settings


def main() -> int:
    try:
        settings = load_operational_settings()
    except OperationalConfigurationError as exc:
        print(f"Operational configuration invalid: {exc}", file=sys.stderr)
        return 2
    print(f"Operational configuration valid for {settings.environment}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
