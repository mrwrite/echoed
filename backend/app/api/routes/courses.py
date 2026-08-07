import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.deps import get_active_org_id, get_current_user, require_roles, require_org_roles
from app.enum import MembershipStatus
from app.enum import CourseVersionStatus
from app.api.routes.analytics import build_course_continuation_guidance
from app.lesson_governance import (
    evaluate_course_competency_evidence_integrity,
    evaluate_course_safe_publish,
    evaluate_course_publish_readiness,
    evaluate_lesson_readiness,
    resolve_review_fields,
    serialize_course,
)
from app.models import (
    Course,
    CourseVersion,
    Unit,
    Lesson,
    Assessment,
    Activity,
    StorybookPage,
    StudentCourse,
    StudentAssessmentAttempt,
    Source,
    OrganizationMembership,
    StudentUnitProgress,
)
from app.crud.progress import resolve_governed_progression
from app.course_governance_summary import (
    build_course_governance_summary,
    load_course_governance_summary_course,
)
from app.runtime_intervention_intelligence import evaluate_runtime_intervention_recommendation
from app.course_authoring_permissions import (
    require_course_authoring_capability,
    resolve_course_authoring_capabilities,
)
from app.course_authoring import (
    CourseAuthoringConflictError,
    CourseAuthoringValidationError,
    create_course_draft,
    build_course_duplicate_payload,
    serialize_course_draft,
    update_course_draft,
)
from app.course_exchange import echoed_json_adapter
from app.course_templates import template_catalog, template_course
from app.observability import emit_event, metrics
from app.schemas import (
    CourseGovernanceSummaryResponse,
    CourseRuntimeInterventionRecommendationResponse,
    CourseDto,
    CourseResponse,
    StudentCourseWithDetails,
    CourseCreateRequest,
    CourseVersionCreateRequest,
    CourseVersionResponse,
    CourseCompetencyEvidenceIntegrityResponse,
    CompetencyEvidenceAffectedAssessmentResponse,
    CoursePublishReadinessResponse,
    CourseSafePublishValidationResponse,
    CourseSummaryResponse,
    CourseAuthoringCapabilityEnvelope,
    CourseAuthoringCapabilitiesResponse,
    CourseAuthoringDraftRequest,
    CourseAuthoringDraftResponse,
    CourseDuplicateRequest,
    CourseReviewDecisionRequest,
    CourseLifecycleResponse,
    CourseTemplateResponse,
    CourseExchangeValidationReport,
    CourseImportRequest,
    PublishReadinessIssueResponse,
    RuntimeInterventionEvidenceBasisResponse,
)
router = APIRouter()


def _course_studio_event(operation: str, result: str, *, actor=None, course_id=None, reason: str | None = None) -> None:
    metrics.increment("echoed_course_studio_operations_total", operation=operation, result=result)
    emit_event(
        f"course.{operation}.{result}",
        component="course_studio",
        operation=operation,
        result=result,
        actor_id=getattr(actor, "id", None),
        actor_role=getattr(actor, "role", None),
        resource_type="course",
        resource_id=course_id,
        reason=reason,
    )


def _load_authoring_course(db: Session, course_id: uuid.UUID) -> Course | None:
    return (
        db.query(Course)
        .options(
            selectinload(Course.units).selectinload(Unit.lessons).selectinload(Lesson.activities),
            selectinload(Course.units).selectinload(Unit.lessons).selectinload(Lesson.sources),
            selectinload(Course.units)
            .selectinload(Unit.lessons)
            .selectinload(Lesson.activities)
            .selectinload(Activity.storybook_pages),
            selectinload(Course.assessments),
            selectinload(Course.versions),
        )
        .filter(Course.id == course_id)
        .first()
    )


def _authoring_validation_http_error(exc: CourseAuthoringValidationError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail={"code": "course_authoring_validation_failed", "issues": exc.issues},
    )


