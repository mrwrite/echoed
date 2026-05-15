import uuid
from datetime import datetime, timedelta

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import courses
from app.api.routes.analytics import _build_mastery_summary
from app.database import get_db
from app.deps import get_current_user
from app.enum import MembershipStatus, OrganizationRole, OrganizationType, ProgressStatus
from app.models import (
    Assessment,
    AssessmentAttemptEvent,
    AssessmentCompetencyAlignment,
    Badge,
    Certification,
    Course,
    Lesson,
    Organization,
    OrganizationMembership,
    Program,
    Question,
    SegmentProgress,
    Source,
    StudentAssessmentAnswer,
    StudentAssessmentAttempt,
    StudentCertification,
    StudentCourse,
    StudentUnitProgress,
    Unit,
    User,
)


def _ready_lesson_kwargs(title: str) -> dict:
    return {
        "title": title,
        "objective": "Explain the lesson idea clearly.",
        "learning_objectives": "Students will describe a lesson idea using evidence.",
        "key_concepts": ["evidence", "understanding"],
        "teacher_notes": "Prompt students to name one supporting detail.",
        "discussion_questions": ["What helped you understand the idea?"],
        "hook": "Begin with one simple observation.",
        "content": "Explain the main idea with a short example.",
        "guided_practice": "Work through one example together.",
        "independent_practice": "Let students respond on their own.",
        "assessment": "Short oral or written check.",
        "review_status": "approved",
        "order": 1,
    }


def _build_test_client(db_session, user):
    app = FastAPI()
    app.include_router(courses.router, prefix="/api")
    app.dependency_overrides[get_current_user] = lambda: user

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


