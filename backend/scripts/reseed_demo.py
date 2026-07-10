from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve()
BACKEND_ROOT_CANDIDATES = (
    SCRIPT_PATH.parents[1],
    SCRIPT_PATH.parents[2] / "backend",
)
for backend_root in BACKEND_ROOT_CANDIDATES:
    if (backend_root / "app").exists() and str(backend_root) not in sys.path:
        sys.path.insert(0, str(backend_root))
        break

from app import seed_demo  # noqa: E402
from app import seed_v2_demo  # noqa: E402


ARCHETYPE_SUMMARY = (
    ("mastered_student", "enrichment/mastered", "enrichment"),
    ("reteach_student", "reteach/struggling", "reteach"),
    ("review_student", "review/moderate", "review"),
    ("monitor_student", "monitor/ambiguous", "monitor"),
    ("normal_student", "normal progression", "normal"),
)


def _print_account_summary() -> None:
    print(f"Demo organization: {seed_demo.DEMO_ORG_NAME}")
    print(f"Flagship course: {seed_demo.DEMO_COURSE_TITLE}")
    print("Core staff accounts:")
    for key, label in (
        ("org_admin", "Org admin"),
        ("teacher", "Teacher"),
        ("content_admin", "Content admin"),
    ):
        profile = seed_demo.DEMO_USERS[key]
        print(
            f"  - {label}: username={profile['username']} "
            f"email={profile['email']} password={seed_demo.DEMO_PASSWORD}"
        )

    print("Reference student accounts:")
    for key in ("student1", "student2"):
        profile = seed_demo.DEMO_USERS[key]
        print(
            f"  - {profile['firstname']} {profile['lastname']}: "
            f"username={profile['username']} password={seed_demo.DEMO_PASSWORD}"
        )

    print("Archetype learners:")
    for key, archetype_label, expected_state in ARCHETYPE_SUMMARY:
        profile = seed_demo.DEMO_USERS[key]
        print(
            f"  - {profile['firstname']} {profile['lastname']} "
            f"({profile['username']}): {archetype_label}, "
            f"expected runtime recommendation={expected_state}"
        )


def main() -> int:
    print("Running EchoEd demo reseed...")
    try:
        seed_demo.run()
        seed_v2_demo.run()
    except Exception as exc:
        print("EchoEd demo reseed failed.", file=sys.stderr)
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("EchoEd demo reseed completed successfully.")
    _print_account_summary()
    print("V2 dogfooding workspace:")
    print(f"  - Workspace route: /workspace")
    print(f"  - Demo guide route: /workspace/demo-readiness")
    print(f"  - Learner route: /learn as normalstudent / {seed_demo.DEMO_PASSWORD}")
    print("Recommended next step: sign in as contentadmin and open /workspace/demo-readiness.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
