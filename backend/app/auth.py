from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Iterable
from uuid import UUID

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer

from app.enum import MembershipStatus, OrganizationType
from app.models import Organization, OrganizationMembership, User
from app.database import SessionLocal
from app.log import logger
from app.observability import emit_event, metrics
from app.operational_config import load_operational_settings

operational_settings = load_operational_settings()
SECRET_KEY = operational_settings.jwt_secret

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@dataclass(frozen=True)
class ActiveOrganizationContext:
    organization_id: UUID
    organization_name: str
    organization_type: str
    organization_role: str


def resolve_active_organization(
    memberships: Iterable[OrganizationMembership],
) -> ActiveOrganizationContext | None:
    membership_list = list(memberships)
    if not membership_list:
        return None

    active_memberships = [
        membership
        for membership in membership_list
        if membership.status == MembershipStatus.ACTIVE
    ]
    candidate_memberships = active_memberships or membership_list

    memberships_with_org = [
        membership for membership in candidate_memberships if getattr(membership, "organization", None)
    ]
    if not memberships_with_org:
        return None

    def membership_sort_key(membership: OrganizationMembership) -> tuple[int, datetime, str]:
        organization: Organization = membership.organization
        return (
            0 if organization.type != OrganizationType.PERSONAL else 1,
            organization.created_at or datetime.min,
            str(organization.id),
        )

    selected_membership = min(memberships_with_org, key=membership_sort_key)
    selected_organization: Organization = selected_membership.organization

    return ActiveOrganizationContext(
        organization_id=selected_organization.id,
        organization_name=selected_organization.name,
        organization_type=selected_organization.type.value,
        organization_role=selected_membership.role.value,
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError:
        db.rollback()
        metrics.increment("echoed_database_operations_total", operation="auth_session", result="failure")
        emit_event("database.operation_failed", level=40, component="database", operation="auth_session", result="failure")
        raise
    finally:
        db.close()


# ---- PASSWORD HASHING / VERIFYING USING BCRYPT DIRECTLY ----

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Note: bcrypt only uses the first 72 bytes of the password.
    You may want to enforce max length in your Pydantic models.
    """
    if isinstance(password, str):
        password_bytes = password.encode("utf-8")
    else:
        password_bytes = password

    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    """
    if not hashed_password:
        return False

    if isinstance(plain_password, str):
        plain_bytes = plain_password.encode("utf-8")
    else:
        plain_bytes = plain_password

    return bcrypt.checkpw(plain_bytes, hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    logger.debug("Generating new token. Expiration time: %s", expire)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Get user from database
def get_user(db: Session, identifier: str):
    return (
        db.query(User)
        .filter(or_(User.username == identifier, User.email == identifier))
        .first()
    )


# Authenticate user
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


# Dependency to get the current user from JWT token
def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    if not token:
        logger.warning("Authentication rejected: missing token")
        raise HTTPException(status_code=401, detail="Invalid token format")

    # Remove ONLY ONE "Bearer " if it exists
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        exp_timestamp = payload.get("exp", 0)

        # Token expiration check
        if datetime.now(timezone.utc).timestamp() > exp_timestamp:
            logger.warning("Authentication rejected: token expired")
            raise HTTPException(status_code=401, detail="Token has expired")

        username: str | None = payload.get("sub")

        if username is None:
            logger.warning("Authentication rejected: subject claim missing")
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )

        user = db.query(User).filter(User.username == username).first()

        if user is None:
            logger.warning("Authentication rejected: subject not found")
            raise HTTPException(status_code=401, detail="User not found")

        request.state.actor_class = "authenticated"
        request.state.actor_id = str(user.id)
        request.state.actor_role = user.role
        active_org_id = payload.get("active_org_id")
        if active_org_id:
            request.state.organization_id = "present"
        return user
    except JWTError as e:
        logger.warning("Authentication rejected: token decode failed")
        raise HTTPException(status_code=401, detail="Invalid token")