def _seed_users_and_course(db_session):
    org = Organization(id=uuid.uuid4(), name="EchoEd Org", type=OrganizationType.SCHOOL)
    admin = User(
        id=uuid.uuid4(),
        firstname="Admin",
        lastname="User",
        username=f"admin_{uuid.uuid4()}",
        email=f"admin_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="admin",
    )
    teacher = User(
        id=uuid.uuid4(),
        firstname="Teacher",
        lastname="User",
        username=f"teacher_{uuid.uuid4()}",
        email=f"teacher_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="teacher",
    )
    student = User(
        id=uuid.uuid4(),
        firstname="Student",
        lastname="User",
        username=f"student_{uuid.uuid4()}",
        email=f"student_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    content_admin = User(
        id=uuid.uuid4(),
        firstname="Content",
        lastname="Admin",
        username=f"content_{uuid.uuid4()}",
        email=f"content_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    org_admin = User(
        id=uuid.uuid4(),
        firstname="Org",
        lastname="Admin",
        username=f"org_admin_{uuid.uuid4()}",
        email=f"org_admin_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    db_session.add_all([org, admin, teacher, student, content_admin, org_admin])
    db_session.flush()
    db_session.add_all(
        [
            OrganizationMembership(
                organization_id=org.id,
                user_id=content_admin.id,
                role=OrganizationRole.CONTENT_ADMIN,
                status=MembershipStatus.ACTIVE,
            ),
            OrganizationMembership(
                organization_id=org.id,
                user_id=org_admin.id,
                role=OrganizationRole.ORG_ADMIN,
                status=MembershipStatus.ACTIVE,
            ),
        ]
    )
    course = Course(
        id=uuid.uuid4(),
        title="Runtime Intervention Endpoint Course",
        description="Phase 2 endpoint coverage",
        organization_id=org.id,
    )
    unit = Unit(id=uuid.uuid4(), title="Unit One", course_id=course.id, order=1, content="Unit content")
    lesson = Lesson(unit_id=unit.id, **_ready_lesson_kwargs("Lesson One"))
    db_session.add_all([course, unit, lesson])
    db_session.flush()
    db_session.add(Source(lesson_id=lesson.id, citation="Lesson source", url="https://example.com/source"))
    db_session.commit()
    db_session.refresh(course)
    db_session.refresh(unit)
    db_session.refresh(lesson)
    return {
        "org": org,
        "admin": admin,
        "teacher": teacher,
        "student": student,
        "content_admin": content_admin,
        "org_admin": org_admin,
        "course": course,
        "unit": unit,
        "lesson": lesson,
    }


def _enroll_student(db_session, *, student: User, course: Course, unit: Unit, lesson: Lesson, status: str = "active"):
    student_course = StudentCourse(student_id=student.id, course_id=course.id, status=status)
    db_session.add(student_course)
    db_session.flush()
    unit_progress = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=unit.id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add(unit_progress)
    db_session.flush()
    db_session.add(
        SegmentProgress(
            student_unit_id=unit_progress.id,
            lesson_id=lesson.id,
            status=ProgressStatus.IN_PROGRESS,
        )
    )
    db_session.commit()
    db_session.refresh(student_course)
    return student_course


def _create_student(db_session, *, first: str, last: str):
    student = User(
        id=uuid.uuid4(),
        firstname=first,
        lastname=last,
        username=f"{first.lower()}_{uuid.uuid4()}",
        email=f"{first.lower()}_{uuid.uuid4()}@example.com",
        hashed_password="hashed",
        role="student",
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)
    return student


def _create_assessment(
    db_session,
    *,
    course: Course,
    unit: Unit,
    lesson: Lesson,
    title: str,
    student: User,
    scope: str = "lesson",
    revision_status: str = "current",
    lineage_status: str = "standalone",
):
    assessment = Assessment(
        id=uuid.uuid4(),
        title=title,
        course_id=course.id,
        unit_id=unit.id if scope in {"unit", "lesson"} else None,
        lesson_id=lesson.id if scope == "lesson" else None,
        assessment_scope=scope,
        revision_status=revision_status,
        lineage_status=lineage_status,
    )
    question = Question(
        id=uuid.uuid4(),
        assessment_id=assessment.id,
        prompt=f"{title} prompt",
        question_type="short_answer",
        correct_answer="A cited detail",
        points=1.0,
        order=1,
    )
    db_session.add_all([assessment, question])
    db_session.commit()
    db_session.refresh(assessment)
    db_session.refresh(question)
    return assessment, question


def _add_alignment(db_session, *, assessment: Assessment, question: Question, objective_key: str):
    alignment = AssessmentCompetencyAlignment(
        assessment_id=assessment.id,
        question_id=question.id,
        objective_key=objective_key,
        objective_title=objective_key.title(),
        objective_type="competency",
        weight=1.0,
        mastery_threshold=80.0,
    )
    db_session.add(alignment)
    db_session.commit()
    db_session.refresh(alignment)
    return alignment


def _add_attempt(
    db_session,
    *,
    assessment: Assessment,
    question: Question,
    student: User,
    passed: bool,
    submitted_at: datetime,
):
    attempt = StudentAssessmentAttempt(
        assessment_id=assessment.id,
        student_id=student.id,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        passed=passed,
        submitted_at=submitted_at,
    )
    db_session.add(attempt)
    db_session.flush()
    db_session.add(
        StudentAssessmentAnswer(
            attempt_id=attempt.id,
            question_id=question.id,
            answer="A cited detail" if passed else "Wrong detail",
            is_correct=passed,
            awarded_points=1.0 if passed else 0.0,
        )
    )
    db_session.commit()
    db_session.refresh(attempt)
    return attempt


def _add_attempt_event(db_session, *, assessment: Assessment, attempt: StudentAssessmentAttempt, student: User, event_type: str = "attempt_scored"):
    event = AssessmentAttemptEvent(
        assessment_id=assessment.id,
        student_id=student.id,
        attempt_id=attempt.id,
        event_type=event_type,
        score=attempt.score,
        max_score=attempt.max_score,
        passed=attempt.passed,
        event_metadata={"source": "phase2-test"},
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def _summary_payload(summary):
    if hasattr(summary, "model_dump"):
        return summary.model_dump()
    return summary.dict()


def _single_recommendation_payload(db_session, *, user, course_id):
    client = _build_test_client(db_session, user)
    response = client.get(f"/api/courses/{course_id}/runtime-intervention-recommendations")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    return payload[0]


def test_staff_admin_content_and_org_roles_can_fetch_runtime_intervention_recommendations(db_session):
    seeded = _seed_users_and_course(db_session)
    learner = _create_student(db_session, first="Learner", last="One")
    learner_course = _enroll_student(
        db_session,
        student=learner,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
    )
    assessment, question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        title="Strong Evidence",
        student=learner,
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="evidence")
    attempt = _add_attempt(
        db_session,
        assessment=assessment,
        question=question,
        student=learner,
        passed=True,
        submitted_at=datetime.now(),
    )
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=learner)

    for user_key in ("admin", "teacher", "content_admin", "org_admin"):
        client = _build_test_client(db_session, seeded[user_key])
        response = client.get(f"/api/courses/{seeded['course'].id}/runtime-intervention-recommendations")
        assert response.status_code == 200
        payload = response.json()
        assert len(payload) == 1
        assert payload[0]["student_course_id"] == str(learner_course.id)
        assert payload[0]["course_id"] == str(seeded["course"].id)


