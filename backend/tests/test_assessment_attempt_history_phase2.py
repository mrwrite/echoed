import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import assessments, certifications, programs
from app.database import get_db
from app.deps import get_current_user
from app.models import (
    AssessmentAttemptEvent,
    Badge,
    Course,
    Program,
    StudentAssessmentAnswer,
    StudentAssessmentAttempt,
    StudentBadge,
    StudentCertification,
    StudentCourse,
    User,
)


@pytest.fixture
def api_client(db_session):
    app = FastAPI()
    app.include_router(programs.router, prefix="/api")
    app.include_router(assessments.router, prefix="/api")
    app.include_router(certifications.router, prefix="/api")

    current_user = {"value": None}

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return current_user["value"]

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    return TestClient(app), current_user


@pytest.fixture
def seeded_users(db_session):
    admin = User(
        id=uuid.uuid4(),
        firstname="Admin",
        lastname="User",
        username=f"admin_{uuid.uuid4().hex[:8]}",
        email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        role="admin",
    )
    student = User(
        id=uuid.uuid4(),
        firstname="Student",
        lastname="User",
        username=f"student_{uuid.uuid4().hex[:8]}",
        email=f"student_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        role="student",
    )
    db_session.add_all([admin, student])
    db_session.commit()
    return admin, student


