import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import courses
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


def _ready_lesson_kwargs(title: str, *, review_status: str = "approved", order: int | None = 1) -> dict:
    return {
        "title": title,
        "objective": "Explain a lesson idea with evidence.",
        "learning_objectives": "Students will explain what they learned using one cited detail.",
        "key_concepts": ["evidence", "citation"],
        "teacher_notes": "Prompt one evidence-based response.",
        "discussion_questions": ["What fact taught you something new?"],
        "hook": "Start with one vivid question.",
        "content": "Share one concise explanation and example.",
        "guided_practice": "Model a response together.",
        "independent_practice": "Ask learners to answer on their own.",
        "assessment": "Short oral or written explanation.",
        "review_status": review_status,
        "order": order,
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
        title="Course Competency Integrity Endpoint",
        description="Phase 3 endpoint coverage",
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


def _create_assessment(db_session, *, course, unit, lesson, student, title: str, scope: str = "lesson", revision_status: str = "current", lineage_status: str = "standalone"):
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


def _add_alignment(db_session, *, assessment: Assessment, question: Question, objective_key: str, objective_title: str | None = None):
    alignment = AssessmentCompetencyAlignment(
        assessment_id=assessment.id,
        question_id=question.id,
        objective_key=objective_key,
        objective_title=objective_title or objective_key.title(),
        objective_type="competency",
        weight=1.0,
        mastery_threshold=80.0,
    )
    db_session.add(alignment)
    db_session.commit()
    db_session.refresh(alignment)
    return alignment


def _add_attempt(db_session, *, assessment: Assessment, question: Question, student: User, passed: bool = True):
    attempt = StudentAssessmentAttempt(
        assessment_id=assessment.id,
        student_id=student.id,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        passed=passed,
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
        event_metadata={"source": "phase3-test"},
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def test_staff_admin_content_and_org_roles_can_fetch_course_competency_integrity(db_session):
    seeded = _seed_users_and_course(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        student=seeded["student"],
        title="Explainable Assessment",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="evidence")
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=seeded["student"])
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=seeded["student"])

    for user_key in ("admin", "teacher", "content_admin", "org_admin"):
        client = _build_test_client(db_session, seeded[user_key])
        response = client.get(f"/api/courses/{seeded['course'].id}/competency-evidence-integrity")
        assert response.status_code == 200
        payload = response.json()
        assert payload["course_id"] == str(seeded["course"].id)
        assert payload["is_valid"] is True
        assert payload["is_explainable"] is True


def test_student_cannot_fetch_course_competency_integrity(db_session):
    seeded = _seed_users_and_course(db_session)
    client = _build_test_client(db_session, seeded["student"])
    response = client.get(f"/api/courses/{seeded['course'].id}/competency-evidence-integrity")
    assert response.status_code == 403


def test_clean_explainable_course_returns_valid_and_explainable_true(db_session):
    seeded = _seed_users_and_course(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        student=seeded["student"],
        title="Aligned Lesson Assessment",
        scope="lesson",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="algebra")
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=seeded["student"])
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=seeded["student"], event_type="attempt_submitted")

    client = _build_test_client(db_session, seeded["admin"])
    response = client.get(f"/api/courses/{seeded['course'].id}/competency-evidence-integrity")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_valid"] is True
    assert payload["is_explainable"] is True
    assert payload["blocking_issue_count"] == 0
    assert payload["warning_count"] == 0
    assert payload["affected_assessments"] == []
    assert payload["affected_competency_identifiers"] == []


def test_unaligned_assessment_evidence_returns_warning_without_invented_mastery(db_session):
    seeded = _seed_users_and_course(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        student=seeded["student"],
        title="Unaligned Course Assessment",
        scope="course",
    )
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=seeded["student"])
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=seeded["student"])

    client = _build_test_client(db_session, seeded["teacher"])
    response = client.get(f"/api/courses/{seeded['course'].id}/competency-evidence-integrity")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_valid"] is True
    assert payload["is_explainable"] is False
    assert any(issue["code"] == "unaligned_assessment_mastery_evidence" for issue in payload["warnings"])
    assert payload["affected_assessments"][0]["assessment_id"] == str(assessment.id)
    assert payload["affected_assessments"][0]["competency_identifiers"] == []
    assert payload["affected_competency_identifiers"] == []


def test_missing_attempt_event_returns_structured_issue(db_session):
    seeded = _seed_users_and_course(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        student=seeded["student"],
        title="Missing Event Assessment",
        scope="unit",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="geometry")
    _add_attempt(db_session, assessment=assessment, question=question, student=seeded["student"])

    client = _build_test_client(db_session, seeded["content_admin"])
    response = client.get(f"/api/courses/{seeded['course'].id}/competency-evidence-integrity")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_valid"] is False
    assert any(issue["code"] == "missing_attempt_event_for_mastery_evidence" for issue in payload["blocking_issues"])
    assert all("entity_type" in issue and "entity_title" in issue for issue in payload["blocking_issues"])


def test_deprecated_or_superseded_assessment_evidence_returns_issue_or_warning(db_session):
    seeded = _seed_users_and_course(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        student=seeded["student"],
        title="Archived Assessment",
        scope="lesson",
        revision_status="archived",
        lineage_status="superseded",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="history")
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=seeded["student"])
    _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=seeded["student"])

    client = _build_test_client(db_session, seeded["org_admin"])
    response = client.get(f"/api/courses/{seeded['course'].id}/competency-evidence-integrity")

    assert response.status_code == 200
    payload = response.json()
    issue_codes = {issue["code"] for issue in payload["blocking_issues"]}
    assert {
        "attempts_on_non_current_assessment_revision",
        "attempt_events_on_non_current_assessment_revision",
    } & issue_codes