def test_student_cannot_fetch_runtime_intervention_recommendations(db_session):
    seeded = _seed_users_and_course(db_session)
    client = _build_test_client(db_session, seeded["student"])
    response = client.get(f"/api/courses/{seeded['course'].id}/runtime-intervention-recommendations")
    assert response.status_code == 403


def test_recommendation_states_serialize_correctly(db_session):
    enrichment_seeded = _seed_users_and_course(db_session)
    enrichment_student = _create_student(db_session, first="Enrich", last="Learner")
    _enroll_student(
        db_session,
        student=enrichment_student,
        course=enrichment_seeded["course"],
        unit=enrichment_seeded["unit"],
        lesson=enrichment_seeded["lesson"],
    )
    enrichment_assessment, enrichment_question = _create_assessment(
        db_session,
        course=enrichment_seeded["course"],
        unit=enrichment_seeded["unit"],
        lesson=enrichment_seeded["lesson"],
        title="Strong Check",
        student=enrichment_student,
    )
    _add_alignment(db_session, assessment=enrichment_assessment, question=enrichment_question, objective_key="evidence")
    enrichment_attempt = _add_attempt(
        db_session,
        assessment=enrichment_assessment,
        question=enrichment_question,
        student=enrichment_student,
        passed=True,
        submitted_at=datetime.now(),
    )
    _add_attempt_event(db_session, assessment=enrichment_assessment, attempt=enrichment_attempt, student=enrichment_student)
    enrichment_payload = _single_recommendation_payload(
        db_session,
        user=enrichment_seeded["admin"],
        course_id=enrichment_seeded["course"].id,
    )
    assert enrichment_payload["recommendation_state"] == "enrichment"
    assert enrichment_payload["learner_safe_message"]
    assert enrichment_payload["course_title"] == enrichment_seeded["course"].title

    review_seeded = _seed_users_and_course(db_session)
    review_student = _create_student(db_session, first="Review", last="Learner")
    _enroll_student(
        db_session,
        student=review_student,
        course=review_seeded["course"],
        unit=review_seeded["unit"],
        lesson=review_seeded["lesson"],
    )
    review_first, review_first_q = _create_assessment(
        db_session, course=review_seeded["course"], unit=review_seeded["unit"], lesson=review_seeded["lesson"], title="Review Earlier", student=review_student
    )
    review_second, review_second_q = _create_assessment(
        db_session, course=review_seeded["course"], unit=review_seeded["unit"], lesson=review_seeded["lesson"], title="Review Latest", student=review_student, scope="unit"
    )
    _add_alignment(db_session, assessment=review_first, question=review_first_q, objective_key="evidence")
    _add_alignment(db_session, assessment=review_second, question=review_second_q, objective_key="evidence")
    review_first_attempt = _add_attempt(
        db_session, assessment=review_first, question=review_first_q, student=review_student, passed=False, submitted_at=datetime.now() - timedelta(minutes=5)
    )
    review_second_attempt = _add_attempt(
        db_session, assessment=review_second, question=review_second_q, student=review_student, passed=True, submitted_at=datetime.now()
    )
    _add_attempt_event(db_session, assessment=review_first, attempt=review_first_attempt, student=review_student)
    _add_attempt_event(db_session, assessment=review_second, attempt=review_second_attempt, student=review_student)
    review_payload = _single_recommendation_payload(
        db_session,
        user=review_seeded["admin"],
        course_id=review_seeded["course"].id,
    )
    assert review_payload["recommendation_state"] == "review"

    reteach_seeded = _seed_users_and_course(db_session)
    reteach_student = _create_student(db_session, first="Reteach", last="Learner")
    _enroll_student(
        db_session,
        student=reteach_student,
        course=reteach_seeded["course"],
        unit=reteach_seeded["unit"],
        lesson=reteach_seeded["lesson"],
    )
    reteach_assessment, reteach_question = _create_assessment(
        db_session, course=reteach_seeded["course"], unit=reteach_seeded["unit"], lesson=reteach_seeded["lesson"], title="Reteach Check", student=reteach_student
    )
    _add_alignment(db_session, assessment=reteach_assessment, question=reteach_question, objective_key="evidence")
    reteach_attempt = _add_attempt(
        db_session, assessment=reteach_assessment, question=reteach_question, student=reteach_student, passed=False, submitted_at=datetime.now()
    )
    _add_attempt_event(db_session, assessment=reteach_assessment, attempt=reteach_attempt, student=reteach_student)
    reteach_payload = _single_recommendation_payload(
        db_session,
        user=reteach_seeded["admin"],
        course_id=reteach_seeded["course"].id,
    )
    assert reteach_payload["recommendation_state"] == "reteach"

    monitor_seeded = _seed_users_and_course(db_session)
    monitor_student = _create_student(db_session, first="Monitor", last="Learner")
    _enroll_student(
        db_session,
        student=monitor_student,
        course=monitor_seeded["course"],
        unit=monitor_seeded["unit"],
        lesson=monitor_seeded["lesson"],
    )
    monitor_assessment, monitor_question = _create_assessment(
        db_session, course=monitor_seeded["course"], unit=monitor_seeded["unit"], lesson=monitor_seeded["lesson"], title="Monitor Check", student=monitor_student
    )
    monitor_attempt = _add_attempt(
        db_session, assessment=monitor_assessment, question=monitor_question, student=monitor_student, passed=True, submitted_at=datetime.now()
    )
    _add_attempt_event(db_session, assessment=monitor_assessment, attempt=monitor_attempt, student=monitor_student)
    monitor_payload = _single_recommendation_payload(
        db_session,
        user=monitor_seeded["admin"],
        course_id=monitor_seeded["course"].id,
    )
    assert monitor_payload["recommendation_state"] == "monitor"

    normal_seeded = _seed_users_and_course(db_session)
    normal_student = _create_student(db_session, first="Normal", last="Learner")
    _enroll_student(
        db_session,
        student=normal_student,
        course=normal_seeded["course"],
        unit=normal_seeded["unit"],
        lesson=normal_seeded["lesson"],
    )
    normal_payload = _single_recommendation_payload(
        db_session,
        user=normal_seeded["admin"],
        course_id=normal_seeded["course"].id,
    )
    assert normal_payload["recommendation_state"] == "normal"


