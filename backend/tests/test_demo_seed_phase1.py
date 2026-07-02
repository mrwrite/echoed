from collections import Counter

from sqlalchemy.orm import sessionmaker

from app import seed_demo
from app.enum import ProgressStatus
from app.models import (
    Assessment,
    AssessmentAttemptEvent,
    Course,
    Enrollment,
    Organization,
    Section,
    StudentAssessmentAttempt,
    StudentCourse,
    StudentUnitProgress,
    User,
)
from app.runtime_intervention_intelligence import evaluate_runtime_intervention_recommendation


def _build_session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def _seed_with_factory(monkeypatch, session_factory):
    monkeypatch.setattr(seed_demo, "SessionLocal", session_factory)
    seed_demo.run()


def _student_course_by_username(session, username: str) -> StudentCourse:
    return (
        session.query(StudentCourse)
        .join(User, User.id == StudentCourse.student_id)
        .join(Course, Course.id == StudentCourse.course_id)
        .filter(
            User.username == username,
            Course.title == seed_demo.DEMO_COURSE_TITLE,
        )
        .one()
    )


def _status_values(student_course: StudentCourse) -> dict[str, object]:
    unit_statuses = [
        getattr(progress.status, "value", str(progress.status))
        for progress in student_course.unit_progress
    ]
    segment_statuses = [
        getattr(segment.status, "value", str(segment.status))
        for progress in student_course.unit_progress
        for segment in progress.segments
    ]
    return {
        "course_status": student_course.status,
        "unit_statuses": unit_statuses,
        "segment_status_counts": dict(Counter(segment_statuses)),
    }


def test_demo_seed_creates_canonical_org_users_and_flagship_relationships(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        assert session.query(Organization).filter(Organization.name == seed_demo.DEMO_ORG_NAME).count() == 1
        assert session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).count() == 1
        assert session.query(Section).filter(Section.name == seed_demo.DEMO_SECTION_NAME).count() == 1
        assert session.query(Enrollment).count() == len(seed_demo.DEMO_SECTION_LEARNER_KEYS)

        seeded_usernames = {profile["username"] for profile in seed_demo.DEMO_USERS.values()}
        actual_usernames = {row[0] for row in session.query(User.username).all()}
        assert seeded_usernames.issubset(actual_usernames)

        archetype_usernames = {
            seed_demo.DEMO_USERS[key]["username"]
            for key in seed_demo.DEMO_ARCHETYPE_LEARNER_KEYS
        }
        student_course_usernames = {
            row[0]
            for row in (
                session.query(User.username)
                .join(StudentCourse, StudentCourse.student_id == User.id)
                .join(Course, Course.id == StudentCourse.course_id)
                .filter(Course.title == seed_demo.DEMO_COURSE_TITLE)
                .all()
            )
        }
        assert student_course_usernames == archetype_usernames

        seeded_assessment_titles = {seed["title"] for seed in seed_demo.DEMO_FLAGSHIP_ASSESSMENTS}
        actual_assessment_titles = {row[0] for row in session.query(Assessment.title).all()}
        assert seeded_assessment_titles.issubset(actual_assessment_titles)

        intro_course = session.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).one()
        regions_lesson = next(
            lesson
            for unit in intro_course.units
            for lesson in unit.lessons
            if lesson.title == "Regions, Rivers, and Routes"
        )
        regions_lesson_activities = sorted(regions_lesson.activities, key=lambda activity: activity.order or 0)
        assert [activity.type for activity in regions_lesson_activities[:2]] == ["storybook", "coloring"]

        intro_lesson = next(
            lesson
            for unit in intro_course.units
            for lesson in unit.lessons
            if lesson.title == "Introduction to Africa"
        )
        intro_lesson_activities = sorted(intro_lesson.activities, key=lambda activity: activity.order or 0)
        assert [activity.type for activity in intro_lesson_activities[:4]] == [
            "image",
            "interactive_map",
            "storybook",
            "coloring",
        ]
        storybook_activity = next(activity for activity in intro_lesson_activities if activity.type == "storybook")
        assert [page.order for page in sorted(storybook_activity.storybook_pages, key=lambda page: page.order or 0)] == [1, 2, 3, 4]
        assert [
            page.image_url.rsplit("/", 1)[-1]
            for page in sorted(storybook_activity.storybook_pages, key=lambda page: page.order or 0)
        ] == [
            "08ef622b-2b8a-41f0-8e43-74f4ee11d216.png",
            "1ca7b568-f7eb-4877-bd9e-22919ec90a36.png",
            "268b14ab-3b76-4153-84ac-5238658d1f72.png",
            "1d7d06af-ad31-4ac4-ba83-82a720079317.png",
        ]
    finally:
        session.close()


