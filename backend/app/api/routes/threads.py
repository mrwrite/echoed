from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.deps import get_current_user
from app.models import Thread, User
from app.rate_limit import enforce_rate_limit
from app.security import require_owner_or_forum_moderator, security_event
from app.schemas import ThreadResponse
from pydantic import BaseModel, ConfigDict

class ThreadCreate(BaseModel):
    title: str
    model_config = ConfigDict(extra="forbid")

class ThreadUpdate(BaseModel):
    title: str
    model_config = ConfigDict(extra="forbid")

router = APIRouter()

@router.post('/threads', response_model=ThreadResponse)
def create_thread(
    thread: ThreadCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "forum_mutation", actor_id=current_user.id)
    new_thread = Thread(user_id=current_user.id, title=thread.title)
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
def update_thread(
    thread_id: UUID,
    thread: ThreadUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "forum_mutation", actor_id=current_user.id)
    db_thread = db.query(Thread).filter_by(id=thread_id).first()
    if not db_thread:
        raise HTTPException(status_code=404, detail='Thread not found')
    require_owner_or_forum_moderator(
        actor_id=current_user.id, actor_role=current_user.role, owner_id=db_thread.user_id
    )
    db_thread.title = thread.title
    db.commit()
    db.refresh(db_thread)
    return db_thread

@router.delete('/threads/{thread_id}')
def delete_thread(
    thread_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "forum_mutation", actor_id=current_user.id)
    db_thread = db.query(Thread).filter_by(id=thread_id).first()
    if not db_thread:
        raise HTTPException(status_code=404, detail='Thread not found')
    require_owner_or_forum_moderator(
        actor_id=current_user.id, actor_role=current_user.role, owner_id=db_thread.user_id
    )
    if current_user.id != db_thread.user_id:
        security_event(
            action="forum_thread_delete",
            result="allowed",
            actor_id=current_user.id,
            target_type="thread",
            target_id=db_thread.id,
            reason="moderator_override",
            request_id=getattr(request.state, "request_id", None),
        )
    db.delete(db_thread)
    db.commit()
    return {'message': 'Thread deleted'}
