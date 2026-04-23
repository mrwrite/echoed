from pydantic import BaseModel, Field, ConfigDict, AliasChoices, model_validator
from app.enum import ProgressStatus 
from typing import Any, List, Optional
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


class OrganizationUpdate(BaseModel):
    name: str


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
    learning_objectives: Optional[str] = None
    skill_tags: List[str] = Field(default_factory=list)
    standards_metadata: dict[str, Any] = Field(default_factory=dict)


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
    learning_objectives: Optional[str] = None
    skill_tags: List[str] = Field(default_factory=list)
    standards_metadata: dict[str, Any] = Field(default_factory=dict)
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


class SourceDto(BaseModel):
    citation: str
    url: Optional[str] = None

    class Config:
        from_attributes = True

class LessonDto(BaseModel):
    title: str
    objective: Optional[str]
    learning_objectives: Optional[str] = None
    key_concepts: List[str] = Field(default_factory=list)
    teacher_notes: Optional[str] = None
    discussion_questions: List[str] = Field(default_factory=list)
    hook: Optional[str] = None
    content: Optional[str] = None
    guided_practice: Optional[str] = None
    independent_practice: Optional[str] = None
    assessment: Optional[str] = None
    review_status: str = "draft"
    reviewed_by: Optional[UUID] = None
    skill_tags: List[str] = Field(default_factory=list)
    standards_metadata: dict[str, Any] = Field(default_factory=dict)
    order: Optional[int]
    duration_minutes: Optional[int]
    activities: List[ActivityDto] = Field(default_factory=list)
    sources: List[SourceDto] = Field(default_factory=list)

class UnitDto(BaseModel):
    title: str
    content: Optional[str]
    order: Optional[int]
    lessons: List[LessonDto] = Field(default_factory=list)
        

class CourseDto(BaseModel):
    title: str
    description: str
    learning_objectives: Optional[str] = None
    skill_tags: List[str] = Field(default_factory=list)
    standards_metadata: dict[str, Any] = Field(default_factory=dict)
    units: List[UnitDto] = Field(default_factory=list)
    
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


