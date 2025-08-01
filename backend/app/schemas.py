from pydantic import BaseModel, Field, ConfigDict
from app.enum import ProgressStatus 
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class UserDto(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    password: str
    role: str
    
    model_config = ConfigDict(from_attributes=True)


class ActivityDto(BaseModel):
    type: str
    title: str
    content: str
    order: Optional[int]
    pages: List['StorybookPageDto'] = []


class StorybookPageDto(BaseModel):
    image_url: str
    order: Optional[int]

    class Config:
        from_attributes = True

class LessonDto(BaseModel):
    title: str
    objective: Optional[str]
    order: Optional[int]
    duration_minutes: Optional[int]
    activities: List[ActivityDto] = []

class UnitDto(BaseModel):
    title: str
    content: Optional[str]
    order: Optional[int]
    lessons: List[LessonDto] = []
        

class CourseDto(BaseModel):
    title: str
    description: str
    units: List[UnitDto] = []
    
    model_config = ConfigDict(from_attributes=True)



class MediaResponse(BaseModel):
    id: UUID
    type: Optional[str]
    title: Optional[str]
    url: Optional[str]
    description: Optional[str]

    class Config:
        from_attributes = True


class StorybookPageResponse(BaseModel):
    id: UUID
    image_url: str
    order: Optional[int]

    class Config:
        from_attributes = True


class ActivityResponse(BaseModel):
    id: UUID
    type: str
    title: str
    content: str
    order: Optional[int]
    media: Optional[MediaResponse]
    pages: List[StorybookPageResponse] = []

    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    id: UUID
    title: str
    objective: Optional[str]
    order: Optional[int]
    duration_minutes: Optional[int]
    activities: List[ActivityResponse] = []

    class Config:
        from_attributes = True


class UnitResponse(BaseModel):
    id: UUID
    title: str
    content: Optional[str]
    order: Optional[int]
    lessons: List[LessonResponse] = []

    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    id: UUID
    title: str
    description: str
    units: List[UnitResponse] = []

    class Config:
        from_attributes = True

class EnrollRequest(BaseModel):
    course_id: UUID

class StartCourseRequest(BaseModel):
    course_id: UUID

class SegmentResponse(BaseModel):
    lesson_id: UUID
    status: ProgressStatus
    unit_progress_id: Optional[UUID] = None

class CompleteSegmentRequest(BaseModel):
    student_unit_id: UUID
    lesson_id: UUID

class StudentCourseResponse(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    enrolled_on: datetime
    status: str

    class Config:
        from_attributes = True


class StudentCourseWithDetails(BaseModel):
    id: UUID
    student_id: UUID
    course_id: UUID
    enrolled_on: datetime
    status: str
    course: CourseResponse
    unit_progress_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class BadgeCreate(BaseModel):
    title: str
    description: Optional[str]
    image_url: Optional[str]


class BadgeResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudentBadgeResponse(BaseModel):
    id: UUID
    student_id: UUID
    badge_id: UUID
    awarded_at: datetime
    badge: Optional[BadgeResponse] = None

    class Config:
        from_attributes = True


class ThreadResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class PostResponse(BaseModel):
    id: UUID
    thread_id: UUID
    user_id: UUID
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