def test_submitting_assessment_creates_append_only_history_events(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    course = Course(id=uuid.uuid4(), title="History Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    current_user["value"] = admin
    assessment_response = client.post(
        "/api/assessments",
        json={
            "title": "History Check",
            "description": "Append-only audit",
            "course_id": str(course.id),
            "passing_score": 50,
            "max_attempts": 2,
            "questions": [
                {
                    "prompt": "First?",
                    "choices": ["A", "B"],
                    "correct_answer": "A",
                    "points": 2,
                    "order": 1,
                },
                {
                    "prompt": "Second?",
                    "choices": ["Yes", "No"],
                    "correct_answer": "Yes",
                    "points": 3,
                    "order": 2,
                },
            ],
        },
    )
    assert assessment_response.status_code == 201
    assessment = assessment_response.json()

    current_user["value"] = student
    submit_response = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={
            "answers": [
                {"question_id": assessment["questions"][0]["id"], "answer": "A"},
                {"question_id": assessment["questions"][1]["id"], "answer": "No"},
            ]
        },
    )

    assert submit_response.status_code == 200
    body = submit_response.json()
    assert body["score"] == 2
    assert body["max_score"] == 5
    assert body["percentage"] == 40
    assert body["passed"] is False

    attempt = db_session.query(StudentAssessmentAttempt).filter_by(id=uuid.UUID(body["id"])).one()
    assert attempt.score == 2
    assert attempt.max_score == 5
    assert attempt.passed is False

    answers = db_session.query(StudentAssessmentAnswer).filter_by(attempt_id=attempt.id).all()
    assert len(answers) == 2

    events = (
        db_session.query(AssessmentAttemptEvent)
        .filter_by(attempt_id=attempt.id)
        .order_by(AssessmentAttemptEvent.created_at)
        .all()
    )
    assert [event.event_type for event in events] == ["attempt_submitted", "attempt_scored"]
    submitted_event, scored_event = events
    assert submitted_event.event_metadata["question_count"] == 2
    assert submitted_event.event_metadata["answer_count"] == 2
    assert submitted_event.event_metadata["assessment_scope"] == "course"
    assert scored_event.score == 2
    assert scored_event.max_score == 5
    assert scored_event.passed is False
    assert scored_event.event_metadata["score_snapshot"] == {
        "score": 2,
        "max_score": 5,
        "passed": False,
    }
    assert len(scored_event.event_metadata["answer_snapshot"]) == 2


def test_multiple_attempts_create_distinct_append_only_event_history(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    course = Course(id=uuid.uuid4(), title="Multi Attempt Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    current_user["value"] = admin
    assessment_response = client.post(
        "/api/assessments",
        json={
            "title": "Multi Attempt Check",
            "description": "Append-only audit",
            "course_id": str(course.id),
            "passing_score": 50,
            "max_attempts": 2,
            "questions": [
                {
                    "prompt": "Answer?",
                    "choices": ["A", "B"],
                    "correct_answer": "A",
                    "points": 1,
                    "order": 1,
                }
            ],
        },
    )
    assert assessment_response.status_code == 201
    assessment = assessment_response.json()

    current_user["value"] = student
    first = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={"answers": [{"question_id": assessment["questions"][0]["id"], "answer": "B"}]},
    )
    assert first.status_code == 200

    second = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={"answers": [{"question_id": assessment["questions"][0]["id"], "answer": "A"}]},
    )
    assert second.status_code == 200

    attempts = (
        db_session.query(StudentAssessmentAttempt)
        .filter_by(student_id=student.id, assessment_id=uuid.UUID(assessment["id"]))
        .order_by(StudentAssessmentAttempt.submitted_at)
        .all()
    )
    assert len(attempts) == 2
    assert attempts[0].id != attempts[1].id

    events = (
        db_session.query(AssessmentAttemptEvent)
        .filter(AssessmentAttemptEvent.student_id == student.id)
        .filter(AssessmentAttemptEvent.assessment_id == uuid.UUID(assessment["id"]))
        .all()
    )
    assert len(events) == 4
    assert {event.attempt_id for event in events} == {attempts[0].id, attempts[1].id}


def test_program_assessment_scoring_and_certification_still_work_with_attempt_events(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    badge = Badge(id=uuid.uuid4(), title="Certified", description="Earned certification")
    course_one = Course(id=uuid.uuid4(), title="Foundations", description="Course 1")
    course_two = Course(id=uuid.uuid4(), title="Capstone", description="Course 2")
    db_session.add_all([badge, course_one, course_two])
    db_session.commit()

    current_user["value"] = admin
    program_response = client.post(
        "/api/programs",
        json={
            "title": "Teacher Certification",
            "description": "Complete the full pathway",
            "course_links": [
                {"course_id": str(course_one.id), "order": 1, "is_required": True},
                {"course_id": str(course_two.id), "order": 2, "is_required": True},
            ],
        },
    )
    assert program_response.status_code == 201
    program_id = program_response.json()["id"]

    assessment_response = client.post(
        "/api/assessments",
        json={
            "title": "Certification Exam",
            "description": "Final assessment",
            "program_id": program_id,
            "passing_score": 80,
            "questions": [
                {
                    "prompt": "Core mission?",
                    "choices": ["Diaspora education", "Random trivia"],
                    "correct_answer": "Diaspora education",
                    "points": 5,
                    "order": 1,
                }
            ],
        },
    )
    assert assessment_response.status_code == 201
    assessment_id = assessment_response.json()["id"]
    question_id = assessment_response.json()["questions"][0]["id"]

    certification_response = client.post(
        "/api/certifications",
        json={
            "program_id": program_id,
            "badge_id": str(badge.id),
            "title": "EchoEd Certified Educator",
            "description": "Awarded for program completion and assessment mastery",
            "requirements": [
                {"requirement_type": "course_completion", "course_id": str(course_one.id)},
                {"requirement_type": "course_completion", "course_id": str(course_two.id)},
                {
                    "requirement_type": "assessment_pass",
                    "assessment_id": assessment_id,
                    "minimum_score": 80,
                },
            ],
        },
    )
    assert certification_response.status_code == 201
    certification_id = certification_response.json()["id"]

    current_user["value"] = student
    enroll_response = client.post(f"/api/programs/{program_id}/enroll")
    assert enroll_response.status_code == 200

    student_courses = db_session.query(StudentCourse).filter(StudentCourse.student_id == student.id).all()
    for student_course in student_courses:
        student_course.status = "completed"
    db_session.commit()

    submit_response = client.post(
        f"/api/assessments/{assessment_id}/attempts",
        json={"answers": [{"question_id": question_id, "answer": "Diaspora education"}]},
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["passed"] is True
    assert submit_response.json()["percentage"] == 100

    evaluation_response = client.post(f"/api/certifications/{certification_id}/evaluate")
    assert evaluation_response.status_code == 200
    body = evaluation_response.json()
    assert body["awarded"] is True
    assert body["missing_requirements"] == []

    issued = db_session.query(StudentCertification).filter(StudentCertification.student_id == student.id).all()
    assert len(issued) == 1

    awarded_badge = db_session.query(StudentBadge).filter(StudentBadge.student_id == student.id).first()
    assert awarded_badge is not None
    assert awarded_badge.badge_id == badge.id

    attempt = (
        db_session.query(StudentAssessmentAttempt)
        .filter_by(student_id=student.id, assessment_id=uuid.UUID(assessment_id))
        .one()
    )
    events = db_session.query(AssessmentAttemptEvent).filter_by(attempt_id=attempt.id).all()
    assert len(events) == 2
    assert {event.event_type for event in events} == {"attempt_submitted", "attempt_scored"}
