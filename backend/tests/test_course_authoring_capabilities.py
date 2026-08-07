import uuid

import pytest
from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.database import SessionLocal
from app.enum import MembershipStatus, OrganizationRole, OrganizationType
from app.main import app
from app.lesson_governance import serialize_course
from app.models import Course, Lesson, Organization, OrganizationMembership, Source, Unit, User


client = TestClient(app)


@pytest.fixture
def authoring_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        app.dependency_overrides = {}
        db.close()


def _user(db, role: str) -> User:
    value = uuid.uuid4()
    user = User(
        id=value,
        firstname=role.title(),
        lastname="Authoring",
        username=f"{role}_{value}",
        email=f"{role}_{value}@example.com",
        hashed_password="fake",
        role=role,
    )
    db.add(user)
    db.commit()
    return user


def _organization(db) -> Organization:
    organization = Organization(
        id=uuid.uuid4(),
        name=f"Authoring Org {uuid.uuid4()}",
        type=OrganizationType.SCHOOL,
    )
    db.add(organization)
    db.commit()
    return organization


def _membership(db, user: User, organization: Organization, role: OrganizationRole):
    membership = OrganizationMembership(
        organization_id=organization.id,
        user_id=user.id,
        role=role,
        status=MembershipStatus.ACTIVE,
    )
    db.add(membership)
    db.commit()
    return membership


def _capabilities(user: User, *, org_id=None, course_id=None):
    app.dependency_overrides[get_current_user] = lambda: user
    headers = {"X-Org-Id": str(org_id)} if org_id else {}
    path = (
        f"/api/courses/{course_id}/authoring-capabilities"
        if course_id
        else "/api/course-authoring/capabilities"
    )
    response = client.get(path, headers=headers)
    assert response.status_code == 200
    return response.json()["capabilities"]


def test_role_and_scope_capability_matrix(authoring_db):
    organization = _organization(authoring_db)
    content_admin = _user(authoring_db, "content_admin")
    org_admin = _user(authoring_db, "org_admin")
    teacher = _user(authoring_db, "teacher")
    student = _user(authoring_db, "student")
    creator = _user(authoring_db, "content_admin")
    _membership(authoring_db, content_admin, organization, OrganizationRole.CONTENT_ADMIN)
    _membership(authoring_db, org_admin, organization, OrganizationRole.ORG_ADMIN)
    _membership(authoring_db, teacher, organization, OrganizationRole.TEACHER)

    course = Course(
        id=uuid.uuid4(),
        title="Scoped draft",
        description="Capability matrix",
        organization_id=organization.id,
        created_by=creator.id,
        revision_status="draft",
    )
    authoring_db.add(course)
    authoring_db.commit()

    content_collection = _capabilities(content_admin, org_id=organization.id)
    assert content_collection == {
        "can_create": True,
        "can_view_draft": True,
        "can_edit": True,
        "can_duplicate": True,
        "can_preview": True,
        "can_submit_review": True,
        "can_review": False,
        "can_publish": False,
    }

    admin_course = _capabilities(org_admin, course_id=course.id)
    assert all(admin_course.values())

    teacher_course = _capabilities(teacher, course_id=course.id)
    assert teacher_course["can_duplicate"] is True
    assert teacher_course["can_edit"] is False
    assert teacher_course["can_publish"] is False

    student_course = _capabilities(student, course_id=course.id)
    assert not any(student_course.values())


def test_org_admin_cannot_review_or_publish_own_course(authoring_db):
    organization = _organization(authoring_db)
    org_admin = _user(authoring_db, "org_admin")
    _membership(authoring_db, org_admin, organization, OrganizationRole.ORG_ADMIN)
    course = Course(
        title="Admin-authored draft",
        description="Independent review",
        organization_id=organization.id,
        created_by=org_admin.id,
        revision_status="submitted",
    )
    authoring_db.add(course)
    authoring_db.commit()

    capabilities = _capabilities(org_admin, course_id=course.id)
    assert capabilities["can_edit"] is True
    assert capabilities["can_review"] is False
    assert capabilities["can_publish"] is False


def test_inactive_membership_grants_no_authoring_actions(authoring_db):
    organization = _organization(authoring_db)
    user = _user(authoring_db, "content_admin")
    membership = OrganizationMembership(
        organization_id=organization.id,
        user_id=user.id,
        role=OrganizationRole.CONTENT_ADMIN,
        status=MembershipStatus.INACTIVE,
    )
    authoring_db.add(membership)
    authoring_db.commit()

    capabilities = _capabilities(user, org_id=organization.id)
    assert not any(capabilities.values())


def test_client_claimed_capabilities_do_not_authorize_student(authoring_db):
    student = _user(authoring_db, "student")
    app.dependency_overrides[get_current_user] = lambda: student

    response = client.post(
        "/api/courses",
        json={
            "title": "Unauthorized",
            "description": "Client claims are ignored",
            "units": [],
            "capabilities": {"can_create": True, "can_publish": True},
        },
    )

    assert response.status_code == 403
    assert authoring_db.query(Course).filter_by(title="Unauthorized").first() is None


def test_authoring_changes_preserve_learner_draft_and_teacher_note_filtering(authoring_db):
    course = Course(title="Learner-safe course", description="Regression")
    authoring_db.add(course)
    authoring_db.flush()
    unit = Unit(course_id=course.id, title="Unit", order=1)
    authoring_db.add(unit)
    authoring_db.flush()
    approved = Lesson(
        unit_id=unit.id,
        title="Approved lesson",
        objective="Compare two primary sources.",
        learning_objectives="Learners will compare two primary sources.",
        key_concepts=["evidence"],
        teacher_notes="This must never reach learners.",
        discussion_questions=["Which detail is strongest?"],
        hook="Inspect the two accounts.",
        content="Two source accounts with contextual framing.",
        guided_practice="Model one comparison with evidence.",
        independent_practice="Complete a second comparison.",
        assessment="Submit an evidence-based comparison.",
        review_status="approved",
        order=1,
    )
    draft = Lesson(
        unit_id=unit.id,
        title="Draft lesson",
        objective="Not deliverable",
        teacher_notes="Draft-only note",
        review_status="draft",
        order=2,
    )
    authoring_db.add_all([approved, draft])
    authoring_db.flush()
    authoring_db.add(
        Source(
            lesson_id=approved.id,
            citation="Archive source",
            url="https://example.com/source",
        )
    )
    authoring_db.commit()
    authoring_db.expire_all()

    serialized = serialize_course(
        authoring_db.query(Course).filter(Course.id == course.id).one(),
        viewer_role="student",
    )

    lessons = serialized.units[0].lessons
    assert [lesson.title for lesson in lessons] == ["Approved lesson"]
    assert lessons[0].teacher_notes is None
    assert lessons[0].review_status is None
