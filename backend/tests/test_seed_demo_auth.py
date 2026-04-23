from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api.routes import auth
from app.auth import verify_password, hash_password
from app.database import get_db
from app.models import Course, CourseVersion, Enrollment, Organization, OrganizationMembership, Section, User
from app import seed_demo


def _build_session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def _seed_with_factory(monkeypatch, session_factory):
    monkeypatch.setattr(seed_demo, "SessionLocal", session_factory)
    seed_demo.run()


def test_seed_demo_is_idempotent_and_resets_passwords(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)

    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        student = session.query(User).filter(User.username == "student1").one()
        student.hashed_password = hash_password("stale-password")
        student.firstname = "Stale"
        session.commit()
    finally:
        session.close()

    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        assert session.query(User).count() == len(seed_demo.DEMO_USERS)
        assert session.query(Organization).filter(Organization.name == seed_demo.DEMO_ORG_NAME).count() == 1
        assert session.query(OrganizationMembership).count() == len(seed_demo.MEMBERSHIP_MAP)
        assert session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).count() == 1
        assert session.query(CourseVersion).count() == 1
        assert session.query(Section).filter(Section.name == seed_demo.DEMO_SECTION_NAME).count() == 1
        assert session.query(Enrollment).count() == 2

        refreshed_student = session.query(User).filter(User.username == "student1").one()
        assert refreshed_student.firstname == seed_demo.DEMO_USERS["student1"]["firstname"]
        assert verify_password(seed_demo.DEMO_PASSWORD, refreshed_student.hashed_password)
    finally:
        session.close()


def test_seeded_demo_users_can_log_in_with_username_and_email(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)

    app = FastAPI()
    app.include_router(auth.router, prefix="/api")

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    student_response = client.post(
        "/api/auth/token",
        data={"username": "student1", "password": seed_demo.DEMO_PASSWORD},
    )
    assert student_response.status_code == 200
    student_payload = student_response.json()
    assert student_payload["token_type"] == "bearer"
    assert student_payload["active_org_id"] is not None

    teacher_response = client.post(
        "/api/auth/token",
        data={"username": "teacher", "password": seed_demo.DEMO_PASSWORD},
    )
    assert teacher_response.status_code == 200
    teacher_payload = teacher_response.json()
    assert teacher_payload["token_type"] == "bearer"
    assert teacher_payload["active_org_id"] is not None

    email_response = client.post(
        "/api/auth/token",
        data={"username": "student1@demo.com", "password": seed_demo.DEMO_PASSWORD},
    )
    assert email_response.status_code == 200

    app.dependency_overrides = {}
