from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Boolean, Text
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Enum as SqlEnum
from app.enum import (
    ProgressStatus,
    OrganizationType,
    OrganizationRole,
    MembershipStatus,
    CourseVersionStatus,
    SectionMode,
    EnrollmentStatus,
    AssignmentTargetType,
    AssignmentSubmissionStatus,
)
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default='student')
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student_courses = relationship("StudentCourse", back_populates="student", cascade="all, delete-orphan")
    completed_units = relationship("Unit", secondary="user_units", back_populates="completed_by")
    organization_memberships = relationship(
        "OrganizationMembership",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    preferences = relationship(
        "UserPreferences",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    sections_created = relationship("Section", back_populates="creator")
    assignments_created = relationship("Assignment", back_populates="creator")
    lesson_sessions_started = relationship("LessonSession", back_populates="starter")


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    type = Column(
        SqlEnum(OrganizationType, name="organization_type_enum", create_constraint=True),
        nullable=False,
    )
    country = Column(String, nullable=True)
    timezone = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    memberships = relationship(
        "OrganizationMembership",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    invites = relationship(
        "OrganizationInvite",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    courses = relationship("Course", back_populates="organization")
    sections = relationship("Section", back_populates="organization")


class OrganizationMembership(Base):
    __tablename__ = "organization_memberships"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role = Column(
        SqlEnum(
            OrganizationRole,
            name="organization_role_enum",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            native_enum=True,
            validate_strings=True,
            create_constraint=True,
            ),
        nullable=False,
    )
    status = Column(
        SqlEnum(
            MembershipStatus,
            name="membership_status_enum",
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            native_enum=True,
            validate_strings=True,
            create_constraint=True,
        ),
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="memberships")
    user = relationship("User", back_populates="organization_memberships")


class OrganizationInvite(Base):
    __tablename__ = "organization_invites"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    email = Column(String, nullable=False)
    role = Column(
        SqlEnum(
        OrganizationRole,
        name="invite_role_enum",
        values_callable=lambda enum_cls: [e.value for e in enum_cls],
        native_enum=True,
        validate_strings=True,
        create_constraint=True,
        ),
        nullable=False,
    )
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    accepted_at = Column(DateTime)
    invited_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="invites")
    invited_by = relationship("User")


class UserPreferences(Base):
    __tablename__ = "user_preferences"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    locale = Column(String, default="en", nullable=False)
    timezone = Column(String, nullable=True)
    theme = Column(String, default="system", nullable=False)
    large_text = Column(Boolean, default=False)
    dyslexia_font = Column(Boolean, default=False)
    preferred_mode = Column(String, default="student")
    reading_level_mode = Column(String, default="standard")

    user = relationship("User", back_populates="preferences")


class Course(Base):
    __tablename__ = 'courses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    age_band_min = Column(Integer, nullable=True)
    age_band_max = Column(Integer, nullable=True)
    default_locale = Column(String, default="en", nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student_courses = relationship("StudentCourse", back_populates="course", cascade="all, delete-orphan")
    units = relationship("Unit", back_populates="course", cascade="all, delete-orphan")
    versions = relationship("CourseVersion", back_populates="course", cascade="all, delete-orphan")
    organization = relationship("Organization", back_populates="courses")


class CourseVersion(Base):
    __tablename__ = "course_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    status = Column(
        SqlEnum(CourseVersionStatus, name="course_version_status_enum", create_constraint=True),
        default=CourseVersionStatus.DRAFT,
        nullable=False,
    )
    changelog = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)
    published_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    course = relationship("Course", back_populates="versions")
    units = relationship("Unit", back_populates="course_version", cascade="all, delete-orphan")

class Unit(Base):
    __tablename__ = 'units'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    course_version_id = Column(UUID(as_uuid=True), ForeignKey("course_versions.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(String)
    order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="units")
    course_version = relationship("CourseVersion", back_populates="units")
    completed_by = relationship("User", secondary="user_units", back_populates="completed_units")

    lessons = relationship("Lesson", back_populates="unit", cascade="all, delete-orphan")

    student_progress = relationship(
        "StudentUnitProgress",
        back_populates="unit",
        cascade="all, delete-orphan",
    )

class Lesson(Base):
    __tablename__ = 'lessons'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey('units.id'), nullable=False)
    title = Column(String, nullable=False)
    objective = Column(String)
    order = Column(Integer)
    duration_minutes = Column(Integer)

    # Relationships
    unit = relationship("Unit", back_populates="lessons")
    activities = relationship("Activity", back_populates="lesson", cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = 'activities'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey('lessons.id'), nullable=False)
    type = Column(String)  # e.g., 'video', 'song', 'story', 'coloring', 'discussion'
    title = Column(String)
    content = Column(String)  # URL, description, or script
    order = Column(Integer)
    media_id = Column(UUID(as_uuid=True), ForeignKey('media.id'), nullable=True)
    
    media = relationship("Media")
    lesson = relationship("Lesson", back_populates="activities")
    storybook_pages = relationship(
        "StorybookPage",
        back_populates="activity",
        cascade="all, delete-orphan",
    )


class StorybookPage(Base):
    __tablename__ = "storybook_pages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    activity_id = Column(UUID(as_uuid=True), ForeignKey("activities.id"), nullable=False)
    image_url = Column(String, nullable=False)
    order = Column(Integer)

    activity = relationship("Activity", back_populates="storybook_pages")


class Media(Base):
    __tablename__ = 'media'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    type = Column(String)  # 'image', 'video', 'audio', etc.
    title = Column(String)
    url = Column(String)
    description = Column(String)


class StudentCourse(Base):
    __tablename__ = 'student_courses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=True)
    enrolled_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, default="active")  # optional: active, completed, withdrawn
    last_activity_at = Column(DateTime)
    completed_at = Column(DateTime)

    student = relationship("User", back_populates="student_courses")
    course = relationship("Course", back_populates="student_courses")
    unit_progress = relationship("StudentUnitProgress", back_populates="student_course", cascade="all, delete-orphan")
    section = relationship("Section", back_populates="student_courses")


class StudentUnitProgress(Base):
    __tablename__ = 'student_unit_progress'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_course_id = Column(UUID(as_uuid=True), ForeignKey('student_courses.id'), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=True)
    unit_id = Column(
        UUID(as_uuid=True),
        ForeignKey('units.id', ondelete='CASCADE'),
        nullable=False,
    )
    status = Column(SqlEnum(ProgressStatus, name="progress_status_enum", create_constraint=True), default=ProgressStatus.NOT_STARTED)
    last_updated = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    student_course = relationship("StudentCourse", back_populates="unit_progress")
    unit = relationship("Unit", back_populates="student_progress")
    section = relationship("Section")

    segments = relationship("SegmentProgress", back_populates="student_unit", cascade="all, delete-orphan")

class SegmentProgress(Base):
    __tablename__ = 'segment_progress'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_unit_id = Column(UUID(as_uuid=True), ForeignKey('student_unit_progress.id'), nullable=False)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=True)
    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey('lessons.id', ondelete='CASCADE'),
        nullable=False
    )
    status = Column(SqlEnum(ProgressStatus, name="segment_status_enum", create_constraint=True), default=ProgressStatus.NOT_STARTED)
    last_updated = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    student_unit = relationship("StudentUnitProgress", back_populates="segments")
    lesson = relationship("Lesson")
    section = relationship("Section")




