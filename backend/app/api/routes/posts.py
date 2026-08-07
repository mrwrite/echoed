from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.deps import get_current_user
from app.models import Post, Thread, User
from app.rate_limit import enforce_rate_limit
from app.security import require_owner_or_forum_moderator, security_event
from app.schemas import PostResponse
from pydantic import BaseModel, ConfigDict

class PostCreate(BaseModel):
    thread_id: UUID
    content: str
    model_config = ConfigDict(extra="forbid")

class PostUpdate(BaseModel):
    content: str
    model_config = ConfigDict(extra="forbid")

router = APIRouter()

@router.post('/posts', response_model=PostResponse)
def create_post(
    post: PostCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "forum_mutation", actor_id=current_user.id)
    if not db.query(Thread).filter_by(id=post.thread_id).first():
        raise HTTPException(status_code=404, detail='Thread not found')
    new_post = Post(thread_id=post.thread_id, user_id=current_user.id, content=post.content)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get('/posts', response_model=list[PostResponse])
def list_posts(db: Session = Depends(get_db)):
    return db.query(Post).all()

@router.get('/posts/{post_id}', response_model=PostResponse)
def get_post(post_id: UUID, db: Session = Depends(get_db)):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail='Post not found')
    return post

@router.put('/posts/{post_id}', response_model=PostResponse)
def update_post(
    post_id: UUID,
    post: PostUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "forum_mutation", actor_id=current_user.id)
    db_post = db.query(Post).filter_by(id=post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail='Post not found')
    require_owner_or_forum_moderator(
        actor_id=current_user.id, actor_role=current_user.role, owner_id=db_post.user_id
    )
    db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete('/posts/{post_id}')
def delete_post(
    post_id: UUID,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enforce_rate_limit(request, "forum_mutation", actor_id=current_user.id)
    db_post = db.query(Post).filter_by(id=post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail='Post not found')
    require_owner_or_forum_moderator(
        actor_id=current_user.id, actor_role=current_user.role, owner_id=db_post.user_id
    )
    if current_user.id != db_post.user_id:
        security_event(
            action="forum_post_delete",
            result="allowed",
            actor_id=current_user.id,
            target_type="post",
            target_id=db_post.id,
            reason="moderator_override",
            request_id=getattr(request.state, "request_id", None),
        )
    db.delete(db_post)
    db.commit()
    return {'message': 'Post deleted'}