def test_demo_seed_progression_states_and_runtime_states_are_deterministic(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        total_lessons = sum(len(unit_seed["lessons"]) for unit_seed in seed_demo.DEMO_UNITS)
        expectation_map = {
            "masteredstudent": {
                "state": "enrichment",
                "course_status": "completed",
                "segment_status_counts": {"completed": total_lessons},
            },
            "reteachstudent": {
                "state": "reteach",
                "course_status": "active",
                "segment_status_counts": {"completed": 1, "in_progress": 1, "not_started": 1},
            },
            "reviewstudent": {
                "state": "review",
                "course_status": "active",
                "segment_status_counts": {"completed": 1, "in_progress": 1, "not_started": 1},
            },
            "monitorstudent": {
                "state": "monitor",
                "course_status": "active",
                "segment_status_counts": {"completed": 1, "in_progress": 1, "not_started": 1},
            },
            "normalstudent": {
                "state": "normal",
                "course_status": "active",
                "segment_status_counts": {"in_progress": 1, "not_started": 2},
            },
        }

        for username, expectation in expectation_map.items():
            student_course = _student_course_by_username(session, username)
            recommendation = evaluate_runtime_intervention_recommendation(session, student_course)
            status_values = _status_values(student_course)

            assert recommendation.recommendation_state == expectation["state"]
            assert status_values["course_status"] == expectation["course_status"]
            assert status_values["segment_status_counts"] == expectation["segment_status_counts"]
    finally:
        session.close()


def test_demo_seed_reseed_restores_expected_learning_state(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        review_course = _student_course_by_username(session, "reviewstudent")
        review_attempts = (
            session.query(StudentAssessmentAttempt)
            .filter(StudentAssessmentAttempt.student_id == review_course.student_id)
            .all()
        )
        for attempt in review_attempts:
            for event in list(attempt.events or []):
                session.delete(event)
            session.delete(attempt)

        mastered_course = _student_course_by_username(session, "masteredstudent")
        mastered_course.status = "active"
        mastered_course.completed_at = None

        first_unit_progress = (
            session.query(StudentUnitProgress)
            .filter(StudentUnitProgress.student_course_id == mastered_course.id)
            .order_by(StudentUnitProgress.id)
            .first()
        )
        assert first_unit_progress is not None
        first_unit_progress.status = ProgressStatus.IN_PROGRESS
        session.commit()
    finally:
        session.close()

    _seed_with_factory(monkeypatch, session_factory)

    session = session_factory()
    try:
        review_course = _student_course_by_username(session, "reviewstudent")
        review_recommendation = evaluate_runtime_intervention_recommendation(session, review_course)
        assert review_recommendation.recommendation_state == "review"

        mastered_course = _student_course_by_username(session, "masteredstudent")
        mastered_recommendation = evaluate_runtime_intervention_recommendation(session, mastered_course)
        assert mastered_course.status == "completed"
        assert mastered_course.completed_at is not None
        assert mastered_recommendation.recommendation_state == "enrichment"

        assert session.query(StudentCourse).count() == len(seed_demo.DEMO_ARCHETYPE_LEARNER_KEYS)
        assert session.query(AssessmentAttemptEvent).count() == 10
        assert session.query(StudentAssessmentAttempt).count() == 5
    finally:
        session.close()
