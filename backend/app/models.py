from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Table,
    Boolean,
    Text,
    Float,
    JSON,
    UniqueConstraint,
)
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

user_units = Table(
"user_units",
Base.metadata,
Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
Column("unit_id", UUID(as_uuid=True), ForeignKey("units.id"), primary_key=True),
)

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
    program_progress = relationship(
        "StudentProgramProgress",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    assessment_attempts = relationship(
        "StudentAssessmentAttempt",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    certifications = relationship(
        "StudentCertification",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    access_grants = relationship("AccessGrant", back_populates="user")


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, nullable=False)
    type = Column(
    SqlEnum(
        OrganizationType,
        name="organization_type_enum",
        values_callable=lambda enum_cls: [e.value for e in enum_cls],
        native_enum=True,
        validate_strings=True,
        create_constraint=True,
    ),
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
    programs = relationship("Program", back_populates="organization")
    workspaces = relationship("Workspace", back_populates="organization")


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
        nullable=False,
        default=MembershipStatus.ACTIVE,
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
    learning_objectives = Column(Text, nullable=True)
    skill_tags = Column(JSON, nullable=True)
    standards_metadata = Column(JSON, nullable=True)
    revision_number = Column(Integer, nullable=False, default=1)
    revision_label = Column(String, nullable=True)
    revision_status = Column(String, nullable=False, default="current")
    revision_metadata = Column(JSON, nullable=True, default=dict)
    previous_revision_id = Column(UUID(as_uuid=True), nullable=True)
    superseded_by_id = Column(UUID(as_uuid=True), nullable=True)
    lineage_status = Column(String, nullable=False, default="standalone")
    lineage_metadata = Column(JSON, nullable=True, default=dict)
    published_at = Column(DateTime, nullable=True)
    deprecated_at = Column(DateTime, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student_courses = relationship("StudentCourse", back_populates="course", cascade="all, delete-orphan")
    units = relationship("Unit", back_populates="course", cascade="all, delete-orphan")
    versions = relationship("CourseVersion", back_populates="course", cascade="all, delete-orphan")
    organization = relationship("Organization", back_populates="courses")
    program_links = relationship(
        "ProgramCourse",
        back_populates="course",
        cascade="all, delete-orphan",
    )
    assessments = relationship("Assessment", back_populates="course")
    products = relationship("Product", back_populates="course")


class CourseVersion(Base):
    __tablename__ = "course_versions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    status = Column(
    SqlEnum(
        CourseVersionStatus,
        name="course_version_status_enum",
        values_callable=lambda enum_cls: [e.value for e in enum_cls],
        native_enum=True,
        validate_strings=True,
        create_constraint=True,
    ),
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
    revision_number = Column(Integer, nullable=False, default=1)
    revision_label = Column(String, nullable=True)
    revision_status = Column(String, nullable=False, default="current")
    revision_metadata = Column(JSON, nullable=True, default=dict)
    previous_revision_id = Column(UUID(as_uuid=True), nullable=True)
    superseded_by_id = Column(UUID(as_uuid=True), nullable=True)
    lineage_status = Column(String, nullable=False, default="standalone")
    lineage_metadata = Column(JSON, nullable=True, default=dict)
    published_at = Column(DateTime, nullable=True)
    deprecated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="units")
    course_version = relationship("CourseVersion", back_populates="units")
    completed_by = relationship("User", secondary="user_units", back_populates="completed_units")

    lessons = relationship("Lesson", back_populates="unit", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="unit")

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
    learning_objectives = Column(Text, nullable=True)
    key_concepts = Column(JSON, nullable=True)
    teacher_notes = Column(Text, nullable=True)
    discussion_questions = Column(JSON, nullable=True)
    hook = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    guided_practice = Column(Text, nullable=True)
    independent_practice = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    review_status = Column(String, nullable=False, default="draft")
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    skill_tags = Column(JSON, nullable=True)
    standards_metadata = Column(JSON, nullable=True)
    revision_number = Column(Integer, nullable=False, default=1)
    revision_label = Column(String, nullable=True)
    revision_status = Column(String, nullable=False, default="current")
    revision_metadata = Column(JSON, nullable=True, default=dict)
    previous_revision_id = Column(UUID(as_uuid=True), nullable=True)
    superseded_by_id = Column(UUID(as_uuid=True), nullable=True)
    lineage_status = Column(String, nullable=False, default="standalone")
    lineage_metadata = Column(JSON, nullable=True, default=dict)
    published_at = Column(DateTime, nullable=True)
    deprecated_at = Column(DateTime, nullable=True)
    order = Column(Integer)
    duration_minutes = Column(Integer)

    # Relationships
    unit = relationship("Unit", back_populates="lessons")
    activities = relationship("Activity", back_populates="lesson", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="lesson")
    reviewer = relationship("User")
    sources = relationship("Source", back_populates="lesson", cascade="all, delete-orphan")


class Source(Base):
    __tablename__ = "sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    citation = Column(Text, nullable=False)
    url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="sources")
    knowledge_sources = relationship("KnowledgeSource", back_populates="source")


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
    status = Column(
    SqlEnum(
        ProgressStatus,
        name="segment_status_enum",
        values_callable=lambda enum_cls: [item.value for item in enum_cls],
        create_constraint=True,
    ),
    default=ProgressStatus.NOT_STARTED,
    nullable=False,
    )
    last_updated = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    student_unit = relationship("StudentUnitProgress", back_populates="segments")
    lesson = relationship("Lesson")
    section = relationship("Section")







class Badge(Base):
    __tablename__ = "badges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    image_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    student_badges = relationship("StudentBadge", back_populates="badge", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="badge")


class StudentBadge(Base):
    __tablename__ = "student_badges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badges.id"), nullable=False)
    awarded_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User")
    badge = relationship("Badge", back_populates="student_badges")


