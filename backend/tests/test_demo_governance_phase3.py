from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app import seed_demo
from app.api.routes import courses
from app.database import get_db
from app.deps import get_current_user
from app.models import Course, User


def _build_session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def _seed_with_factory(monkeypatch, session_factory):
    monkeypatch.setattr(seed_demo, "SessionLocal", session_factory)
    seed_demo.run()


def _build_test_client(db_session, user):
    app = FastAPI()
    app.include_router(courses.router, prefix="/api")
    app.dependency_overrides[get_current_user] = lambda: user

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _seeded_course_and_users(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    session = session_factory()
    course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
    users = {
        username: session.query(User).filter(User.username == username).one()
        for username in (
            "orgadmin",
            "teacher",
            "contentadmin",
            "student1",
            "student2",
            "masteredstudent",
            "reteachstudent",
            "reviewstudent",
            "monitorstudent",
            "normalstudent",
        )
    }
    return session, course, users


def test_flagship_governance_summary_returns_expected_demo_sections(db_engine, monkeypatch):
    session, course, users = _seeded_course_and_users(db_engine, monkeypatch)
    try:
        client = _build_test_client(session, users["orgadmin"])

        response = client.get(f"/api/courses/{course.id}/governance-summary")

        assert response.status_code == 200
        payload = response.json()
        assert payload["course_id"] == str(course.id)
        assert payload["course_title"] == seed_demo.DEMO_COURSE_TITLE
        assert set(payload) == {
            "course_id",
            "course_title",
            "publish_readiness",
            "safe_publish_validation",
            "lineage_safety_visibility",
            "competency_evidence_integrity",
            "runtime_intervention_recommendations",
        }

        publish_readiness = payload["publish_readiness"]
        assert publish_readiness["is_ready"] is True
        assert publish_readiness["blocking_issue_count"] == 0
        assert publish_readiness["warning_count"] == 0

        safe_publish = payload["safe_publish_validation"]
        assert safe_publish["is_safe"] is True
        assert safe_publish["blocking_issue_count"] == 0
        assert safe_publish["warning_count"] == 0

        lineage_visibility = payload["lineage_safety_visibility"]
        assert lineage_visibility["is_coherent"] is True
        assert lineage_visibility["is_safe"] is True
        assert lineage_visibility["blocking_issues"] == []
        assert lineage_visibility["warnings"] == []

        competency_integrity = payload["competency_evidence_integrity"]
        assert competency_integrity["is_valid"] is True
        assert competency_integrity["is_explainable"] is False
        assert competency_integrity["blocking_issue_count"] == 0
        assert competency_integrity["warning_count"] == 1
        assert [issue["code"] for issue in competency_integrity["warnings"]] == [
            "unaligned_assessment_mastery_evidence"
        ]
        assert [item["assessment_title"] for item in competency_integrity["affected_assessments"]] == [
            "Introduction to Africa Ambiguous Evidence Check"
        ]
    finally:
        session.close()


def test_flagship_runtime_recommendations_cover_all_demo_archetypes(db_engine, monkeypatch):
    session, course, users = _seeded_course_and_users(db_engine, monkeypatch)
    try:
        client = _build_test_client(session, users["teacher"])

        response = client.get(f"/api/courses/{course.id}/runtime-intervention-recommendations")

        assert response.status_code == 200
        rows = {row["student_name"]: row for row in response.json()}
        assert {row["recommendation_state"] for row in rows.values()} == {
            "enrichment",
            "reteach",
            "review",
            "monitor",
            "normal",
        }
        assert rows["Amara Mastery"]["recommendation_state"] == "enrichment"
        assert rows["Binta Reteach"]["recommendation_state"] == "reteach"
        assert rows["Chidi Review"]["recommendation_state"] == "review"
        assert rows["Dayo Monitor"]["recommendation_state"] == "monitor"
        assert rows["Eshe Steady"]["recommendation_state"] == "normal"
        assert "ambiguous_competency_evidence" in rows["Dayo Monitor"]["caution_flags"]
        assert "limited_mastery_evidence" in rows["Dayo Monitor"]["caution_flags"]
        assert "limited_mastery_evidence" in rows["Eshe Steady"]["caution_flags"]
    finally:
        session.close()


def test_flagship_demo_governance_endpoints_deny_learners(db_engine, monkeypatch):
    session, course, users = _seeded_course_and_users(db_engine, monkeypatch)
    try:
        client = _build_test_client(session, users["student1"])

        for path in (
            f"/api/courses/{course.id}/publish-readiness",
            f"/api/courses/{course.id}/safe-publish-validation",
            f"/api/courses/{course.id}/competency-evidence-integrity",
            f"/api/courses/{course.id}/runtime-intervention-recommendations",
            f"/api/courses/{course.id}/governance-summary",
        ):
            response = client.get(path)
            assert response.status_code == 403
    finally:
        session.close()
