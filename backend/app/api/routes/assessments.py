from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.crud.certifications import evaluate_certification
from app.database import get_db
from app.deps import get_current_user, require_roles
from app.models import (
    Assessment,
    Certification,
    Course,
    Lesson,
    Program,
    Question,
    StudentAssessmentAnswer,
    StudentAssessmentAttempt,
    StudentProgramProgress,
    User,
)
from app.schemas import (
    AssessmentAttemptCreateRequest,
    AssessmentCreateRequest,
    AssessmentResponse,
    QuestionResponse,
    StudentAssessmentAttemptResponse,
    StudentAssessmentAnswerResponse,
)

router = APIRouter()


def _serialize_assessment(assessment: Assessment) -> AssessmentResponse:
    return AssessmentResponse(
        id=assessment.id,
        title=assessment.title,
        description=assessment.description,
        lesson_id=assessment.lesson_id,
        course_id=assessment.course_id,
        program_id=assessment.program_id,
        passing_score=assessment.passing_score,
        max_attempts=assessment.max_attempts,
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
        ],
    )


@router.get("/assessments", response_model=list[AssessmentResponse])
def list_assessments(
    lesson_id: UUID | None = None,
    course_id: UUID | None = None,
    program_id: UUID | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Assessment).options(joinedload(Assessment.questions)).order_by(Assessment.created_at.desc())
    if lesson_id:
        query = query.filter(Assessment.lesson_id == lesson_id)
    if course_id:
        query = query.filter(Assessment.course_id == course_id)
    if program_id:
        query = query.filter(Assessment.program_id == program_id)
    return [_serialize_assessment(assessment) for assessment in query.all()]


@router.get("/assessments/{assessment_id}", response_model=AssessmentResponse)
def get_assessment(
    assessment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assessment = (
        db.query(Assessment)
        .options(joinedload(Assessment.questions))
        .filter(Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return _serialize_assessment(assessment)


@router.post("/assessments", response_model=AssessmentResponse, status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    if payload.lesson_id and not db.get(Lesson, payload.lesson_id):
        raise HTTPException(status_code=404, detail="Lesson not found")
    if payload.course_id and not db.get(Course, payload.course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    if payload.program_id and not db.get(Program, payload.program_id):
        raise HTTPException(status_code=404, detail="Program not found")

    assessment = Assessment(
        title=payload.title,
        description=payload.description,
        lesson_id=payload.lesson_id,
        course_id=payload.course_id,
        program_id=payload.program_id,
        passing_score=payload.passing_score,
        max_attempts=payload.max_attempts,
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

    db.commit()
    db.refresh(assessment)
    assessment = (
        db.query(Assessment)
        .options(joinedload(Assessment.questions))
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
