import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app import seed_demo
from app.api.routes import analytics, assessments, courses
from app.crud import progress as progress_crud
from app.database import get_db
from app.deps import get_current_user
from app.models import Assessment, Course, StudentCourse, User


def _build_session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def _seed_with_factory(monkeypatch, session_factory):
    monkeypatch.setattr(seed_demo, "SessionLocal", session_factory)
    seed_demo.run()


def _build_api_client(session_factory):
    app = FastAPI()
    app.include_router(courses.router, prefix="/api")
    app.include_router(assessments.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")

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


def _enroll_flagship_student(session, student: User, course: Course) -> StudentCourse:
    student_course = StudentCourse(student_id=student.id, course_id=course.id)
    session.add(student_course)
    session.commit()
    session.refresh(student_course)
    return student_course


def _create_runtime_user(session, *, role: str, username_prefix: str) -> User:
    user = User(
        id=uuid.uuid4(),
        firstname="Runtime",
        lastname=role.title(),
        username=f"{username_prefix}_{uuid.uuid4().hex[:8]}",
        email=f"{username_prefix}_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        role=role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def test_remediation_guidance_is_learner_safe_and_does_not_change_governed_progression(
    db_engine, monkeypatch
):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    client, current_user = _build_api_client(session_factory)

    session = session_factory()
    try:
        student = _create_runtime_user(session, role="student", username_prefix="runtime_student")
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        student_course = _enroll_flagship_student(session, student, course)

        before_state = progress_crud.resolve_governed_progression(session, student_course.id)
        lesson_assessment = (
            session.query(Assessment)
            .filter(Assessment.title == "Introduction to Africa Lesson Check")
            .one()
        )

        current_user["value"] = student
        fetch_response = client.get(f"/api/assessments/{lesson_assessment.id}")
        questions = fetch_response.json()["questions"]

        submit_response = client.post(
            f"/api/assessments/{lesson_assessment.id}/attempts",
            json={
                "answers": [
                    {"question_id": questions[0]["id"], "answer": "Africa is one country."},
                    {"question_id": questions[1]["id"], "answer": "It does not matter."},
                ]
            },
        )
        assert submit_response.status_code == 200

        course_response = client.get("/api/student-courses")
        assert course_response.status_code == 200
        payload = course_response.json()
        assert len(payload) == 1
        guidance = payload[0]["continuation_guidance"]
        assert guidance["support_state"] == "remediation"
        assert guidance["recommended_action"] == "review-and-continue"
        assert guidance["educator_note"] is None
        assert guidance["educator_intervention_hint"] is None
        assert "support" in guidance["learner_title"].lower()
        assert "confidence" in guidance["learner_message"].lower()
        assert guidance["reinforcement_title"] == "Learning can be rebuilt"
        assert "does not erase your progress" in guidance["reinforcement_message"]
        assert guidance["review_lesson_title"] == "Introduction to Africa"
        assert len(guidance["review_prompts"]) >= 1
        assert "Introduction to Africa" in guidance["review_prompts"][0]
        assert guidance["review_key_concepts"]

        after_state = progress_crud.resolve_governed_progression(session, student_course.id)
        assert before_state["delivery_state"] == after_state["delivery_state"]
        assert before_state["lesson_id"] == after_state["lesson_id"]
        assert before_state["unit_progress_id"] == after_state["unit_progress_id"]
    finally:
        session.close()


def test_normal_guidance_includes_encouraging_reinforcement_copy(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    client, current_user = _build_api_client(session_factory)

    session = session_factory()
    try:
        student = _create_runtime_user(session, role="student", username_prefix="runtime_student")
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        _enroll_flagship_student(session, student, course)

        current_user["value"] = student
        course_response = client.get("/api/student-courses")
        assert course_response.status_code == 200
        guidance = course_response.json()[0]["continuation_guidance"]
        assert guidance["support_state"] == "normal"
        assert guidance["reinforcement_title"]
        assert "lesson is another chance" in guidance["reinforcement_message"]
    finally:
        session.close()


def test_enrichment_guidance_is_deterministic_for_strong_flagship_mastery(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    client, current_user = _build_api_client(session_factory)

    session = session_factory()
    try:
        student = _create_runtime_user(session, role="student", username_prefix="runtime_student")
        educator = _create_runtime_user(session, role="teacher", username_prefix="runtime_teacher")
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        student_course = _enroll_flagship_student(session, student, course)
        lesson_assessment = (
            session.query(Assessment)
            .filter(Assessment.title == "Introduction to Africa Lesson Check")
            .one()
        )
        before_state = progress_crud.resolve_governed_progression(session, student_course.id)

        current_user["value"] = student
        fetch_response = client.get(f"/api/assessments/{lesson_assessment.id}")
        questions = fetch_response.json()["questions"]

        submit_response = client.post(
            f"/api/assessments/{lesson_assessment.id}/attempts",
            json={
                "answers": [
                    {"question_id": questions[0]["id"], "answer": "Africa is a diverse continent."},
                    {"question_id": questions[1]["id"], "answer": "Because places and people deserve respect."},
                ]
            },
        )
        assert submit_response.status_code == 200

        first_fetch = client.get("/api/student-courses")
        second_fetch = client.get("/api/student-courses")
        assert first_fetch.status_code == 200
        assert second_fetch.status_code == 200
        first_guidance = first_fetch.json()[0]["continuation_guidance"]
        second_guidance = second_fetch.json()[0]["continuation_guidance"]
        assert first_guidance == second_guidance
        assert first_guidance["support_state"] == "enrichment"
        assert first_guidance["recommended_action"] == "continue-with-enrichment"
        assert "optional extension prompts" in first_guidance["learner_message"]
        assert first_guidance["reinforcement_title"] == "Your understanding is growing strong"
        assert "Follow your curiosity" in first_guidance["reinforcement_message"]
        assert first_guidance["extension_lesson_title"] == "Introduction to Africa"
        assert first_guidance["extension_key_concepts"]
        assert len(first_guidance["extension_prompts"]) >= 1
        assert "Introduction to Africa" in first_guidance["extension_prompts"][0]

        current_user["value"] = educator
        report_response = client.get(
            f"/api/analytics/reporting-summary?course_id={course.id}&student_id={student.id}"
        )
        assert report_response.status_code == 200
        report_guidance = report_response.json()["continuation_guidance"]
        assert report_guidance["support_state"] == "enrichment"
        assert report_guidance["educator_note"]
        assert "optional enrichment" in report_guidance["educator_note"]

        after_state = progress_crud.resolve_governed_progression(session, student_course.id)
        assert before_state["delivery_state"] == after_state["delivery_state"]
        assert before_state["lesson_id"] == after_state["lesson_id"]
        assert before_state["unit_progress_id"] == after_state["unit_progress_id"]
    finally:
        session.close()


def test_reporting_summary_exposes_educator_visible_continuation_context(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    client, current_user = _build_api_client(session_factory)

    session = session_factory()
    try:
        student = _create_runtime_user(session, role="student", username_prefix="runtime_student")
        admin = _create_runtime_user(session, role="teacher", username_prefix="runtime_teacher")
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        _enroll_flagship_student(session, student, course)
        lesson_assessment = (
            session.query(Assessment)
            .filter(Assessment.title == "Introduction to Africa Lesson Check")
            .one()
        )

        current_user["value"] = student
        fetch_response = client.get(f"/api/assessments/{lesson_assessment.id}")
        questions = fetch_response.json()["questions"]
        client.post(
            f"/api/assessments/{lesson_assessment.id}/attempts",
            json={
                "answers": [
                    {"question_id": questions[0]["id"], "answer": "Africa is one country."},
                    {"question_id": questions[1]["id"], "answer": "It does not matter."},
                ]
            },
        )

        current_user["value"] = admin
        report_response = client.get(
            f"/api/analytics/reporting-summary?course_id={course.id}&student_id={student.id}"
        )
        assert report_response.status_code == 200
        report = report_response.json()
        guidance = report["continuation_guidance"]
        assert guidance["support_state"] == "remediation"
        assert guidance["educator_note"]
        assert "benefit from brief review" in guidance["educator_note"]
        assert guidance["review_lesson_title"] == "Introduction to Africa"
        assert guidance["review_prompts"]
        assert guidance["educator_intervention_hint"]
    finally:
        session.close()
