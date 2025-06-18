from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID

class UserDto(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    password: str
    role: str
    
    class Config:
        from_attributes = True


class ActivityDto(BaseModel):
    type: str
    title: str
    content: str
    order: Optional[int]

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
    
    class Config:
        from_attributes = True



class MediaResponse(BaseModel):
    id: UUID
    type: Optional[str]
    title: Optional[str]
    url: Optional[str]
    description: Optional[str]

class ActivityResponse(BaseModel):
    id: UUID
    type: str
    title: str
    content: str
    order: Optional[int]
    media: Optional[MediaResponse]

class LessonResponse(BaseModel):
    id: UUID
    title: str
    objective: Optional[str]
    order: Optional[int]
    duration_minutes: Optional[int]
    activities: List[ActivityResponse] = []

class UnitResponse(BaseModel):
    id: UUID
    title: str
    content: Optional[str]
    order: Optional[int]
    lessons: List[LessonResponse] = []

class CourseResponse(BaseModel):
    id: UUID
    title: str
    description: str
    units: List[UnitResponse] = []

class EnrollRequest(BaseModel):
    course_id: UUID

