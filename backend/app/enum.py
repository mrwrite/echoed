import enum
from sqlalchemy import Enum as SQLEnum

class ProgressStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    SKIPPED = "skipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"