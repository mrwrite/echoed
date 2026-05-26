import os
import uuid
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes import start_course
from app.auth import get_current_user
from app.crud import progress as progress_crud
from app.database import get_db
from app.models import (
    User,
    Course,
    Unit,
    Lesson,
    Source,
    StudentCourse,
    StudentUnitProgress,
    SegmentProgress,
)
from app.enum import ProgressStatus


@pytest.fixture
def test_student(db_session):
    student = User(
        id=uuid.uuid4(),
        firstname="Start",
        lastname="User",
        username=f"start_user_{uuid.uuid4()}",
        email=f"start_{uuid.uuid4()}@example.com",
        hashed_password="fake",
        role="student"
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


@pytest.fixture
def test_course_and_unit_and_lesson(db_session):
    course = Course(id=uuid.uuid4(), title="Course A", description="Test")
    unit = Unit(id=uuid.uuid4(), title="Unit A", course_id=course.id, order=1)
    lesson = Lesson(
        id=uuid.uuid4(),
        title="Lesson A",
        unit_id=unit.id,
        duration_minutes=10,
        order=1,
        objective="Objective",
        learning_objectives="Learning objective",
        key_concepts=["concept"],
        hook="Hook",
        content="Content",
        guided_practice="Guided",
        independent_practice="Independent",
        assessment="Assessment",
        review_status="approved",
    )

    db_session.add_all([course, unit, lesson])
    db_session.commit()
    db_session.add(Source(lesson_id=lesson.id, citation="Source", url="https://example.com/source"))
    db_session.commit()
    return course, unit, lesson


def override_get_current_user(user):
    return lambda: user


def _build_test_client(db_session, user):
    test_app = FastAPI()
    test_app.include_router(start_course.router, prefix="/api")
    test_app.dependency_overrides[get_current_user] = override_get_current_user(user)

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    return TestClient(test_app)


def test_student_can_start_course(db_session, test_student, test_course_and_unit_and_lesson):
    course, unit, lesson = test_course_and_unit_and_lesson

    # Enroll the student
    student_course = StudentCourse(student_id=test_student.id, course_id=course.id)
    db_session.add(student_course)
    db_session.commit()
    db_session.refresh(student_course)

    client = _build_test_client(db_session, test_student)

    response = client.post("/api/start-course", json={"course_id": str(course.id)})

    assert response.status_code == 200
    data = response.json()
    assert data["delivery_state"] == "governed_available"
    assert data["lesson_id"] == str(lesson.id)
    assert data["status"] == ProgressStatus.IN_PROGRESS.value

    # Verify unit progress
    unit_progress = db_session.query(StudentUnitProgress).filter_by(
        student_course_id=student_course.id,
        unit_id=unit.id
    ).first()
    assert unit_progress is not None
    assert unit_progress.status == ProgressStatus.IN_PROGRESS

    # Verify segment progress
    segment_progress = db_session.query(SegmentProgress).filter_by(
        student_unit_id=unit_progress.id,
        lesson_id=lesson.id
    ).first()
    assert segment_progress is not None
    assert segment_progress.status == ProgressStatus.IN_PROGRESS


def test_start_course_requires_enrollment(db_session, test_student, test_course_and_unit_and_lesson):
    course, _, _ = test_course_and_unit_and_lesson

    client = _build_test_client(db_session, test_student)

    response = client.post("/api/start-course", json={"course_id": str(course.id)})

    assert response.status_code == 403
    assert response.json()["detail"] == "Not enrolled in this course."


def test_start_course_rejects_completed_course(db_session, test_student, test_course_and_unit_and_lesson):
    course, _, _ = test_course_and_unit_and_lesson

    # Enroll the student and mark the course as completed
    student_course = StudentCourse(student_id=test_student.id, course_id=course.id, status="completed")
    db_session.add(student_course)
    db_session.commit()

    client = _build_test_client(db_session, test_student)

    response = client.post("/api/start-course", json={"course_id": str(course.id)})

    assert response.status_code == 400
    assert response.json()["detail"] == "Course already completed"


def test_start_course_resumes_in_progress_unit(db_session, test_student):
    """If a student already has an in-progress unit, the endpoint should
    return the next segment from that unit rather than restarting the course."""

    # Create course with two units and one lesson each
    course = Course(id=uuid.uuid4(), title="Course B", description="Test")
    unit1 = Unit(id=uuid.uuid4(), title="Unit 1", course_id=course.id, order=1)
    unit2 = Unit(id=uuid.uuid4(), title="Unit 2", course_id=course.id, order=2)
    lesson1 = Lesson(
        id=uuid.uuid4(),
        title="Lesson 1",
        unit_id=unit1.id,
        duration_minutes=5,
        order=1,
        objective="Objective",
        learning_objectives="Learning objective",
        key_concepts=["concept"],
        hook="Hook",
        content="Content",
        guided_practice="Guided",
        independent_practice="Independent",
        assessment="Assessment",
        review_status="approved",
    )
    lesson2 = Lesson(
        id=uuid.uuid4(),
        title="Lesson 2",
        unit_id=unit2.id,
        duration_minutes=5,
        order=1,
        objective="Objective",
        learning_objectives="Learning objective",
        key_concepts=["concept"],
        hook="Hook",
        content="Content",
        guided_practice="Guided",
        independent_practice="Independent",
        assessment="Assessment",
        review_status="approved",
    )

    db_session.add_all([course, unit1, unit2, lesson1, lesson2])
    db_session.commit()
    db_session.add_all([
        Source(lesson_id=lesson1.id, citation="Source 1", url="https://example.com/1"),
        Source(lesson_id=lesson2.id, citation="Source 2", url="https://example.com/2"),
    ])
    db_session.commit()

    # Enroll student and set progress: unit1 completed, unit2 in progress
    student_course = StudentCourse(student_id=test_student.id, course_id=course.id)
    db_session.add(student_course)
    db_session.commit()
    db_session.refresh(student_course)

    up1 = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=unit1.id,
        status=ProgressStatus.COMPLETED,
    )
    up2 = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=unit2.id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add_all([up1, up2])
    db_session.commit()
    db_session.refresh(up2)

    seg1 = SegmentProgress(
        student_unit_id=up1.id,
        lesson_id=lesson1.id,
        status=ProgressStatus.COMPLETED,
    )
    seg2 = SegmentProgress(
        student_unit_id=up2.id,
        lesson_id=lesson2.id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add_all([seg1, seg2])
    db_session.commit()

    client = _build_test_client(db_session, test_student)

    response = client.post("/api/start-course", json={"course_id": str(course.id)})

    assert response.status_code == 200
    data = response.json()
    assert data["delivery_state"] == "governed_available"
    # Should return the lesson from the second unit (in progress)
    assert data["lesson_id"] == str(lesson2.id)
    assert data["unit_progress_id"] == str(up2.id)


def test_start_course_blocks_draft_only_unit(db_session, test_student):
    course = Course(id=uuid.uuid4(), title="Course C", description="Test")
    unit = Unit(id=uuid.uuid4(), title="Unit Draft", course_id=course.id, order=1)
    lesson = Lesson(id=uuid.uuid4(), title="Draft Lesson", unit_id=unit.id, duration_minutes=5, order=1, review_status="draft")
    db_session.add_all([course, unit, lesson])
    db_session.commit()

    student_course = StudentCourse(student_id=test_student.id, course_id=course.id)
    db_session.add(student_course)
    db_session.commit()

    client = _build_test_client(db_session, test_student)

    response = client.post("/api/start-course", json={"course_id": str(course.id)})

    assert response.status_code == 200
    data = response.json()
    assert data["delivery_state"] == "no_approved_content"
    assert data["lesson_id"] is None


def test_completed_governed_unit_advances_to_next_governed_unit(db_session, test_student):
    course = Course(id=uuid.uuid4(), title="Course D", description="Test")
    unit1 = Unit(id=uuid.uuid4(), title="Unit 1", course_id=course.id, order=1)
    unit2 = Unit(id=uuid.uuid4(), title="Unit 2", course_id=course.id, order=2)
    lesson1 = Lesson(
        id=uuid.uuid4(),
        title="Lesson 1",
        unit_id=unit1.id,
        duration_minutes=5,
        order=1,
        objective="Objective",
        learning_objectives="Learning objective",
        key_concepts=["concept"],
        hook="Hook",
        content="Content",
        guided_practice="Guided",
        independent_practice="Independent",
        assessment="Assessment",
        review_status="approved",
    )
    lesson2 = Lesson(
        id=uuid.uuid4(),
        title="Lesson 2",
        unit_id=unit2.id,
        duration_minutes=5,
        order=1,
        objective="Objective",
        learning_objectives="Learning objective",
        key_concepts=["concept"],
        hook="Hook",
        content="Content",
        guided_practice="Guided",
        independent_practice="Independent",
        assessment="Assessment",
        review_status="approved",
    )
    db_session.add_all([course, unit1, unit2, lesson1, lesson2])
    db_session.commit()
    db_session.add_all([
        Source(lesson_id=lesson1.id, citation="Source 1", url="https://example.com/1"),
        Source(lesson_id=lesson2.id, citation="Source 2", url="https://example.com/2"),
    ])
    db_session.commit()

    student_course = StudentCourse(student_id=test_student.id, course_id=course.id)
    db_session.add(student_course)
    db_session.commit()
    db_session.refresh(student_course)

    start_state = progress_crud.resolve_governed_progression(db_session, student_course.id)
    current_segment = (
        db_session.query(SegmentProgress)
        .filter_by(
            student_unit_id=start_state["unit_progress_id"],
            lesson_id=lesson1.id,
        )
        .one()
    )

    progress_crud.update_segment_progress_status(
        db_session,
        current_segment.id,
        ProgressStatus.COMPLETED,
    )

    next_state = progress_crud.resolve_governed_progression(db_session, student_course.id)
    assert next_state["delivery_state"] == "governed_available"
    assert next_state["lesson_id"] == lesson2.id


def test_completion_does_not_advance_to_stale_non_governed_segment(db_session, test_student):
    course = Course(id=uuid.uuid4(), title="Course E", description="Test")
    unit = Unit(id=uuid.uuid4(), title="Unit 1", course_id=course.id, order=1)
    approved_lesson = Lesson(
        id=uuid.uuid4(),
        title="Approved Lesson",
        unit_id=unit.id,
        duration_minutes=5,
        order=1,
        objective="Objective",
        learning_objectives="Learning objective",
        key_concepts=["concept"],
        hook="Hook",
        content="Content",
        guided_practice="Guided",
        independent_practice="Independent",
        assessment="Assessment",
        review_status="approved",
    )
    draft_lesson = Lesson(
        id=uuid.uuid4(),
        title="Draft Lesson",
        unit_id=unit.id,
        duration_minutes=5,
        order=2,
        review_status="draft",
    )
    db_session.add_all([course, unit, approved_lesson, draft_lesson])
    db_session.commit()
    db_session.add(Source(lesson_id=approved_lesson.id, citation="Source", url="https://example.com/source"))
    db_session.commit()

    student_course = StudentCourse(student_id=test_student.id, course_id=course.id)
    db_session.add(student_course)
    db_session.commit()
    db_session.refresh(student_course)

    start_state = progress_crud.resolve_governed_progression(db_session, student_course.id)
    unit_progress = db_session.query(StudentUnitProgress).filter_by(id=start_state["unit_progress_id"]).one()
    approved_segment = (
        db_session.query(SegmentProgress)
        .filter_by(student_unit_id=unit_progress.id, lesson_id=approved_lesson.id)
        .one()
    )
    stale_draft_segment = SegmentProgress(
        student_unit_id=unit_progress.id,
        lesson_id=draft_lesson.id,
        status=ProgressStatus.NOT_STARTED,
    )
    db_session.add(stale_draft_segment)
    db_session.commit()
    db_session.refresh(stale_draft_segment)

    progress_crud.update_segment_progress_status(
        db_session,
        approved_segment.id,
        ProgressStatus.COMPLETED,
    )

    db_session.refresh(stale_draft_segment)
    db_session.refresh(unit_progress)
    db_session.refresh(student_course)
    assert stale_draft_segment.status == ProgressStatus.NOT_STARTED
    assert unit_progress.status == ProgressStatus.COMPLETED
    assert student_course.status == "completed"
