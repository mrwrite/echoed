from sqlalchemy.orm import Session
from app.models import StudentUnitProgress, SegmentProgress
from uuid import UUID
from datetime import datetime

# ---------- StudentUnitProgress ----------

def create_student_unit_progress(db: Session, student_course_id: UUID, unit_id: UUID) -> StudentUnitProgress:
    progress = StudentUnitProgress(
        student_course_id=student_course_id,
        unit_id=unit_id,
        status="not_started"
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress

def update_student_unit_progress_status(db: Session, progress_id: UUID, new_status: str):
    progress = db.get(StudentUnitProgress, progress_id)
    if progress:
        progress.status = new_status
        progress.last_updated = datetime.utcnow()
        db.commit()
    return progress

def get_student_unit_progress(db: Session, student_course_id: UUID, unit_id: UUID):
    return db.query(StudentUnitProgress).filter_by(
        student_course_id=student_course_id,
        unit_id=unit_id
    ).first()


# ---------- SegmentProgress ----------

def create_segment_progress(db: Session, student_unit_id: UUID, lesson_id: UUID) -> SegmentProgress:
    progress = SegmentProgress(
        student_unit_id=student_unit_id,
        lesson_id=lesson_id,
        status="not_started"
    )
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress

def update_segment_progress_status(db: Session, progress_id: UUID, new_status: str):
    progress = db.get(SegmentProgress, progress_id)
    if progress:
        progress.status = new_status
        progress.last_updated = datetime.utcnow()
        db.commit()
    return progress

def get_segment_progress(db: Session, student_unit_id: UUID, lesson_id: UUID):
    return db.query(SegmentProgress).filter_by(
        student_unit_id=student_unit_id,
        lesson_id=lesson_id
    ).first()
