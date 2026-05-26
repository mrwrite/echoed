import uuid

from app.enum import ProgressStatus
from app.lesson_governance import evaluate_course_publish_readiness
from app.models import Course, Lesson, SegmentProgress, Source, StudentCourse, StudentUnitProgress, Unit, User


def _ready_lesson_kwargs(title: str, *, order: int | None = 1, review_status: str = "approved") -> dict:
    return {
        "title": title,
        "objective": "Evaluate evidence and explain what it teaches.",
        "learning_objectives": "Students will explain a key idea using evidence from the lesson.",
        "key_concepts": ["evidence", "source", "explanation"],
        "teacher_notes": "Prompt learners to cite one detail before answering.",
        "discussion_questions": ["What detail helped you learn something new?"],
        "hook": "Start with a short observable fact.",
        "content": "Explain the lesson idea with a brief supporting example.",
        "guided_practice": "Model one response with the class.",
        "independent_practice": "Have learners write or say one response on their own.",
        "assessment": "Short oral or written check for understanding.",
        "review_status": review_status,
        "order": order,
    }


def _add_source(db_session, lesson: Lesson, citation: str | None = None):
    db_session.add(
        Source(
            lesson_id=lesson.id,
            citation=citation or f"{lesson.title} source",
            url="https://example.com/source",
        )
    )


def _create_ready_course(db_session) -> Course:
    course = Course(id=uuid.uuid4(), title="Ready Course", description="Publish-ready course")
    unit_one = Unit(id=uuid.uuid4(), title="Unit One", course_id=course.id, order=1)
    unit_two = Unit(id=uuid.uuid4(), title="Unit Two", course_id=course.id, order=2)
    db_session.add_all([course, unit_one, unit_two])
    db_session.flush()

    lessons = [
        Lesson(unit_id=unit_one.id, **_ready_lesson_kwargs("Lesson 1", order=1)),
        Lesson(unit_id=unit_one.id, **_ready_lesson_kwargs("Lesson 2", order=2)),
        Lesson(unit_id=unit_two.id, **_ready_lesson_kwargs("Lesson 3", order=1)),
    ]
    db_session.add_all(lessons)
    db_session.flush()
    for lesson in lessons:
        _add_source(db_session, lesson)

    db_session.commit()
    db_session.refresh(course)
    return course


def test_ready_course_passes_publish_readiness_checks(db_session):
    course = _create_ready_course(db_session)

    readiness = evaluate_course_publish_readiness(course)

    assert readiness.is_ready is True
    assert readiness.blocking_issues == []
    assert readiness.warnings == []


def test_draft_or_not_ready_lesson_blocks_course_readiness(db_session):
    course = Course(id=uuid.uuid4(), title="Blocked Course", description="Course with a draft lesson")
    unit = Unit(id=uuid.uuid4(), title="Unit One", course_id=course.id, order=1)
    db_session.add_all([course, unit])
    db_session.flush()

    lesson = Lesson(unit_id=unit.id, **_ready_lesson_kwargs("Draft Lesson", review_status="draft"))
    db_session.add(lesson)
    db_session.flush()
    _add_source(db_session, lesson)
    db_session.commit()
    db_session.refresh(course)

    readiness = evaluate_course_publish_readiness(course)

    assert readiness.is_ready is False
    assert any(issue.code == "review_status_not_approved" for issue in readiness.blocking_issues)


def test_missing_sources_block_course_readiness(db_session):
    course = Course(id=uuid.uuid4(), title="Missing Source Course", description="Course with missing source")
    unit = Unit(id=uuid.uuid4(), title="Unit One", course_id=course.id, order=1)
    db_session.add_all([course, unit])
    db_session.flush()

    lesson = Lesson(unit_id=unit.id, **_ready_lesson_kwargs("Unsourced Lesson"))
    db_session.add(lesson)
    db_session.commit()
    db_session.refresh(course)

    readiness = evaluate_course_publish_readiness(course)

    assert readiness.is_ready is False
    assert any(
        issue.code == "missing_readiness_field" and "sources" in issue.message
        for issue in readiness.blocking_issues
    )


def test_duplicate_or_missing_order_produces_blocking_issues(db_session):
    course = Course(id=uuid.uuid4(), title="Unordered Course", description="Course with ordering problems")
    unit_one = Unit(id=uuid.uuid4(), title="Unit One", course_id=course.id, order=1)
    unit_two = Unit(id=uuid.uuid4(), title="Unit Two", course_id=course.id, order=1)
    db_session.add_all([course, unit_one, unit_two])
    db_session.flush()

    lesson_one = Lesson(unit_id=unit_one.id, **_ready_lesson_kwargs("Lesson One", order=1))
    lesson_two = Lesson(unit_id=unit_one.id, **_ready_lesson_kwargs("Lesson Two", order=1))
    lesson_three = Lesson(unit_id=unit_two.id, **_ready_lesson_kwargs("Lesson Three", order=None))
    db_session.add_all([lesson_one, lesson_two, lesson_three])
    db_session.flush()
    for lesson in (lesson_one, lesson_two, lesson_three):
        _add_source(db_session, lesson)
    db_session.commit()
    db_session.refresh(course)

    readiness = evaluate_course_publish_readiness(course)

    duplicate_codes = [issue.code for issue in readiness.blocking_issues if issue.code == "duplicate_order"]
    missing_codes = [issue.code for issue in readiness.blocking_issues if issue.code == "missing_order"]

    assert readiness.is_ready is False
    assert len(duplicate_codes) >= 2
    assert missing_codes


def test_publish_readiness_check_is_read_only_for_progress_state(db_session):
    course = _create_ready_course(db_session)
    student = User(
        id=uuid.uuid4(),
        firstname="Learner",
        lastname="State",
        username=f"learner_{uuid.uuid4()}",
        email=f"learner_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(course)

    first_unit = sorted(course.units, key=lambda unit: unit.order)[0]
    first_lesson = sorted(first_unit.lessons, key=lambda lesson: lesson.order)[0]

    student_course = StudentCourse(student_id=student.id, course_id=course.id, status="in_progress")
    db_session.add(student_course)
    db_session.commit()
    db_session.refresh(student_course)

    unit_progress = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=first_unit.id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add(unit_progress)
    db_session.commit()
    db_session.refresh(unit_progress)

    segment_progress = SegmentProgress(
        student_unit_id=unit_progress.id,
        lesson_id=first_lesson.id,
        status=ProgressStatus.NOT_STARTED,
    )
    db_session.add(segment_progress)
    db_session.commit()
    db_session.refresh(segment_progress)

    baseline = (
        student_course.status,
        unit_progress.status,
        segment_progress.status,
        db_session.query(StudentCourse).count(),
        db_session.query(StudentUnitProgress).count(),
        db_session.query(SegmentProgress).count(),
    )

    readiness = evaluate_course_publish_readiness(course)

    db_session.refresh(student_course)
    db_session.refresh(unit_progress)
    db_session.refresh(segment_progress)
    after = (
        student_course.status,
        unit_progress.status,
        segment_progress.status,
        db_session.query(StudentCourse).count(),
        db_session.query(StudentUnitProgress).count(),
        db_session.query(SegmentProgress).count(),
    )

    assert readiness.is_ready is True
    assert after == baseline
