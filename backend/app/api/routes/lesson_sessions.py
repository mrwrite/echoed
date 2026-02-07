from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_org_roles
from app.models import LessonSession
from app.schemas import LessonSessionResponse, LessonSessionEndRequest

router = APIRouter()


@router.post("/sections/{section_id}/lessons/{lesson_id}/start", response_model=LessonSessionResponse)
def start_lesson_session(
    section_id: str,
    lesson_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_org_roles("teacher", "org_admin", "instructor")),
):
    session = LessonSession(
        section_id=section_id,
        lesson_id=lesson_id,
        started_by=current_user.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/lesson-sessions/{session_id}/end", response_model=LessonSessionResponse)
def end_lesson_session(
    session_id: str,
    payload: LessonSessionEndRequest,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("teacher", "org_admin", "instructor")),
):
    session = db.query(LessonSession).filter(LessonSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.ended_at = payload.ended_at or datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session
