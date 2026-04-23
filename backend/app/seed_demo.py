from __future__ import annotations

from datetime import datetime

from sqlalchemy import or_

from app.auth import hash_password
from app.database import SessionLocal
from app.enum import (
    CourseVersionStatus,
    MembershipStatus,
    OrganizationRole,
    OrganizationType,
    SectionMode,
)
from app.models import (
    Course,
    CourseVersion,
    Enrollment,
    Organization,
    OrganizationMembership,
    Section,
    User,
)

DEMO_PASSWORD = "password"
DEMO_ORG_NAME = "EchoEd Demo School"
DEMO_COURSE_TITLE = "K-5 Introduction to Africa"
DEMO_SECTION_NAME = "Grade 3 - Cohort A"

DEMO_USERS = {
    "org_admin": {
        "firstname": "Olivia",
        "lastname": "Admin",
        "username": "orgadmin",
        "email": "orgadmin@demo.com",
        "role": "admin",
    },
    "teacher": {
        "firstname": "Tariq",
        "lastname": "Teacher",
        "username": "teacher",
        "email": "teacher@demo.com",
        "role": "teacher",
    },
    "parent": {
        "firstname": "Paula",
        "lastname": "Parent",
        "username": "parent",
        "email": "parent@demo.com",
        "role": "parent",
    },
    "student1": {
        "firstname": "Sami",
        "lastname": "Student",
        "username": "student1",
        "email": "student1@demo.com",
        "role": "student",
    },
    "student2": {
        "firstname": "Sasha",
        "lastname": "Student",
        "username": "student2",
        "email": "student2@demo.com",
        "role": "student",
    },
    "content_admin": {
        "firstname": "Carmen",
        "lastname": "Content",
        "username": "contentadmin",
        "email": "content@demo.com",
        "role": "content_admin",
    },
    "super_admin": {
        "firstname": "Sam",
        "lastname": "Super",
        "username": "superadmin",
        "email": "superadmin@demo.com",
        "role": "super_admin",
    },
}

MEMBERSHIP_MAP = {
    "org_admin": OrganizationRole.ORG_ADMIN,
    "teacher": OrganizationRole.TEACHER,
    "parent": OrganizationRole.PARENT,
    "student1": OrganizationRole.STUDENT,
    "student2": OrganizationRole.STUDENT,
    "content_admin": OrganizationRole.CONTENT_ADMIN,
}


def _get_or_create_demo_org(db) -> Organization:
    org = db.query(Organization).filter(Organization.name == DEMO_ORG_NAME).first()
    if org is None:
        org = Organization(
            name=DEMO_ORG_NAME,
            type=OrganizationType.SCHOOL,
            country="US",
            timezone="America/New_York",
        )
        db.add(org)
        db.flush()
        return org

    org.type = OrganizationType.SCHOOL
    org.country = "US"
    org.timezone = "America/New_York"
    db.flush()
    return org


def _upsert_demo_user(db, profile: dict[str, str]) -> User:
    user = (
        db.query(User)
        .filter(
            or_(
                User.username == profile["username"],
                User.email == profile["email"],
            )
        )
        .first()
    )

    if user is None:
        user = User(username=profile["username"], email=profile["email"])
        db.add(user)

    user.firstname = profile["firstname"]
    user.lastname = profile["lastname"]
    user.username = profile["username"]
    user.email = profile["email"]
    user.role = profile["role"]
    user.hashed_password = hash_password(DEMO_PASSWORD)
    user.updated_at = datetime.utcnow()

    db.flush()
    return user


def _ensure_membership(db, org: Organization, user: User, role: OrganizationRole) -> None:
    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == org.id,
            OrganizationMembership.user_id == user.id,
        )
        .first()
    )
    if membership is None:
        membership = OrganizationMembership(
            organization_id=org.id,
            user_id=user.id,
            role=role,
            status=MembershipStatus.ACTIVE,
        )
        db.add(membership)
    else:
        membership.role = role
        membership.status = MembershipStatus.ACTIVE

    db.flush()


def _get_or_create_course(db, org: Organization, content_admin: User) -> Course:
    course = (
        db.query(Course)
        .filter(
            Course.organization_id == org.id,
            Course.title == DEMO_COURSE_TITLE,
        )
        .first()
    )
    if course is None:
        course = Course(
            title=DEMO_COURSE_TITLE,
            description="Flagship K-5 course with an updated course versioning flow.",
            subject="History",
            age_band_min=5,
            age_band_max=11,
            default_locale="en",
            created_by=content_admin.id,
            organization_id=org.id,
        )
        db.add(course)
    else:
        course.description = "Flagship K-5 course with an updated course versioning flow."
        course.subject = "History"
        course.age_band_min = 5
        course.age_band_max = 11
        course.default_locale = "en"
        course.created_by = content_admin.id
        course.organization_id = org.id
        course.updated_at = datetime.utcnow()

    db.flush()
    return course


def _get_or_create_course_version(db, course: Course, content_admin: User) -> CourseVersion:
    version = (
        db.query(CourseVersion)
        .filter(
            CourseVersion.course_id == course.id,
            CourseVersion.version_number == 1,
        )
        .first()
    )
    if version is None:
        version = CourseVersion(
            course_id=course.id,
            version_number=1,
            status=CourseVersionStatus.PUBLISHED,
            changelog="Initial published version",
            published_at=datetime.utcnow(),
            published_by=content_admin.id,
        )
        db.add(version)
    else:
        version.status = CourseVersionStatus.PUBLISHED
        version.changelog = "Initial published version"
        version.published_at = version.published_at or datetime.utcnow()
        version.published_by = content_admin.id

    db.flush()
    return version


def _get_or_create_section(db, org: Organization, version: CourseVersion, teacher: User) -> Section:
    section = (
        db.query(Section)
        .filter(
            Section.organization_id == org.id,
            Section.course_version_id == version.id,
            Section.name == DEMO_SECTION_NAME,
        )
        .first()
    )
    if section is None:
        section = Section(
            organization_id=org.id,
            course_version_id=version.id,
            name=DEMO_SECTION_NAME,
            mode=SectionMode.IN_PERSON,
            start_date=datetime.utcnow(),
            created_by=teacher.id,
        )
        db.add(section)
    else:
        section.mode = SectionMode.IN_PERSON
        section.start_date = section.start_date or datetime.utcnow()
        section.created_by = teacher.id

    db.flush()
    return section


def _ensure_enrollment(db, section: Section, user: User) -> None:
    enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.section_id == section.id,
            Enrollment.user_id == user.id,
        )
        .first()
    )
    if enrollment is None:
        db.add(Enrollment(section_id=section.id, user_id=user.id))
        db.flush()


def run() -> None:
    db = SessionLocal()
    try:
        org = _get_or_create_demo_org(db)
        users = {
            key: _upsert_demo_user(db, profile)
            for key, profile in DEMO_USERS.items()
        }

        for key, role in MEMBERSHIP_MAP.items():
            _ensure_membership(db, org, users[key], role)

        course = _get_or_create_course(db, org, users["content_admin"])
        version = _get_or_create_course_version(db, course, users["content_admin"])
        section = _get_or_create_section(db, org, version, users["teacher"])

        _ensure_enrollment(db, section, users["student1"])
        _ensure_enrollment(db, section, users["student2"])

        db.commit()
        print(
            "Seeded demo data. Login uses usernames with password "
            f"'{DEMO_PASSWORD}' (for example: student1 / {DEMO_PASSWORD}, teacher / {DEMO_PASSWORD})."
        )
    finally:
        db.close()


if __name__ == "__main__":
    run()
