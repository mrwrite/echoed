from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def check_endpoint(base_url: str, path: str, expected_status: int = 200, timeout: float = 5.0) -> tuple[bool, str]:
    try:
        with urlopen(Request(f"{base_url.rstrip('/')}{path}", headers={"Accept": "application/json"}), timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
            if response.status != expected_status:
                return False, f"{path}: unexpected status"
            return True, str(body.get("status", "ok"))
    except (HTTPError, URLError, TimeoutError, ValueError):
        return False, f"{path}: unavailable or invalid response"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify EchoEd post-deployment health gates.")
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()
    for path in ("/health/live", "/health/ready"):
        passed, detail = check_endpoint(args.base_url, path, timeout=args.timeout)
        print(f"{'PASS' if passed else 'FAIL'} {path}: {detail}")
        if not passed:
            return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
