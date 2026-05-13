from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload, selectinload

from app.crud.certifications import evaluate_certification
from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import (
    Assessment,
    AssessmentAttemptEvent,
    AssessmentCompetencyAlignment,
    Certification,
    Course,
    Lesson,
    Program,
    Question,
    Unit,
    StudentAssessmentAnswer,
    StudentAssessmentAttempt,
    StudentProgramProgress,
    User,
)
from app.schemas import (
    AssessmentAttemptCreateRequest,
    AssessmentCreateRequest,
    AssessmentCompetencyAlignmentCreateRequest,
    AssessmentCompetencyAlignmentResponse,
    AssessmentResponse,
    QuestionResponse,
    StudentAssessmentAttemptResponse,
    StudentAssessmentAnswerResponse,
)

router = APIRouter()


def _resolve_assessment_scope(assessment: Assessment) -> str:
    if assessment.assessment_scope:
        return assessment.assessment_scope
    if assessment.unit_id:
        return "unit"
    if assessment.lesson_id:
        return "lesson"
    if assessment.course_id:
        return "course"
    if assessment.program_id:
        return "program"
    return "lesson"


def _resolve_learner_delivery_state(assessment: Assessment) -> tuple[str, str | None, bool]:
    assessment_state = assessment.assessment_state or "published"
    availability_state = assessment.availability_state or "available"

    if assessment_state == "draft":
        return "draft", "This assessment is not yet published.", False
    if assessment_state == "archived":
        return "archived", "This assessment has been archived.", False
    if availability_state == "pending_review":
        return "pending_review", "This assessment is pending review.", False
    if availability_state == "unavailable":
        return "unavailable", "This assessment is currently unavailable.", False
    return "available", None, True


def _serialize_assessment(
    assessment: Assessment,
    *,
    current_user: User | None = None,
) -> AssessmentResponse:
    learner_delivery_state, learner_delivery_detail, is_available_for_learner = _resolve_learner_delivery_state(assessment)
    is_staff = current_user is not None and current_user.role in {"admin", "teacher"}
    include_questions = is_staff or is_available_for_learner
    return AssessmentResponse(
        id=assessment.id,
        title=assessment.title,
        description=assessment.description,
        unit_id=assessment.unit_id,
        lesson_id=assessment.lesson_id,
        course_id=assessment.course_id,
        program_id=assessment.program_id,
        assessment_scope=_resolve_assessment_scope(assessment),
        assessment_state=assessment.assessment_state or "published",
        availability_state=assessment.availability_state or "available",
        passing_score=assessment.passing_score,
        max_attempts=assessment.max_attempts,
        policy_metadata=assessment.policy_metadata or {},
        lifecycle_metadata=assessment.lifecycle_metadata or {},
        revision_number=assessment.revision_number,
        revision_label=assessment.revision_label,
        revision_status=assessment.revision_status,
        revision_metadata=assessment.revision_metadata or {},
        previous_revision_id=assessment.previous_revision_id,
        superseded_by_id=assessment.superseded_by_id,
        lineage_status=assessment.lineage_status,
        lineage_metadata=assessment.lineage_metadata or {},
        published_at=assessment.published_at,
        deprecated_at=assessment.deprecated_at,
        learner_delivery_state=learner_delivery_state,
        learner_delivery_detail=learner_delivery_detail,
        is_available_for_learner=is_available_for_learner,
        competency_alignments=[
            AssessmentCompetencyAlignmentResponse(
                id=alignment.id,
                assessment_id=alignment.assessment_id,
                question_id=alignment.question_id,
                objective_key=alignment.objective_key,
                objective_title=alignment.objective_title,
                objective_type=alignment.objective_type,
                weight=alignment.weight,
                mastery_threshold=alignment.mastery_threshold,
                metadata=alignment.metadata_ or {},
                created_at=alignment.created_at,
            )
            for alignment in sorted(
                assessment.competency_alignments,
                key=lambda alignment: (
                    alignment.objective_key,
                    alignment.question_id is None,
                    alignment.created_at,
                    str(alignment.id),
                ),
            )
        ],
        created_by=assessment.created_by,
        created_at=assessment.created_at,
        questions=[
            QuestionResponse(
                id=question.id,
                prompt=question.prompt,
                question_type=question.question_type,
                choices=question.choices or [],
                explanation=question.explanation,
                points=question.points,
                order=question.order,
            )
            for question in assessment.questions
        ]
        if include_questions
        else [],
    )


