import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_roles
from app.models import User, Post, Thread, StudentBadge, user_units
from app.schemas import UserDto
from app.auth import hash_password

router = APIRouter()


@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    return db.query(User).all()


@router.get("/users/{user_id}")
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/users/students")
def get_student_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    return db.query(User).filter(User.role == "student").all()


@router.put("/users/{user_id}")
def update_user(
    user_id: str,
    user: UserDto,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.firstname = user.firstname
    db_user.lastname = user.lastname
    db_user.username = user.username
    db_user.email = user.email
    db_user.role = user.role.lower()

    if user.password:
        db_user.hashed_password = hash_password(user.password)

    db.commit()
    return {"message": "User updated successfully"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin")),
):
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user id")
    db_user = db.query(User).filter(User.id == uid).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(Post).filter(Post.user_id == uid).delete()

    user_threads = db.query(Thread).filter(Thread.user_id == uid).all()
    for thread in user_threads:
        db.delete(thread)

    db.query(StudentBadge).filter(StudentBadge.student_id == uid).delete()

    db.execute(user_units.delete().where(user_units.c.user_id == uid))

    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
