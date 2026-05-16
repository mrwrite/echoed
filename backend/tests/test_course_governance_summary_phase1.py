import uuid
from datetime import datetime

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import courses
from app.api.routes.analytics import _build_mastery_summary, _course_assessments_with_evidence
from app.course_governance_summary import load_course_governance_summary_course
from app.database import get_db
from app.deps import get_current_user
from app.enum import MembershipStatus, OrganizationRole, OrganizationType, ProgressStatus
from app.lesson_governance import (
    evaluate_assessment_evidence_safety,
    evaluate_assessment_lineage_coherence,
    evaluate_course_learner_progress_safety,
    evaluate_course_lineage_coherence,
    evaluate_lesson_learner_progress_safety,
    evaluate_lesson_lineage_coherence,
    evaluate_unit_learner_progress_safety,
    evaluate_unit_lineage_coherence,
)
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
    learner = User(
        id=uuid.uuid4(),
        firstname="Learner",
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
    db_session.add_all([org, admin, teacher, learner, content_admin, org_admin])
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
        title="Governance Summary Course",
        description="Phase 1 governance summary coverage",
        organization_id=org.id,
        revision_status="deprecated",
        lineage_status="deprecated",
    )
    unit = Unit(
        id=uuid.uuid4(),
        title="Unit One",
        course_id=course.id,
        order=1,
        content="Unit content",
        revision_status="deprecated",
        lineage_status="deprecated",
    )
    lesson = Lesson(
        unit_id=unit.id,
        revision_status="superseded",
        lineage_status="superseded",
        **_ready_lesson_kwargs("Lesson One"),
    )
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
        "learner": learner,
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


