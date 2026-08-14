import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.audit import append_audit_event
from app.deps import require_roles
from app.models import User, Post, Thread, StudentBadge, user_units
from app.rate_limit import enforce_rate_limit
from app.schemas import PlatformUserRoleUpdate, PlatformUserSummary, StudentUserSummary
from app.security import (
    HIGHEST_PLATFORM_ROLE,
    PLATFORM_ADMIN_ROLES,
    PLATFORM_ROLES,
    can_manage_platform_target,
    normalize_platform_role,
    security_event,
)

router = APIRouter()


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _reject_self_action(current_user: User, target: User, action: str) -> None:
    if current_user.id == target.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You cannot {action} your own administrative account.",
        )


def _ensure_target_allowed(current_user: User, target: User, requested_role: str | None = None) -> None:
    if not can_manage_platform_target(current_user.role, target.role, requested_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this account.",
        )


def _ensure_super_admin_remains(db: Session, target: User, requested_role: str | None) -> None:
    removes_highest_role = target.role == HIGHEST_PLATFORM_ROLE and requested_role != HIGHEST_PLATFORM_ROLE
    if not removes_highest_role:
        return
    highest_admins = (
        db.query(User)
        .filter(User.role == HIGHEST_PLATFORM_ROLE)
        .with_for_update()
        .all()
    )
    if len(highest_admins) <= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This action would remove the final platform super administrator.",
        )


@router.get("/users", response_model=list[PlatformUserSummary])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "super_admin")),
):
    return db.query(User).all()


@router.get("/users/students", response_model=list[StudentUserSummary])
def get_student_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "super_admin", "teacher")),
):
    return db.query(User).filter(User.role == "student").all()


@router.get("/users/{user_id}", response_model=PlatformUserSummary)
def get_user_by_id(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "super_admin")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/users/{user_id}")
def update_user(
    user_id: uuid.UUID,
    user: PlatformUserRoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "super_admin")),
):
    enforce_rate_limit(request, "user_management", actor_id=current_user.id)
    db_user = db.query(User).filter(User.id == user_id).with_for_update().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    _reject_self_action(current_user, db_user, "change the role of")
    try:
        requested_role = normalize_platform_role(user.role)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Unsupported platform role.") from exc
    _ensure_target_allowed(current_user, db_user, requested_role)
    try:
        _ensure_super_admin_remains(db, db_user, requested_role)
    except HTTPException:
        security_event(
            action="platform_role_change",
            result="denied",
            actor_id=current_user.id,
            target_type="user",
            target_id=db_user.id,
            reason="final_super_admin",
            request_id=_request_id(request),
        )
        raise
    previous_role = db_user.role
    db_user.role = requested_role
    append_audit_event(
        db,
        action="platform.role.changed",
        actor_id=current_user.id,
        actor_role=current_user.role,
        target_type="user",
        target_id=db_user.id,
        before={"role": previous_role},
        after={"role": requested_role},
        request_id=_request_id(request),
    )
    db.commit()
    security_event(
        action="platform_role_change",
        result="allowed",
        actor_id=current_user.id,
        target_type="user",
        target_id=db_user.id,
        reason=f"{previous_role}_to_{requested_role}",
        request_id=_request_id(request),
    )
    return {"message": "User role updated successfully"}


@router.delete("/users/{user_id}")
def delete_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "super_admin")),
):
    enforce_rate_limit(request, "user_management", actor_id=current_user.id)
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user id")
    db_user = db.query(User).filter(User.id == uid).with_for_update().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    _reject_self_action(current_user, db_user, "delete")
    _ensure_target_allowed(current_user, db_user)
    try:
        _ensure_super_admin_remains(db, db_user, None)
    except HTTPException:
        security_event(
            action="platform_user_delete",
            result="denied",
            actor_id=current_user.id,
            target_type="user",
            target_id=db_user.id,
            reason="final_super_admin",
            request_id=_request_id(request),
        )
        raise

    db.query(Post).filter(Post.user_id == uid).delete()

    user_threads = db.query(Thread).filter(Thread.user_id == uid).all()
    for thread in user_threads:
        db.delete(thread)

    db.query(StudentBadge).filter(StudentBadge.student_id == uid).delete()

    db.execute(user_units.delete().where(user_units.c.user_id == uid))

    deleted_role = db_user.role
    db.delete(db_user)
    append_audit_event(
        db,
        action="platform.user.deleted",
        actor_id=current_user.id,
        actor_role=current_user.role,
        target_type="user",
        target_id=uid,
        before={"role": deleted_role},
        after={},
        request_id=_request_id(request),
    )
    db.commit()
    security_event(
        action="platform_user_delete",
        result="allowed",
        actor_id=current_user.id,
        target_type="user",
        target_id=uid,
        request_id=_request_id(request),
    )
    return {"message": "User deleted successfully"}
