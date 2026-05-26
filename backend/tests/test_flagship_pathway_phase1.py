from sqlalchemy.orm import sessionmaker

from app import seed_demo
from app.crud import progress as progress_crud
from app.lesson_governance import GOVERNED_AVAILABLE, governed_lessons_for_unit, serialize_course
from app.models import Course, Program, StudentCourse, StudentUnitProgress, SegmentProgress, User


def _build_session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def _seed_with_factory(monkeypatch, session_factory):
    monkeypatch.setattr(seed_demo, "SessionLocal", session_factory)
    seed_demo.run()


def test_flagship_course_exists_with_deterministic_unit_and_lesson_order(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        assert course.standards_metadata["pathway_key"] == "introduction-to-africa"
        assert course.standards_metadata["flagship"] is True

        units = sorted(course.units, key=lambda unit: (unit.order, str(unit.id)))
        assert 2 <= len(units) <= 4
        assert [unit.order for unit in units] == [1, 2, 3]

        for unit, unit_seed in zip(units, seed_demo.DEMO_UNITS):
            assert unit.title == unit_seed["title"]
            selection = governed_lessons_for_unit(unit)
            assert selection.state == GOVERNED_AVAILABLE
            lessons = selection.lessons
            assert 3 <= len(lessons) <= 6
            assert [lesson.order for lesson in lessons] == [1, 2, 3]
            assert [lesson.title for lesson in lessons] == [
                lesson_seed["title"] for lesson_seed in unit_seed["lessons"]
            ]
            assert all(lesson.review_status == "approved" for lesson in lessons)
            assert all(lesson.sources for lesson in lessons)
            assert all(lesson.activities for lesson in lessons)
    finally:
        session.close()


def test_flagship_lessons_include_ordered_meaningful_existing_activities(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)

    allowed_types = {"story", "reflection", "checkpoint", "quiz"}

    session = session_factory()
    try:
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        units = sorted(course.units, key=lambda unit: (unit.order, str(unit.id)))

        for unit, unit_seed in zip(units, seed_demo.DEMO_UNITS):
            lessons = sorted(unit.lessons, key=lambda lesson: (lesson.order, str(lesson.id)))
            for lesson, lesson_seed in zip(lessons, unit_seed["lessons"]):
                activities = sorted(lesson.activities, key=lambda activity: (activity.order, str(activity.id)))
                assert [activity.order for activity in activities] == [
                    activity_seed["order"] for activity_seed in lesson_seed["activities"]
                ]
                assert [activity.title for activity in activities] == [
                    activity_seed["title"] for activity_seed in lesson_seed["activities"]
                ]
                assert all(activity.lesson_id == lesson.id for activity in activities)
                assert all(activity.type in allowed_types for activity in activities)
                assert all(activity.content for activity in activities)
                assert len(activities) >= 3
    finally:
        session.close()


def test_flagship_start_and_continue_flow_uses_existing_progress_models(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        student = session.query(User).filter(User.username == "student1").one()
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        student_course = StudentCourse(student_id=student.id, course_id=course.id)
        session.add(student_course)
        session.commit()
        session.refresh(student_course)

        first_state = progress_crud.resolve_governed_progression(session, student_course.id)
        assert first_state["delivery_state"] == GOVERNED_AVAILABLE

        first_unit = sorted(course.units, key=lambda unit: (unit.order, str(unit.id)))[0]
        first_lesson = sorted(first_unit.lessons, key=lambda lesson: (lesson.order, str(lesson.id)))[0]
        second_lesson = sorted(first_unit.lessons, key=lambda lesson: (lesson.order, str(lesson.id)))[1]

        assert first_state["lesson_id"] == first_lesson.id
        unit_progress = session.query(StudentUnitProgress).filter_by(id=first_state["unit_progress_id"]).one()
        assert unit_progress.unit_id == first_unit.id

        first_segment = session.query(SegmentProgress).filter_by(
            student_unit_id=unit_progress.id,
            lesson_id=first_lesson.id,
        ).one()
        progress_crud.update_segment_progress_status(
            session,
            first_segment.id,
            "completed",
        )

        second_state = progress_crud.resolve_governed_progression(session, student_course.id)
        assert second_state["delivery_state"] == GOVERNED_AVAILABLE
        assert second_state["lesson_id"] == second_lesson.id

        assert session.query(Program).filter(Program.title == seed_demo.DEMO_COURSE_TITLE).count() == 0
    finally:
        session.close()


def test_teacher_can_see_flagship_authoring_metadata_and_sources(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        serialized = serialize_course(course, viewer_role="teacher")

        assert serialized.units
        first_lesson = serialized.units[0].lessons[0]
        assert first_lesson.teacher_notes
        assert "Facilitation:" in first_lesson.teacher_notes
        assert first_lesson.review_status == "approved"
        assert first_lesson.is_ready_for_approval is True
        assert first_lesson.discussion_questions
        assert len(first_lesson.discussion_questions) >= 3
        assert first_lesson.sources
        assert course.skill_tags
        assert first_lesson.standards_metadata["family_extensions"]
        assert first_lesson.standards_metadata["homeschool_adaptations"]
        assert first_lesson.standards_metadata["classroom_facilitation"]
        assert first_lesson.standards_metadata["pacing_hints"]
        assert first_lesson.standards_metadata["intervention_hints"]
        assert first_lesson.standards_metadata["community_extensions"]
    finally:
        session.close()


def test_student_serialization_hides_teacher_only_guidance_but_keeps_governed_availability(
    db_engine, monkeypatch
):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        serialized = serialize_course(course, viewer_role="student")

        assert serialized.units
        first_unit = serialized.units[0]
        assert first_unit.learner_availability == GOVERNED_AVAILABLE
        first_lesson = first_unit.lessons[0]
        assert first_lesson.teacher_notes is None
        assert first_lesson.review_status is None
        assert first_lesson.is_ready_for_approval is None
        assert first_lesson.discussion_questions
        assert first_lesson.standards_metadata["family_extensions"]
    finally:
        session.close()


def test_flagship_family_and_educator_supports_are_metadata_driven(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        units = sorted(course.units, key=lambda unit: (unit.order, str(unit.id)))

        for unit in units:
            lessons = sorted(unit.lessons, key=lambda lesson: (lesson.order, str(lesson.id)))
            for lesson in lessons:
                assert lesson.teacher_notes
                assert "Facilitation:" in lesson.teacher_notes
                assert lesson.discussion_questions
                assert len(lesson.discussion_questions) >= 3
                assert lesson.standards_metadata["family_extensions"]
                assert lesson.standards_metadata["homeschool_adaptations"]
                assert lesson.standards_metadata["classroom_facilitation"]
                assert lesson.standards_metadata["pacing_hints"]
                assert lesson.standards_metadata["intervention_hints"]
                assert lesson.standards_metadata["community_extensions"]

        assert session.query(Program).filter(Program.title == seed_demo.DEMO_COURSE_TITLE).count() == 0
    finally:
        session.close()
