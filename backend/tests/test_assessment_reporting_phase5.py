import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import analytics, assessments, certifications, programs
from app.database import get_db
from app.deps import get_current_user
from app.models import (
    Badge,
    Course,
    SegmentProgress,
    StudentCertification,
    StudentCourse,
    StudentUnitProgress,
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


def test_reporting_summary_matches_attempt_evidence_and_mastery_output(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    course = Course(id=uuid.uuid4(), title="Reporting Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    current_user["value"] = admin
    assessment_response = client.post(
        "/api/assessments",
        json={
            "title": "Reporting Check",
            "description": "Evidence-backed reporting",
            "course_id": str(course.id),
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
                    "objective_key": "reporting-objective",
                    "objective_title": "Reporting Objective",
                    "objective_type": "objective",
                    "weight": 1,
                    "mastery_threshold": 80,
                }
            ],
        },
    )
    assert assessment_response.status_code == 201
    assessment = assessment_response.json()

    current_user["value"] = student
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

    report_response = client.get(f"/api/analytics/reporting-summary?course_id={course.id}")
    mastery_response = client.get(f"/api/analytics/mastery-summary?course_id={course.id}")
    assert report_response.status_code == 200
    assert mastery_response.status_code == 200

    report = report_response.json()
    mastery = mastery_response.json()
    assert report["mastery_summary"] == mastery
    assert len(report["assessment_evidence"]) == 1
    evidence = report["assessment_evidence"][0]
    assert evidence["assessment_id"] == assessment["id"]
    assert evidence["attempt_count"] == 2
    assert evidence["passed_attempt_count"] == 1
    assert evidence["scored_event_count"] == 2
    assert evidence["submitted_event_count"] == 2
    assert evidence["latest_event_metadata"]["score_snapshot"]["passed"] is True


def test_reporting_ignores_unavailable_and_unsubmitted_assessments(api_client, seeded_users, db_session):
    client, current_user = api_client
    admin, student = seeded_users

    course = Course(id=uuid.uuid4(), title="Ignored Reporting Course", description="Testing")
    db_session.add(course)
    db_session.commit()

    current_user["value"] = admin
    unavailable_response = client.post(
        "/api/assessments",
        json={
            "title": "Unavailable Reporting Check",
            "description": "No learner evidence",
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

    unsubmitted_response = client.post(
        "/api/assessments",
        json={
            "title": "Unsubmitted Reporting Check",
            "description": "No learner evidence",
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
                    "objective_key": "unsubmitted-objective",
                    "objective_title": "Unsubmitted Objective",
                    "objective_type": "objective",
                    "weight": 1,
                    "mastery_threshold": 80,
                }
            ],
        },
    )
    assert unsubmitted_response.status_code == 201

    current_user["value"] = student
    report_response = client.get(f"/api/analytics/reporting-summary?course_id={course.id}")
    assert report_response.status_code == 200
    report = report_response.json()
    assert report["assessment_evidence"] == []
    assert report["mastery_summary"]["objectives"] == []


def test_reporting_is_read_only_and_certification_compatibility_remains_unchanged(api_client, seeded_users, db_session):
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
            "title": "Reporting Program",
            "description": "Program for read-only reporting",
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
            "title": "Reporting Certification Exam",
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
            "title": "Reporting Certified",
            "description": "Awarded for reporting test",
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

    before_progress = {
        "student_courses": [(row.id, row.status) for row in db_session.query(StudentCourse).order_by(StudentCourse.id).all()],
        "student_unit_progress": [(row.id, row.status) for row in db_session.query(StudentUnitProgress).order_by(StudentUnitProgress.id).all()],
        "segment_progress": [(row.id, row.status) for row in db_session.query(SegmentProgress).order_by(SegmentProgress.id).all()],
        "student_certifications": [(row.id, row.certification_id) for row in db_session.query(StudentCertification).order_by(StudentCertification.id).all()],
    }

    report_response = client.get(f"/api/analytics/reporting-summary?program_id={program_id}")
    assert report_response.status_code == 200

    after_progress = {
        "student_courses": [(row.id, row.status) for row in db_session.query(StudentCourse).order_by(StudentCourse.id).all()],
        "student_unit_progress": [(row.id, row.status) for row in db_session.query(StudentUnitProgress).order_by(StudentUnitProgress.id).all()],
        "segment_progress": [(row.id, row.status) for row in db_session.query(SegmentProgress).order_by(SegmentProgress.id).all()],
        "student_certifications": [(row.id, row.certification_id) for row in db_session.query(StudentCertification).order_by(StudentCertification.id).all()],
    }
    assert before_progress == after_progress

    submit_response = client.post(
        f"/api/assessments/{assessment['id']}/attempts",
        json={"answers": [{"question_id": assessment["questions"][0]["id"], "answer": "Diaspora education"}]},
    )
    assert submit_response.status_code == 200

    evaluation_response = client.post(f"/api/certifications/{certification_id}/evaluate")
    assert evaluation_response.status_code == 200
    evaluation = evaluation_response.json()
    assert evaluation["awarded"] is True
    assert evaluation["missing_requirements"] == []

    issued = db_session.query(StudentCertification).filter(StudentCertification.student_id == student.id).all()
    assert len(issued) == 1