class SourceResponse(BaseModel):
    id: UUID
    citation: str
    url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class LessonResponse(BaseModel):
    id: UUID
    title: str
    objective: Optional[str]
    learning_objectives: Optional[str] = None
    key_concepts: List[str] = Field(default_factory=list)
    teacher_notes: Optional[str] = None
    discussion_questions: List[str] = Field(default_factory=list)
    hook: Optional[str] = None
    content: Optional[str] = None
    guided_practice: Optional[str] = None
    independent_practice: Optional[str] = None
    assessment: Optional[str] = None
    review_status: str
    reviewed_by: Optional[UUID] = None
    skill_tags: List[str] = Field(default_factory=list)
    standards_metadata: dict[str, Any] = Field(default_factory=dict)
    order: Optional[int]
    duration_minutes: Optional[int]
    activities: List[ActivityResponse] = Field(default_factory=list)
    sources: List[SourceResponse] = Field(default_factory=list)
    is_ready_for_approval: bool = False
    missing_readiness_fields: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class UnitResponse(BaseModel):
    id: UUID
    title: str
    content: Optional[str]
    order: Optional[int]
    lessons: List[LessonResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CourseResponse(BaseModel):
    id: UUID
    title: str
    description: str
    learning_objectives: Optional[str] = None
    skill_tags: List[str] = Field(default_factory=list)
    standards_metadata: dict[str, Any] = Field(default_factory=dict)
    units: List[UnitResponse] = Field(default_factory=list)

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


class ProgramCourseLinkRequest(BaseModel):
    course_id: UUID
    order: int = 1
    is_required: bool = True


class ProgramCreateRequest(BaseModel):
    title: str
    description: str
    course_links: List[ProgramCourseLinkRequest] = Field(default_factory=list)


class ProgramCourseResponse(BaseModel):
    id: UUID
    course_id: UUID
    order: int
    is_required: bool
    course: CourseSummaryResponse

    class Config:
        from_attributes = True


class StudentProgramProgressResponse(BaseModel):
    id: UUID
    student_id: UUID
    program_id: UUID
    status: str
    enrolled_on: datetime
    last_activity_at: Optional[datetime]
    completed_at: Optional[datetime]
    completion_percentage: float = 0
    completed_courses: int = 0
    total_courses: int = 0

    class Config:
        from_attributes = True


class ProgramResponse(BaseModel):
    id: UUID
    title: str
    description: str
    organization_id: Optional[UUID]
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    courses: List[ProgramCourseResponse] = Field(default_factory=list)
    progress: Optional[StudentProgramProgressResponse] = None

    class Config:
        from_attributes = True


class QuestionCreateRequest(BaseModel):
    prompt: str
    question_type: str = "multiple_choice"
    choices: List[str] = Field(default_factory=list)
    correct_answer: str
    explanation: Optional[str] = None
    points: float = 1.0
    order: int = 1


class AssessmentCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    lesson_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    program_id: Optional[UUID] = None
    passing_score: float = 70.0
    max_attempts: Optional[int] = None
    questions: List[QuestionCreateRequest] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_scope(self) -> "AssessmentCreateRequest":
        scope_count = sum(
            value is not None for value in (self.lesson_id, self.course_id, self.program_id)
        )
        if scope_count != 1:
            raise ValueError("Assessment must target exactly one of lesson, course, or program.")
        return self


class QuestionResponse(BaseModel):
    id: UUID
    prompt: str
    question_type: str
    choices: List[str] = Field(default_factory=list)
    explanation: Optional[str]
    points: float
    order: int

    class Config:
        from_attributes = True


class AssessmentResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    lesson_id: Optional[UUID]
    course_id: Optional[UUID]
    program_id: Optional[UUID]
    passing_score: float
    max_attempts: Optional[int]
    created_by: Optional[UUID]
    created_at: datetime
    questions: List[QuestionResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class AssessmentAnswerRequest(BaseModel):
    question_id: UUID
    answer: str


class AssessmentAttemptCreateRequest(BaseModel):
    answers: List[AssessmentAnswerRequest] = Field(default_factory=list)


class StudentAssessmentAnswerResponse(BaseModel):
    question_id: UUID
    answer: str
    is_correct: bool
    awarded_points: float

    class Config:
        from_attributes = True


class StudentAssessmentAttemptResponse(BaseModel):
    id: UUID
    assessment_id: UUID
    student_id: UUID
    program_progress_id: Optional[UUID]
    score: float
    max_score: float
    percentage: float
    passed: bool
    submitted_at: datetime
    answers: List[StudentAssessmentAnswerResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class CertificationRequirementCreateRequest(BaseModel):
    requirement_type: str
    course_id: Optional[UUID] = None
    assessment_id: Optional[UUID] = None
    minimum_score: Optional[float] = None


class CertificationCreateRequest(BaseModel):
    program_id: UUID
    title: str
    description: Optional[str] = None
    badge_id: Optional[UUID] = None
    requirements: List[CertificationRequirementCreateRequest] = Field(default_factory=list)


class CertificationRequirementResponse(BaseModel):
    id: UUID
    requirement_type: str
    course_id: Optional[UUID]
    assessment_id: Optional[UUID]
    minimum_score: Optional[float]

    class Config:
        from_attributes = True


class CertificationResponse(BaseModel):
    id: UUID
    program_id: UUID
    badge_id: Optional[UUID]
    title: str
    description: Optional[str]
    created_at: datetime
    requirements: List[CertificationRequirementResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


class StudentCertificationResponse(BaseModel):
    id: UUID
    student_id: UUID
    certification_id: UUID
    awarded_at: datetime
    score_snapshot: Optional[float]
    certification: CertificationResponse

    class Config:
        from_attributes = True


class CertificationEvaluationResponse(BaseModel):
    certification_id: UUID
    awarded: bool
    missing_requirements: List[str] = Field(default_factory=list)
    student_certification: Optional[StudentCertificationResponse] = None
