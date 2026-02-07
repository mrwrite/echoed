from datetime import datetime
import uuid

from app.database import SessionLocal
from app.models import (
    User,
    Organization,
    OrganizationMembership,
    Course,
    CourseVersion,
    Section,
    Enrollment,
)
from app.enum import OrganizationType, OrganizationRole, CourseVersionStatus, SectionMode
from app.auth import hash_password


def run():
    db = SessionLocal()
    try:
        org = Organization(
            name="EchoEd Demo School",
            type=OrganizationType.SCHOOL,
            country="US",
            timezone="America/New_York",
        )
        db.add(org)
        db.flush()

        users = {
            "org_admin": User(
                firstname="Olivia",
                lastname="Admin",
                username="orgadmin",
                email="orgadmin@demo.com",
                role="admin",
                hashed_password=hash_password("password"),
            ),
            "teacher": User(
                firstname="Tariq",
                lastname="Teacher",
                username="teacher",
                email="teacher@demo.com",
                role="teacher",
                hashed_password=hash_password("password"),
            ),
            "parent": User(
                firstname="Paula",
                lastname="Parent",
                username="parent",
                email="parent@demo.com",
                role="parent",
                hashed_password=hash_password("password"),
            ),
            "student1": User(
                firstname="Sami",
                lastname="Student",
                username="student1",
                email="student1@demo.com",
                role="student",
                hashed_password=hash_password("password"),
            ),
            "student2": User(
                firstname="Sasha",
                lastname="Student",
                username="student2",
                email="student2@demo.com",
                role="student",
                hashed_password=hash_password("password"),
            ),
            "content_admin": User(
                firstname="Carmen",
                lastname="Content",
                username="contentadmin",
                email="content@demo.com",
                role="teacher",
                hashed_password=hash_password("password"),
            ),
        }
        db.add_all(users.values())
        db.flush()

        membership_map = {
            "org_admin": OrganizationRole.ORG_ADMIN,
            "teacher": OrganizationRole.TEACHER,
            "parent": OrganizationRole.PARENT,
            "student1": OrganizationRole.STUDENT,
            "student2": OrganizationRole.STUDENT,
            "content_admin": OrganizationRole.CONTENT_ADMIN,
        }
        for key, role in membership_map.items():
            db.add(
                OrganizationMembership(
                    organization_id=org.id,
                    user_id=users[key].id,
                    role=role,
                )
            )

        course = Course(
            title="K–5 Introduction to Africa",
            description="Flagship K–5 course with an updated course versioning flow.",
            subject="History",
            age_band_min=5,
            age_band_max=11,
            default_locale="en",
            created_by=users["content_admin"].id,
            organization_id=org.id,
        )
        db.add(course)
        db.flush()

        version = CourseVersion(
            course_id=course.id,
            version_number=1,
            status=CourseVersionStatus.PUBLISHED,
            changelog="Initial published version",
            published_at=datetime.utcnow(),
            published_by=users["content_admin"].id,
        )
        db.add(version)
        db.flush()

        section = Section(
            organization_id=org.id,
            course_version_id=version.id,
            name="Grade 3 - Cohort A",
            mode=SectionMode.IN_PERSON,
            start_date=datetime.utcnow(),
            created_by=users["teacher"].id,
        )
        db.add(section)
        db.flush()

        db.add_all([
            Enrollment(section_id=section.id, user_id=users["student1"].id),
            Enrollment(section_id=section.id, user_id=users["student2"].id),
        ])

        db.commit()
        print("Seeded demo data.")
    finally:
        db.close()


if __name__ == "__main__":
    run()
