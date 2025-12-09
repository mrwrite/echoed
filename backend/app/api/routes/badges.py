from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from uuid import UUID
from app.database import get_db
from app.models import Badge, StudentBadge, User
from app.schemas import BadgeCreate, BadgeResponse, StudentBadgeResponse
from app.auth import get_current_user

router = APIRouter()

@router.get('/badges', response_model=list[BadgeResponse])
def list_badges(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Badge).all()

@router.post('/badges', response_model=BadgeResponse)
def create_badge(badge: BadgeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Admin access required')
    new_badge = Badge(title=badge.title, description=badge.description, image_url=badge.image_url)
    db.add(new_badge)
    db.commit()
    db.refresh(new_badge)
    return new_badge

@router.get('/students/{student_id}/badges', response_model=list[StudentBadgeResponse])
def get_student_badges(student_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin' and current_user.id != student_id:
        raise HTTPException(status_code=403, detail='Not authorized')
    badges = db.query(StudentBadge).options(joinedload(StudentBadge.badge)).filter_by(student_id=student_id).all()
    return badges

@router.post('/students/{student_id}/badges/{badge_id}', response_model=StudentBadgeResponse)
def assign_badge(student_id: UUID, badge_id: UUID, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail='Admin access required')
    if not db.query(User).filter_by(id=student_id).first():
        raise HTTPException(status_code=404, detail='Student not found')
    if not db.query(Badge).filter_by(id=badge_id).first():
        raise HTTPException(status_code=404, detail='Badge not found')
    existing = db.query(StudentBadge).filter_by(student_id=student_id, badge_id=badge_id).first()
    if existing:
        return existing
    sb = StudentBadge(student_id=student_id, badge_id=badge_id)
    db.add(sb)
    db.commit()
    db.refresh(sb)
    return sb
