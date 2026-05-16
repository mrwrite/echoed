import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app import seed_demo
from app.api.routes import analytics, assessments, courses
from app.crud import progress as progress_crud
from app.database import get_db
from app.deps import get_current_user
from app.models import Assessment, Course, StudentAssessmentAttempt, StudentCertification, StudentCourse, User


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


def _create_user(session, *, role: str, first: str, last: str, username_prefix: str) -> User:
    token = uuid.uuid4().hex[:8]
    user = User(
        id=uuid.uuid4(),
        firstname=first,
        lastname=last,
        username=f"{username_prefix}_{token}",
        email=f"{username_prefix}_{token}@example.com",
        hashed_password="hashed",
        role=role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def _enroll_student(session, student: User, course: Course, *, status: str = "active") -> StudentCourse:
    student_course = StudentCourse(student_id=student.id, course_id=course.id, status=status)
    session.add(student_course)
    session.commit()
    session.refresh(student_course)
    return student_course


def _submit_flagship_attempt(client: TestClient, assessment_id, answers):
    fetch_response = client.get(f"/api/assessments/{assessment_id}")
    assert fetch_response.status_code == 200
    questions = fetch_response.json()["questions"]
    submit_response = client.post(
        f"/api/assessments/{assessment_id}/attempts",
        json={
            "answers": [
                {"question_id": questions[index]["id"], "answer": answer}
                for index, answer in enumerate(answers)
            ]
        },
    )
    assert submit_response.status_code == 200


def test_educator_runtime_support_endpoint_reports_remediation_enrichment_normal_and_completed(
    db_engine, monkeypatch
):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    client, current_user = _build_api_client(session_factory)

    session = session_factory()
    try:
        teacher = _create_user(
            session,
            role="teacher",
            first="Teacher",
            last="Viewer",
            username_prefix="runtime_teacher",
        )
        remediation_student = _create_user(
            session,
            role="student",
            first="Amara",
            last="Review",
            username_prefix="runtime_student",
        )
        enrichment_student = _create_user(
            session,
            role="student",
            first="Biko",
            last="Extension",
            username_prefix="runtime_student",
        )
        normal_student = _create_user(
            session,
            role="student",
            first="Chika",
            last="Steady",
            username_prefix="runtime_student",
        )
        completed_student = _create_user(
            session,
            role="student",
            first="Dara",
            last="Complete",
            username_prefix="runtime_student",
        )
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        remediation_course = _enroll_student(session, remediation_student, course)
        enrichment_course = _enroll_student(session, enrichment_student, course)
        _enroll_student(session, normal_student, course)
        completed_course = _enroll_student(session, completed_student, course, status="completed")
        lesson_assessment = (
            session.query(Assessment)
            .filter(Assessment.title == "Introduction to Africa Lesson Check")
            .one()
        )

        current_user["value"] = remediation_student
        _submit_flagship_attempt(
            client,
            lesson_assessment.id,
            ["Africa is one country.", "It does not matter."],
        )

        current_user["value"] = enrichment_student
        _submit_flagship_attempt(
            client,
            lesson_assessment.id,
            ["Africa is a diverse continent.", "Because places and people deserve respect."],
        )

        before_remediation_state = progress_crud.resolve_governed_progression(session, remediation_course.id)
        before_completed_state = progress_crud.resolve_governed_progression(session, completed_course.id)
        attempts_before = session.query(StudentAssessmentAttempt).count()
        certifications_before = session.query(StudentCertification).count()

        current_user["value"] = teacher
        response = client.get(f"/api/analytics/educator-runtime-support?course_id={course.id}")
        assert response.status_code == 200
        payload = response.json()
        expected_names = [
            "Amara Review",
            "Biko Extension",
            "Chika Steady",
            "Dara Complete",
        ]
        payload_names = [row["student_name"] for row in payload]
        assert all(name in payload_names for name in expected_names)

        by_name = {row["student_name"]: row for row in payload}
        remediation_row = by_name["Amara Review"]
        assert remediation_row["support_state"] == "remediation"
        assert remediation_row["course_title"] == seed_demo.DEMO_COURSE_TITLE
        assert remediation_row["recommended_action"] == "review-and-continue"
        assert remediation_row["context_lesson_title"] == "Introduction to Africa"
        assert remediation_row["context_prompts"]
        assert remediation_row["educator_intervention_hint"]
        assert "benefit from brief review" in remediation_row["support_summary"]
        assert remediation_row["last_evidence_at"] is not None

        enrichment_row = by_name["Biko Extension"]
        assert enrichment_row["support_state"] == "enrichment"
        assert enrichment_row["recommended_action"] == "continue-with-enrichment"
        assert enrichment_row["context_lesson_title"] == "Introduction to Africa"
        assert enrichment_row["context_key_concepts"]
        assert enrichment_row["context_prompts"]
        assert "optional enrichment" in enrichment_row["support_summary"]
        assert enrichment_row["last_evidence_at"] is not None

        normal_row = by_name["Chika Steady"]
        assert normal_row["support_state"] == "normal"
        assert normal_row["recommended_action"] == "continue"
        assert "normal continuation" in normal_row["support_summary"].lower()
        assert "governed lesson path" in normal_row["support_summary"].lower()

        completed_row = by_name["Dara Complete"]
        assert completed_row["support_state"] == "completed"
        assert completed_row["recommended_action"] == "celebrate-and-reflect"
        assert "completed the current flagship pathway" in completed_row["support_summary"]

        after_remediation_state = progress_crud.resolve_governed_progression(session, remediation_course.id)
        after_completed_state = progress_crud.resolve_governed_progression(session, completed_course.id)
        assert before_remediation_state["delivery_state"] == after_remediation_state["delivery_state"]
        assert before_remediation_state["lesson_id"] == after_remediation_state["lesson_id"]
        assert before_completed_state["delivery_state"] == after_completed_state["delivery_state"]
        assert before_completed_state["lesson_id"] == after_completed_state["lesson_id"]
        assert session.query(StudentAssessmentAttempt).count() == attempts_before
        assert session.query(StudentCertification).count() == certifications_before
    finally:
        session.close()


def test_educator_runtime_support_is_flagship_only_and_reporting_summary_stays_compatible(
    db_engine, monkeypatch
):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)
    client, current_user = _build_api_client(session_factory)

    session = session_factory()
    try:
        student = _create_user(
            session,
            role="student",
            first="Esi",
            last="Learner",
            username_prefix="runtime_student",
        )
        teacher = _create_user(
            session,
            role="teacher",
            first="Teacher",
            last="Viewer",
            username_prefix="runtime_teacher",
        )
        flagship_course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        non_flagship_course = Course(
            title="General Reading Practice",
            description="Non-flagship comparison course",
            subject="Literacy",
        )
        session.add(non_flagship_course)
        session.commit()
        session.refresh(non_flagship_course)

        _enroll_student(session, student, flagship_course)
        _enroll_student(session, student, non_flagship_course)
        lesson_assessment = (
            session.query(Assessment)
            .filter(Assessment.title == "Introduction to Africa Lesson Check")
            .one()
        )

        current_user["value"] = student
        _submit_flagship_attempt(
            client,
            lesson_assessment.id,
            ["Africa is a diverse continent.", "Because places and people deserve respect."],
        )

        current_user["value"] = teacher
        flagship_summary = client.get(
            f"/api/analytics/reporting-summary?course_id={flagship_course.id}&student_id={student.id}"
        )
        assert flagship_summary.status_code == 200
        flagship_payload = flagship_summary.json()
        assert flagship_payload["continuation_guidance"]["support_state"] == "enrichment"
        educator_summary = flagship_payload["educator_runtime_support_summary"]
        assert educator_summary is not None
        assert educator_summary["student_name"] == "Esi Learner"
        assert educator_summary["support_state"] == "enrichment"
        assert educator_summary["context_lesson_title"] == "Introduction to Africa"

        non_flagship_response = client.get(
            f"/api/analytics/educator-runtime-support?course_id={non_flagship_course.id}"
        )
        assert non_flagship_response.status_code == 200
        assert non_flagship_response.json() == []

        non_flagship_summary = client.get(
            f"/api/analytics/reporting-summary?course_id={non_flagship_course.id}&student_id={student.id}"
        )
        assert non_flagship_summary.status_code == 200
        assert non_flagship_summary.json()["educator_runtime_support_summary"] is None

        current_user["value"] = student
        learner_summary = client.get(f"/api/analytics/reporting-summary?course_id={flagship_course.id}")
        assert learner_summary.status_code == 200
        learner_payload = learner_summary.json()
        assert learner_payload["educator_runtime_support_summary"] is None
        assert learner_payload["continuation_guidance"]["educator_note"] is None
        assert learner_payload["continuation_guidance"]["educator_intervention_hint"] is None
    finally:
        session.close()
