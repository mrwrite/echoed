import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import courses
from app.auth import get_current_user
from app.database import get_db
from app.enum import MembershipStatus, OrganizationRole, OrganizationType, ProgressStatus
from app.models import (
    Assessment,
    Course,
    Lesson,
    Organization,
    OrganizationMembership,
    SegmentProgress,
    Source,
    StudentAssessmentAttempt,
    StudentCourse,
    StudentUnitProgress,
    Unit,
    User,
)


def _ready_lesson_kwargs(title: str, *, review_status: str = "approved", order: int | None = 1) -> dict:
    return {
        "title": title,
        "objective": "Explain a lesson idea with evidence.",
        "learning_objectives": "Students will explain what they learned using one cited detail.",
        "key_concepts": ["evidence", "citation"],
        "teacher_notes": "Prompt one evidence-based response.",
        "discussion_questions": ["What fact taught you something new?"],
        "hook": "Start with one vivid question.",
        "content": "Share one concise explanation and example.",
        "guided_practice": "Model a response together.",
        "independent_practice": "Ask learners to answer on their own.",
        "assessment": "Short oral or written explanation.",
        "review_status": review_status,
        "order": order,
    }


def _build_test_client(db_session, user):
    app = FastAPI()
    app.include_router(courses.router, prefix="/api")
    app.dependency_overrides[get_current_user] = lambda: user

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _seed_users_and_course(db_session):
    org = Organization(
        id=uuid.uuid4(),
        name="EchoEd Org",
        type=OrganizationType.SCHOOL,
    )
    admin = User(
        id=uuid.uuid4(),
        firstname="Admin",
        lastname="User",
        username=f"admin_{uuid.uuid4()}",
        email=f"admin_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="admin",
    )
    teacher = User(
        id=uuid.uuid4(),
        firstname="Teacher",
        lastname="User",
        username=f"teacher_{uuid.uuid4()}",
        email=f"teacher_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="teacher",
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
    content_admin = User(
        id=uuid.uuid4(),
        firstname="Content",
        lastname="Admin",
        username=f"content_{uuid.uuid4()}",
        email=f"content_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    db_session.add_all([org, admin, teacher, student, content_admin])
    db_session.flush()
    db_session.add(
        OrganizationMembership(
            organization_id=org.id,
            user_id=content_admin.id,
            role=OrganizationRole.CONTENT_ADMIN,
            status=MembershipStatus.ACTIVE,
        )
    )
    course = Course(
        id=uuid.uuid4(),
        title="Governed Safe Publish Course",
        description="Safe publish endpoint coverage",
        organization_id=org.id,
    )
    unit = Unit(id=uuid.uuid4(), title="Unit One", course_id=course.id, order=1)
    db_session.add_all([course, unit])
    db_session.commit()
    return {
        "org": org,
        "admin": admin,
        "teacher": teacher,
        "student": student,
        "content_admin": content_admin,
        "course": course,
        "unit": unit,
    }


def _add_lesson(
    db_session,
    unit: Unit,
    *,
    review_status: str = "approved",
    order: int | None = 1,
    with_source: bool = True,
    revision_status: str = "current",
):
    lesson = Lesson(
        unit_id=unit.id,
        revision_status=revision_status,
        **_ready_lesson_kwargs(f"Lesson {uuid.uuid4()}", review_status=review_status, order=order),
    )
    db_session.add(lesson)
    db_session.flush()
    if with_source:
        db_session.add(
            Source(
                lesson_id=lesson.id,
                citation="Lesson source",
                url="https://example.com/source",
            )
        )
    db_session.commit()
    db_session.refresh(lesson)
    return lesson


def test_staff_and_content_admin_can_fetch_course_safe_publish_validation(db_session):
    seeded = _seed_users_and_course(db_session)
    _add_lesson(db_session, seeded["unit"])

    teacher_client = _build_test_client(db_session, seeded["teacher"])
    teacher_response = teacher_client.get(f"/api/courses/{seeded['course'].id}/safe-publish-validation")
    assert teacher_response.status_code == 200
    assert teacher_response.json()["is_safe"] is True

    content_admin_client = _build_test_client(db_session, seeded["content_admin"])
    content_admin_response = content_admin_client.get(
        f"/api/courses/{seeded['course'].id}/safe-publish-validation"
    )
    assert content_admin_response.status_code == 200
    assert content_admin_response.json()["course_id"] == str(seeded["course"].id)


def test_student_cannot_fetch_course_safe_publish_validation(db_session):
    seeded = _seed_users_and_course(db_session)
    _add_lesson(db_session, seeded["unit"])

    client = _build_test_client(db_session, seeded["student"])
    response = client.get(f"/api/courses/{seeded['course'].id}/safe-publish-validation")

    assert response.status_code == 403


def test_safe_course_returns_is_safe_true(db_session):
    seeded = _seed_users_and_course(db_session)
    _add_lesson(db_session, seeded["unit"])

    client = _build_test_client(db_session, seeded["admin"])
    response = client.get(f"/api/courses/{seeded['course'].id}/safe-publish-validation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_safe"] is True
    assert payload["blocking_issue_count"] == 0


def test_blocked_course_returns_structured_blocking_issues(db_session):
    seeded = _seed_users_and_course(db_session)
    seeded["course"].revision_status = "deprecated"
    db_session.commit()
    _add_lesson(db_session, seeded["unit"], revision_status="deprecated")

    client = _build_test_client(db_session, seeded["admin"])
    response = client.get(f"/api/courses/{seeded['course'].id}/safe-publish-validation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_safe"] is False
    assert payload["blocking_issue_count"] >= 1
    assert any(issue["code"] == "blocked_revision_status" for issue in payload["blocking_issues"])
    assert all("entity_type" in issue and "entity_title" in issue for issue in payload["blocking_issues"])


def test_warning_scenarios_return_warnings(db_session):
    seeded = _seed_users_and_course(db_session)
    seeded["course"].published_at = seeded["course"].created_at
    seeded["course"].revision_status = "draft"
    db_session.commit()
    _add_lesson(db_session, seeded["unit"], revision_status="draft")

    client = _build_test_client(db_session, seeded["teacher"])
    response = client.get(f"/api/courses/{seeded['course'].id}/safe-publish-validation")

    assert response.status_code == 200
    payload = response.json()
    assert payload["warning_count"] >= 1
    assert any(issue["code"] == "draft_has_published_at" for issue in payload["warnings"])


def test_safe_publish_endpoint_is_read_only(db_session):
    seeded = _seed_users_and_course(db_session)
    lesson = _add_lesson(db_session, seeded["unit"])

    student_course = StudentCourse(student_id=seeded["student"].id, course_id=seeded["course"].id, status="active")
    db_session.add(student_course)
    db_session.commit()
    db_session.refresh(student_course)

    unit_progress = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=seeded["unit"].id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add(unit_progress)
    db_session.commit()
    db_session.refresh(unit_progress)

    segment_progress = SegmentProgress(
        student_unit_id=unit_progress.id,
        lesson_id=lesson.id,
        status=ProgressStatus.NOT_STARTED,
    )
    db_session.add(segment_progress)
    db_session.commit()
    db_session.refresh(segment_progress)

    assessment = Assessment(
        title="Archived Assessment",
        lesson_id=lesson.id,
        course_id=seeded["course"].id,
        assessment_scope="lesson",
        revision_status="archived",
    )
    db_session.add(assessment)
    db_session.flush()
    db_session.add(
        StudentAssessmentAttempt(
            assessment_id=assessment.id,
            student_id=seeded["student"].id,
            score=0,
            max_score=1,
            passed=False,
        )
    )
    db_session.commit()

    baseline = (
        db_session.query(Course).count(),
        db_session.query(Unit).count(),
        db_session.query(Lesson).count(),
        db_session.query(StudentCourse).count(),
        db_session.query(StudentUnitProgress).count(),
        db_session.query(SegmentProgress).count(),
        db_session.query(StudentAssessmentAttempt).count(),
        student_course.status,
        unit_progress.status,
        segment_progress.status,
    )

    client = _build_test_client(db_session, seeded["teacher"])
    response = client.get(f"/api/courses/{seeded['course'].id}/safe-publish-validation")

    db_session.refresh(student_course)
    db_session.refresh(unit_progress)
    db_session.refresh(segment_progress)
    after = (
        db_session.query(Course).count(),
        db_session.query(Unit).count(),
        db_session.query(Lesson).count(),
        db_session.query(StudentCourse).count(),
        db_session.query(StudentUnitProgress).count(),
        db_session.query(SegmentProgress).count(),
        db_session.query(StudentAssessmentAttempt).count(),
        student_course.status,
        unit_progress.status,
        segment_progress.status,
    )

    assert response.status_code == 200
    assert after == baseline
