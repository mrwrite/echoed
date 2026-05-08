import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import assessments, certifications, programs
from app.database import get_db
from app.deps import get_current_user
from app.models import Assessment, Badge, Course, Lesson, Program, StudentBadge, StudentCertification, StudentCourse, Unit, User


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


def test_program_assessment_flow_remains_backward_compatible(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    course_one = Course(id=uuid.uuid4(), title="Roots I", description="Foundations")
    course_two = Course(id=uuid.uuid4(), title="Roots II", description="Advanced")
    badge = Badge(id=uuid.uuid4(), title="Certified", description="Earned certification")
    db_session.add_all([course_one, course_two, badge])
    db_session.commit()

    current_user["value"] = admin
    program_response = client.post(
        "/api/programs",
        json={
            "title": "Assessment Pathway",
            "description": "Program with a canonical assessment",
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
            "title": "Program Entrance Quiz",
            "description": "Measure readiness",
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
    assert assessment["assessment_scope"] == "program"
    assert assessment["assessment_state"] == "published"
    assert assessment["availability_state"] == "available"
    assert assessment["unit_id"] is None
    assert assessment["policy_metadata"] == {}
    assert assessment["lifecycle_metadata"] == {}

    current_user["value"] = student
    enroll_response = client.post(f"/api/programs/{program_id}/enroll")
    assert enroll_response.status_code == 200

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
                {"requirement_type": "course_completion", "course_id": str(course_one.id)},
                {"requirement_type": "course_completion", "course_id": str(course_two.id)},
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
    body = evaluation_response.json()
    assert body["awarded"] is True
    assert body["missing_requirements"] == []

    issued = db_session.query(StudentCertification).filter(StudentCertification.student_id == student.id).all()
    assert len(issued) == 1

    awarded_badge = db_session.query(StudentBadge).filter(StudentBadge.student_id == student.id).first()
    assert awarded_badge is not None
    assert awarded_badge.badge_id == badge.id


def test_assessment_create_validates_scope_and_state(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, _student = seeded_users
    current_user["value"] = admin

    course = Course(id=uuid.uuid4(), title="Scope Course", description="Testing")
    unit = Unit(id=uuid.uuid4(), course_id=course.id, title="Scope Unit", content="Unit content", order=1)
    db_session.add_all([course, unit])
    db_session.commit()

    missing_scope = client.post(
        "/api/assessments",
        json={
            "title": "Missing Scope",
            "description": "Should fail",
            "passing_score": 70,
            "questions": [],
        },
    )
    assert missing_scope.status_code == 422
    assert "exactly one of lesson, unit, course, or program" in str(missing_scope.json())

    mismatched_scope = client.post(
        "/api/assessments",
        json={
            "title": "Mismatched Scope",
            "description": "Should fail",
            "lesson_id": str(uuid.uuid4()),
            "assessment_scope": "course",
            "questions": [],
        },
    )
    assert mismatched_scope.status_code == 422
    assert "scope must match the provided target field" in str(mismatched_scope.json()).lower()

    invalid_state = client.post(
        "/api/assessments",
        json={
            "title": "Invalid State",
            "description": "Should fail",
            "unit_id": str(unit.id),
            "assessment_scope": "unit",
            "assessment_state": "retired",
            "questions": [],
        },
    )
    assert invalid_state.status_code == 422
    assert "assessment state must be draft, published, or archived" in str(invalid_state.json()).lower()


def test_unit_scope_assessment_supports_additive_future_compatibility(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, _student = seeded_users
    current_user["value"] = admin

    course = Course(id=uuid.uuid4(), title="Unit Course", description="Testing")
    unit = Unit(id=uuid.uuid4(), course_id=course.id, title="Unit One", content="Unit content", order=1)
    db_session.add_all([course, unit])
    db_session.commit()

    create_response = client.post(
        "/api/assessments",
        json={
            "title": "Unit Check",
            "description": "Future unit scope support",
            "unit_id": str(unit.id),
            "assessment_scope": "unit",
            "questions": [
                {
                    "prompt": "Unit question?",
                    "choices": ["Yes", "No"],
                    "correct_answer": "Yes",
                    "points": 1,
                    "order": 1,
                }
            ],
        },
    )

    assert create_response.status_code == 201
    body = create_response.json()
    assert body["unit_id"] == str(unit.id)
    assert body["assessment_scope"] == "unit"

    list_response = client.get(f"/api/assessments?unit_id={unit.id}")
    assert list_response.status_code == 200
    listed = list_response.json()
    assert len(listed) == 1
    assert listed[0]["id"] == body["id"]
    assert listed[0]["assessment_scope"] == "unit"


@pytest.mark.parametrize(
    "payload_key, expected_scope",
    [
        ("lesson_id", "lesson"),
        ("course_id", "course"),
        ("program_id", "program"),
        ("unit_id", "unit"),
    ],
)
def test_assessment_scope_matches_selected_target(api_client, seeded_users, db_session, payload_key, expected_scope):
    client, current_user = api_client
    admin, _student = seeded_users
    current_user["value"] = admin

    course = Course(id=uuid.uuid4(), title="Scope Matrix Course", description="Testing")
    unit = Unit(id=uuid.uuid4(), course_id=course.id, title="Scope Matrix Unit", content="Unit content", order=1)
    lesson = Lesson(id=uuid.uuid4(), unit_id=unit.id, title="Scope Matrix Lesson")
    program = Program(id=uuid.uuid4(), title="Scope Matrix Program", description="Testing")
    db_session.add_all([course, unit, lesson, program])
    db_session.commit()

    targets = {
        "unit_id": unit.id,
        "lesson_id": lesson.id,
        "course_id": course.id,
        "program_id": program.id,
    }

    payload = {
        "title": f"{expected_scope.title()} Assessment",
        "description": "Scope validation",
        "questions": [
            {
                "prompt": "Scope?",
                "choices": ["Yes", "No"],
                "correct_answer": "Yes",
                "points": 1,
                "order": 1,
            }
        ],
    }
    payload[payload_key] = str(targets[payload_key])
    if payload_key == "unit_id":
        payload["assessment_scope"] = "unit"
    elif payload_key == "lesson_id":
        payload["assessment_scope"] = "lesson"
    elif payload_key == "course_id":
        payload["assessment_scope"] = "course"
    else:
        payload["assessment_scope"] = "program"

    response = client.post("/api/assessments", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["assessment_scope"] == expected_scope
    assert body[payload_key] == str(targets[payload_key])


def test_legacy_assessment_rows_serialize_with_derived_defaults(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, _student = seeded_users
    current_user["value"] = admin

    course = Course(id=uuid.uuid4(), title="Legacy Course", description="Legacy testing")
    db_session.add(course)
    db_session.commit()

    legacy_assessment = Assessment(
        id=uuid.uuid4(),
        title="Legacy Assessment",
        description="Pre-metadata row",
        course_id=course.id,
        passing_score=75,
        max_attempts=2,
        created_by=admin.id,
    )
    db_session.add(legacy_assessment)
    db_session.commit()

    response = client.get(f"/api/assessments/{legacy_assessment.id}")
    assert response.status_code == 200
    body = response.json()
    assert body["assessment_scope"] == "course"
    assert body["assessment_state"] == "published"
    assert body["availability_state"] == "available"
    assert body["policy_metadata"] == {}
    assert body["lifecycle_metadata"] == {}
    assert body["unit_id"] is None