def test_affected_assessment_and_competency_context_is_serialized(db_session):
    seeded = _seed_users_and_course(db_session)
    aligned_assessment, aligned_question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        student=seeded["student"],
        title="Aligned Assessment",
        scope="lesson",
    )
    _add_alignment(db_session, assessment=aligned_assessment, question=aligned_question, objective_key="algebra", objective_title="Algebra")
    _add_attempt(db_session, assessment=aligned_assessment, question=aligned_question, student=seeded["student"])

    unaligned_assessment, unaligned_question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        student=seeded["student"],
        title="Unaligned Assessment",
        scope="course",
    )
    unaligned_attempt = _add_attempt(db_session, assessment=unaligned_assessment, question=unaligned_question, student=seeded["student"])
    _add_attempt_event(db_session, assessment=unaligned_assessment, attempt=unaligned_attempt, student=seeded["student"])

    client = _build_test_client(db_session, seeded["admin"])
    response = client.get(f"/api/courses/{seeded['course'].id}/competency-evidence-integrity")

    assert response.status_code == 200
    payload = response.json()
    affected_by_id = {item["assessment_id"]: item for item in payload["affected_assessments"]}
    assert affected_by_id[str(aligned_assessment.id)]["assessment_title"] == aligned_assessment.title
    assert affected_by_id[str(aligned_assessment.id)]["competency_identifiers"] == ["algebra"]
    assert affected_by_id[str(unaligned_assessment.id)]["competency_identifiers"] == []
    assert payload["affected_competency_identifiers"] == ["algebra"]


def test_endpoint_is_read_only_and_does_not_mutate_evidence_or_progress(db_session):
    seeded = _seed_users_and_course(db_session)
    assessment, question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        student=seeded["student"],
        title="Archived Endpoint Assessment",
        scope="lesson",
        revision_status="archived",
        lineage_status="superseded",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="science")
    attempt = _add_attempt(db_session, assessment=assessment, question=question, student=seeded["student"])
    event = _add_attempt_event(db_session, assessment=assessment, attempt=attempt, student=seeded["student"])

    student_course = StudentCourse(student_id=seeded["student"].id, course_id=seeded["course"].id, status="in_progress")
    db_session.add(student_course)
    db_session.commit()
    db_session.refresh(student_course)

    unit_progress = StudentUnitProgress(
        student_course_id=student_course.id,
        unit_id=seeded["unit"].id,
        status=ProgressStatus.IN_PROGRESS,
    )
    db_session.add(unit_progress)
    db_session.commit()
    db_session.refresh(unit_progress)

    segment_progress = SegmentProgress(
        student_unit_id=unit_progress.id,
        lesson_id=seeded["lesson"].id,
        status=ProgressStatus.NOT_STARTED,
    )
    program = Program(id=uuid.uuid4(), title="Endpoint Integrity Program", description="Program")
    badge = Badge(id=uuid.uuid4(), title="Endpoint Integrity Badge", description="Badge")
    certification_record = Certification(
        id=uuid.uuid4(),
        program_id=program.id,
        badge_id=badge.id,
        title="Endpoint Integrity Certification",
        description="Certification",
    )
    certification = StudentCertification(
        student_id=seeded["student"].id,
        certification_id=certification_record.id,
        score_snapshot=100.0,
    )
    db_session.add_all([program, badge, certification_record, segment_progress, certification])
    db_session.commit()
    db_session.refresh(segment_progress)
    db_session.refresh(certification)

    baseline = {
        "assessment_count": db_session.query(Assessment).count(),
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "alignment_count": db_session.query(AssessmentCompetencyAlignment).count(),
        "student_course_count": db_session.query(StudentCourse).count(),
        "unit_progress_count": db_session.query(StudentUnitProgress).count(),
        "segment_progress_count": db_session.query(SegmentProgress).count(),
        "certification_count": db_session.query(StudentCertification).count(),
        "attempt_snapshot": (attempt.id, attempt.assessment_id, attempt.score, attempt.max_score, attempt.passed),
        "event_snapshot": (event.id, event.assessment_id, event.attempt_id, event.event_type),
        "student_course_status": student_course.status,
        "unit_progress_status": unit_progress.status,
        "segment_progress_status": segment_progress.status,
        "certification_snapshot": (certification.id, certification.student_id, certification.score_snapshot),
    }

    client = _build_test_client(db_session, seeded["teacher"])
    response = client.get(f"/api/courses/{seeded['course'].id}/competency-evidence-integrity")

    db_session.refresh(assessment)
    db_session.refresh(attempt)
    db_session.refresh(event)
    db_session.refresh(student_course)
    db_session.refresh(unit_progress)
    db_session.refresh(segment_progress)
    db_session.refresh(certification)
    after = {
        "assessment_count": db_session.query(Assessment).count(),
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "alignment_count": db_session.query(AssessmentCompetencyAlignment).count(),
        "student_course_count": db_session.query(StudentCourse).count(),
        "unit_progress_count": db_session.query(StudentUnitProgress).count(),
        "segment_progress_count": db_session.query(SegmentProgress).count(),
        "certification_count": db_session.query(StudentCertification).count(),
        "attempt_snapshot": (attempt.id, attempt.assessment_id, attempt.score, attempt.max_score, attempt.passed),
        "event_snapshot": (event.id, event.assessment_id, event.attempt_id, event.event_type),
        "student_course_status": student_course.status,
        "unit_progress_status": unit_progress.status,
        "segment_progress_status": segment_progress.status,
        "certification_snapshot": (certification.id, certification.student_id, certification.score_snapshot),
    }

    assert response.status_code == 200
    assert baseline == after
