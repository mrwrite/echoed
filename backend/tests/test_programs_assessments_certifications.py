import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import assessments, certifications, programs
from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Badge,
    Course,
    Program,
    StudentBadge,
    StudentCertification,
    StudentCourse,
    StudentProgramProgress,
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

    client = TestClient(app)
    return client, current_user


@pytest.fixture
def seeded_users(db_session):
    admin = User(
        id=uuid.uuid4(),
        firstname="Admin",
        lastname="User",
        username=f"admin_{uuid.uuid4()}",
        email=f"admin_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="admin",
    )
    student = User(
        id=uuid.uuid4(),
        firstname="Student",
        lastname="User",
        username=f"student_{uuid.uuid4()}",
        email=f"student_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    db_session.add_all([admin, student])
    db_session.commit()
    return admin, student


def test_program_enrollment_creates_student_courses_and_progress(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    course_one = Course(id=uuid.uuid4(), title="Roots I", description="Foundations")
    course_two = Course(id=uuid.uuid4(), title="Roots II", description="Advanced")
    db_session.add_all([course_one, course_two])
    db_session.commit()

    current_user["value"] = admin
    create_response = client.post(
        "/api/programs",
        json={
            "title": "Diaspora Foundations",
            "description": "Structured certification path",
            "course_links": [
                {"course_id": str(course_one.id), "order": 1, "is_required": True},
                {"course_id": str(course_two.id), "order": 2, "is_required": True},
            ],
        },
    )

    assert create_response.status_code == 201
    program_id = create_response.json()["id"]

    current_user["value"] = student
    enroll_response = client.post(f"/api/programs/{program_id}/enroll")

    assert enroll_response.status_code == 200
    body = enroll_response.json()
    assert body["completed_courses"] == 0
    assert body["total_courses"] == 2
    assert body["completion_percentage"] == 0

    enrollments = db_session.query(StudentCourse).filter(StudentCourse.student_id == student.id).all()
    assert len(enrollments) == 2

    progress = (
        db_session.query(StudentProgramProgress)
        .filter(
            StudentProgramProgress.student_id == student.id,
            StudentProgramProgress.program_id == uuid.UUID(program_id),
        )
        .first()
    )
    assert progress is not None
    assert progress.status == "active"


def test_assessment_attempt_scores_answers_and_respects_max_attempts(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    course = Course(id=uuid.uuid4(), title="Assessment Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    current_user["value"] = admin
    create_response = client.post(
        "/api/assessments",
        json={
            "title": "Program Entrance Quiz",
            "description": "Measure readiness",
            "course_id": str(course.id),
            "passing_score": 50,
            "max_attempts": 1,
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

    assert create_response.status_code == 201
    assessment = create_response.json()

    current_user["value"] = student
    submit_response = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={
            "answers": [
                {"question_id": assessment["questions"][0]["id"], "answer": "A"},
                {"question_id": assessment["questions"][1]["id"], "answer": "Chemistry"},
            ]
        },
    )

    assert submit_response.status_code == 200
    body = submit_response.json()
    assert body["score"] == 2
    assert body["max_score"] == 5
    assert body["percentage"] == 40
    assert body["passed"] is False

    second_attempt = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={
            "answers": [
                {"question_id": assessment["questions"][0]["id"], "answer": "A"},
                {"question_id": assessment["questions"][1]["id"], "answer": "History"},
            ]
        },
    )
    assert second_attempt.status_code == 400
    assert second_attempt.json()["detail"] == "Maximum attempts reached"


def test_certification_evaluation_issues_certificate_and_badge(api_client, seeded_users, db_session):
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

    stored_program = db_session.get(Program, uuid.UUID(program_id))
    progress = (
        db_session.query(StudentProgramProgress)
        .filter(
            StudentProgramProgress.student_id == student.id,
            StudentProgramProgress.program_id == stored_program.id,
        )
        .first()
    )
    assert progress is not None
    assert progress.status == "completed"
