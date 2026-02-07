import os
import uuid
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import (
    User,
    Organization,
    OrganizationMembership,
    Course,
    CourseVersion,
)
from app.enum import OrganizationType, OrganizationRole, CourseVersionStatus
from app.auth import get_current_user
from app.models import Base

client = TestClient(app)


@pytest.fixture
def test_db():
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=db.get_bind())
        yield db
    finally:
        db.close()


def create_org_with_member(db, user, role):
    organization = Organization(
        id=uuid.uuid4(),
        name="Test Org",
        type=OrganizationType.SCHOOL,
    )
    db.add(organization)
    db.flush()
    membership = OrganizationMembership(
        organization_id=organization.id,
        user_id=user.id,
        role=role,
    )
    db.add(membership)
    db.commit()
    return organization


def test_org_admin_can_create_invite(test_db):
    suffix = uuid.uuid4()
    user = User(
        id=uuid.uuid4(),
        firstname="Org",
        lastname="Admin",
        username=f"org_admin_user_{suffix}",
        email=f"org_admin_{suffix}@example.com",
        hashed_password="fake",
        role="admin",
    )
    test_db.add(user)
    test_db.commit()

    org = create_org_with_member(test_db, user, OrganizationRole.ORG_ADMIN)

    app.dependency_overrides[get_current_user] = lambda: user

    resp = client.post(
        f"/api/orgs/{org.id}/invites",
        headers={"X-Org-Id": str(org.id)},
        json={"email": "teacher@example.com", "role": "teacher"},
    )

    assert resp.status_code == 200
    app.dependency_overrides = {}


def test_student_cannot_publish_course_version(test_db):
    suffix = uuid.uuid4()
    user = User(
        id=uuid.uuid4(),
        firstname="Student",
        lastname="User",
        username=f"student_user_{suffix}",
        email=f"student_{suffix}@example.com",
        hashed_password="fake",
        role="student",
    )
    test_db.add(user)
    test_db.commit()

    org = create_org_with_member(test_db, user, OrganizationRole.STUDENT)

    course = Course(id=uuid.uuid4(), title="Course", description="Desc", organization_id=org.id)
    test_db.add(course)
    test_db.flush()
    version = CourseVersion(
        id=uuid.uuid4(),
        course_id=course.id,
        version_number=1,
        status=CourseVersionStatus.DRAFT,
    )
    test_db.add(version)
    test_db.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    resp = client.post(
        f"/api/course-versions/{version.id}/publish",
        headers={"X-Org-Id": str(org.id)},
    )

    assert resp.status_code == 403
    app.dependency_overrides = {}


def test_teacher_can_create_section(test_db):
    suffix = uuid.uuid4()
    user = User(
        id=uuid.uuid4(),
        firstname="Teach",
        lastname="User",
        username=f"teacher_user_{suffix}",
        email=f"teacher_{suffix}@example.com",
        hashed_password="fake",
        role="teacher",
    )
    test_db.add(user)
    test_db.commit()

    org = create_org_with_member(test_db, user, OrganizationRole.TEACHER)

    course = Course(id=uuid.uuid4(), title="Course", description="Desc", organization_id=org.id)
    test_db.add(course)
    test_db.flush()
    version = CourseVersion(
        id=uuid.uuid4(),
        course_id=course.id,
        version_number=1,
        status=CourseVersionStatus.PUBLISHED,
    )
    test_db.add(version)
    test_db.commit()

    app.dependency_overrides[get_current_user] = lambda: user

    resp = client.post(
        "/api/sections",
        headers={"X-Org-Id": str(org.id)},
        json={"course_version_id": str(version.id), "name": "Section A", "mode": "remote"},
    )

    assert resp.status_code == 200
    app.dependency_overrides = {}
