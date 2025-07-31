from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import Enum as SqlEnum
from app.enum import ProgressStatus 
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


class Course(Base):
    __tablename__ = 'courses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student_courses = relationship("StudentCourse", back_populates="course", cascade="all, delete-orphan")
    units = relationship("Unit", back_populates="course", cascade="all, delete-orphan")

class Unit(Base):
    __tablename__ = 'units'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey('courses.id'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(String)
    order = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="units")
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
    enrolled_on = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String, default="active")  # optional: active, completed, withdrawn

    student = relationship("User", back_populates="student_courses")
    course = relationship("Course", back_populates="student_courses")
    unit_progress = relationship("StudentUnitProgress", back_populates="student_course", cascade="all, delete-orphan")


class StudentUnitProgress(Base):
    __tablename__ = 'student_unit_progress'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_course_id = Column(UUID(as_uuid=True), ForeignKey('student_courses.id'), nullable=False)
    unit_id = Column(
        UUID(as_uuid=True),
        ForeignKey('units.id', ondelete='CASCADE'),
        nullable=False,
    )
    status = Column(SqlEnum(ProgressStatus, name="progress_status_enum", create_constraint=True), default=ProgressStatus.NOT_STARTED)
    last_updated = Column(DateTime, default=datetime.utcnow)

    student_course = relationship("StudentCourse", back_populates="unit_progress")
    unit = relationship("Unit", back_populates="student_progress")

    segments = relationship("SegmentProgress", back_populates="student_unit", cascade="all, delete-orphan")

class SegmentProgress(Base):
    __tablename__ = 'segment_progress'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    student_unit_id = Column(UUID(as_uuid=True), ForeignKey('student_unit_progress.id'), nullable=False)
    lesson_id = Column(
        UUID(as_uuid=True),
        ForeignKey('lessons.id', ondelete='CASCADE'),
        nullable=False
    )
    status = Column(SqlEnum(ProgressStatus, name="segment_status_enum", create_constraint=True), default=ProgressStatus.NOT_STARTED)
    last_updated = Column(DateTime, default=datetime.utcnow)

    student_unit = relationship("StudentUnitProgress", back_populates="segments")
    lesson = relationship("Lesson")




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

