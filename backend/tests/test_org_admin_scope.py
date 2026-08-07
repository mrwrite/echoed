import uuid

from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.database import get_db as database_get_db
from app.deps import get_db as dependency_get_db
from app.enum import CourseVersionStatus, OrganizationRole, OrganizationType
from app.main import app
from app.models import (
    Course,
    CourseVersion,
    Enrollment,
    Lesson,
    LessonSession,
    Organization,
    OrganizationMembership,
    Section,
    Unit,
    User,
)


def _user(label: str, role: str) -> User:
    suffix = uuid.uuid4()
    return User(
        id=uuid.uuid4(),
        firstname=label,
        lastname="Member",
        username=f"{label.lower()}-{suffix}",
        email=f"{label.lower()}-{suffix}@example.com",
        hashed_password="test",
        role=role,
    )


def _client(db_session, current_user: User) -> TestClient:
    def override_db():
        yield db_session

    app.dependency_overrides[database_get_db] = override_db
    app.dependency_overrides[dependency_get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: current_user
    return TestClient(app)


def _organization(db_session, name: str) -> Organization:
    organization = Organization(id=uuid.uuid4(), name=name, type=OrganizationType.SCHOOL)
    db_session.add(organization)
    db_session.flush()
    return organization


def _membership(db_session, organization: Organization, user: User, role: OrganizationRole):
    membership = OrganizationMembership(
        id=uuid.uuid4(),
        organization_id=organization.id,
        user_id=user.id,
        role=role,
    )
    db_session.add(membership)
    return membership


def _section(db_session, organization: Organization, creator: User, name: str) -> Section:
    course = Course(
        id=uuid.uuid4(),
        organization_id=organization.id,
        created_by=creator.id,
        title=f"{name} Course",
        description="Scoped course",
    )
    db_session.add(course)
    db_session.flush()
    version = CourseVersion(
        id=uuid.uuid4(),
        course_id=course.id,
        version_number=1,
        status=CourseVersionStatus.PUBLISHED,
    )
    db_session.add(version)
    db_session.flush()
    section = Section(
        id=uuid.uuid4(),
        organization_id=organization.id,
        course_version_id=version.id,
        name=name,
        mode="remote",
        created_by=creator.id,
    )
    db_session.add(section)
    db_session.flush()
    return section


def test_org_admin_member_directory_is_minimal_and_scoped(db_session):
    admin = _user("Admin", "org_admin")
    teacher = _user("Teacher", "teacher")
    outsider = _user("Outsider", "student")
    own_org = _organization(db_session, "Own School")
    other_org = _organization(db_session, "Other School")
    db_session.add_all([admin, teacher, outsider])
    db_session.flush()
    _membership(db_session, own_org, admin, OrganizationRole.ORG_ADMIN)
    _membership(db_session, own_org, teacher, OrganizationRole.TEACHER)
    _membership(db_session, other_org, outsider, OrganizationRole.STUDENT)
    db_session.commit()

    client = _client(db_session, admin)
    response = client.get(f"/api/orgs/{own_org.id}/members", headers={"X-Org-Id": str(own_org.id)})

    assert response.status_code == 200
    assert {row["display_name"] for row in response.json()} == {"Admin Member", "Teacher Member"}
    assert all("email" not in row for row in response.json())
    assert all("hashed_password" not in row for row in response.json())

    mismatch = client.get(f"/api/orgs/{other_org.id}/members", headers={"X-Org-Id": str(own_org.id)})
    assert mismatch.status_code == 403
    app.dependency_overrides.clear()


def test_org_admin_section_list_includes_only_active_organization(db_session):
    admin = _user("Admin", "org_admin")
    learner = _user("Learner", "student")
    own_org = _organization(db_session, "Own School")
    other_org = _organization(db_session, "Other School")
    db_session.add_all([admin, learner])
    db_session.flush()
    _membership(db_session, own_org, admin, OrganizationRole.ORG_ADMIN)
    _membership(db_session, own_org, learner, OrganizationRole.STUDENT)
    own_section = _section(db_session, own_org, admin, "Own Class")
    _section(db_session, other_org, admin, "Other Class")
    db_session.add(Enrollment(section_id=own_section.id, user_id=learner.id, role_in_section="student"))
    db_session.commit()

    client = _client(db_session, admin)
    response = client.get(f"/api/orgs/{own_org.id}/sections", headers={"X-Org-Id": str(own_org.id)})

    assert response.status_code == 200
    assert [row["name"] for row in response.json()] == ["Own Class"]
    assert response.json()[0]["learner_count"] == 1
    app.dependency_overrides.clear()


def test_nested_section_reads_reject_cross_organization_ids(db_session):
    admin = _user("Admin", "org_admin")
    own_org = _organization(db_session, "Own School")
    other_org = _organization(db_session, "Other School")
    db_session.add(admin)
    db_session.flush()
    _membership(db_session, own_org, admin, OrganizationRole.ORG_ADMIN)
    other_section = _section(db_session, other_org, admin, "Other Class")
    db_session.commit()

    client = _client(db_session, admin)
    headers = {"X-Org-Id": str(own_org.id)}

    assert client.get(f"/api/sections/{other_section.id}/roster", headers=headers).status_code == 404
    assert client.get(f"/api/sections/{other_section.id}/assignments", headers=headers).status_code == 404
    assert client.get(f"/api/sections/{other_section.id}/analytics/summary", headers=headers).status_code == 404
    app.dependency_overrides.clear()


def test_section_enrollment_requires_active_organization_member(db_session):
    admin = _user("Admin", "org_admin")
    outsider = _user("Outsider", "student")
    own_org = _organization(db_session, "Own School")
    db_session.add_all([admin, outsider])
    db_session.flush()
    _membership(db_session, own_org, admin, OrganizationRole.ORG_ADMIN)
    section = _section(db_session, own_org, admin, "Own Class")
    db_session.commit()

    client = _client(db_session, admin)
    response = client.post(
        f"/api/sections/{section.id}/enrollments",
        headers={"X-Org-Id": str(own_org.id)},
        json={"user_id": str(outsider.id)},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "User is not an active member of this organization"
    app.dependency_overrides.clear()


def test_lesson_sessions_reject_cross_organization_and_parent_mismatch(db_session):
    teacher = _user("Teacher", "teacher")
    own_org = _organization(db_session, "Own School")
    other_org = _organization(db_session, "Other School")
    db_session.add(teacher)
    db_session.flush()
    _membership(db_session, own_org, teacher, OrganizationRole.TEACHER)
    own_section = _section(db_session, own_org, teacher, "Own Class")
    other_section = _section(db_session, other_org, teacher, "Other Class")
    other_version = other_section.course_version
    other_unit = Unit(
        id=uuid.uuid4(), course_id=other_version.course_id,
        course_version_id=other_version.id, title="Other Unit",
    )
    db_session.add(other_unit)
    db_session.flush()
    other_lesson = Lesson(id=uuid.uuid4(), unit_id=other_unit.id, title="Other Lesson")
    db_session.add(other_lesson)
    db_session.flush()
    other_session = LessonSession(
        id=uuid.uuid4(), section_id=other_section.id,
        lesson_id=other_lesson.id, started_by=teacher.id,
    )
    db_session.add(other_session)
    db_session.commit()

    client = _client(db_session, teacher)
    headers = {"X-Org-Id": str(own_org.id)}

    assert client.post(
        f"/api/sections/{other_section.id}/lessons/{other_lesson.id}/start",
        headers=headers,
    ).status_code == 404
    assert client.post(
        f"/api/sections/{own_section.id}/lessons/{other_lesson.id}/start",
        headers=headers,
    ).status_code == 404
    assert client.post(
        f"/api/lesson-sessions/{other_session.id}/end",
        headers=headers,
        json={},
    ).status_code == 404
    app.dependency_overrides.clear()


def test_section_creation_conceals_another_organizations_course_version(db_session):
    teacher = _user("Teacher", "teacher")
    own_org = _organization(db_session, "Own School")
    other_org = _organization(db_session, "Other School")
    db_session.add(teacher)
    db_session.flush()
    _membership(db_session, own_org, teacher, OrganizationRole.TEACHER)
    other_section = _section(db_session, other_org, teacher, "Other Class")
    db_session.commit()

    client = _client(db_session, teacher)
    response = client.post(
        "/api/sections",
        headers={"X-Org-Id": str(own_org.id)},
        json={
            "course_version_id": str(other_section.course_version_id),
            "name": "Cross-org class",
            "mode": "remote",
        },
    )

    assert response.status_code == 404
    app.dependency_overrides.clear()
