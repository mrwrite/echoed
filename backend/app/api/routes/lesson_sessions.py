from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_org_roles
from app.models import LessonSession, Section
from app.schemas import LessonSessionResponse, LessonSessionEndRequest
from app.section_scope import require_scoped_section, require_section_lesson

router = APIRouter()


@router.post("/sections/{section_id}/lessons/{lesson_id}/start", response_model=LessonSessionResponse)
def start_lesson_session(
    section_id: str,
    lesson_id: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_org_roles("teacher", "org_admin", "instructor")),
):
    section = require_scoped_section(db, membership, section_id)
    lesson = require_section_lesson(db, section, lesson_id)
    session = LessonSession(
        section_id=section.id,
        lesson_id=lesson.id,
        started_by=current_user.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/lesson-sessions/{session_id}/end", response_model=LessonSessionResponse)
def end_lesson_session(
    session_id: UUID,
    payload: LessonSessionEndRequest,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("teacher", "org_admin", "instructor")),
):
    session = (
        db.query(LessonSession)
        .join(Section, Section.id == LessonSession.section_id)
        .filter(
            LessonSession.id == session_id,
            Section.organization_id == membership.organization_id,
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.ended_at = payload.ended_at or datetime.utcnow()
    db.commit()
    db.refresh(session)
    return session
