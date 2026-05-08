from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.deps import require_roles
from app.lesson_governance import (
    evaluate_lesson_readiness,
    governed_lesson_for_student,
    raise_governed_unavailable,
    resolve_review_fields,
    serialize_lesson,
)
from app.models import Lesson, Source
from app.schemas import LessonResponse
from pydantic import BaseModel, Field
from typing import Optional


class SourceCreate(BaseModel):
    citation: str
    url: Optional[str] = None


class LessonCreate(BaseModel):
    unit_id: UUID
    title: str
    objective: str | None = None
    learning_objectives: str | None = None
    key_concepts: list[str] = Field(default_factory=list)
    teacher_notes: str | None = None
    discussion_questions: list[str] = Field(default_factory=list)
    hook: str | None = None
    content: str | None = None
    guided_practice: str | None = None
    independent_practice: str | None = None
    assessment: str | None = None
    review_status: str = "draft"
    reviewed_by: UUID | None = None
    skill_tags: list[str] = Field(default_factory=list)
    standards_metadata: dict = Field(default_factory=dict)
    order: int | None = None
    duration_minutes: int | None = None
    sources: list[SourceCreate] = Field(default_factory=list)

class LessonUpdate(LessonCreate):
    pass

router = APIRouter()


def _replace_sources(db_lesson: Lesson, sources: list[SourceCreate]) -> None:
    db_lesson.sources.clear()
    for source in sources:
        db_lesson.sources.append(Source(citation=source.citation, url=source.url))


def _lesson_readiness_for_payload(lesson: LessonCreate) -> object:
    return evaluate_lesson_readiness(
        title=lesson.title,
        objective=lesson.objective,
        learning_objectives=lesson.learning_objectives,
        key_concepts=lesson.key_concepts,
        hook=lesson.hook,
        content=lesson.content,
        guided_practice=lesson.guided_practice,
        independent_practice=lesson.independent_practice,
        assessment=lesson.assessment,
        sources=lesson.sources,
    )

@router.post('/lessons', response_model=LessonResponse)
def create_lesson(
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    readiness = _lesson_readiness_for_payload(lesson)
    review_status, reviewed_by = resolve_review_fields(
        db=db,
        current_user=current_user,
        requested_status=lesson.review_status,
        unit_id=lesson.unit_id,
        readiness=readiness,
    )
    new_lesson = Lesson(
        unit_id=lesson.unit_id,
        title=lesson.title,
        objective=lesson.objective,
        learning_objectives=lesson.learning_objectives,
        key_concepts=lesson.key_concepts,
        teacher_notes=lesson.teacher_notes,
        discussion_questions=lesson.discussion_questions,
        hook=lesson.hook,
        content=lesson.content,
        guided_practice=lesson.guided_practice,
        independent_practice=lesson.independent_practice,
        assessment=lesson.assessment,
        review_status=review_status,
        reviewed_by=reviewed_by,
        skill_tags=lesson.skill_tags,
        standards_metadata=lesson.standards_metadata,
        order=lesson.order,
        duration_minutes=lesson.duration_minutes,
    )
    _replace_sources(new_lesson, lesson.sources)
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return serialize_lesson(new_lesson, viewer_role=current_user.role)

@router.get('/lessons', response_model=list[LessonResponse])
def list_lessons(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    return [
        serialize_lesson(lesson, viewer_role=current_user.role)
        for lesson in db.query(Lesson).all()
    ]

@router.get('/lessons/{lesson_id}', response_model=LessonResponse)
def get_lesson(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    lesson = db.query(Lesson).filter_by(id=lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail='Lesson not found')
    if current_user.role == "student":
        selection = governed_lesson_for_student(lesson)
        if selection.lesson is None:
            raise_governed_unavailable(selection, lesson_id=lesson_id)
        lesson = selection.lesson
    return serialize_lesson(lesson, viewer_role=current_user.role)

@router.put('/lessons/{lesson_id}', response_model=LessonResponse)
def update_lesson(
    lesson_id: UUID,
    lesson: LessonUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    db_lesson = db.query(Lesson).filter_by(id=lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail='Lesson not found')
    readiness = _lesson_readiness_for_payload(lesson)
    review_status, reviewed_by = resolve_review_fields(
        db=db,
        current_user=current_user,
        requested_status=lesson.review_status,
        unit_id=lesson.unit_id,
        lesson=db_lesson,
        readiness=readiness,
    )
    db_lesson.unit_id = lesson.unit_id
    db_lesson.title = lesson.title
    db_lesson.objective = lesson.objective
    db_lesson.learning_objectives = lesson.learning_objectives
    db_lesson.key_concepts = lesson.key_concepts
    db_lesson.teacher_notes = lesson.teacher_notes
    db_lesson.discussion_questions = lesson.discussion_questions
    db_lesson.hook = lesson.hook
    db_lesson.content = lesson.content
    db_lesson.guided_practice = lesson.guided_practice
    db_lesson.independent_practice = lesson.independent_practice
    db_lesson.assessment = lesson.assessment
    db_lesson.review_status = review_status
    db_lesson.reviewed_by = reviewed_by
    db_lesson.skill_tags = lesson.skill_tags
    db_lesson.standards_metadata = lesson.standards_metadata
    db_lesson.order = lesson.order
    db_lesson.duration_minutes = lesson.duration_minutes
    _replace_sources(db_lesson, lesson.sources)
    db.commit()
    db.refresh(db_lesson)
    return serialize_lesson(db_lesson, viewer_role=current_user.role)

@router.delete('/lessons/{lesson_id}')
def delete_lesson(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    db_lesson = db.query(Lesson).filter_by(id=lesson_id).first()
    if not db_lesson:
        raise HTTPException(status_code=404, detail='Lesson not found')
    db.delete(db_lesson)
    db.commit()
    return {'message': 'Lesson deleted'}
