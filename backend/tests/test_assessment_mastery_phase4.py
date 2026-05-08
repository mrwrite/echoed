import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import analytics, assessments, certifications, programs
from app.database import get_db
from app.deps import get_current_user
from app.models import (
    AssessmentCompetencyAlignment,
    Badge,
    Course,
    Program,
    StudentCourse,
    StudentCertification,
    StudentUnitProgress,
    SegmentProgress,
    User,
)


@pytest.fixture
def api_client(db_session):
    app = FastAPI()
    app.include_router(programs.router, prefix="/api")
    app.include_router(assessments.router, prefix="/api")
    app.include_router(certifications.router, prefix="/api")
    app.include_router(analytics.router, prefix="/api")

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


def test_assessment_competency_alignment_serializes_and_resolves_question_order(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, _student = seeded_users
    current_user["value"] = admin

    course = Course(id=uuid.uuid4(), title="Mastery Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    response = client.post(
        "/api/assessments",
        json={
            "title": "Aligned Assessment",
            "description": "Alignment metadata",
            "course_id": str(course.id),
            "questions": [
                {
                    "prompt": "Question 1",
                    "choices": ["A", "B"],
                    "correct_answer": "A",
                    "points": 1,
                    "order": 1,
                },
                {
                    "prompt": "Question 2",
                    "choices": ["Yes", "No"],
                    "correct_answer": "Yes",
                    "points": 1,
                    "order": 2,
                },
            ],
            "competency_alignments": [
                {
                    "objective_key": "fractions",
                    "objective_title": "Fractions",
                    "objective_type": "objective",
                    "weight": 1,
                    "mastery_threshold": 80,
                },
                {
                    "objective_key": "fractions-addition",
                    "objective_title": "Add Fractions",
                    "objective_type": "competency",
                    "weight": 2,
                    "mastery_threshold": 75,
                    "question_order": 2,
                },
            ],
        },
    )

    assert response.status_code == 201
    assessment = response.json()
    assert len(assessment["competency_alignments"]) == 2
    assert db_session.query(AssessmentCompetencyAlignment).filter_by(assessment_id=uuid.UUID(assessment["id"])).count() == 2

    objective_alignment = next(item for item in assessment["competency_alignments"] if item["objective_key"] == "fractions")
    question_alignment = next(item for item in assessment["competency_alignments"] if item["objective_key"] == "fractions-addition")

    assert objective_alignment["question_id"] is None
    assert question_alignment["question_id"] == assessment["questions"][1]["id"]

    fetch_response = client.get(f"/api/assessments/{assessment['id']}")
    assert fetch_response.status_code == 200
    fetched = fetch_response.json()
    assert len(fetched["competency_alignments"]) == 2
    assert fetched["competency_alignments"][0]["assessment_id"] == assessment["id"]


def test_mastery_summary_derives_deterministically_from_latest_attempt_and_does_not_mutate_progress(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    badge = Badge(id=uuid.uuid4(), title="Certified", description="Earned certification")
    course = Course(id=uuid.uuid4(), title="Progress Course", description="Testing")
    db_session.add_all([badge, course])
    db_session.commit()

    current_user["value"] = admin
    program_response = client.post(
        "/api/programs",
        json={
            "title": "Progress Program",
            "description": "Program for mastery testing",
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
            "title": "Mastery Check",
            "description": "Latest attempt should win",
            "course_id": str(course.id),
            "passing_score": 80,
            "max_attempts": 3,
            "questions": [
                {
                    "prompt": "Question 1",
                    "choices": ["A", "B"],
                    "correct_answer": "A",
                    "points": 2,
                    "order": 1,
                },
                {
                    "prompt": "Question 2",
                    "choices": ["Yes", "No"],
                    "correct_answer": "Yes",
                    "points": 3,
                    "order": 2,
                },
            ],
            "competency_alignments": [
                {
                    "objective_key": "algebra",
                    "objective_title": "Algebra",
                    "objective_type": "competency",
                    "weight": 1,
                    "mastery_threshold": 80,
                }
            ],
        },
    )
    assert assessment_response.status_code == 201
    assessment = assessment_response.json()

    current_user["value"] = student
    enroll_response = client.post(f"/api/programs/{program_id}/enroll")
    assert enroll_response.status_code == 200

    before_courses = [(item.id, item.status) for item in db_session.query(StudentCourse).all()]
    before_unit_progress = db_session.query(StudentUnitProgress).count()
    before_segment_progress = db_session.query(SegmentProgress).count()

    first_attempt = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={
            "answers": [
                {"question_id": assessment["questions"][0]["id"], "answer": "B"},
                {"question_id": assessment["questions"][1]["id"], "answer": "No"},
            ]
        },
    )
    assert first_attempt.status_code == 200

    second_attempt = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={
            "answers": [
                {"question_id": assessment["questions"][0]["id"], "answer": "A"},
                {"question_id": assessment["questions"][1]["id"], "answer": "Yes"},
            ]
        },
    )
    assert second_attempt.status_code == 200

    summary_one = client.get(f"/api/analytics/mastery-summary?course_id={course.id}")
    summary_two = client.get(f"/api/analytics/mastery-summary?course_id={course.id}")
    assert summary_one.status_code == 200
    assert summary_two.status_code == 200
    assert summary_one.json() == summary_two.json()

    summary = summary_one.json()
    assert summary["student_id"] == str(student.id)
    assert len(summary["objectives"]) == 1
    objective = summary["objectives"][0]
    assert objective["objective_key"] == "algebra"
    assert objective["mastered"] is True
    assert objective["mastery_percentage"] == 100.0
    assert objective["attempts_considered"] == 1

    after_courses = [(item.id, item.status) for item in db_session.query(StudentCourse).all()]
    after_unit_progress = db_session.query(StudentUnitProgress).count()
    after_segment_progress = db_session.query(SegmentProgress).count()

    assert before_courses == after_courses
    assert before_unit_progress == after_unit_progress
    assert before_segment_progress == after_segment_progress


