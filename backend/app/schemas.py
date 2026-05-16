from pydantic import BaseModel, Field, ConfigDict, AliasChoices, model_validator
from app.enum import ProgressStatus 
from typing import Any, List, Optional
from uuid import UUID
from datetime import datetime


class RevisionMetadataResponseMixin(BaseModel):
    revision_number: int = 1
    revision_label: Optional[str] = None
    revision_status: str = "current"
    revision_metadata: dict[str, Any] = Field(default_factory=dict)
    previous_revision_id: Optional[UUID] = None
    superseded_by_id: Optional[UUID] = None
    lineage_status: str = "standalone"
    lineage_metadata: dict[str, Any] = Field(default_factory=dict)
    published_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None

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


class CourseSummaryResponse(RevisionMetadataResponseMixin):
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


class LessonResponse(RevisionMetadataResponseMixin):
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
    review_status: Optional[str] = None
    reviewed_by: Optional[UUID] = None
    skill_tags: List[str] = Field(default_factory=list)
    standards_metadata: dict[str, Any] = Field(default_factory=dict)
    order: Optional[int]
    duration_minutes: Optional[int]
    activities: List[ActivityResponse] = Field(default_factory=list)
    sources: List[SourceResponse] = Field(default_factory=list)
    is_ready_for_approval: Optional[bool] = None
    missing_readiness_fields: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class UnitResponse(RevisionMetadataResponseMixin):
    id: UUID
    title: str
    content: Optional[str]
    order: Optional[int]
    lessons: List[LessonResponse] = Field(default_factory=list)
    learner_availability: Optional[str] = None
    learner_availability_detail: Optional[str] = None

    class Config:
        from_attributes = True


class CourseResponse(RevisionMetadataResponseMixin):
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
    lesson_id: Optional[UUID] = None
    status: Optional[ProgressStatus] = None
    unit_progress_id: Optional[UUID] = None
    delivery_state: Optional[str] = None
    detail: Optional[str] = None

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
    continuation_guidance: Optional["ContinuationGuidanceResponse"] = None

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
    unit_id: Optional[UUID] = None
    lesson_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    program_id: Optional[UUID] = None
    assessment_scope: Optional[str] = None
    assessment_state: Optional[str] = None
    availability_state: Optional[str] = None
    passing_score: float = 70.0
    max_attempts: Optional[int] = None
    policy_metadata: dict[str, Any] = Field(default_factory=dict)
    lifecycle_metadata: dict[str, Any] = Field(default_factory=dict)
    competency_alignments: List["AssessmentCompetencyAlignmentCreateRequest"] = Field(default_factory=list)
    questions: List[QuestionCreateRequest] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_scope(self) -> "AssessmentCreateRequest":
        scope_count = sum(
            value is not None for value in (self.unit_id, self.lesson_id, self.course_id, self.program_id)
        )
        if scope_count != 1:
            raise ValueError("Assessment must target exactly one of lesson, unit, course, or program.")

        if self.unit_id is not None:
            resolved_scope = "unit"
        elif self.lesson_id is not None:
            resolved_scope = "lesson"
        elif self.course_id is not None:
            resolved_scope = "course"
        else:
            resolved_scope = "program"

        if self.assessment_scope is None:
            self.assessment_scope = resolved_scope
        elif self.assessment_scope != resolved_scope:
            raise ValueError("Assessment scope must match the provided target field.")

        if self.assessment_state is None:
            self.assessment_state = "published"
        if self.availability_state is None:
            self.availability_state = "available"

        if self.assessment_state not in {"draft", "published", "archived"}:
            raise ValueError("Assessment state must be draft, published, or archived.")
        if self.availability_state not in {"available", "unavailable", "pending_review"}:
            raise ValueError(
                "Assessment availability state must be available, unavailable, or pending_review."
            )
        return self


