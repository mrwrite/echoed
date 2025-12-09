from datetime import datetime, timedelta, timezone
import os

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.models import User
from app.database import SessionLocal
from app.log import logger

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET environment variable not set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
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
def get_user(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# Authenticate user
def authenticate_user(db: Session, username: str, password: str):
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user


# Dependency to get the current user from JWT token
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    logger.debug("Raw Token Received: %s", token)

    if not token:
        logger.error("ERROR: Missing token")
        raise HTTPException(status_code=401, detail="Invalid token format")

    # Remove ONLY ONE "Bearer " if it exists
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.debug("Decoded Token Payload: %s", payload)

        exp_timestamp = payload.get("exp", 0)
        exp_time = datetime.fromtimestamp(
            exp_timestamp, tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")
        logger.debug("Token Expiration Timestamp: %s", exp_timestamp)
        logger.debug("Token Expiration Time: %s", exp_time)

        # Token expiration check
        if datetime.now(timezone.utc).timestamp() > exp_timestamp:
            logger.error("ERROR: Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")

        username: str | None = payload.get("sub")
        logger.debug("Username from Token: %s", username)

        if username is None:
            logger.error("ERROR: No username found in token")
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )

        user = db.query(User).filter(User.username == username).first()
        logger.debug("User from Database: %s", user)

        if user is None:
            logger.error("ERROR: User not found in the database")
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError as e:
        logger.error("JWT Decode Error: %s", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