class Program(Base):
    __tablename__ = "programs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="programs")
    courses = relationship(
        "ProgramCourse",
        back_populates="program",
        cascade="all, delete-orphan",
        order_by="ProgramCourse.order",
    )
    assessments = relationship("Assessment", back_populates="program")
    student_progress = relationship(
        "StudentProgramProgress",
        back_populates="program",
        cascade="all, delete-orphan",
    )
    certifications = relationship(
        "Certification",
        back_populates="program",
        cascade="all, delete-orphan",
    )
    products = relationship("Product", back_populates="program")


class Workspace(Base):
    __tablename__ = "workspaces"
    __table_args__ = (
        UniqueConstraint("organization_id", name="uq_workspace_organization"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=True)
    name = Column(String, nullable=False)
    slug = Column(String, nullable=True, unique=True, index=True)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="active")
    workspace_metadata = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    organization = relationship("Organization", back_populates="workspaces")
    projects = relationship("Project", back_populates="workspace", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="workspace", cascade="all, delete-orphan")
    knowledge_sources = relationship("KnowledgeSource", back_populates="workspace", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="workspace", cascade="all, delete-orphan")
    generation_runs = relationship("GenerationRun", back_populates="workspace", cascade="all, delete-orphan")
    access_grants = relationship("AccessGrant", back_populates="workspace", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="active")
    project_metadata = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="projects")
    products = relationship("Product", back_populates="project")
    knowledge_sources = relationship("KnowledgeSource", back_populates="project", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="project", cascade="all, delete-orphan")
    generation_runs = relationship("GenerationRun", back_populates="project", cascade="all, delete-orphan")
    access_grants = relationship("AccessGrant", back_populates="project")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("course_id", name="uq_product_course"),
        UniqueConstraint("program_id", name="uq_product_program"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=True)
    product_type = Column(String, nullable=False, default="course")
    title = Column(String, nullable=False)
    subtitle = Column(String, nullable=True)
    slug = Column(String, nullable=True, unique=True, index=True)
    description = Column(Text, nullable=True)
    hero_image_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft")
    review_state = Column(String, nullable=False, default="not_reviewed")
    access_state = Column(String, nullable=False, default="private")
    visibility = Column(String, nullable=False, default="draft")
    pricing_model = Column(String, nullable=False, default="internal")
    price_placeholder = Column(String, nullable=True)
    currency = Column(String, nullable=True)
    audience = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    estimated_duration = Column(String, nullable=True)
    tags = Column(JSON, nullable=True, default=list)
    category = Column(String, nullable=True)
    version = Column(String, nullable=True)
    language = Column(String, nullable=True)
    last_updated = Column(DateTime, nullable=True)
    certificate_available = Column(Boolean, nullable=False, default=False)
    featured = Column(Boolean, nullable=False, default=False)
    product_metadata = Column("metadata", JSON, nullable=True, default=dict)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="products")
    project = relationship("Project", back_populates="products")
    course = relationship("Course", back_populates="products")
    program = relationship("Program", back_populates="products")
    artifacts = relationship("Artifact", back_populates="product")
    generation_runs = relationship("GenerationRun", back_populates="product")
    access_grants = relationship("AccessGrant", back_populates="product", cascade="all, delete-orphan")