class AssessmentCompetencyAlignmentCreateRequest(BaseModel):
    objective_key: str
    objective_title: Optional[str] = None
    objective_type: str = "objective"
    weight: float = 1.0
    mastery_threshold: float = 80.0
    question_order: Optional[int] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_alignment(self) -> "AssessmentCompetencyAlignmentCreateRequest":
        if self.objective_type not in {"objective", "competency"}:
            raise ValueError("Objective type must be objective or competency.")
        if self.weight <= 0:
            raise ValueError("Alignment weight must be greater than 0.")
        if self.mastery_threshold < 0 or self.mastery_threshold > 100:
            raise ValueError("Mastery threshold must be between 0 and 100.")
        if self.question_order is not None and self.question_order <= 0:
            raise ValueError("Question order must be greater than 0.")
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


class AssessmentCompetencyAlignmentResponse(BaseModel):
    id: UUID
    assessment_id: UUID
    question_id: Optional[UUID] = None
    objective_key: str
    objective_title: Optional[str] = None
    objective_type: str
    weight: float
    mastery_threshold: float
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True


class AssessmentResponse(RevisionMetadataResponseMixin):
    id: UUID
    title: str
    description: Optional[str]
    unit_id: Optional[UUID]
    lesson_id: Optional[UUID]
    course_id: Optional[UUID]
    program_id: Optional[UUID]
    assessment_scope: str
    assessment_state: str
    availability_state: str
    passing_score: float
    max_attempts: Optional[int]
    policy_metadata: dict[str, Any] = Field(default_factory=dict)
    lifecycle_metadata: dict[str, Any] = Field(default_factory=dict)
    learner_delivery_state: str = "available"
    learner_delivery_detail: Optional[str] = None
    is_available_for_learner: bool = True
    competency_alignments: List[AssessmentCompetencyAlignmentResponse] = Field(default_factory=list)
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


class MasteryObjectiveSummaryResponse(BaseModel):
    objective_key: str
    objective_title: Optional[str] = None
    objective_type: str
    mastery_threshold: float
    total_weight: float
    passed_weight: float
    mastery_percentage: float
    mastered: bool
    assessments_considered: int
    attempts_considered: int
    latest_attempt_at: Optional[datetime] = None


class MasterySummaryResponse(BaseModel):
    student_id: UUID
    lesson_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    program_id: Optional[UUID] = None
    objectives: List[MasteryObjectiveSummaryResponse] = Field(default_factory=list)


class ReportingProgressSnapshotResponse(BaseModel):
    lessons_completed: int
    units_completed: int
    courses_completed: int
    last_activity_at: Optional[datetime] = None


class ContinuationGuidanceResponse(BaseModel):
    support_state: str
    learner_title: str
    learner_message: str
    reinforcement_title: Optional[str] = None
    reinforcement_message: Optional[str] = None
    recommended_action: str
    evidence_source: str
    review_lesson_id: Optional[UUID] = None
    review_lesson_title: Optional[str] = None
    review_key_concepts: List[str] = Field(default_factory=list)
    review_prompts: List[str] = Field(default_factory=list)
    extension_lesson_id: Optional[UUID] = None
    extension_lesson_title: Optional[str] = None
    extension_key_concepts: List[str] = Field(default_factory=list)
    extension_prompts: List[str] = Field(default_factory=list)
    educator_note: Optional[str] = None
    educator_intervention_hint: Optional[str] = None


class EducatorRuntimeSupportSummaryResponse(BaseModel):
    student_id: UUID
    student_name: str
    student_course_id: UUID
    course_id: UUID
    course_title: str
    support_state: str
    support_summary: str
    evidence_source: str
    recommended_action: str
    last_evidence_at: Optional[datetime] = None
    context_lesson_id: Optional[UUID] = None
    context_lesson_title: Optional[str] = None
    context_key_concepts: List[str] = Field(default_factory=list)
    context_prompts: List[str] = Field(default_factory=list)
    educator_intervention_hint: Optional[str] = None


class PublishReadinessIssueResponse(BaseModel):
    entity_type: str
    entity_id: Optional[UUID] = None
    entity_title: str
    code: str
    message: str


class CoursePublishReadinessResponse(BaseModel):
    course_id: UUID
    course_title: str
    is_ready: bool
    blocking_issue_count: int
    warning_count: int
    blocking_issues: List[PublishReadinessIssueResponse] = Field(default_factory=list)
    warnings: List[PublishReadinessIssueResponse] = Field(default_factory=list)


