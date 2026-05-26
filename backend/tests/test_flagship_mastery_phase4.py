import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app import seed_demo
from app.api.routes import analytics, assessments, certifications, programs
from app.crud import progress as progress_crud
from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Assessment,
    AssessmentAttemptEvent,
    Course,
    SegmentProgress,
    StudentAssessmentAttempt,
    StudentCourse,
    StudentUnitProgress,
    User,
)


def _build_session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def _seed_with_factory(monkeypatch, session_factory):
    monkeypatch.setattr(seed_demo, "SessionLocal", session_factory)
    seed_demo.run()


def _build_api_client(session_factory):
    app = FastAPI()
    app.include_router(programs.router, prefix="/api")
    app.include_router(assessments.router, prefix="/api")
    app.include_router(certifications.router, prefix="/api")
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


def test_flagship_assessments_seed_deterministically_and_remain_learner_deliverable(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    client, current_user = _build_api_client(session_factory)

    session = session_factory()
    try:
        student = session.query(User).filter(User.username == "student1").one()
        current_user["value"] = student

        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        seeded_titles = [seed["title"] for seed in seed_demo.DEMO_FLAGSHIP_ASSESSMENTS]
        assessments_by_title = {assessment.title: assessment for assessment in session.query(Assessment).all()}

        assert all(title in assessments_by_title for title in seeded_titles)

        available = assessments_by_title["Introduction to Africa Lesson Check"]
        assert available.assessment_scope == "lesson"
        assert available.lesson_id is not None
        assert available.unit_id is None
        assert [question.order for question in available.questions] == [1, 2]
        assert [question.prompt for question in available.questions] == [
            question_seed["prompt"]
            for question_seed in next(
                seed["questions"] for seed in seed_demo.DEMO_FLAGSHIP_ASSESSMENTS if seed["title"] == available.title
            )
        ]

        learner_fetch = client.get(f"/api/assessments/{available.id}")
        assert learner_fetch.status_code == 200
        learner_payload = learner_fetch.json()
        assert learner_payload["learner_delivery_state"] == "available"
        assert learner_payload["is_available_for_learner"] is True
        assert [question["order"] for question in learner_payload["questions"]] == [1, 2]

        unavailable = assessments_by_title["Teacher Preview: Geography Extension Check"]
        assert unavailable.assessment_scope == "lesson"
        assert unavailable.assessment_state == "draft"
        assert unavailable.availability_state == "pending_review"

        blocked_fetch = client.get(f"/api/assessments/{unavailable.id}")
        assert blocked_fetch.status_code == 200
        blocked_payload = blocked_fetch.json()
        assert blocked_payload["learner_delivery_state"] == "draft"
        assert blocked_payload["is_available_for_learner"] is False
        assert blocked_payload["questions"] == []

        course_summary = client.get(f"/api/analytics/mastery-summary?course_id={course.id}")
        assert course_summary.status_code == 200
        assert course_summary.json()["objectives"] == []
    finally:
        session.close()


def test_flagship_attempt_events_and_mastery_summary_do_not_mutate_progress(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    client, current_user = _build_api_client(session_factory)

    session = session_factory()
    try:
        student = session.query(User).filter(User.username == "student1").one()
        current_user["value"] = student

        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        lesson_assessment = (
            session.query(Assessment)
            .filter(Assessment.title == "Introduction to Africa Lesson Check")
            .one()
        )

        before_courses = session.query(StudentCourse).count()
        before_unit_progress = session.query(StudentUnitProgress).count()
        before_segment_progress = session.query(SegmentProgress).count()

        fetch_response = client.get(f"/api/assessments/{lesson_assessment.id}")
        assert fetch_response.status_code == 200
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
        attempt_id = uuid.UUID(submit_response.json()["id"])

        attempt = session.query(StudentAssessmentAttempt).filter_by(id=attempt_id).one()
        assert attempt.assessment_id == lesson_assessment.id

        events = (
            session.query(AssessmentAttemptEvent)
            .filter_by(attempt_id=attempt_id)
            .order_by(AssessmentAttemptEvent.created_at)
            .all()
        )
        assert [event.event_type for event in events] == ["attempt_submitted", "attempt_scored"]
        assert events[1].passed is True
        assert events[1].event_metadata["score_snapshot"]["passed"] is True

        mastery_response = client.get(f"/api/analytics/mastery-summary?lesson_id={lesson_assessment.lesson_id}")
        assert mastery_response.status_code == 200
        mastery = mastery_response.json()
        objective_keys = {objective["objective_key"] for objective in mastery["objectives"]}
        assert "africa-diversity-and-respect" in objective_keys
        assert "careful-place-learning" in objective_keys

        after_courses = session.query(StudentCourse).count()
        after_unit_progress = session.query(StudentUnitProgress).count()
        after_segment_progress = session.query(SegmentProgress).count()
        assert before_courses == after_courses
        assert before_unit_progress == after_unit_progress
        assert before_segment_progress == after_segment_progress
    finally:
        session.close()


def test_unavailable_flagship_assessment_behavior_and_governed_progression_remain_unchanged(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    client, current_user = _build_api_client(session_factory)

    session = session_factory()
    try:
        student = session.query(User).filter(User.username == "student1").one()
        current_user["value"] = student

        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        student_course = StudentCourse(student_id=student.id, course_id=course.id)
        session.add(student_course)
        session.commit()
        session.refresh(student_course)

        before_state = progress_crud.resolve_governed_progression(session, student_course.id)

        blocked_assessment = (
            session.query(Assessment)
            .filter(Assessment.title == "Teacher Preview: Geography Extension Check")
            .one()
        )
        attempts_before = session.query(StudentAssessmentAttempt).count()
        events_before = session.query(AssessmentAttemptEvent).count()

        blocked_submit = client.post(
            f"/api/assessments/{blocked_assessment.id}/attempts",
            json={"answers": []},
        )
        assert blocked_submit.status_code == 403
        assert blocked_submit.json()["detail"]["learner_delivery_state"] == "draft"

        attempts_after = session.query(StudentAssessmentAttempt).count()
        events_after = session.query(AssessmentAttemptEvent).count()
        assert attempts_before == attempts_after
        assert events_before == events_after

        after_state = progress_crud.resolve_governed_progression(session, student_course.id)
        assert before_state["delivery_state"] == after_state["delivery_state"]
        assert before_state["lesson_id"] == after_state["lesson_id"]
        assert before_state["unit_progress_id"] == after_state["unit_progress_id"]
    finally:
        session.close()
