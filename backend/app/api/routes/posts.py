from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.models import Post
from app.schemas import PostResponse
from pydantic import BaseModel

class PostCreate(BaseModel):
    thread_id: UUID
    user_id: UUID
    content: str

class PostUpdate(PostCreate):
    pass

router = APIRouter()

@router.post('/posts', response_model=PostResponse)
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(thread_id=post.thread_id, user_id=post.user_id, content=post.content)
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
def update_post(post_id: UUID, post: PostUpdate, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter_by(id=post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail='Post not found')
    db_post.thread_id = post.thread_id
    db_post.user_id = post.user_id
    db_post.content = post.content
    db.commit()
    db.refresh(db_post)
    return db_post

@router.delete('/posts/{post_id}')
def delete_post(post_id: UUID, db: Session = Depends(get_db)):
    db_post = db.query(Post).filter_by(id=post_id).first()
    if not db_post:
        raise HTTPException(status_code=404, detail='Post not found')
    db.delete(db_post)
    db.commit()
    return {'message': 'Post deleted'}
