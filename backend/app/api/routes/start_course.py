from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.crud import progress as crud
from app.database import get_db
from app.deps import require_roles
from app.lesson_governance import GOVERNED_AVAILABLE
from app.log import logger
from app.models import StudentCourse
from app.schemas import SegmentResponse, StartCourseRequest

router = APIRouter()


@router.post("/start-course", response_model=SegmentResponse)
def start_course(
    request: StartCourseRequest,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("student")),
):
    logger.debug("RAW Request Data: %s", request)
    enrollment = (
        db.query(StudentCourse)
        .filter_by(student_id=current_user.id, course_id=request.course_id)
        .first()
    )

    if not enrollment:
        raise HTTPException(status_code=403, detail="Not enrolled in this course.")

    if enrollment.status == "completed":
        raise HTTPException(status_code=400, detail="Course already completed")

    progression = crud.resolve_governed_progression(db, enrollment.id)
    if (
        progression.get("delivery_state") == GOVERNED_AVAILABLE
        and progression.get("unit_progress_id") is not None
    ):
        ensured_progression = crud.resolve_governed_segment_for_unit_progress(
            db, progression["unit_progress_id"]
        )
        if ensured_progression is not None:
            progression = ensured_progression
    return SegmentResponse(**progression)