@router.get("/course-authoring/templates", response_model=list[CourseTemplateResponse])
def list_course_authoring_templates(
    active_org_id: uuid.UUID | None = Depends(get_active_org_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    capabilities = resolve_course_authoring_capabilities(db, current_user, active_organization_id=active_org_id)
    require_course_authoring_capability(capabilities, "create")
    _course_studio_event("template_list", "success", actor=current_user)
    return template_catalog()


@router.post("/course-authoring/import-validation", response_model=CourseExchangeValidationReport)
def validate_course_import(
    request: CourseImportRequest,
    active_org_id: uuid.UUID | None = Depends(get_active_org_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    capabilities = resolve_course_authoring_capabilities(db, current_user, active_organization_id=active_org_id)
    require_course_authoring_capability(capabilities, "create")
    issues = echoed_json_adapter.validate_import(request.document)
    result = "failure" if any(issue.severity == "blocking" for issue in issues) else "success"
    _course_studio_event("import_validation", result, actor=current_user, reason="blocking_issue" if result == "failure" else None)
    return {
        "format": request.document.get("format", "unknown"),
        "can_import": not any(issue.severity == "blocking" for issue in issues),
        "issues": [issue.__dict__ for issue in issues],
    }


@router.get(
    "/course-authoring/capabilities",
    response_model=CourseAuthoringCapabilityEnvelope,
)
def get_course_authoring_collection_capabilities(
    active_org_id: uuid.UUID | None = Depends(get_active_org_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    capabilities = resolve_course_authoring_capabilities(
        db,
        current_user,
        active_organization_id=active_org_id,
    )
    return CourseAuthoringCapabilityEnvelope(
        organization_id=active_org_id,
        capabilities=CourseAuthoringCapabilitiesResponse(**capabilities.model_payload()),
    )


@router.get(
    "/courses/{course_id}/authoring-capabilities",
    response_model=CourseAuthoringCapabilityEnvelope,
)
def get_course_authoring_course_capabilities(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc
    course = db.query(Course).filter(Course.id == parsed_course_id).first()
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    return CourseAuthoringCapabilityEnvelope(
        organization_id=course.organization_id,
        course_id=course.id,
        capabilities=CourseAuthoringCapabilitiesResponse(**capabilities.model_payload()),
    )


def _can_view_course_publish_readiness(db: Session, current_user, course: Course) -> bool:
    if current_user.role in {"admin", "teacher"}:
        return True

    if course.organization_id is None:
        return False

    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == course.organization_id,
            OrganizationMembership.user_id == current_user.id,
        )
        .first()
    )
    if membership is None:
        return False

    membership_role = getattr(membership.role, "value", membership.role)
    membership_status = getattr(membership.status, "value", membership.status)
    return membership_role in {"content_admin", "org_admin"} and membership_status == MembershipStatus.ACTIVE.value


def _serialize_publish_readiness_issue(issue) -> PublishReadinessIssueResponse:
    return PublishReadinessIssueResponse(
        entity_type=issue.entity_type,
        entity_id=issue.entity_id,
        entity_title=issue.entity_title,
        code=issue.code,
        message=issue.message,
    )


def _serialize_affected_assessment(context) -> CompetencyEvidenceAffectedAssessmentResponse:
    return CompetencyEvidenceAffectedAssessmentResponse(
        assessment_id=context.assessment_id,
        assessment_title=context.assessment_title,
        competency_identifiers=list(context.competency_identifiers),
    )


def _serialize_runtime_intervention_evidence_basis(basis) -> RuntimeInterventionEvidenceBasisResponse:
    return RuntimeInterventionEvidenceBasisResponse(
        source=basis.source,
        detail=basis.detail,
        assessment_id=basis.assessment_id,
        assessment_title=basis.assessment_title,
        competency_identifiers=list(basis.competency_identifiers),
    )


def _serialize_course_summary(course: Course) -> CourseSummaryResponse:
    return CourseSummaryResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        subject=course.subject,
        age_band_min=course.age_band_min,
        age_band_max=course.age_band_max,
        default_locale=course.default_locale,
        learning_objectives=course.learning_objectives,
        skill_tags=course.skill_tags or [],
        standards_metadata=course.standards_metadata or {},
        revision_number=course.revision_number,
        revision_label=course.revision_label,
        revision_status=course.revision_status,
        revision_metadata=course.revision_metadata or {},
        previous_revision_id=course.previous_revision_id,
        superseded_by_id=course.superseded_by_id,
        lineage_status=course.lineage_status,
        lineage_metadata=course.lineage_metadata or {},
        published_at=course.published_at,
        deprecated_at=course.deprecated_at,
        created_by=course.created_by,
        organization_id=course.organization_id,
    )


@router.get("/courses", response_model=list[CourseSummaryResponse])
def get_courses(
    subject: str | None = Query(default=None),
    age_min: int | None = Query(default=None),
    age_max: int | None = Query(default=None),
    locale: str | None = Query(default=None),
    org_id: str | None = Query(default=None),
    active_org_id: uuid.UUID | None = Depends(get_active_org_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Course)
    platform_role = getattr(current_user.role, "value", current_user.role)
    if platform_role not in {"admin", "super_admin", "teacher", "student"}:
        capabilities = resolve_course_authoring_capabilities(
            db,
            current_user,
            active_organization_id=active_org_id,
        )
        if not (capabilities.can_create or capabilities.can_duplicate or capabilities.can_view_draft):
            raise HTTPException(status_code=403, detail="Not authorized")
        query = query.filter(Course.organization_id == active_org_id)
    if subject:
        query = query.filter(Course.subject == subject)
    if age_min is not None:
        query = query.filter(Course.age_band_min <= age_min)
    if age_max is not None:
        query = query.filter(Course.age_band_max >= age_max)
    if locale:
        query = query.filter(Course.default_locale == locale)
    if org_id:
        if platform_role not in {"admin", "super_admin"} and (
            active_org_id is None or str(active_org_id) != org_id
        ):
            raise HTTPException(status_code=403, detail="Not authorized for the requested organization")
        query = query.filter(Course.organization_id == org_id)
    return [_serialize_course_summary(course) for course in query.all()]


@router.get("/student-courses", response_model=list[StudentCourseWithDetails])
def get_student_courses(
    db: Session = Depends(get_db), current_user=Depends(require_roles("student"))
):
    student_courses = (
        db.query(StudentCourse)
        .options(joinedload(StudentCourse.course).joinedload(Course.units))
        .filter(StudentCourse.student_id == current_user.id)
        .all()
    )

    results = []
    for sc in sorted(
        student_courses,
        key=lambda row: (
            row.enrolled_on or datetime.min,
            (row.course.title if row.course else ""),
            str(row.id),
        ),
    ):
        progression_state = resolve_governed_progression(db, sc.id)
        unit_progress_id = progression_state.get("unit_progress_id")

        results.append(
            {
                "id": sc.id,
                "student_id": sc.student_id,
                "course_id": sc.course_id,
                "enrolled_on": sc.enrolled_on,
                "status": sc.status,
                "course": serialize_course(sc.course, viewer_role=current_user.role),
                "unit_progress_id": unit_progress_id,
                "continuation_guidance": build_course_continuation_guidance(
                    db,
                    sc.course,
                    current_user.id,
                    educator_visible=False,
                ),
            }
        )

    return results


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course_by_id(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    course = db.query(Course).filter(Course.id == parsed_course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return serialize_course(course, viewer_role=current_user.role)


@router.get("/courses/{course_id}/governance-summary", response_model=CourseGovernanceSummaryResponse)
def get_course_governance_summary(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    course = load_course_governance_summary_course(db, parsed_course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if not _can_view_course_publish_readiness(db, current_user, course):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    return build_course_governance_summary(db, course)


@router.get("/courses/{course_id}/publish-readiness", response_model=CoursePublishReadinessResponse)
def get_course_publish_readiness(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    course = (
        db.query(Course)
        .options(
            joinedload(Course.units).joinedload(Unit.lessons).joinedload(Lesson.sources),
        )
        .filter(Course.id == parsed_course_id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if not _can_view_course_publish_readiness(db, current_user, course):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    readiness = evaluate_course_publish_readiness(course)
    blocking_issues = [_serialize_publish_readiness_issue(issue) for issue in readiness.blocking_issues]
    warnings = [_serialize_publish_readiness_issue(issue) for issue in readiness.warnings]

    return CoursePublishReadinessResponse(
        course_id=course.id,
        course_title=course.title,
        is_ready=readiness.is_ready,
        blocking_issue_count=len(blocking_issues),
        warning_count=len(warnings),
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


@router.get("/courses/{course_id}/safe-publish-validation", response_model=CourseSafePublishValidationResponse)
def get_course_safe_publish_validation(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    course = (
        db.query(Course)
        .options(
            joinedload(Course.student_courses),
            joinedload(Course.assessments).joinedload(Assessment.attempts),
            joinedload(Course.assessments).joinedload(Assessment.events),
            joinedload(Course.units)
            .joinedload(Unit.lessons)
            .joinedload(Lesson.sources),
            joinedload(Course.units)
            .joinedload(Unit.lessons)
            .joinedload(Lesson.assessments)
            .joinedload(Assessment.attempts),
            joinedload(Course.units)
            .joinedload(Unit.lessons)
            .joinedload(Lesson.assessments)
            .joinedload(Assessment.events),
            joinedload(Course.units)
            .joinedload(Unit.assessments)
            .joinedload(Assessment.attempts),
            joinedload(Course.units)
            .joinedload(Unit.assessments)
            .joinedload(Assessment.events),
        )
        .filter(Course.id == parsed_course_id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if not _can_view_course_publish_readiness(db, current_user, course):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    validation = evaluate_course_safe_publish(course)
    blocking_issues = [_serialize_publish_readiness_issue(issue) for issue in validation.blocking_issues]
    warnings = [_serialize_publish_readiness_issue(issue) for issue in validation.warnings]

    return CourseSafePublishValidationResponse(
        course_id=course.id,
        course_title=course.title,
        is_safe=validation.is_safe,
        blocking_issue_count=len(blocking_issues),
        warning_count=len(warnings),
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


@router.get("/courses/{course_id}/competency-evidence-integrity", response_model=CourseCompetencyEvidenceIntegrityResponse)
def get_course_competency_evidence_integrity(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    course = (
        db.query(Course)
        .options(
            joinedload(Course.assessments)
            .joinedload(Assessment.attempts)
            .joinedload(StudentAssessmentAttempt.events),
            joinedload(Course.assessments).joinedload(Assessment.competency_alignments),
            joinedload(Course.units)
            .joinedload(Unit.assessments)
            .joinedload(Assessment.attempts)
            .joinedload(StudentAssessmentAttempt.events),
            joinedload(Course.units)
            .joinedload(Unit.assessments)
            .joinedload(Assessment.competency_alignments),
            joinedload(Course.units)
            .joinedload(Unit.lessons)
            .joinedload(Lesson.assessments)
            .joinedload(Assessment.attempts)
            .joinedload(StudentAssessmentAttempt.events),
            joinedload(Course.units)
            .joinedload(Unit.lessons)
            .joinedload(Lesson.assessments)
            .joinedload(Assessment.competency_alignments),
        )
        .filter(Course.id == parsed_course_id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if not _can_view_course_publish_readiness(db, current_user, course):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    integrity = evaluate_course_competency_evidence_integrity(course)
    blocking_issues = [_serialize_publish_readiness_issue(issue) for issue in integrity.blocking_issues]
    warnings = [_serialize_publish_readiness_issue(issue) for issue in integrity.warnings]
    affected_assessments = [_serialize_affected_assessment(context) for context in integrity.affected_assessments]

    return CourseCompetencyEvidenceIntegrityResponse(
        course_id=course.id,
        course_title=course.title,
        is_valid=integrity.is_valid,
        is_explainable=integrity.is_explainable,
        blocking_issue_count=len(blocking_issues),
        warning_count=len(warnings),
        blocking_issues=blocking_issues,
        warnings=warnings,
        affected_assessments=affected_assessments,
        affected_competency_identifiers=list(integrity.affected_competency_identifiers),
    )


@router.get(
    "/courses/{course_id}/runtime-intervention-recommendations",
    response_model=list[CourseRuntimeInterventionRecommendationResponse],
)
def get_course_runtime_intervention_recommendations(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    course = (
        db.query(Course)
        .options(
            selectinload(Course.assessments)
            .selectinload(Assessment.attempts)
            .selectinload(StudentAssessmentAttempt.events),
            selectinload(Course.assessments).selectinload(Assessment.events),
            selectinload(Course.assessments).selectinload(Assessment.competency_alignments),
            selectinload(Course.units)
            .selectinload(Unit.assessments)
            .selectinload(Assessment.attempts)
            .selectinload(StudentAssessmentAttempt.events),
            selectinload(Course.units)
            .selectinload(Unit.assessments)
            .selectinload(Assessment.events),
            selectinload(Course.units)
            .selectinload(Unit.assessments)
            .selectinload(Assessment.competency_alignments),
            selectinload(Course.units)
            .selectinload(Unit.lessons)
            .selectinload(Lesson.assessments)
            .selectinload(Assessment.attempts)
            .selectinload(StudentAssessmentAttempt.events),
            selectinload(Course.units)
            .selectinload(Unit.lessons)
            .selectinload(Lesson.assessments)
            .selectinload(Assessment.events),
            selectinload(Course.units)
            .selectinload(Unit.lessons)
            .selectinload(Lesson.assessments)
            .selectinload(Assessment.competency_alignments),
            selectinload(Course.student_courses)
            .joinedload(StudentCourse.student),
            selectinload(Course.student_courses)
            .selectinload(StudentCourse.unit_progress)
            .selectinload(StudentUnitProgress.segments),
        )
        .filter(Course.id == parsed_course_id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if not _can_view_course_publish_readiness(db, current_user, course):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    recommendations: list[CourseRuntimeInterventionRecommendationResponse] = []
    for student_course in sorted(
        course.student_courses or [],
        key=lambda row: (
            row.student.firstname.lower() if row.student and row.student.firstname else "",
            row.student.lastname.lower() if row.student and row.student.lastname else "",
            row.enrolled_on or datetime.min,
            str(row.id),
        ),
    ):
        recommendation = evaluate_runtime_intervention_recommendation(db, student_course)
        recommendations.append(
            CourseRuntimeInterventionRecommendationResponse(
                student_id=student_course.student_id,
                student_name=(f"{student_course.student.firstname} {student_course.student.lastname}".strip()
                              if student_course.student is not None
                              else "Unknown learner"),
                student_course_id=student_course.id,
                course_id=course.id,
                course_title=course.title,
                recommendation_state=recommendation.recommendation_state,
                educator_attention_level=recommendation.educator_attention_level,
                summary=recommendation.summary,
                evidence_basis=[
                    _serialize_runtime_intervention_evidence_basis(basis)
                    for basis in recommendation.evidence_basis
                ],
                confidence_level=recommendation.confidence_level,
                caution_flags=list(recommendation.caution_flags),
                learner_safe_message=recommendation.learner_safe_tone,
            )
        )

    return recommendations


@router.post("/courses")
def create_course(
    course: CourseDto,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    active_org_id: uuid.UUID | None = Depends(get_active_org_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    capabilities = resolve_course_authoring_capabilities(
        db, current_user, active_organization_id=active_org_id
    )
    require_course_authoring_capability(capabilities, "create")
    payload = CourseAuthoringDraftRequest.model_validate(course.model_dump())
    try:
        create_course_draft(
            db,
            payload,
            current_user_id=current_user.id,
            organization_id=active_org_id,
            idempotency_key=idempotency_key or f"legacy-{uuid.uuid4()}",
        )
        db.commit()
        _course_studio_event("draft_create", "success", actor=current_user)
    except CourseAuthoringValidationError as exc:
        db.rollback()
        _course_studio_event("draft_create", "failure", actor=current_user, reason="validation")
        raise _authoring_validation_http_error(exc) from exc
    except Exception:
        db.rollback()
        _course_studio_event("draft_create", "failure", actor=current_user, reason="unexpected")
        raise
    return {"message": "Course draft created successfully."}


@router.post("/courses/authoring", response_model=CourseAuthoringDraftResponse)
def create_course_authoring(
    course: CourseAuthoringDraftRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    active_org_id: uuid.UUID | None = Depends(get_active_org_id),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    capabilities = resolve_course_authoring_capabilities(
        db,
        current_user,
        active_organization_id=active_org_id,
    )
    require_course_authoring_capability(capabilities, "create")
    if course.template_id and not course.units:
        template_payload = template_course(course.template_id)
        if template_payload is None:
            raise HTTPException(status_code=422, detail={"code": "unknown_course_template"})
        merged = dict(template_payload)
        merged.update(course.model_dump(exclude={"units"}, exclude_none=True))
        merged["units"] = template_payload.get("units", [])
        course = CourseAuthoringDraftRequest.model_validate(merged)
    try:
        new_course = create_course_draft(
            db,
            course,
            current_user_id=current_user.id,
            organization_id=active_org_id,
            idempotency_key=idempotency_key or f"compat-{uuid.uuid4()}",
        )
        db.commit()
        loaded = _load_authoring_course(db, new_course.id)
        _course_studio_event("draft_create", "success", actor=current_user, course_id=new_course.id)
        return serialize_course_draft(db, loaded, capabilities)
    except CourseAuthoringValidationError as exc:
        db.rollback()
        _course_studio_event("draft_create", "failure", actor=current_user, reason="validation")
        raise _authoring_validation_http_error(exc) from exc
    except Exception:
        db.rollback()
        _course_studio_event("draft_create", "failure", actor=current_user, reason="unexpected")
        raise


@router.get("/courses/{course_id}/authoring-preview", response_model=CourseResponse)
def preview_course_authoring_draft(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc
    course = _load_authoring_course(db, parsed_course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    require_course_authoring_capability(capabilities, "preview")
    try:
        response = serialize_course(course, viewer_role="student", learner_preview=True)
    except Exception:
        _course_studio_event("preview", "failure", actor=current_user, course_id=course.id, reason="unexpected")
        raise
    _course_studio_event("preview", "success", actor=current_user, course_id=course.id)
    return response


@router.get("/courses/{course_id}/export")
def export_course_authoring_document(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc
    course = _load_authoring_course(db, parsed_course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    require_course_authoring_capability(capabilities, "view_draft")
    draft = serialize_course_draft(db, course, capabilities)
    for key in ("capabilities", "organization_id", "created_by"):
        draft.pop(key, None)
    return echoed_json_adapter.export(json.loads(json.dumps(draft, default=str)))


@router.post("/courses/{course_id}/submit-review", response_model=CourseLifecycleResponse)
def submit_course_for_review(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc
    course = _load_authoring_course(db, parsed_course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    require_course_authoring_capability(capabilities, "submit_review")
    submission_issues = []
    if not course.units:
        submission_issues.append({"entity_type": "course", "entity_id": str(course.id), "entity_title": course.title, "code": "course_has_no_units", "message": "Add at least one unit before review."})
    for unit in course.units:
        if not unit.lessons:
            submission_issues.append({"entity_type": "unit", "entity_id": str(unit.id), "entity_title": unit.title, "code": "unit_has_no_lessons", "message": "Add at least one lesson before review."})
    if submission_issues:
        _course_studio_event("review_submit", "failure", actor=current_user, course_id=course.id, reason="validation")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "course_not_ready_for_review",
                "issues": submission_issues,
            },
        )
    changed_at = datetime.utcnow()
    metadata = dict(course.revision_metadata or {})
    metadata.update({"authoring_state": "submitted", "submitted_by": str(current_user.id), "submitted_at": changed_at.isoformat()})
    course.revision_metadata = metadata
    course.updated_at = changed_at
    db.commit()
    _course_studio_event("review_submit", "success", actor=current_user, course_id=course.id)
    return CourseLifecycleResponse(course_id=course.id, lifecycle_state="submitted", revision_number=course.revision_number, changed_at=changed_at)


@router.post("/courses/{course_id}/review", response_model=CourseLifecycleResponse)
def review_course_authoring_draft(
    course_id: str,
    payload: CourseReviewDecisionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc
    course = _load_authoring_course(db, parsed_course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    require_course_authoring_capability(capabilities, "review")
    if (course.revision_metadata or {}).get("authoring_state") != "submitted":
        _course_studio_event("review_transition", "failure", actor=current_user, course_id=course.id, reason="state_conflict")
        raise HTTPException(status_code=409, detail="Only a submitted course can be reviewed")
    changed_at = datetime.utcnow()
    metadata = dict(course.revision_metadata or {})
    metadata.update({"authoring_state": payload.decision, "review_feedback": payload.feedback, "reviewed_by": str(current_user.id), "reviewed_at": changed_at.isoformat()})
    course.revision_metadata = metadata
    course.updated_at = changed_at
    if payload.decision == "approved":
        for unit in course.units:
            for lesson in unit.lessons:
                lesson.review_status = "approved"
                lesson.reviewed_by = current_user.id
    db.commit()
    _course_studio_event("review_transition", "success", actor=current_user, course_id=course.id)
    return CourseLifecycleResponse(course_id=course.id, lifecycle_state=payload.decision, revision_number=course.revision_number, feedback=payload.feedback, changed_at=changed_at)


@router.get(
    "/courses/{course_id}/authoring-draft",
    response_model=CourseAuthoringDraftResponse,
)
def get_course_authoring_draft(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc
    course = _load_authoring_course(db, parsed_course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    require_course_authoring_capability(capabilities, "view_draft")
    return serialize_course_draft(db, course, capabilities)


@router.put(
    "/courses/{course_id}/authoring-draft",
    response_model=CourseAuthoringDraftResponse,
)
def save_course_authoring_draft(
    course_id: str,
    course_payload: CourseAuthoringDraftRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc
    course = _load_authoring_course(db, parsed_course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    require_course_authoring_capability(capabilities, "edit")
    try:
        update_course_draft(db, course, course_payload)
        db.commit()
        loaded = _load_authoring_course(db, course.id)
        _course_studio_event("draft_save", "success", actor=current_user, course_id=course.id)
        return serialize_course_draft(db, loaded, capabilities)
    except CourseAuthoringConflictError as exc:
        db.rollback()
        _course_studio_event("draft_save", "conflict", actor=current_user, course_id=course.id, reason="revision_conflict")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "course_authoring_revision_conflict",
                "course_id": str(exc.course_id),
                "current_revision": exc.current_revision,
                "updated_at": exc.updated_at.isoformat() if exc.updated_at else None,
            },
        ) from exc
    except CourseAuthoringValidationError as exc:
        db.rollback()
        _course_studio_event("draft_save", "failure", actor=current_user, course_id=course.id, reason="validation")
        raise _authoring_validation_http_error(exc) from exc
    except Exception:
        db.rollback()
        _course_studio_event("draft_save", "failure", actor=current_user, course_id=course.id, reason="unexpected")
        raise


@router.post(
    "/courses/{course_id}/duplicate",
    response_model=CourseAuthoringDraftResponse,
)
def duplicate_course_for_authoring(
    course_id: str,
    request: CourseDuplicateRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc
    source_course = _load_authoring_course(db, parsed_course_id)
    if source_course is None:
        raise HTTPException(status_code=404, detail="Course not found")
    source_capabilities = resolve_course_authoring_capabilities(db, current_user, course=source_course)
    require_course_authoring_capability(source_capabilities, "duplicate")
    duplicate_payload = build_course_duplicate_payload(source_course)
    if request.title and request.title.strip():
        duplicate_payload["title"] = request.title.strip()
    payload = CourseAuthoringDraftRequest.model_validate(duplicate_payload)
    try:
        duplicate = create_course_draft(
            db,
            payload,
            current_user_id=current_user.id,
            organization_id=source_course.organization_id,
            idempotency_key=idempotency_key or f"duplicate-{uuid.uuid4()}",
        )
        metadata = dict(duplicate.revision_metadata or {})
        metadata["derivative_source_course_id"] = str(source_course.id)
        duplicate.revision_metadata = metadata
        db.commit()
        loaded = _load_authoring_course(db, duplicate.id)
        capabilities = resolve_course_authoring_capabilities(db, current_user, course=loaded)
        _course_studio_event("duplicate", "success", actor=current_user, course_id=duplicate.id)
        return serialize_course_draft(db, loaded, capabilities)
    except CourseAuthoringValidationError as exc:
        db.rollback()
        _course_studio_event("duplicate", "failure", actor=current_user, reason="validation")
        raise _authoring_validation_http_error(exc) from exc
    except Exception:
        db.rollback()
        _course_studio_event("duplicate", "failure", actor=current_user, reason="unexpected")
        raise


@router.post("/courses/{course_id}/versions", response_model=CourseVersionResponse)
def create_course_version(
    course_id: str,
    payload: CourseVersionCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc
    course = db.query(Course).filter(Course.id == parsed_course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    require_course_authoring_capability(capabilities, "edit")

    latest_version = (
        db.query(CourseVersion)
        .filter(CourseVersion.course_id == course.id)
        .order_by(CourseVersion.version_number.desc())
        .first()
    )
    next_version = 1 if not latest_version else latest_version.version_number + 1
    new_version = CourseVersion(
        course_id=course.id,
        version_number=next_version,
        status=CourseVersionStatus.DRAFT,
        changelog=payload.changelog,
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    return new_version


@router.get("/courses/{course_id}/versions", response_model=list[CourseVersionResponse])
def list_course_versions(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course id") from exc
    course = db.query(Course).filter(Course.id == parsed_course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    require_course_authoring_capability(capabilities, "view_draft")
    return (
        db.query(CourseVersion)
        .filter(CourseVersion.course_id == course.id)
        .order_by(CourseVersion.version_number.desc())
        .all()
    )


@router.put("/course-versions/{version_id}", response_model=CourseVersionResponse)
def update_course_version(
    version_id: str,
    payload: CourseVersionCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_version_id = uuid.UUID(version_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course version id") from exc
    version = db.query(CourseVersion).filter(CourseVersion.id == parsed_version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Course version not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=version.course)
    require_course_authoring_capability(capabilities, "edit")
    if version.status != CourseVersionStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only drafts can be edited")

    version.changelog = payload.changelog
    db.commit()
    db.refresh(version)
    return version


@router.post("/course-versions/{version_id}/publish", response_model=CourseVersionResponse)
def publish_course_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _course_studio_event("publish", "attempt", actor=current_user)
    try:
        parsed_version_id = uuid.UUID(version_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid course version id") from exc
    version = db.query(CourseVersion).filter(CourseVersion.id == parsed_version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Course version not found")
    if version.status != CourseVersionStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Version is not a draft")

    course = _load_authoring_course(db, version.course_id)
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    require_course_authoring_capability(capabilities, "publish")
    if (course.revision_metadata or {}).get("authoring_state") != "approved":
        _course_studio_event("publish", "failure", actor=current_user, course_id=course.id, reason="approval_required")
        raise HTTPException(status_code=409, detail="Course requires independent approval before publishing")
    validation = evaluate_course_safe_publish(course)
    if validation.blocking_issues:
        _course_studio_event("publish", "failure", actor=current_user, course_id=course.id, reason="safe_publish_blocked")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "course_safe_publish_blocked",
                "issues": [_serialize_publish_readiness_issue(issue).model_dump(mode="json") for issue in validation.blocking_issues],
            },
        )

    changed_at = datetime.utcnow()
    for other_version in course.versions:
        if other_version.id != version.id and other_version.status == CourseVersionStatus.PUBLISHED:
            other_version.status = CourseVersionStatus.ARCHIVED
    version.status = CourseVersionStatus.PUBLISHED
    version.published_at = changed_at
    version.published_by = current_user.id
    course.revision_status = "current"
    course.published_at = changed_at
    snapshot = serialize_course_draft(db, course, capabilities)
    metadata = dict(course.revision_metadata or {})
    metadata.update({
        "authoring_state": "published",
        "published_version_id": str(version.id),
        "published_snapshot": json.loads(json.dumps(snapshot, default=str)),
    })
    course.revision_metadata = metadata
    for unit in course.units:
        unit.revision_status = "current"
        unit.published_at = changed_at
        for lesson in unit.lessons:
            lesson.revision_status = "current"
            lesson.published_at = changed_at
    db.commit()
    db.refresh(version)
    _course_studio_event("publish", "success", actor=current_user, course_id=course.id)
    return version


@router.put("/courses/{course_id}")
def update_course(
    course_id: str,
    course_dto: CourseDto,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        cid = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    existing_course = _load_authoring_course(db, cid)
    if not existing_course:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=existing_course)
    require_course_authoring_capability(capabilities, "edit")
    payload = CourseAuthoringDraftRequest(
        title=course_dto.title,
        description=course_dto.description,
        subject=existing_course.subject,
        age_band_min=existing_course.age_band_min,
        age_band_max=existing_course.age_band_max,
        default_locale=existing_course.default_locale,
        learning_objectives=course_dto.learning_objectives,
        skill_tags=course_dto.skill_tags,
        standards_metadata=course_dto.standards_metadata,
        revision_number=existing_course.revision_number,
        units=course_dto.model_dump()["units"],
    )
    try:
        update_course_draft(db, existing_course, payload)
        db.commit()
    except CourseAuthoringValidationError as exc:
        db.rollback()
        raise _authoring_validation_http_error(exc) from exc
    except Exception:
        db.rollback()
        raise

    return {"message": "Course updated successfully"}


@router.delete("/courses/{course_id}")
def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        cid = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")
    course = db.query(Course).filter(Course.id == cid).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    capabilities = resolve_course_authoring_capabilities(db, current_user, course=course)
    require_course_authoring_capability(capabilities, "edit")

    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}