@router.get("/assessments", response_model=list[AssessmentResponse])
def list_assessments(
    unit_id: UUID | None = None,
    lesson_id: UUID | None = None,
    course_id: UUID | None = None,
    program_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Assessment).options(
        joinedload(Assessment.questions),
        selectinload(Assessment.competency_alignments),
    ).order_by(Assessment.created_at.desc())
    if unit_id:
        query = query.filter(Assessment.unit_id == unit_id)
    if lesson_id:
        query = query.filter(Assessment.lesson_id == lesson_id)
    if course_id:
        query = query.filter(Assessment.course_id == course_id)
    if program_id:
        query = query.filter(Assessment.program_id == program_id)
    return [_serialize_assessment(assessment, current_user=current_user) for assessment in query.all()]


@router.get("/assessments/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assessment = (
        db.query(Assessment)
        .options(
            joinedload(Assessment.questions),
            selectinload(Assessment.competency_alignments),
        )
        .filter(Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return _serialize_assessment(assessment, current_user=current_user)


@router.post("/assessments", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    if payload.unit_id and not db.get(Unit, payload.unit_id):
        raise HTTPException(status_code=404, detail="Unit not found")
    if payload.lesson_id and not db.get(Lesson, payload.lesson_id):
        raise HTTPException(status_code=404, detail="Lesson not found")
    if payload.course_id and not db.get(Course, payload.course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    if payload.program_id and not db.get(Program, payload.program_id):
        raise HTTPException(status_code=404, detail="Program not found")
    question_orders = {question.order for question in payload.questions}
    for alignment_payload in payload.competency_alignments:
        if alignment_payload.question_order is not None and alignment_payload.question_order not in question_orders:
            raise HTTPException(
                status_code=400,
                detail=f"Question order {alignment_payload.question_order} does not exist for this assessment.",
            )

    assessment = Assessment(
        title=payload.title,
        description=payload.description,
        unit_id=payload.unit_id,
        lesson_id=payload.lesson_id,
        course_id=payload.course_id,
        program_id=payload.program_id,
        assessment_scope=payload.assessment_scope,
        assessment_state=payload.assessment_state or "published",
        availability_state=payload.availability_state or "available",
        passing_score=payload.passing_score,
        max_attempts=payload.max_attempts,
        policy_metadata=payload.policy_metadata or {},
        lifecycle_metadata=payload.lifecycle_metadata or {},
        created_by=current_user.id,
    )
    db.add(assessment)
    db.flush()

    for question in payload.questions:
        db.add(
            Question(
                assessment_id=assessment.id,
                prompt=question.prompt,
                question_type=question.question_type,
                choices=question.choices,
                correct_answer=question.correct_answer.strip(),
                explanation=question.explanation,
                points=question.points,
                order=question.order,
            )
        )

    db.flush()
    questions_by_order = {
        question.order: question.id
        for question in assessment.questions
    }
    for alignment_payload in payload.competency_alignments:
        resolved_question_id = None
        if alignment_payload.question_order is not None:
            resolved_question_id = questions_by_order.get(alignment_payload.question_order)
        db.add(
            AssessmentCompetencyAlignment(
                assessment_id=assessment.id,
                question_id=resolved_question_id,
                objective_key=alignment_payload.objective_key,
                objective_title=alignment_payload.objective_title,
                objective_type=alignment_payload.objective_type,
                weight=alignment_payload.weight,
                mastery_threshold=alignment_payload.mastery_threshold,
                metadata_=alignment_payload.metadata or {},
            )
        )

    db.commit()
    db.refresh(assessment)
    assessment = (
        db.query(Assessment)
        .options(
            joinedload(Assessment.questions),
            selectinload(Assessment.competency_alignments),
        )
        .filter(Assessment.id == assessment.id)
        .first()
    )
    return _serialize_assessment(assessment)


@router.post("/assessments/{assessment_id}/attempts", response_model=StudentAssessmentAttemptResponse)
def submit_assessment_attempt(
    assessment_id: UUID,
    payload: AssessmentAttemptCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student")),
):
    assessment = (
        db.query(Assessment)
        .options(joinedload(Assessment.questions))
        .filter(Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    learner_delivery_state, learner_delivery_detail, is_available_for_learner = _resolve_learner_delivery_state(assessment)
    if not is_available_for_learner:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Assessment is not available for learner submission.",
                "learner_delivery_state": learner_delivery_state,
                "learner_delivery_detail": learner_delivery_detail,
            },
        )

    prior_attempts = (
        db.query(StudentAssessmentAttempt)
        .filter(
            StudentAssessmentAttempt.assessment_id == assessment.id,
            StudentAssessmentAttempt.student_id == current_user.id,
        )
        .count()
    )
    if assessment.max_attempts is not None and prior_attempts >= assessment.max_attempts:
        raise HTTPException(status_code=400, detail="Maximum attempts reached")

    answers_by_question = {answer.question_id: answer.answer for answer in payload.answers}
    if len(answers_by_question) != len(assessment.questions):
        raise HTTPException(status_code=400, detail="Each assessment question requires an answer.")

    program_progress = None
    if assessment.program_id:
        program_progress = (
            db.query(StudentProgramProgress)
            .filter(
                StudentProgramProgress.program_id == assessment.program_id,
                StudentProgramProgress.student_id == current_user.id,
            )
            .first()
        )

    attempt = StudentAssessmentAttempt(
        assessment_id=assessment.id,
        student_id=current_user.id,
        program_progress_id=program_progress.id if program_progress else None,
        submitted_at=datetime.utcnow(),
    )
    db.add(attempt)
    db.flush()

    db.add(
        AssessmentAttemptEvent(
            assessment_id=assessment.id,
            student_id=current_user.id,
            attempt_id=attempt.id,
            event_type="attempt_submitted",
            event_metadata={
                "question_count": len(assessment.questions),
                "answer_count": len(payload.answers),
                "assessment_scope": _resolve_assessment_scope(assessment),
                "program_id": str(assessment.program_id) if assessment.program_id else None,
                "course_id": str(assessment.course_id) if assessment.course_id else None,
                "lesson_id": str(assessment.lesson_id) if assessment.lesson_id else None,
                "unit_id": str(assessment.unit_id) if assessment.unit_id else None,
            },
        )
    )

    max_score = 0.0
    earned_score = 0.0
    answer_rows: list[StudentAssessmentAnswerResponse] = []

    for question in assessment.questions:
        submitted_answer = answers_by_question.get(question.id)
        normalized_answer = submitted_answer.strip()
        expected_answer = question.correct_answer.strip()
        is_correct = normalized_answer.casefold() == expected_answer.casefold()
        awarded_points = question.points if is_correct else 0.0
        max_score += question.points
        earned_score += awarded_points
        db.add(
            StudentAssessmentAnswer(
                attempt_id=attempt.id,
                question_id=question.id,
                answer=normalized_answer,
                is_correct=is_correct,
                awarded_points=awarded_points,
            )
        )
        answer_rows.append(
            StudentAssessmentAnswerResponse(
                question_id=question.id,
                answer=normalized_answer,
                is_correct=is_correct,
                awarded_points=awarded_points,
            )
        )

    percentage = (earned_score / max_score) * 100 if max_score else 0.0
    attempt.score = earned_score
    attempt.max_score = max_score
    attempt.passed = percentage >= assessment.passing_score
    db.add(
        AssessmentAttemptEvent(
            assessment_id=assessment.id,
            student_id=current_user.id,
            attempt_id=attempt.id,
            event_type="attempt_scored",
            score=earned_score,
            max_score=max_score,
            passed=attempt.passed,
            event_metadata={
                "percentage": percentage,
                "passing_score": assessment.passing_score,
                "score_snapshot": {
                    "score": earned_score,
                    "max_score": max_score,
                    "passed": attempt.passed,
                },
                "answer_snapshot": [
                    {
                        "question_id": str(answer.question_id),
                        "answer": answer.answer,
                        "is_correct": answer.is_correct,
                        "awarded_points": answer.awarded_points,
                    }
                    for answer in answer_rows
                ],
            },
        )
    )
    db.commit()
    db.refresh(attempt)

    if assessment.program_id:
        certifications = db.query(Certification).filter(Certification.program_id == assessment.program_id).all()
        for certification in certifications:
            evaluate_certification(db, certification, current_user.id)

    return StudentAssessmentAttemptResponse(
        id=attempt.id,
        assessment_id=attempt.assessment_id,
        student_id=attempt.student_id,
        program_progress_id=attempt.program_progress_id,
        score=attempt.score,
        max_score=attempt.max_score,
        percentage=percentage,
        passed=attempt.passed,
        submitted_at=attempt.submitted_at,
        answers=answer_rows,
    )