class AccessGrant(Base):
    __tablename__ = "access_grants"
    __table_args__ = (
        UniqueConstraint("user_id", "product_id", "grant_type", name="uq_access_grant_user_product_type"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    grant_type = Column(String, nullable=False, default="manual")
    status = Column(String, nullable=False, default="active")
    source = Column(String, nullable=False, default="manual")
    starts_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    grant_metadata = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="access_grants")
    product = relationship("Product", back_populates="access_grants")
    workspace = relationship("Workspace", back_populates="access_grants")
    project = relationship("Project", back_populates="access_grants")


class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=True)
    title = Column(String, nullable=False)
    source_type = Column(String, nullable=False, default="document")
    uri = Column(String, nullable=True)
    citation = Column(Text, nullable=True)
    content_hash = Column(String, nullable=True)
    status = Column(String, nullable=False, default="available")
    source_metadata = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="knowledge_sources")
    project = relationship("Project", back_populates="knowledge_sources")
    source = relationship("Source", back_populates="knowledge_sources")
    artifacts = relationship("Artifact", back_populates="knowledge_source")


class GenerationRun(Base):
    __tablename__ = "generation_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    status = Column(String, nullable=False, default="queued")
    provider = Column(String, nullable=True)
    model_name = Column(String, nullable=True)
    prompt = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    input_metadata = Column(JSON, nullable=True, default=dict)
    output_metadata = Column(JSON, nullable=True, default=dict)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="generation_runs")
    project = relationship("Project", back_populates="generation_runs")
    product = relationship("Product", back_populates="generation_runs")
    artifacts = relationship("Artifact", back_populates="generation_run")


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=True)
    generation_run_id = Column(UUID(as_uuid=True), ForeignKey("generation_runs.id"), nullable=True)
    knowledge_source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id"), nullable=True)
    artifact_type = Column(String, nullable=False, default="documentation")
    title = Column(String, nullable=False)
    body = Column(Text, nullable=True)
    uri = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft")
    review_state = Column(String, nullable=False, default="review_required")
    artifact_metadata = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    workspace = relationship("Workspace", back_populates="artifacts")
    project = relationship("Project", back_populates="artifacts")
    product = relationship("Product", back_populates="artifacts")
    generation_run = relationship("GenerationRun", back_populates="artifacts")
    knowledge_source = relationship("KnowledgeSource", back_populates="artifacts")


