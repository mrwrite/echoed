from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Activity
from app.schemas import ActivityResponse
from pydantic import BaseModel

class ActivityCreate(BaseModel):
    lesson_id: UUID
    type: str
    title: str
    content: str
    order: int | None = None

class ActivityUpdate(ActivityCreate):
    pass

router = APIRouter()

@router.post('/activities', response_model=ActivityResponse)
def create_activity(activity: ActivityCreate, db: Session = Depends(get_db)):
    new_activity = Activity(
        lesson_id=activity.lesson_id,
        type=activity.type,
        title=activity.title,
        content=activity.content,
        order=activity.order,
    )
    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity

@router.get('/activities', response_model=list[ActivityResponse])
def list_activities(db: Session = Depends(get_db)):
    return db.query(Activity).all()

@router.get('/activities/{activity_id}', response_model=ActivityResponse)
def get_activity(activity_id: UUID, db: Session = Depends(get_db)):
    activity = db.query(Activity).filter_by(id=activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail='Activity not found')
    return activity

@router.put('/activities/{activity_id}', response_model=ActivityResponse)
def update_activity(activity_id: UUID, activity: ActivityUpdate, db: Session = Depends(get_db)):
    db_activity = db.query(Activity).filter_by(id=activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail='Activity not found')
    db_activity.lesson_id = activity.lesson_id
    db_activity.type = activity.type
    db_activity.title = activity.title
    db_activity.content = activity.content
    db_activity.order = activity.order
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.delete('/activities/{activity_id}')
def delete_activity(activity_id: UUID, db: Session = Depends(get_db)):
    db_activity = db.query(Activity).filter_by(id=activity_id).first()
    if not db_activity:
        raise HTTPException(status_code=404, detail='Activity not found')
    db.delete(db_activity)
    db.commit()
    return {'message': 'Activity deleted'}