def _create_assessment(
    db_session,
    *,
    course: Course,
    unit: Unit,
    lesson: Lesson,
    title: str,
    revision_status: str = "deprecated",
    lineage_status: str = "superseded",
):
    assessment = Assessment(
        id=uuid.uuid4(),
        title=title,
        course_id=course.id,
        unit_id=unit.id,
        lesson_id=lesson.id,
        assessment_scope="lesson",
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


def _add_attempt(db_session, *, assessment: Assessment, question: Question, student: User, passed: bool):
    attempt = StudentAssessmentAttempt(
        assessment_id=assessment.id,
        student_id=student.id,
        score=1.0 if passed else 0.0,
        max_score=1.0,
        passed=passed,
        submitted_at=datetime.now(),
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


def _add_attempt_event(db_session, *, assessment: Assessment, attempt: StudentAssessmentAttempt, student: User):
    event = AssessmentAttemptEvent(
        assessment_id=assessment.id,
        student_id=student.id,
        attempt_id=attempt.id,
        event_type="attempt_scored",
        score=attempt.score,
        max_score=attempt.max_score,
        passed=attempt.passed,
        event_metadata={"source": "governance-summary-phase1"},
    )
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    return event


def _seed_governance_summary_course(db_session):
    seeded = _seed_users_and_course(db_session)
    _enroll_student(
        db_session,
        student=seeded["learner"],
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
    )
    assessment, question = _create_assessment(
        db_session,
        course=seeded["course"],
        unit=seeded["unit"],
        lesson=seeded["lesson"],
        title="Deprecated Assessment",
    )
    _add_alignment(db_session, assessment=assessment, question=question, objective_key="evidence")
    attempt = _add_attempt(
        db_session,
        assessment=assessment,
        question=question,
        student=seeded["learner"],
        passed=False,
    )
    _add_attempt_event(
        db_session,
        assessment=assessment,
        attempt=attempt,
        student=seeded["learner"],
    )
    seeded["assessment"] = assessment
    return seeded


def _lineage_expectations(course):
    coherence_results = [evaluate_course_lineage_coherence(course)]
    progress_results = [evaluate_course_learner_progress_safety(course)]

    for unit in course.units or []:
        coherence_results.append(evaluate_unit_lineage_coherence(unit))
        progress_results.append(evaluate_unit_learner_progress_safety(unit))
        for lesson in unit.lessons or []:
            coherence_results.append(evaluate_lesson_lineage_coherence(lesson))
            progress_results.append(evaluate_lesson_learner_progress_safety(lesson))

    assessment_results = []
    assessment_ids = set()
    for assessment in course.assessments or []:
        assessment_ids.add(assessment.id)
        coherence_results.append(evaluate_assessment_lineage_coherence(assessment))
        assessment_results.append(evaluate_assessment_evidence_safety(assessment))
    for unit in course.units or []:
        for assessment in unit.assessments or []:
            if assessment.id in assessment_ids:
                continue
            assessment_ids.add(assessment.id)
            coherence_results.append(evaluate_assessment_lineage_coherence(assessment))
            assessment_results.append(evaluate_assessment_evidence_safety(assessment))
        for lesson in unit.lessons or []:
            for assessment in lesson.assessments or []:
                if assessment.id in assessment_ids:
                    continue
                assessment_ids.add(assessment.id)
                coherence_results.append(evaluate_assessment_lineage_coherence(assessment))
                assessment_results.append(evaluate_assessment_evidence_safety(assessment))

    blocking_codes = [
        issue.code
        for result in (*coherence_results, *progress_results, *assessment_results)
        for issue in result.blocking_issues
    ]
    warning_codes = [
        issue.code
        for result in (*coherence_results, *progress_results, *assessment_results)
        for issue in result.warnings
    ]

    return {
        "is_coherent": all(result.is_coherent for result in coherence_results),
        "is_safe": all(result.is_safe for result in (*progress_results, *assessment_results)),
        "blocking_codes": sorted(blocking_codes),
        "warning_codes": sorted(warning_codes),
    }


def test_staff_admin_content_and_org_admin_can_fetch_governance_summary(db_session):
    seeded = _seed_governance_summary_course(db_session)

    for user_key in ("admin", "teacher", "content_admin", "org_admin"):
        client = _build_test_client(db_session, seeded[user_key])
        response = client.get(f"/api/courses/{seeded['course'].id}/governance-summary")
        assert response.status_code == 200
        payload = response.json()
        assert payload["course_id"] == str(seeded["course"].id)
        assert payload["course_title"] == seeded["course"].title


def test_learners_cannot_fetch_governance_summary(db_session):
    seeded = _seed_governance_summary_course(db_session)

    client = _build_test_client(db_session, seeded["learner"])
    response = client.get(f"/api/courses/{seeded['course'].id}/governance-summary")

    assert response.status_code == 403


def test_governance_summary_includes_all_required_sections_and_matches_existing_endpoints(db_session):
    seeded = _seed_governance_summary_course(db_session)
    client = _build_test_client(db_session, seeded["admin"])

    summary_response = client.get(f"/api/courses/{seeded['course'].id}/governance-summary")
    publish_response = client.get(f"/api/courses/{seeded['course'].id}/publish-readiness")
    safe_publish_response = client.get(f"/api/courses/{seeded['course'].id}/safe-publish-validation")
    competency_response = client.get(f"/api/courses/{seeded['course'].id}/competency-evidence-integrity")
    runtime_response = client.get(f"/api/courses/{seeded['course'].id}/runtime-intervention-recommendations")

    assert summary_response.status_code == 200
    assert publish_response.status_code == 200
    assert safe_publish_response.status_code == 200
    assert competency_response.status_code == 200
    assert runtime_response.status_code == 200

    summary = summary_response.json()
    assert set(summary) == {
        "course_id",
        "course_title",
        "publish_readiness",
        "safe_publish_validation",
        "lineage_safety_visibility",
        "competency_evidence_integrity",
        "runtime_intervention_recommendations",
    }
    assert summary["publish_readiness"] == publish_response.json()
    assert summary["safe_publish_validation"] == safe_publish_response.json()
    assert summary["competency_evidence_integrity"] == competency_response.json()
    assert summary["runtime_intervention_recommendations"] == runtime_response.json()


def test_lineage_safety_visibility_matches_existing_validator_behavior(db_session):
    seeded = _seed_governance_summary_course(db_session)
    client = _build_test_client(db_session, seeded["org_admin"])

    response = client.get(f"/api/courses/{seeded['course'].id}/governance-summary")
    assert response.status_code == 200

    course = load_course_governance_summary_course(db_session, seeded["course"].id)
    expected = _lineage_expectations(course)
    lineage_payload = response.json()["lineage_safety_visibility"]

    assert lineage_payload["is_coherent"] == expected["is_coherent"]
    assert lineage_payload["is_safe"] == expected["is_safe"]
    assert sorted(issue["code"] for issue in lineage_payload["blocking_issues"]) == expected["blocking_codes"]
    assert sorted(issue["code"] for issue in lineage_payload["warnings"]) == expected["warning_codes"]


def test_governance_summary_is_read_only_and_does_not_mutate_progress_or_certification_state(db_session):
    seeded = _seed_governance_summary_course(db_session)

    program = Program(id=uuid.uuid4(), title="Governance Program", description="Read-only verification")
    badge = Badge(id=uuid.uuid4(), title="Governance Badge", description="Read-only verification")
    db_session.add_all([program, badge])
    db_session.flush()
    certification = Certification(
        id=uuid.uuid4(),
        program_id=program.id,
        badge_id=badge.id,
        title="Governance Certification",
    )
    db_session.add(certification)
    db_session.flush()
    db_session.add(StudentCertification(student_id=seeded["learner"].id, certification_id=certification.id))
    db_session.commit()

    student_course = (
        db_session.query(StudentCourse)
        .filter(StudentCourse.course_id == seeded["course"].id, StudentCourse.student_id == seeded["learner"].id)
        .first()
    )
    loaded_course = load_course_governance_summary_course(db_session, seeded["course"].id)
    reporting_assessments = _course_assessments_with_evidence(db_session, loaded_course)
    mastery_before = _build_mastery_summary(
        reporting_assessments,
        seeded["learner"].id,
        course_id=seeded["course"].id,
    ).model_dump()
    snapshot_before = {
        "course_count": db_session.query(Course).count(),
        "unit_count": db_session.query(Unit).count(),
        "lesson_count": db_session.query(Lesson).count(),
        "student_course_count": db_session.query(StudentCourse).count(),
        "unit_progress_count": db_session.query(StudentUnitProgress).count(),
        "segment_count": db_session.query(SegmentProgress).count(),
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "certification_count": db_session.query(StudentCertification).count(),
        "student_course_status": student_course.status,
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

    client = _build_test_client(db_session, seeded["teacher"])
    response = client.get(f"/api/courses/{seeded['course'].id}/governance-summary")
    assert response.status_code == 200

    db_session.refresh(student_course)
    for progress in student_course.unit_progress:
        db_session.refresh(progress)
        for segment in progress.segments:
            db_session.refresh(segment)

    loaded_course = load_course_governance_summary_course(db_session, seeded["course"].id)
    reporting_assessments = _course_assessments_with_evidence(db_session, loaded_course)
    mastery_after = _build_mastery_summary(
        reporting_assessments,
        seeded["learner"].id,
        course_id=seeded["course"].id,
    ).model_dump()
    snapshot_after = {
        "course_count": db_session.query(Course).count(),
        "unit_count": db_session.query(Unit).count(),
        "lesson_count": db_session.query(Lesson).count(),
        "student_course_count": db_session.query(StudentCourse).count(),
        "unit_progress_count": db_session.query(StudentUnitProgress).count(),
        "segment_count": db_session.query(SegmentProgress).count(),
        "attempt_count": db_session.query(StudentAssessmentAttempt).count(),
        "answer_count": db_session.query(StudentAssessmentAnswer).count(),
        "event_count": db_session.query(AssessmentAttemptEvent).count(),
        "certification_count": db_session.query(StudentCertification).count(),
        "student_course_status": student_course.status,
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

    assert mastery_before == mastery_after
    assert snapshot_before == snapshot_after
