from fastapi import FastAPI, Depends, HTTPException, status, Request, Path
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.auth import create_access_token, authenticate_user, get_current_user, hash_password
from app.database import SessionLocal, engine, Base
from app.models import User, Course, Unit, Lesson, Activity, Media
from app.schemas import UserDto, CourseDto, CourseResponse, UnitDto, LessonDto, ActivityDto, MediaResponse, ActivityResponse, LessonResponse, UnitResponse
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

@app.get("/api/courses/{course_id}", response_model=CourseResponse)
def get_course_by_id(course_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_data = CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        units=[
            UnitResponse(
                id=unit.id,
                title=unit.title,
                content=unit.content,
                order=unit.order,
                lessons=[
                    LessonResponse(
                        id=lesson.id,
                        title=lesson.title,
                        objective=lesson.objective,
                        order=lesson.order,
                        duration_minutes=lesson.duration_minutes,
                        activities=[
                            ActivityResponse(
                                id=activity.id,
                                type=activity.type,
                                title=activity.title,
                                content=activity.content,
                                order=activity.order,
                                media=MediaResponse(
                                    id=activity.media.id,
                                    type=activity.media.type,
                                    title=activity.media.title,
                                    url=activity.media.url,
                                    description=activity.media.description
                                ) if activity.media else None
                            )
                            for activity in lesson.activities
                        ]
                    )
                    for lesson in unit.lessons
                ]
            )
            for unit in course.units
        ]
    )

    return course_data

@app.post("/api/courses")
def create_course(course: CourseDto, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_course = Course(title=course.title, description=course.description)
    db.add(new_course)
    db.flush()  # So we have new_course.id immediately

    for unit_data in course.units:
        new_unit = Unit(
            title=unit_data.title,
            content=unit_data.content,
            order=unit_data.order,
            course_id=new_course.id
        )
        db.add(new_unit)
        db.flush()  # Get unit_id for lessons

        for lesson_data in unit_data.lessons:
            new_lesson = Lesson(
                title=lesson_data.title,
                objective=lesson_data.objective,
                order=lesson_data.order,
                duration_minutes=lesson_data.duration_minutes,
                unit_id=new_unit.id
            )
            db.add(new_lesson)
            db.flush()  # Get lesson_id for activities

            for activity_data in lesson_data.activities:
                new_activity = Activity(
                    type=activity_data.type,
                    title=activity_data.title,
                    content=activity_data.content,
                    order=activity_data.order,
                    lesson_id=new_lesson.id
                )
                db.add(new_activity)

    db.commit()

    return {"message": "Course with units, lessons, and activities created successfully!"}

@app.put("/api/courses/{course_id}")
def update_course(course_id: str, course_dto: CourseDto, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing_course = db.query(Course).filter(Course.id == course_id).first()
    if not existing_course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Update basic fields
    existing_course.title = course_dto.title
    existing_course.description = course_dto.description

    # Clear existing units (and lessons/activities) - simplest approach
    existing_course.units.clear()
    db.commit()

    # Rebuild Units, Lessons, Activities fresh
    for unit_dto in course_dto.units:
        new_unit = Unit(
            title=unit_dto.title,
            content=unit_dto.content,
            order=unit_dto.order,
            course_id=existing_course.id
        )
        db.add(new_unit)
        db.flush()  # get unit id for relationship if needed

        for lesson_dto in unit_dto.lessons:
            new_lesson = Lesson(
                title=lesson_dto.title,
                objective=lesson_dto.objective,
                order=lesson_dto.order,
                duration_minutes=lesson_dto.duration_minutes,
                unit_id=new_unit.id
            )
            db.add(new_lesson)
            db.flush()

            for activity_dto in lesson_dto.activities:
                new_activity = Activity(
                    title=activity_dto.title,
                    type=activity_dto.type,
                    content=activity_dto.content,
                    order=activity_dto.order,
                    lesson_id=new_lesson.id
                )
                db.add(new_activity)

    db.commit()
    db.refresh(existing_course)

    return {"message": "Course updated successfully"}

