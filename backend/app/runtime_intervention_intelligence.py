from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from sqlalchemy.orm import Session

from app.api.routes.analytics import (
    _build_mastery_summary,
    _course_assessments_with_evidence,
    _latest_attempt_for_assessment,
    build_course_continuation_guidance,
)
from app.lesson_governance import (
    CompetencyEvidenceAffectedAssessment,
    evaluate_course_competency_evidence_integrity,
)
from app.models import StudentCourse


SAFE_ENRICHMENT_THRESHOLD = 90.0
WEAK_EVIDENCE_THRESHOLD = 50.0
VALID_RECOMMENDATION_STATES = {"normal", "monitor", "review", "reteach", "enrichment"}


@dataclass(frozen=True)
class RuntimeInterventionEvidenceBasis:
    source: str
    detail: str
    assessment_id: object | None = None
    assessment_title: str | None = None
    competency_identifiers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RuntimeInterventionRecommendation:
    recommendation_state: str
    educator_attention_level: str
    summary: str
    evidence_basis: list[RuntimeInterventionEvidenceBasis]
    confidence_level: str
    caution_flags: list[str]
    learner_safe_tone: str


def _affected_assessment_basis(
    contexts: Iterable[CompetencyEvidenceAffectedAssessment],
) -> list[RuntimeInterventionEvidenceBasis]:
    basis: list[RuntimeInterventionEvidenceBasis] = []
    for context in contexts:
        basis.append(
            RuntimeInterventionEvidenceBasis(
                source="competency_evidence_integrity",
                detail=f"Affected assessment: {context.assessment_title}",
                assessment_id=context.assessment_id,
                assessment_title=context.assessment_title,
                competency_identifiers=list(context.competency_identifiers or []),
            )
        )
    return basis


def _read_only_progress_basis(student_course: StudentCourse) -> RuntimeInterventionEvidenceBasis:
    unit_statuses = sorted(
        {
            getattr(progress.status, "value", str(progress.status))
            for progress in (student_course.unit_progress or [])
        }
    )
    segment_statuses = sorted(
        {
            getattr(segment.status, "value", str(segment.status))
            for progress in (student_course.unit_progress or [])
            for segment in (progress.segments or [])
        }
    )
    status_bits = [f"course_status={student_course.status or 'active'}"]
    if unit_statuses:
        status_bits.append(f"unit_statuses={','.join(unit_statuses)}")
    if segment_statuses:
        status_bits.append(f"segment_statuses={','.join(segment_statuses)}")
    return RuntimeInterventionEvidenceBasis(
        source="learner_progress_state",
        detail="Read-only learner progress context: " + "; ".join(status_bits),
    )


def _latest_attempt_basis(assessments, student_id) -> RuntimeInterventionEvidenceBasis | None:
    latest_assessment = None
    latest_attempt = None
    for assessment in assessments:
        attempt = _latest_attempt_for_assessment(assessment, student_id)
        if attempt is None:
            continue
        if latest_attempt is None or (attempt.submitted_at, str(attempt.id)) > (
            latest_attempt.submitted_at,
            str(latest_attempt.id),
        ):
            latest_assessment = assessment
            latest_attempt = attempt

    if latest_assessment is None or latest_attempt is None:
        return None

    percentage = (
        round((latest_attempt.score / latest_attempt.max_score) * 100, 1)
        if latest_attempt.max_score
        else 0.0
    )
    return RuntimeInterventionEvidenceBasis(
        source="latest_assessment_attempt",
        detail=(
            f"Latest attempt on {latest_assessment.title} scored {percentage:.1f}% and "
            f"{'passed' if latest_attempt.passed else 'did not pass'}."
        ),
        assessment_id=latest_assessment.id,
        assessment_title=latest_assessment.title,
        competency_identifiers=[
            alignment.objective_key
            for alignment in latest_assessment.competency_alignments or []
            if alignment.objective_key
        ],
    )


def _mastery_basis(mastery_summary) -> list[RuntimeInterventionEvidenceBasis]:
    if not mastery_summary.objectives:
        return [
            RuntimeInterventionEvidenceBasis(
                source="mastery_summary",
                detail="No competency-aligned mastery summary evidence is available yet.",
            )
        ]

    basis: list[RuntimeInterventionEvidenceBasis] = []
    for objective in mastery_summary.objectives:
        basis.append(
            RuntimeInterventionEvidenceBasis(
                source="mastery_summary",
                detail=(
                    f"{objective.objective_key} mastery is {objective.mastery_percentage:.1f}% "
                    f"against a {objective.mastery_threshold:.1f}% threshold."
                ),
                competency_identifiers=[objective.objective_key],
            )
        )
    return basis


def _guidance_basis(guidance) -> RuntimeInterventionEvidenceBasis | None:
    if guidance is None:
        return None
    return RuntimeInterventionEvidenceBasis(
        source="runtime_support_guidance",
        detail=(
            f"Existing runtime support guidance is '{guidance.support_state}' from "
            f"{guidance.evidence_source}."
        ),
    )


def _caution_flags(course_integrity, mastery_summary, assessments) -> list[str]:
    flags: list[str] = []
    warning_codes = {issue.code for issue in course_integrity.warnings}
    blocking_codes = {issue.code for issue in course_integrity.blocking_issues}
    historical_assessments = [
        assessment
        for assessment in assessments
        if (assessment.attempts or assessment.events)
    ]

    if warning_codes:
        flags.append("ambiguous_competency_evidence")
    if "missing_attempt_event_for_mastery_evidence" in blocking_codes:
        flags.append("incomplete_attempt_event_history")
    if blocking_codes & {
        "attempts_on_non_current_assessment_revision",
        "attempt_events_on_non_current_assessment_revision",
        "missing_successor_metadata_with_historical_evidence",
        "ambiguous_evidence_revision_state",
        "historical_evidence_on_deprecated_curriculum_context",
    }:
        flags.append("unsafe_historical_evidence")
    if any(
        getattr(assessment, "revision_status", "current") in {"deprecated", "archived"}
        for assessment in historical_assessments
    ):
        flags.append("deprecated_evidence_revision")
    if any(
        getattr(assessment, "lineage_status", "standalone") == "superseded"
        for assessment in historical_assessments
    ):
        flags.append("superseded_evidence_revision")
    if not mastery_summary.objectives:
        flags.append("limited_mastery_evidence")
    return flags


