from pydantic import BaseModel, Field, ConfigDict, AliasChoices
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


class OrganizationCreate(BaseModel):
    name: str
    type: str
    country: Optional[str] = None
    timezone: Optional[str] = None


class OrganizationResponse(BaseModel):
    id: UUID
    name: str
    type: str
    country: Optional[str]
    timezone: Optional[str]
    created_at: datetime
    role: Optional[str] = None

    class Config:
        from_attributes = True


class OrganizationMembershipResponse(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
    status: str

    class Config:
        from_attributes = True


class OrganizationInviteCreate(BaseModel):
    email: str
    role: str
    expires_at: Optional[datetime] = None


class OrganizationInviteResponse(BaseModel):
    id: UUID
    organization_id: UUID
    email: str
    role: str
    token: str
    expires_at: datetime
    accepted_at: Optional[datetime]
    invited_by_user_id: UUID

    class Config:
        from_attributes = True


class InviteAcceptRequest(BaseModel):
    token: str


class UserPreferencesDto(BaseModel):
    locale: str = "en"
    timezone: Optional[str] = None
    theme: str = "system"
    large_text: bool = False
    dyslexia_font: bool = False
    preferred_mode: str = "student"
    reading_level_mode: str = "standard"

    class Config:
        from_attributes = True


class CourseCreateRequest(BaseModel):
    title: str
    description: str
    subject: Optional[str] = None
    age_band_min: Optional[int] = None
    age_band_max: Optional[int] = None
    default_locale: str = "en"


class CourseVersionCreateRequest(BaseModel):
    changelog: Optional[str] = None


class CourseVersionResponse(BaseModel):
    id: UUID
    course_id: UUID
    version_number: int
    status: str
    changelog: Optional[str]
    created_at: datetime
    published_at: Optional[datetime]
    published_by: Optional[UUID]

    class Config:
        from_attributes = True


class CourseSummaryResponse(BaseModel):
    id: UUID
    title: str
    description: str
    subject: Optional[str] = None
    age_band_min: Optional[int] = None
    age_band_max: Optional[int] = None
    default_locale: str
    created_by: Optional[UUID]
    organization_id: Optional[UUID]

    class Config:
        from_attributes = True


class SectionCreateRequest(BaseModel):
    course_version_id: UUID
    name: str
    mode: str = "remote"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class SectionResponse(BaseModel):
    id: UUID
    organization_id: UUID
    course_version_id: UUID
    name: str
    mode: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_by: UUID

    class Config:
        from_attributes = True


class EnrollmentCreateRequest(BaseModel):
    email: Optional[str] = None
    user_id: Optional[UUID] = None


class EnrollmentResponse(BaseModel):
    id: UUID
    section_id: UUID
    user_id: UUID
    role_in_section: str
    status: str
    enrolled_at: datetime

    class Config:
        from_attributes = True


class LessonSessionResponse(BaseModel):
    id: UUID
    section_id: UUID
    lesson_id: UUID
    started_by: UUID
    started_at: datetime
    ended_at: Optional[datetime]

    class Config:
        from_attributes = True


class LessonSessionEndRequest(BaseModel):
    ended_at: Optional[datetime] = None


class AssignmentCreateRequest(BaseModel):
    target_type: str
    target_id: UUID
    due_at: Optional[datetime] = None
    instructions: Optional[str] = None


class AssignmentResponse(BaseModel):
    id: UUID
    section_id: UUID
    target_type: str
    target_id: UUID
    due_at: Optional[datetime]
    instructions: Optional[str]
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class AssignmentSubmissionRequest(BaseModel):
    status: str = "submitted"


class AssignmentSubmissionResponse(BaseModel):
    id: UUID
    assignment_id: UUID
    user_id: UUID
    status: str
    submitted_at: Optional[datetime]

    class Config:
        from_attributes = True


class ActivityDto(BaseModel):
    type: str
    title: str
    content: str
    order: Optional[int]
    pages: List['StorybookPageDto'] = Field(
        default_factory=list,
        validation_alias=AliasChoices("pages", "storybook_pages"),
    )


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
    pages: List[StorybookPageResponse] = Field(
        default_factory=list,
        validation_alias=AliasChoices("pages", "storybook_pages"),
    )

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


class AssignCourseRequest(BaseModel):
    student_id: UUID
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