def test_caution_flags_and_evidence_basis_serialize_correctly(db_session):
    seeded = _seed_users_and_course(db_session)
    learner = _create_student(db_session, first="Caution", last="Learner")
    _enroll_student(db_session, student=learner, course=seeded["course"], unit=seeded["unit"], lesson=seeded["lesson"])
    assessment, question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        title="Deprecated Check",
        student=learner,
        revision_status="deprecated",
        lineage_status="superseded",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="evidence")
    _add_attempt(
        db_session, assessment=assessment, question=question, student=learner, passed=True, submitted_at=datetime.now()
    )

    client = _build_test_client(db_session, seeded["content_admin"])
    response = client.get(f"/api/courses/{seeded['course'].id}/runtime-intervention-recommendations")

    assert response.status_code == 200
    payload = response.json()[0]
    assert payload["recommendation_state"] == "monitor"
    assert "incomplete_attempt_event_history" in payload["caution_flags"]
    assert "deprecated_evidence_revision" in payload["caution_flags"]
    assert "superseded_evidence_revision" in payload["caution_flags"]
    assert any(basis["source"] == "mastery_summary" for basis in payload["evidence_basis"])
    assert all("source" in basis and "detail" in basis for basis in payload["evidence_basis"])


def test_course_level_ambiguity_downgrades_multiple_learners_to_monitor(db_session):
    seeded = _seed_users_and_course(db_session)
    strong_learner = _create_student(db_session, first="SharedStrong", last="Learner")
    ambiguous_learner = _create_student(db_session, first="SharedAmbiguous", last="Learner")
    _enroll_student(
        db_session, student=strong_learner, course=seeded["course"], unit=seeded["unit"], lesson=seeded["lesson"]
    )
    _enroll_student(
        db_session, student=ambiguous_learner, course=seeded["course"], unit=seeded["unit"], lesson=seeded["lesson"]
    )

    strong_assessment, strong_question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        title="Strong Shared Check",
        student=strong_learner,
    )
    _add_alignment(db_session, assessment=strong_assessment, question=strong_question, objective_key="evidence")
    strong_attempt = _add_attempt(
        db_session,
        assessment=strong_assessment,
        question=strong_question,
        student=strong_learner,
        passed=True,
        submitted_at=datetime.now(),
    )
    _add_attempt_event(db_session, assessment=strong_assessment, attempt=strong_attempt, student=strong_learner)

    ambiguous_assessment, ambiguous_question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        title="Ambiguous Shared Check",
        student=ambiguous_learner,
    )
    ambiguous_attempt = _add_attempt(
        db_session,
        assessment=ambiguous_assessment,
        question=ambiguous_question,
        student=ambiguous_learner,
        passed=True,
        submitted_at=datetime.now(),
    )
    _add_attempt_event(
        db_session,
        assessment=ambiguous_assessment,
        attempt=ambiguous_attempt,
        student=ambiguous_learner,
    )

    client = _build_test_client(db_session, seeded["admin"])
    response = client.get(f"/api/courses/{seeded['course'].id}/runtime-intervention-recommendations")

    assert response.status_code == 200
    rows = {row["student_name"]: row for row in response.json()}
    assert rows["SharedStrong Learner"]["recommendation_state"] == "monitor"
    assert rows["SharedAmbiguous Learner"]["recommendation_state"] == "monitor"
    assert "ambiguous" in rows["SharedStrong Learner"]["summary"].lower()
    assert "ambiguous_competency_evidence" in rows["SharedStrong Learner"]["caution_flags"]


