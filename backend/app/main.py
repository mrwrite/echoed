from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.auth import create_access_token, authenticate_user, get_current_user, hash_password
from app.database import SessionLocal, engine, Base
from app.models import User, Course, Unit
from app.schemas import UserDto
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api")
def read_root():
    return {"message": "Echoed API is running"}

@app.post("/api/auth/register")
def register_user(user: UserDto, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    new_user = User(username=user.username, firstname=user.firstname, lastname=user.lastname, email=user.email, role=user.role.lower(), hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

@app.post("/api/auth/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user.username, "user_id": str(user.id), "fullname": f"{user.firstname} {user.lastname}", "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}, you have access!"}

@app.get("/api/users")
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    users = db.query(User).all()
    return users

@app.get("/api/users/{user_id}")
def get_user_by_id(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/api/users/{user_id}")
def update_user(user_id: str, user: UserDto, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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

@app.delete("/api/users/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}


@app.get("/api/courses")
def get_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    courses = db.query(Course).all()
    return courses

@app.get("/api/courses/{course_id}")
def get_course_by_id(course_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

# @app.post("/api/courses")
# def create_course(course: Course, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
#     db.add(course)
#     db.commit()
#     db.refresh(course)
#     return {"message": "Course created successfully", "course_id": str(course.id)}  