class ProgramCourse(Base):
    __tablename__ = "program_courses"
    __table_args__ = (UniqueConstraint("program_id", "course_id", name="uq_program_course"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    order = Column(Integer, nullable=False, default=1)
    is_required = Column(Boolean, nullable=False, default=True)

    program = relationship("Program", back_populates="courses")
    course = relationship("Course", back_populates="program_links")


class StudentProgramProgress(Base):
    __tablename__ = "student_program_progress"
    __table_args__ = (
        UniqueConstraint("student_id", "program_id", name="uq_student_program_progress"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    status = Column(String, nullable=False, default="active")
    enrolled_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_activity_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("User", back_populates="program_progress")
    program = relationship("Program", back_populates="student_progress")
    assessment_attempts = relationship(
        "StudentAssessmentAttempt",
        back_populates="program_progress",
    )


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("units.id"), nullable=True)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=True)
    assessment_scope = Column(String, nullable=True)
    assessment_state = Column(String, nullable=True, default="published")
    availability_state = Column(String, nullable=True, default="available")
    passing_score = Column(Float, nullable=False, default=70.0)
    max_attempts = Column(Integer, nullable=True)
    policy_metadata = Column(JSON, nullable=True, default=dict)
    lifecycle_metadata = Column(JSON, nullable=True, default=dict)
    revision_number = Column(Integer, nullable=False, default=1)
    revision_label = Column(String, nullable=True)
    revision_status = Column(String, nullable=False, default="current")
    revision_metadata = Column(JSON, nullable=True, default=dict)
    previous_revision_id = Column(UUID(as_uuid=True), nullable=True)
    superseded_by_id = Column(UUID(as_uuid=True), nullable=True)
    lineage_status = Column(String, nullable=False, default="standalone")
    lineage_metadata = Column(JSON, nullable=True, default=dict)
    published_at = Column(DateTime, nullable=True)
    deprecated_at = Column(DateTime, nullable=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    unit = relationship("Unit", back_populates="assessments")
    lesson = relationship("Lesson", back_populates="assessments")
    course = relationship("Course", back_populates="assessments")
    program = relationship("Program", back_populates="assessments")
    questions = relationship(
        "Question",
        back_populates="assessment",
        cascade="all, delete-orphan",
        order_by="Question.order",
    )
    attempts = relationship(
        "StudentAssessmentAttempt",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )
    events = relationship("AssessmentAttemptEvent", back_populates="assessment")
    competency_alignments = relationship(
        "AssessmentCompetencyAlignment",
        back_populates="assessment",
        cascade="all, delete-orphan",
    )


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    question_type = Column(String, nullable=False, default="multiple_choice")
    choices = Column(JSON, nullable=True)
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    points = Column(Float, nullable=False, default=1.0)
    order = Column(Integer, nullable=False, default=1)

    assessment = relationship("Assessment", back_populates="questions")
    answers = relationship(
        "StudentAssessmentAnswer",
        back_populates="question",
        cascade="all, delete-orphan",
    )
    competency_alignments = relationship(
        "AssessmentCompetencyAlignment",
        back_populates="question",
        cascade="all, delete-orphan",
    )


class AssessmentCompetencyAlignment(Base):
    __tablename__ = "assessment_competency_alignments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=True)
    objective_key = Column(String, nullable=False)
    objective_title = Column(String, nullable=True)
    objective_type = Column(String, nullable=False, default="objective")
    weight = Column(Float, nullable=False, default=1.0)
    mastery_threshold = Column(Float, nullable=False, default=80.0)
    metadata_ = Column("metadata", JSON, nullable=True, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="competency_alignments")
    question = relationship("Question", back_populates="competency_alignments")


class StudentAssessmentAttempt(Base):
    __tablename__ = "student_assessment_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    program_progress_id = Column(
        UUID(as_uuid=True),
        ForeignKey("student_program_progress.id"),
        nullable=True,
    )
    score = Column(Float, nullable=False, default=0.0)
    max_score = Column(Float, nullable=False, default=0.0)
    passed = Column(Boolean, nullable=False, default=False)
    submitted_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    assessment = relationship("Assessment", back_populates="attempts")
    student = relationship("User", back_populates="assessment_attempts")
    program_progress = relationship(
        "StudentProgramProgress",
        back_populates="assessment_attempts",
    )
    answers = relationship(
        "StudentAssessmentAnswer",
        back_populates="attempt",
        cascade="all, delete-orphan",
    )
    events = relationship(
        "AssessmentAttemptEvent",
        back_populates="attempt",
        order_by="AssessmentAttemptEvent.created_at",
    )


class StudentAssessmentAnswer(Base):
    __tablename__ = "student_assessment_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    attempt_id = Column(
        UUID(as_uuid=True),
        ForeignKey("student_assessment_attempts.id"),
        nullable=False,
    )
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    awarded_points = Column(Float, nullable=False, default=0.0)

    attempt = relationship("StudentAssessmentAttempt", back_populates="answers")
    question = relationship("Question", back_populates="answers")


class AssessmentAttemptEvent(Base):
    __tablename__ = "assessment_attempt_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    attempt_id = Column(
        UUID(as_uuid=True),
        ForeignKey("student_assessment_attempts.id"),
        nullable=False,
    )
    event_type = Column(String, nullable=False)
    score = Column(Float, nullable=True)
    max_score = Column(Float, nullable=True)
    passed = Column(Boolean, nullable=True)
    event_metadata = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    assessment = relationship("Assessment")
    student = relationship("User")
    attempt = relationship("StudentAssessmentAttempt", back_populates="events")