def test_endpoint_is_read_only_and_does_not_mutate_progress_or_certification_state(db_session):
    seeded = _seed_users_and_course(db_session)
    learner = _create_student(db_session, first="Stable", last="Learner")
    student_course = _enroll_student(
        db_session, student=learner, course=seeded["course"], unit=seeded["unit"], lesson=seeded["lesson"]
    )
    assessment, question = _create_assessment(
        db_session, course=seeded["course"], unit=seeded["unit"], lesson=seeded["lesson"], title="Read Only", student=learner
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="evidence")
    attempt = _add_attempt(
        db_session, assessment=assessment, question=question, student=learner, passed=True, submitted_at=datetime.now()
    )
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=learner)

    program = Program(id=uuid.uuid4(), title="Runtime Program", description="Read-only verification")
    badge = Badge(id=uuid.uuid4(), title="Runtime Badge", description="Read-only verification")
    db_session.add_all([program, badge])
    db_session.flush()
    certification = Certification(id=uuid.uuid4(), program_id=program.id, badge_id=badge.id, title="Runtime Certification")
    db_session.add(certification)
    db_session.flush()
    db_session.add(StudentCertification(student_id=learner.id, certification_id=certification.id))
    db_session.commit()

    mastery_before = _summary_payload(_build_mastery_summary([assessment], learner.id, course_id=seeded["course"].id))
    snapshot_before = {
        "student_course_status": student_course.status,
        "student_course_completed_at": student_course.completed_at,
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "student_certification_count": db_session.query(StudentCertification).count(),
        "unit_progress_statuses": [
            getattr(progress.status, "value", str(progress.status))
            for progress in student_course.unit_progress
        ],
        "segment_statuses": [
            getattr(segment.status, "value", str(segment.status))
            for progress in student_course.unit_progress
            for segment in progress.segments
        ],
    }

    client = _build_test_client(db_session, seeded["org_admin"])
    response = client.get(f"/api/courses/{seeded['course'].id}/runtime-intervention-recommendations")

    db_session.refresh(student_course)
    for progress in student_course.unit_progress:
        db_session.refresh(progress)
        for segment in progress.segments:
            db_session.refresh(segment)

    mastery_after = _summary_payload(_build_mastery_summary([assessment], learner.id, course_id=seeded["course"].id))
    snapshot_after = {
        "student_course_status": student_course.status,
        "student_course_completed_at": student_course.completed_at,
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "student_certification_count": db_session.query(StudentCertification).count(),
        "unit_progress_statuses": [
            getattr(progress.status, "value", str(progress.status))
            for progress in student_course.unit_progress
        ],
        "segment_statuses": [
            getattr(segment.status, "value", str(segment.status))
            for progress in student_course.unit_progress
            for segment in progress.segments
        ],
    }

    assert response.status_code == 200
    assert mastery_before == mastery_after
    assert snapshot_before == snapshot_after
