from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.deps import require_roles
from app.models import Lesson
from app.schemas import LessonResponse
from pydantic import BaseModel

class LessonCreate(BaseModel):
    unit_id: UUID
    title: str
    objective: str | None = None
    order: int | None = None
    duration_minutes: int | None = None

class LessonUpdate(LessonCreate):
    pass

router = APIRouter()

@router.post('/lessons', response_model=LessonResponse)
def create_lesson(
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    new_lesson = Lesson(
        unit_id=lesson.unit_id,
        title=lesson.title,
        objective=lesson.objective,
        order=lesson.order,
        duration_minutes=lesson.duration_minutes,
    )
    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson

@router.get('/lessons', response_model=list[LessonResponse])
def list_lessons(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    return db.query(Lesson).all()

@router.get('/lessons/{lesson_id}', response_model=LessonResponse)
def get_lesson(
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    lesson = db.query(Lesson).filter_by(id=lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail='Lesson not found')
    return lesson

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
    db_lesson.unit_id = lesson.unit_id
    db_lesson.title = lesson.title
    db_lesson.objective = lesson.objective
    db_lesson.order = lesson.order
    db_lesson.duration_minutes = lesson.duration_minutes
    db.commit()
    db.refresh(db_lesson)
    return db_lesson

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
