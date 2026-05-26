from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session, joinedload, selectinload

from app.lesson_governance import (
    evaluate_assessment_evidence_safety,
    evaluate_assessment_lineage_coherence,
    evaluate_course_competency_evidence_integrity,
    evaluate_course_learner_progress_safety,
    evaluate_course_lineage_coherence,
    evaluate_course_publish_readiness,
    evaluate_course_safe_publish,
    evaluate_lesson_learner_progress_safety,
    evaluate_lesson_lineage_coherence,
    evaluate_unit_learner_progress_safety,
    evaluate_unit_lineage_coherence,
)
from app.models import (
    Assessment,
    Course,
    Lesson,
    StudentAssessmentAttempt,
    StudentCourse,
    StudentUnitProgress,
    Unit,
)
from app.runtime_intervention_intelligence import evaluate_runtime_intervention_recommendation
from app.schemas import (
    CompetencyEvidenceAffectedAssessmentResponse,
    CourseCompetencyEvidenceIntegrityResponse,
    CourseGovernanceSummaryResponse,
    CourseLineageSafetyVisibilityResponse,
    CoursePublishReadinessResponse,
    CourseRuntimeInterventionRecommendationResponse,
    CourseSafePublishValidationResponse,
    PublishReadinessIssueResponse,
    RuntimeInterventionEvidenceBasisResponse,
)


def load_course_governance_summary_course(db: Session, course_id: UUID) -> Course | None:
    return (
        db.query(Course)
        .options(
            selectinload(Course.student_courses).joinedload(StudentCourse.student),
            selectinload(Course.student_courses)
            .selectinload(StudentCourse.unit_progress)
            .selectinload(StudentUnitProgress.segments),
            selectinload(Course.assessments)
            .selectinload(Assessment.attempts)
            .selectinload(StudentAssessmentAttempt.events),
            selectinload(Course.assessments).selectinload(Assessment.events),
            selectinload(Course.assessments).selectinload(Assessment.competency_alignments),
            selectinload(Course.units).selectinload(Unit.student_progress).selectinload(StudentUnitProgress.segments),
            selectinload(Course.units)
            .selectinload(Unit.assessments)
            .selectinload(Assessment.attempts)
            .selectinload(StudentAssessmentAttempt.events),
            selectinload(Course.units).selectinload(Unit.assessments).selectinload(Assessment.events),
            selectinload(Course.units).selectinload(Unit.assessments).selectinload(Assessment.competency_alignments),
            selectinload(Course.units).selectinload(Unit.lessons).selectinload(Lesson.sources),
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
        )
        .filter(Course.id == course_id)
        .first()
    )


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


def _collect_course_assessments(course: Course) -> list[Assessment]:
    assessments_by_id: dict[object, Assessment] = {}

    for assessment in course.assessments or []:
        assessments_by_id[assessment.id] = assessment
    for unit in course.units or []:
        for assessment in unit.assessments or []:
            assessments_by_id[assessment.id] = assessment
        for lesson in unit.lessons or []:
            for assessment in lesson.assessments or []:
                assessments_by_id[assessment.id] = assessment

    return list(assessments_by_id.values())


def _build_publish_readiness_section(course: Course) -> CoursePublishReadinessResponse:
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


def _build_safe_publish_section(course: Course) -> CourseSafePublishValidationResponse:
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


def _build_lineage_safety_section(course: Course) -> CourseLineageSafetyVisibilityResponse:
    coherence_results = [evaluate_course_lineage_coherence(course)]
    learner_progress_results = [evaluate_course_learner_progress_safety(course)]

    for unit in course.units or []:
        coherence_results.append(evaluate_unit_lineage_coherence(unit))
        learner_progress_results.append(evaluate_unit_learner_progress_safety(unit))
        for lesson in unit.lessons or []:
            coherence_results.append(evaluate_lesson_lineage_coherence(lesson))
            learner_progress_results.append(evaluate_lesson_learner_progress_safety(lesson))

    assessment_results = []
    for assessment in _collect_course_assessments(course):
        coherence_results.append(evaluate_assessment_lineage_coherence(assessment))
        assessment_results.append(evaluate_assessment_evidence_safety(assessment))

    blocking_issues = []
    warnings = []
    for result in (*coherence_results, *learner_progress_results, *assessment_results):
        blocking_issues.extend(_serialize_publish_readiness_issue(issue) for issue in result.blocking_issues)
        warnings.extend(_serialize_publish_readiness_issue(issue) for issue in result.warnings)

    return CourseLineageSafetyVisibilityResponse(
        course_id=course.id,
        course_title=course.title,
        is_coherent=all(result.is_coherent for result in coherence_results),
        is_safe=all(result.is_safe for result in (*learner_progress_results, *assessment_results)),
        blocking_issue_count=len(blocking_issues),
        warning_count=len(warnings),
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


def _build_competency_integrity_section(course: Course) -> CourseCompetencyEvidenceIntegrityResponse:
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


def _build_runtime_intervention_section(
    db: Session,
    course: Course,
) -> list[CourseRuntimeInterventionRecommendationResponse]:
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
                student_name=(
                    f"{student_course.student.firstname} {student_course.student.lastname}".strip()
                    if student_course.student is not None
                    else "Unknown learner"
                ),
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


def build_course_governance_summary(
    db: Session,
    course: Course,
) -> CourseGovernanceSummaryResponse:
    return CourseGovernanceSummaryResponse(
        course_id=course.id,
        course_title=course.title,
        publish_readiness=_build_publish_readiness_section(course),
        safe_publish_validation=_build_safe_publish_section(course),
        lineage_safety_visibility=_build_lineage_safety_section(course),
        competency_evidence_integrity=_build_competency_integrity_section(course),
        runtime_intervention_recommendations=_build_runtime_intervention_section(db, course),
    )
