from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Thread
from app.schemas import ThreadResponse
from pydantic import BaseModel

class ThreadCreate(BaseModel):
    user_id: UUID
    title: str

class ThreadUpdate(ThreadCreate):
    pass

router = APIRouter()

@router.post('/threads', response_model=ThreadResponse)
def create_thread(thread: ThreadCreate, db: Session = Depends(get_db)):
    new_thread = Thread(user_id=thread.user_id, title=thread.title)
    db.add(new_thread)
    db.commit()
    db.refresh(new_thread)
    return new_thread

@router.get('/threads', response_model=list[ThreadResponse])
def list_threads(db: Session = Depends(get_db)):
    return db.query(Thread).all()

@router.get('/threads/{thread_id}', response_model=ThreadResponse)
def get_thread(thread_id: UUID, db: Session = Depends(get_db)):
    thread = db.query(Thread).filter_by(id=thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail='Thread not found')
    return thread

@router.put('/threads/{thread_id}', response_model=ThreadResponse)
def update_thread(thread_id: UUID, thread: ThreadUpdate, db: Session = Depends(get_db)):
    db_thread = db.query(Thread).filter_by(id=thread_id).first()
    if not db_thread:
        raise HTTPException(status_code=404, detail='Thread not found')
    db_thread.user_id = thread.user_id
    db_thread.title = thread.title
    db.commit()
    db.refresh(db_thread)
    return db_thread

@router.delete('/threads/{thread_id}')
def delete_thread(thread_id: UUID, db: Session = Depends(get_db)):
    db_thread = db.query(Thread).filter_by(id=thread_id).first()
    if not db_thread:
        raise HTTPException(status_code=404, detail='Thread not found')
    db.delete(db_thread)
    db.commit()
    return {'message': 'Thread deleted'}
