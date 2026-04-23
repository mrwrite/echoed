from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import SessionLocal  # noqa: E402
from app.models import Lesson  # noqa: E402


REQUIRED_FIELDS = [
    "learning_objectives",
    "key_concepts",
    "hook",
    "content",
    "guided_practice",
    "independent_practice",
    "assessment",
    "sources",
]


def _has_text(value: object | None) -> bool:
    return bool(str(value).strip()) if value is not None else False


def _has_non_empty_list(value: object | None) -> bool:
    return isinstance(value, list) and any(_has_text(item) for item in value)


def audit_lesson(lesson: Lesson) -> dict[str, object]:
    missing: list[str] = []

    if not _has_text(lesson.learning_objectives):
        missing.append("learning_objectives")
    if not _has_non_empty_list(lesson.key_concepts):
        missing.append("key_concepts")
    if not _has_text(lesson.hook):
        missing.append("hook")
    if not _has_text(lesson.content):
        missing.append("content")
    if not _has_text(lesson.guided_practice):
        missing.append("guided_practice")
    if not _has_text(lesson.independent_practice):
        missing.append("independent_practice")
    if not _has_text(lesson.assessment):
        missing.append("assessment")
    if not list(lesson.sources or []):
        missing.append("sources")

    return {
        "lesson_id": str(lesson.id),
        "lesson_title": lesson.title,
        "unit_id": str(lesson.unit_id),
        "review_status": lesson.review_status,
        "missing_fields": missing,
        "is_complete": not missing,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Report lessons that are missing academic-quality structure fields or sources. "
            "This is a read-only audit and does not modify application behavior."
        )
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format for the audit report.",
    )
    parser.add_argument(
        "--only-failures",
        action="store_true",
        help="Only print lessons missing one or more required academic fields.",
    )
    args = parser.parse_args()

    session = SessionLocal()
    try:
        try:
            lessons = (
                session.query(Lesson)
                .options(joinedload(Lesson.sources))
                .order_by(Lesson.title.asc())
                .all()
            )
        except OperationalError as exc:
            print("Academic Lesson Completeness Audit", file=sys.stderr)
            print(
                "Unable to connect to the configured database. "
                "Set DATABASE_URL to a reachable EchoEd database and rerun:",
                file=sys.stderr,
            )
            print(
                "backend\\venv\\Scripts\\python.exe backend\\scripts\\audit_academic_lesson_completeness.py --only-failures",
                file=sys.stderr,
            )
            print(f"Database error: {exc}", file=sys.stderr)
            return 2

        results = [audit_lesson(lesson) for lesson in lessons]
    finally:
        session.close()

    if args.only_failures:
        results = [result for result in results if not result["is_complete"]]

    summary = {
        "total_lessons": len(results) if args.only_failures else len(lessons),
        "incomplete_lessons": sum(1 for result in results if not result["is_complete"]),
        "results": results,
    }

    if args.format == "json":
        print(json.dumps(summary, indent=2))
        return 0

    print("Academic Lesson Completeness Audit")
    print(
        "Command: backend\\venv\\Scripts\\python.exe backend\\scripts\\audit_academic_lesson_completeness.py --only-failures"
    )
    print(f"Lessons reviewed: {summary['total_lessons']}")
    print(f"Incomplete lessons: {summary['incomplete_lessons']}")
    print("")

    if not results:
        print("No lessons matched the current audit filter.")
        return 0

    for result in results:
        missing = ", ".join(result["missing_fields"]) if result["missing_fields"] else "none"
        print(f"- {result['lesson_title']} ({result['lesson_id']})")
        print(f"  review_status: {result['review_status']}")
        print(f"  missing: {missing}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