user_units = Table(
    "user_units",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("unit_id", UUID(as_uuid=True), ForeignKey("units.id"), primary_key=True),
)


class Badge(Base):
    __tablename__ = "badges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    student_badges = relationship("StudentBadge", back_populates="badge", cascade="all, delete-orphan")


class StudentBadge(Base):
    __tablename__ = "student_badges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badges.id"), nullable=False)
    awarded_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User")
    badge = relationship("Badge", back_populates="student_badges")


class Thread(Base):
    __tablename__ = "threads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    posts = relationship("Post", back_populates="thread", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    thread_id = Column(UUID(as_uuid=True), ForeignKey("threads.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    thread = relationship("Thread", back_populates="posts")
    user = relationship("User")


class Section(Base):
    __tablename__ = "sections"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    course_version_id = Column(UUID(as_uuid=True), ForeignKey("course_versions.id"), nullable=False)
    name = Column(String, nullable=False)
    mode = Column(
        SqlEnum(SectionMode, name="section_mode_enum", create_constraint=True),
        default=SectionMode.REMOTE,
        nullable=False,
    )
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="sections")
    course_version = relationship("CourseVersion")
    creator = relationship("User", back_populates="sections_created")
    enrollments = relationship("Enrollment", back_populates="section", cascade="all, delete-orphan")
    lesson_sessions = relationship("LessonSession", back_populates="section", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="section", cascade="all, delete-orphan")
    student_courses = relationship("StudentCourse", back_populates="section")


class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    role_in_section = Column(String, default="student")
    status = Column(
        SqlEnum(EnrollmentStatus, name="enrollment_status_enum", create_constraint=True),
        default=EnrollmentStatus.ACTIVE,
        nullable=False,
    )
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    section = relationship("Section", back_populates="enrollments")
    user = relationship("User")


class LessonSession(Base):
    __tablename__ = "lesson_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    started_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)

    section = relationship("Section", back_populates="lesson_sessions")
    starter = relationship("User", back_populates="lesson_sessions_started")
    lesson = relationship("Lesson")


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"), nullable=False)
    target_type = Column(
        SqlEnum(AssignmentTargetType, name="assignment_target_enum", create_constraint=True),
        nullable=False,
    )
    target_id = Column(UUID(as_uuid=True), nullable=False)
    due_at = Column(DateTime, nullable=True)
    instructions = Column(Text, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    section = relationship("Section", back_populates="assignments")
    creator = relationship("User", back_populates="assignments_created")
    submissions = relationship(
        "AssignmentSubmission",
        back_populates="assignment",
        cascade="all, delete-orphan",
    )


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    assignment_id = Column(UUID(as_uuid=True), ForeignKey("assignments.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(
        SqlEnum(
            AssignmentSubmissionStatus,
            name="assignment_submission_status_enum",
            create_constraint=True,
        ),
        default=AssignmentSubmissionStatus.NOT_STARTED,
        nullable=False,
    )
    submitted_at = Column(DateTime, nullable=True)

    assignment = relationship("Assignment", back_populates="submissions")
    user = relationship("User")