def evaluate_runtime_intervention_recommendation(
    db: Session,
    student_course: StudentCourse,
) -> RuntimeInterventionRecommendation:
    course = student_course.course
    assessments = _course_assessments_with_evidence(db, course)
    mastery_summary = _build_mastery_summary(
        assessments,
        student_course.student_id,
        course_id=course.id if course is not None else None,
    )
    course_integrity = evaluate_course_competency_evidence_integrity(course) if course is not None else None
    guidance = build_course_continuation_guidance(
        db,
        course,
        student_course.student_id,
        educator_visible=True,
    )

    evidence_basis: list[RuntimeInterventionEvidenceBasis] = []
    evidence_basis.append(_read_only_progress_basis(student_course))
    evidence_basis.extend(_mastery_basis(mastery_summary))
    latest_attempt_basis = _latest_attempt_basis(assessments, student_course.student_id)
    if latest_attempt_basis is not None:
        evidence_basis.append(latest_attempt_basis)
    guidance_basis = _guidance_basis(guidance)
    if guidance_basis is not None:
        evidence_basis.append(guidance_basis)
    if course_integrity is not None:
        evidence_basis.extend(_affected_assessment_basis(course_integrity.affected_assessments))

    caution_flags = (
        _caution_flags(course_integrity, mastery_summary, assessments)
        if course_integrity is not None
        else []
    )
    latest_percentage = 0.0
    latest_passed = None
    if latest_attempt_basis is not None:
        latest_assessment = next(
            (
                assessment
                for assessment in assessments
                if assessment.id == latest_attempt_basis.assessment_id
            ),
            None,
        )
        if latest_assessment is not None:
            latest_attempt = _latest_attempt_for_assessment(latest_assessment, student_course.student_id)
            if latest_attempt is not None:
                latest_percentage = (
                    (latest_attempt.score / latest_attempt.max_score) * 100
                    if latest_attempt.max_score
                    else 0.0
                )
                latest_passed = latest_attempt.passed

    mastered_objectives = mastery_summary.objectives and all(
        objective.mastered for objective in mastery_summary.objectives
    )
    lowest_mastery_percentage = min(
        (objective.mastery_percentage for objective in mastery_summary.objectives),
        default=None,
    )

    recommendation_state = "normal"
    educator_attention_level = "low"
    confidence_level = "medium"
    summary = "Current governed evidence supports normal continuation without a special intervention signal."
    learner_safe_tone = "Keep support steady and confidence-preserving while the learner continues."

    if course_integrity is not None and (
        not course_integrity.is_valid or not course_integrity.is_explainable
    ):
        recommendation_state = "monitor"
        educator_attention_level = "medium" if course_integrity.warning_count else "high"
        confidence_level = "low"
        summary = (
            "Competency evidence needs educator monitoring because some mastery evidence is ambiguous, incomplete, or historically unsafe."
        )
        learner_safe_tone = "Use a calm check-in tone and avoid overreacting to evidence that still needs verification."
    elif latest_passed is False and (
        lowest_mastery_percentage is None or lowest_mastery_percentage < WEAK_EVIDENCE_THRESHOLD
    ):
        recommendation_state = "reteach"
        educator_attention_level = "high"
        confidence_level = "high"
        summary = "Recent governed evidence is weak enough to support a targeted reteach recommendation before deeper extension."
        learner_safe_tone = "Frame reteaching as rebuilding one idea at a time, not as failure."
    elif latest_passed is False or (
        lowest_mastery_percentage is not None and lowest_mastery_percentage < SAFE_ENRICHMENT_THRESHOLD
    ):
        recommendation_state = "review"
        educator_attention_level = "medium"
        confidence_level = "medium"
        summary = "Recent governed evidence suggests a short review to reinforce understanding before continuing."
        learner_safe_tone = "Position review as a confidence-building refresh of key ideas."
    elif mastered_objectives and latest_passed and latest_percentage >= SAFE_ENRICHMENT_THRESHOLD:
        recommendation_state = "enrichment"
        educator_attention_level = "low"
        confidence_level = "high"
        summary = "Strong valid mastery evidence supports optional enrichment while preserving the governed path."
        learner_safe_tone = "Offer enrichment as an optional stretch, not as pressure to perform."
    elif guidance is not None and guidance.support_state == "normal":
        recommendation_state = "normal"
        educator_attention_level = "low"
        confidence_level = "medium" if latest_attempt_basis is not None else "low"
        summary = "Current governed evidence supports normal continuation with no immediate intervention need."
        learner_safe_tone = "Keep encouragement steady and specific as the learner continues."

    if recommendation_state not in VALID_RECOMMENDATION_STATES:
        raise ValueError(f"Unsupported intervention recommendation state: {recommendation_state}")

    return RuntimeInterventionRecommendation(
        recommendation_state=recommendation_state,
        educator_attention_level=educator_attention_level,
        summary=summary,
        evidence_basis=evidence_basis,
        confidence_level=confidence_level,
        caution_flags=caution_flags,
        learner_safe_tone=learner_safe_tone,
    )