class Certification(Base):
    __tablename__ = "certifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    program_id = Column(UUID(as_uuid=True), ForeignKey("programs.id"), nullable=False)
    badge_id = Column(UUID(as_uuid=True), ForeignKey("badges.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    program = relationship("Program", back_populates="certifications")
    badge = relationship("Badge", back_populates="certifications")
    requirements = relationship(
        "CertificationRequirement",
        back_populates="certification",
        cascade="all, delete-orphan",
    )
    issued = relationship(
        "StudentCertification",
        back_populates="certification",
        cascade="all, delete-orphan",
    )


class CertificationRequirement(Base):
    __tablename__ = "certification_requirements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    certification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("certifications.id"),
        nullable=False,
    )
    requirement_type = Column(String, nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True)
    assessment_id = Column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=True)
    minimum_score = Column(Float, nullable=True)

    certification = relationship("Certification", back_populates="requirements")
    course = relationship("Course")
    assessment = relationship("Assessment")


class StudentCertification(Base):
    __tablename__ = "student_certifications"
    __table_args__ = (
        UniqueConstraint("student_id", "certification_id", name="uq_student_certification"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    certification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("certifications.id"),
        nullable=False,
    )
    awarded_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    score_snapshot = Column(Float, nullable=True)

    student = relationship("User", back_populates="certifications")
    certification = relationship("Certification", back_populates="issued")


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
    SqlEnum(
        SectionMode,
        name="section_mode_enum",
        values_callable=lambda enum_cls: [e.value for e in enum_cls],
        native_enum=True,
        validate_strings=True,
        create_constraint=True,
    ),
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
    SqlEnum(
        EnrollmentStatus,
        name="enrollment_status_enum",
        values_callable=lambda enum_cls: [e.value for e in enum_cls],
        native_enum=True,
        validate_strings=True,
        create_constraint=True,
    ),
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
    SqlEnum(
        AssignmentTargetType,
        name="assignment_target_enum",
        values_callable=lambda enum_cls: [e.value for e in enum_cls],
        native_enum=True,
        validate_strings=True,
        create_constraint=True,
    ),
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
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            native_enum=True,
            validate_strings=True,
            create_constraint=True,
        ),
        default=AssignmentSubmissionStatus.NOT_STARTED,
        nullable=False,
    )
    submitted_at = Column(DateTime, nullable=True)

    assignment = relationship("Assignment", back_populates="submissions")
    user = relationship("User")
