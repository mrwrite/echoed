from datetime import datetime, timedelta, timezone
import os
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models import User
from app.database import SessionLocal
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

SECRET_KEY = os.getenv("JWT_SECRET")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET environment variable not set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    print("Generating new token. Expiration time:", expire)
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
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):  
    print("Raw Token Received:", token)  # ✅ Debugging

    if not token:
        print("ERROR: Missing token")
        raise HTTPException(status_code=401, detail="Invalid token format")

    # ✅ Remove ONLY ONE "Bearer " if it exists
    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
        print("Decoded Token Payload:", payload)  # ✅ Debugging

        exp_timestamp = payload.get("exp", 0)
        exp_time = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
        print("Token Expiration Timestamp:", exp_timestamp)  
        print("Token Expiration Time:", exp_time)

        # ✅ Fix token expiration check
        if datetime.now(timezone.utc).timestamp() > exp_timestamp:
            print("ERROR: Token has expired")
            raise HTTPException(status_code=401, detail="Token has expired")

        username: str = payload.get("sub")
        print("Username from Token:", username)  # ✅ Debugging

        if username is None:
            print("ERROR: No username found in token")
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

        # ✅ Query the database for the user
        user = db.query(User).filter(User.username == username).first()
        print("User from Database:", user)  # ✅ Debugging

        if user is None:
            print("ERROR: User not found in the database")
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError as e:
        print("JWT Decode Error:", str(e))  
        raise HTTPException(status_code=401, detail="Invalid token")