class CourseSafePublishValidationResponse(BaseModel):
    course_id: UUID
    course_title: str
    is_safe: bool
    blocking_issue_count: int
    warning_count: int
    blocking_issues: List[PublishReadinessIssueResponse] = Field(default_factory=list)
    warnings: List[PublishReadinessIssueResponse] = Field(default_factory=list)


class CompetencyEvidenceAffectedAssessmentResponse(BaseModel):
    assessment_id: Optional[UUID] = None
    assessment_title: str
    competency_identifiers: List[str] = Field(default_factory=list)


class CourseCompetencyEvidenceIntegrityResponse(BaseModel):
    course_id: UUID
    course_title: str
    is_valid: bool
    is_explainable: bool
    blocking_issue_count: int
    warning_count: int
    blocking_issues: List[PublishReadinessIssueResponse] = Field(default_factory=list)
    warnings: List[PublishReadinessIssueResponse] = Field(default_factory=list)
    affected_assessments: List[CompetencyEvidenceAffectedAssessmentResponse] = Field(default_factory=list)
    affected_competency_identifiers: List[str] = Field(default_factory=list)


class RuntimeInterventionEvidenceBasisResponse(BaseModel):
    source: str
    detail: str
    assessment_id: Optional[UUID] = None
    assessment_title: Optional[str] = None
    competency_identifiers: List[str] = Field(default_factory=list)


class CourseRuntimeInterventionRecommendationResponse(BaseModel):
    student_id: UUID
    student_name: str
    student_course_id: UUID
    course_id: UUID
    course_title: str
    recommendation_state: str
    educator_attention_level: str
    summary: str
    evidence_basis: List[RuntimeInterventionEvidenceBasisResponse] = Field(default_factory=list)
    confidence_level: str
    caution_flags: List[str] = Field(default_factory=list)
    learner_safe_message: str


class CourseLineageSafetyVisibilityResponse(BaseModel):
    course_id: UUID
    course_title: str
    is_coherent: bool
    is_safe: bool
    blocking_issue_count: int
    warning_count: int
    blocking_issues: List[PublishReadinessIssueResponse] = Field(default_factory=list)
    warnings: List[PublishReadinessIssueResponse] = Field(default_factory=list)


class CourseGovernanceSummaryResponse(BaseModel):
    course_id: UUID
    course_title: str
    publish_readiness: CoursePublishReadinessResponse
    safe_publish_validation: CourseSafePublishValidationResponse
    lineage_safety_visibility: CourseLineageSafetyVisibilityResponse
    competency_evidence_integrity: CourseCompetencyEvidenceIntegrityResponse
    runtime_intervention_recommendations: List[CourseRuntimeInterventionRecommendationResponse] = Field(
        default_factory=list
    )


class AssessmentEvidenceSummaryResponse(BaseModel):
    assessment_id: UUID
    assessment_title: str
    assessment_scope: str
    assessment_state: str
    availability_state: str
    question_count: int
    attempt_count: int
    passed_attempt_count: int
    latest_attempt_id: Optional[UUID] = None
    latest_attempt_at: Optional[datetime] = None
    latest_score: Optional[float] = None
    latest_max_score: Optional[float] = None
    latest_percentage: Optional[float] = None
    latest_passed: Optional[bool] = None
    submitted_event_count: int = 0
    scored_event_count: int = 0
    latest_event_metadata: dict[str, Any] = Field(default_factory=dict)


class AssessmentReportingSummaryResponse(BaseModel):
    student_id: UUID
    lesson_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None
    course_id: Optional[UUID] = None
    program_id: Optional[UUID] = None
    progress: ReportingProgressSnapshotResponse
    assessment_evidence: List[AssessmentEvidenceSummaryResponse] = Field(default_factory=list)
    mastery_summary: MasterySummaryResponse
    continuation_guidance: Optional[ContinuationGuidanceResponse] = None
    educator_runtime_support_summary: Optional[EducatorRuntimeSupportSummaryResponse] = None
