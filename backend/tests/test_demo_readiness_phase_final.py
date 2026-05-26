from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app import seed_demo
from app.api.routes import analytics, courses, start_course
from app.database import get_db
from app.deps import get_current_user
from app.models import (
    AssessmentAttemptEvent,
    Course,
    Lesson,
    StudentAssessmentAnswer,
    StudentAssessmentAttempt,
    StudentCertification,
    StudentCourse,
    StudentUnitProgress,
    SegmentProgress,
    User,
)


def _build_session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def _seed_with_factory(monkeypatch, session_factory):
    monkeypatch.setattr(seed_demo, "SessionLocal", session_factory)
    seed_demo.run()


def _build_api_client(session_factory):
    app = FastAPI()
    app.include_router(courses.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")
    app.include_router(start_course.router, prefix="/api")

    current_user = {"value": None}

    def override_get_db():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    def override_get_current_user():
        return current_user["value"]

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    return TestClient(app), current_user


def _seeded_context(session_factory):
    session = session_factory()
    try:
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        users = {
            username: session.query(User).filter(User.username == username).one()
            for username in (
                "orgadmin",
                "teacher",
                "student1",
                "normalstudent",
                "masteredstudent",
                "reteachstudent",
                "reviewstudent",
                "monitorstudent",
            )
        }
        return course.id, users
    finally:
        session.close()


def _read_only_snapshot(session_factory, course_id):
    session = session_factory()
    try:
        student_courses = (
            session.query(StudentCourse)
            .filter(StudentCourse.course_id == course_id)
            .order_by(StudentCourse.student_id)
            .all()
        )
        unit_progress = (
            session.query(StudentUnitProgress)
            .join(StudentCourse, StudentCourse.id == StudentUnitProgress.student_course_id)
            .filter(StudentCourse.course_id == course_id)
            .all()
        )
        segments = (
            session.query(SegmentProgress)
            .join(StudentUnitProgress, StudentUnitProgress.id == SegmentProgress.student_unit_id)
            .join(StudentCourse, StudentCourse.id == StudentUnitProgress.student_course_id)
            .filter(StudentCourse.course_id == course_id)
            .all()
        )
        return {
            "student_course_rows": len(student_courses),
            "unit_progress_rows": len(unit_progress),
            "segment_rows": len(segments),
            "attempt_rows": session.query(StudentAssessmentAttempt).count(),
            "answer_rows": session.query(StudentAssessmentAnswer).count(),
            "event_rows": session.query(AssessmentAttemptEvent).count(),
            "certification_rows": session.query(StudentCertification).count(),
            "course_statuses": sorted(
                (str(row.student_id), row.status, row.completed_at.isoformat() if row.completed_at else None)
                for row in student_courses
            ),
            "unit_statuses": sorted(
                (str(row.student_course_id), getattr(row.status, "value", str(row.status)))
                for row in unit_progress
            ),
            "segment_statuses": sorted(
                (str(row.student_unit_id), str(row.lesson_id), getattr(row.status, "value", str(row.status)))
                for row in segments
            ),
        }
    finally:
        session.close()


def _collect_story(session_factory, client, current_user, course_id, users):
    current_user["value"] = users["normalstudent"]
    start_response = client.post("/api/start-course", json={"course_id": str(course_id)})
    assert start_response.status_code == 200
    start_payload = start_response.json()
    assert start_payload["delivery_state"] == "governed_available"

    session = session_factory()
    try:
        start_lesson = session.query(Lesson).filter(Lesson.id == UUID(start_payload["lesson_id"])).one()
        start_lesson_title = start_lesson.title
    finally:
        session.close()

    reporting_response = client.get(f"/api/analytics/reporting-summary?course_id={course_id}")
    assert reporting_response.status_code == 200
    reporting_payload = reporting_response.json()
    assert reporting_payload["continuation_guidance"]["support_state"] == "normal"
    assert reporting_payload["continuation_guidance"]["recommended_action"] == "continue"
    assert reporting_payload["educator_runtime_support_summary"] is None

    snapshot_before_reads = _read_only_snapshot(session_factory, course_id)

    current_user["value"] = users["teacher"]
    runtime_support_response = client.get(f"/api/analytics/educator-runtime-support?course_id={course_id}")
    assert runtime_support_response.status_code == 200
    runtime_support_rows = runtime_support_response.json()
    runtime_support_by_name = {
        row["student_name"]: {
            "support_state": row["support_state"],
            "recommended_action": row["recommended_action"],
        }
        for row in runtime_support_rows
    }
    assert sorted(runtime_support_by_name) == [
        "Amara Mastery",
        "Binta Reteach",
        "Chidi Review",
        "Dayo Monitor",
        "Eshe Steady",
    ]
    assert runtime_support_by_name == {
        "Amara Mastery": {
            "support_state": "completed",
            "recommended_action": "celebrate-and-reflect",
        },
        "Binta Reteach": {
            "support_state": "remediation",
            "recommended_action": "review-and-continue",
        },
        "Chidi Review": {
            "support_state": "remediation",
            "recommended_action": "review-and-continue",
        },
        "Dayo Monitor": {
            "support_state": "normal",
            "recommended_action": "continue",
        },
        "Eshe Steady": {
            "support_state": "normal",
            "recommended_action": "continue",
        },
    }

    runtime_response = client.get(f"/api/courses/{course_id}/runtime-intervention-recommendations")
    assert runtime_response.status_code == 200
    runtime_by_name = {
        row["student_name"]: row["recommendation_state"]
        for row in runtime_response.json()
    }
    assert runtime_by_name == {
        "Amara Mastery": "enrichment",
        "Binta Reteach": "reteach",
        "Chidi Review": "review",
        "Dayo Monitor": "monitor",
        "Eshe Steady": "normal",
    }

    current_user["value"] = users["orgadmin"]
    publish_response = client.get(f"/api/courses/{course_id}/publish-readiness")
    safe_publish_response = client.get(f"/api/courses/{course_id}/safe-publish-validation")
    integrity_response = client.get(f"/api/courses/{course_id}/competency-evidence-integrity")
    assert publish_response.status_code == 200
    assert safe_publish_response.status_code == 200
    assert integrity_response.status_code == 200
    publish_payload = publish_response.json()
    safe_publish_payload = safe_publish_response.json()
    integrity_payload = integrity_response.json()
    assert publish_payload["is_ready"] is True
    assert safe_publish_payload["is_safe"] is True
    assert integrity_payload["is_valid"] is True
    assert integrity_payload["is_explainable"] is False
    assert [warning["code"] for warning in integrity_payload["warnings"]] == [
        "unaligned_assessment_mastery_evidence"
    ]

    snapshot_after_reads = _read_only_snapshot(session_factory, course_id)
    assert snapshot_before_reads == snapshot_after_reads

    current_user["value"] = users["student1"]
    learner_denied_response = client.get(f"/api/courses/{course_id}/governance-summary")
    assert learner_denied_response.status_code == 403

    return {
        "student_start_lesson_title": start_lesson_title,
        "student_continuation_state": reporting_payload["continuation_guidance"]["support_state"],
        "student_continuation_action": reporting_payload["continuation_guidance"]["recommended_action"],
        "teacher_runtime_support": runtime_support_by_name,
        "teacher_runtime_recommendations": runtime_by_name,
        "admin_publish_ready": publish_payload["is_ready"],
        "admin_safe_publish": safe_publish_payload["is_safe"],
        "admin_integrity_valid": integrity_payload["is_valid"],
        "admin_integrity_explainable": integrity_payload["is_explainable"],
        "admin_integrity_warning_codes": [warning["code"] for warning in integrity_payload["warnings"]],
        "learner_denied": learner_denied_response.status_code,
    }


def test_demo_readiness_reseed_is_repeatable_and_story_stable(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    client, current_user = _build_api_client(session_factory)

    snapshots = []
    for _ in range(2):
        _seed_with_factory(monkeypatch, session_factory)
        course_id, users = _seeded_context(session_factory)
        snapshots.append(_collect_story(session_factory, client, current_user, course_id, users))

    assert snapshots[0] == snapshots[1]


def test_ambiguous_integrity_warning_remains_intentional_and_deterministic(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    client, current_user = _build_api_client(session_factory)
    course_id, users = _seeded_context(session_factory)

    current_user["value"] = users["orgadmin"]
    integrity_response = client.get(f"/api/courses/{course_id}/competency-evidence-integrity")

    assert integrity_response.status_code == 200

    integrity_payload = integrity_response.json()
    assert integrity_payload["is_valid"] is True
    assert integrity_payload["is_explainable"] is False
    assert integrity_payload["blocking_issue_count"] == 0
    assert integrity_payload["warning_count"] == 1
    assert [warning["code"] for warning in integrity_payload["warnings"]] == [
        "unaligned_assessment_mastery_evidence"
    ]
    assert [warning["entity_title"] for warning in integrity_payload["warnings"]] == [
        "Introduction to Africa Ambiguous Evidence Check"
    ]
    assert [row["assessment_title"] for row in integrity_payload["affected_assessments"]] == [
        "Introduction to Africa Ambiguous Evidence Check"
    ]