def test_unsubmitted_or_unavailable_assessments_do_not_generate_mastery(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users
    current_user["value"] = admin

    course = Course(id=uuid.uuid4(), title="Blocked Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    unavailable_response = client.post(
        "/api/assessments",
        json={
            "title": "Blocked Assessment",
            "description": "Unavailable for learners",
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
            "competency_alignments": [
                {
                    "objective_key": "blocked-objective",
                    "objective_title": "Blocked Objective",
                    "objective_type": "objective",
                    "weight": 1,
                    "mastery_threshold": 80,
                }
            ],
        },
    )
    assert unavailable_response.status_code == 201
    assessment = unavailable_response.json()

    current_user["value"] = student
    blocked_submit = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={"answers": []},
    )
    assert blocked_submit.status_code == 403

    summary_response = client.get(f"/api/analytics/mastery-summary?course_id={course.id}")
    assert summary_response.status_code == 200
    assert summary_response.json()["objectives"] == []


def test_unsubmitted_assessments_do_not_generate_mastery(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users
    current_user["value"] = admin

    course = Course(id=uuid.uuid4(), title="Unsubmitted Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    assessment_response = client.post(
        "/api/assessments",
        json={
            "title": "Unsubmitted Assessment",
            "description": "Never attempted",
            "course_id": str(course.id),
            "questions": [
                {
                    "prompt": "Unsubmitted?",
                    "choices": ["Yes", "No"],
                    "correct_answer": "Yes",
                    "points": 1,
                    "order": 1,
                }
            ],
            "competency_alignments": [
                {
                    "objective_key": "never-attempted",
                    "objective_title": "Never Attempted",
                    "objective_type": "objective",
                    "weight": 1,
                    "mastery_threshold": 80,
                }
            ],
        },
    )
    assert assessment_response.status_code == 201

    current_user["value"] = student
    summary_response = client.get(f"/api/analytics/mastery-summary?course_id={course.id}")
    assert summary_response.status_code == 200
    assert summary_response.json()["objectives"] == []


def test_program_scoring_and_certification_still_work_with_mastery_alignment_metadata(api_client, seeded_users, db_session):
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
            "competency_alignments": [
                {
                    "objective_key": "mission",
                    "objective_title": "Core Mission",
                    "objective_type": "objective",
                    "weight": 1,
                    "mastery_threshold": 80,
                }
            ],
        },
    )
    assert assessment_response.status_code == 201
    assessment = assessment_response.json()

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
                    "assessment_id": assessment["id"],
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
    for student_course in db_session.query(StudentCourse).filter(StudentCourse.student_id == student.id).all():
        student_course.status = "completed"
    db_session.commit()

    submit_response = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={"answers": [{"question_id": assessment["questions"][0]["id"], "answer": "Diaspora education"}]},
    )
    assert submit_response.status_code == 200
    assert submit_response.json()["passed"] is True

    evaluation_response = client.post(f"/api/certifications/{certification_id}/evaluate")
    assert evaluation_response.status_code == 200
    evaluation = evaluation_response.json()
    assert evaluation["awarded"] is True
    assert evaluation["missing_requirements"] == []

    issued = db_session.query(StudentCertification).filter(StudentCertification.student_id == student.id).all()
    assert len(issued) == 1
