import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import assessments, certifications, programs
from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Assessment,
    Badge,
    Course,
    Program,
    StudentAssessmentAttempt,
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


def test_learner_can_fetch_and_submit_available_assessment(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    badge = Badge(id=uuid.uuid4(), title="Certified", description="Earned certification")
    course = Course(id=uuid.uuid4(), title="Available Course", description="Testing")
    db_session.add_all([badge, course])
    db_session.commit()

    current_user["value"] = admin
    program_response = client.post(
        "/api/programs",
        json={
            "title": "Availability Program",
            "description": "Program for assessment delivery",
            "course_links": [
                {"course_id": str(course.id), "order": 1, "is_required": True},
            ],
        },
    )
    assert program_response.status_code == 201
    program_id = program_response.json()["id"]

    assessment_response = client.post(
        "/api/assessments",
        json={
            "title": "Available Exam",
            "description": "Learner ready",
            "program_id": program_id,
            "passing_score": 80,
            "questions": [
                {
                    "prompt": "Which answer is correct?",
                    "choices": ["A", "B"],
                    "correct_answer": "A",
                    "points": 2,
                    "order": 1,
                },
                {
                    "prompt": "EchoEd focus?",
                    "choices": ["History", "Chemistry"],
                    "correct_answer": "History",
                    "points": 3,
                    "order": 2,
                },
            ],
        },
    )
    assert assessment_response.status_code == 201
    assessment = assessment_response.json()

    current_user["value"] = student
    enroll_response = client.post(f"/api/programs/{program_id}/enroll")
    assert enroll_response.status_code == 200

    fetch_response = client.get(f"/api/assessments/{assessment['id']}")
    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert fetched["is_available_for_learner"] is True
    assert fetched["learner_delivery_state"] == "available"
    assert len(fetched["questions"]) == 2

    submit_response = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={
            "answers": [
                {"question_id": assessment["questions"][0]["id"], "answer": "A"},
                {"question_id": assessment["questions"][1]["id"], "answer": "History"},
            ]
        },
    )
    assert submit_response.status_code == 200
    body = submit_response.json()
    assert body["score"] == 5
    assert body["max_score"] == 5
    assert body["percentage"] == 100
    assert body["passed"] is True

    student_courses = db_session.query(StudentCourse).filter(StudentCourse.student_id == student.id).all()
    for student_course in student_courses:
        student_course.status = "completed"
    db_session.commit()

    current_user["value"] = admin
    certification_response = client.post(
        "/api/certifications",
        json={
            "program_id": program_id,
            "badge_id": str(badge.id),
            "title": "EchoEd Certified",
            "description": "Awarded for assessment and coursework",
            "requirements": [
                {"requirement_type": "course_completion", "course_id": str(course.id)},
                {
                    "requirement_type": "assessment_pass",
                    "assessment_id": assessment["id"],
                    "minimum_score": 80,
                },
            ],
        },
    )
    assert certification_response.status_code == 201
    certification_id = certification_response.json()["id"]

    current_user["value"] = student
    evaluation_response = client.post(f"/api/certifications/{certification_id}/evaluate")
    assert evaluation_response.status_code == 200
    evaluation = evaluation_response.json()
    assert evaluation["awarded"] is True
    assert evaluation["missing_requirements"] == []

    issued = db_session.query(StudentCertification).filter(StudentCertification.student_id == student.id).all()
    assert len(issued) == 1


def test_learner_fetch_of_unavailable_assessment_returns_explicit_delivery_state(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    course = Course(id=uuid.uuid4(), title="Blocked Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    current_user["value"] = admin
    assessment_response = client.post(
        "/api/assessments",
        json={
            "title": "Blocked Exam",
            "description": "Learner blocked",
            "course_id": str(course.id),
            "availability_state": "unavailable",
            "questions": [
                {
                    "prompt": "Blocked?",
                    "choices": ["Yes", "No"],
                    "correct_answer": "Yes",
                    "points": 1,
                    "order": 1,
                }
            ],
        },
    )
    assert assessment_response.status_code == 201
    unavailable_assessment = assessment_response.json()

    current_user["value"] = student
    fetch_response = client.get(f"/api/assessments/{unavailable_assessment['id']}")
    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert fetched["id"] == unavailable_assessment["id"]
    assert fetched["title"] == "Blocked Exam"
    assert fetched["is_available_for_learner"] is False
    assert fetched["learner_delivery_state"] == "unavailable"
    assert fetched["learner_delivery_detail"] == "This assessment is currently unavailable."
    assert fetched["questions"] == []


def test_learner_cannot_submit_unavailable_assessment_and_no_attempt_is_created(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    course = Course(id=uuid.uuid4(), title="Locked Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    current_user["value"] = admin
    assessment_response = client.post(
        "/api/assessments",
        json={
            "title": "Locked Exam",
            "description": "Submission blocked",
            "course_id": str(course.id),
            "assessment_state": "published",
            "availability_state": "unavailable",
            "questions": [
                {
                    "prompt": "Locked?",
                    "choices": ["Yes", "No"],
                    "correct_answer": "Yes",
                    "points": 1,
                    "order": 1,
                }
            ],
        },
    )
    assert assessment_response.status_code == 201
    blocked_assessment = assessment_response.json()

    current_user["value"] = student
    submit_response = client.post(
        f"/api/assessments/{blocked_assessment['id']}/attempts",
        json={"answers": []},
    )
    assert submit_response.status_code == 403
    detail = submit_response.json()["detail"]
    assert detail["learner_delivery_state"] == "unavailable"
    assert detail["learner_delivery_detail"] == "This assessment is currently unavailable."

    attempts = db_session.query(StudentAssessmentAttempt).filter_by(assessment_id=uuid.UUID(blocked_assessment["id"])).all()
    assert attempts == []


def test_admin_can_inspect_unavailable_or_draft_assessment_with_questions(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    course = Course(id=uuid.uuid4(), title="Admin Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    current_user["value"] = admin
    assessment_response = client.post(
        "/api/assessments",
        json={
            "title": "Draft Exam",
            "description": "Admin can inspect",
            "course_id": str(course.id),
            "assessment_state": "draft",
            "availability_state": "pending_review",
            "questions": [
                {
                    "prompt": "Inspect?",
                    "choices": ["Yes", "No"],
                    "correct_answer": "Yes",
                    "points": 1,
                    "order": 1,
                }
            ],
        },
    )
    assert assessment_response.status_code == 201
    draft_assessment = assessment_response.json()

    fetch_response = client.get(f"/api/assessments/{draft_assessment['id']}")
    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert fetched["is_available_for_learner"] is False
    assert fetched["learner_delivery_state"] == "draft"
    assert fetched["questions"]
