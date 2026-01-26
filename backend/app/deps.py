from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user as auth_get_current_user
from app.database import SessionLocal
from app.models import User


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(current_user: User = Depends(auth_get_current_user)) -> User:
    return current_user


def require_roles(*roles: str):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_user

    return role_checker
