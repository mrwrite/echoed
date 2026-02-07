import enum
from sqlalchemy import Enum as SQLEnum

class ProgressStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SKIPPED = "skipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"


class OrganizationType(enum.Enum):
    SCHOOL = "school"
    HOMESCHOOL = "homeschool"
    DISTRICT = "district"
    INSTRUCTOR = "instructor"
    PERSONAL = "personal"


class OrganizationRole(enum.Enum):
    ORG_ADMIN = "org_admin"
    CONTENT_ADMIN = "content_admin"
    TEACHER = "teacher"
    PARENT = "parent"
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    VIEWER = "viewer"


class MembershipStatus(enum.Enum):
    ACTIVE = "active"
    INVITED = "invited"
    INACTIVE = "inactive"


class CourseVersionStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class SectionMode(enum.Enum):
    IN_PERSON = "in_person"
    REMOTE = "remote"
    HYBRID = "hybrid"
    HOME = "home"


class EnrollmentStatus(enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"


class AssignmentTargetType(enum.Enum):
    UNIT = "unit"
    LESSON = "lesson"


class AssignmentSubmissionStatus(enum.Enum):
    NOT_STARTED = "not_started"
    SUBMITTED = "submitted"
    COMPLETED = "completed"
