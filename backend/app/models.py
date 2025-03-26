from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
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
    enrolled_courses = relationship("Course", secondary="user_courses", back_populates="students")
    completed_units = relationship("Unit", secondary="user_units", back_populates="completed_by")


class Course(Base):
    __tablename__ = 'courses'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    students = relationship("User", secondary="user_courses", back_populates="enrolled_courses")
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


user_courses = Table(
    "user_courses",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("course_id", UUID(as_uuid=True), ForeignKey("courses.id"), primary_key=True),
)

user_units = Table(
    "user_units",
    Base.metadata,
    Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),
    Column("unit_id", UUID(as_uuid=True), ForeignKey("units.id"), primary_key=True),
)