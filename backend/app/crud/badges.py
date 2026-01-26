from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.enum import ProgressStatus
from app.models import Badge, SegmentProgress, StudentBadge, StudentCourse, StudentUnitProgress


BADGE_RULES = [
    {
        "key": "first_lesson",
        "title": "Story Starter",
        "description": "Completed your first lesson and opened the door to history.",
        "threshold": 1,
        "metric": "lessons_completed",
    },
    {
        "key": "unit_pathfinder",
        "title": "Unit Pathfinder",
        "description": "Completed a full unit with focus and curiosity.",
        "threshold": 1,
        "metric": "units_completed",
    },
    {
        "key": "course_trailblazer",
        "title": "Course Trailblazer",
        "description": "Completed an entire course and earned a milestone legacy.",
        "threshold": 1,
        "metric": "courses_completed",
    },
    {
        "key": "streak_keeper",
        "title": "Streak Keeper",
        "description": "Learned 3 days in a row and kept the rhythm going.",
        "threshold": 3,
        "metric": "streak_days",
    },
]


def get_or_create_badge(db: Session, title: str, description: str | None = None) -> Badge:
    badge = db.query(Badge).filter(Badge.title == title).first()
    if badge:
        return badge
    badge = Badge(title=title, description=description)
    db.add(badge)
    db.commit()
    db.refresh(badge)
    return badge


def calculate_streak_days(db: Session, student_id) -> int:
    completed_segments = (
        db.query(SegmentProgress)
        .join(StudentUnitProgress, StudentUnitProgress.id == SegmentProgress.student_unit_id)
        .join(StudentCourse, StudentCourse.id == StudentUnitProgress.student_course_id)
        .filter(
            StudentCourse.student_id == student_id,
            SegmentProgress.status == ProgressStatus.COMPLETED,
        )
        .all()
    )
    completed_dates = {
        seg.completed_at.date()
        for seg in completed_segments
        if seg.completed_at is not None
    }
    if not completed_dates:
        return 0
    today = datetime.utcnow().date()
    streak = 0
    day = today
    while day in completed_dates:
        streak += 1
        day = day - timedelta(days=1)
    return streak


def award_badges_for_student(db: Session, student_id) -> list[StudentBadge]:
    lessons_completed = (
        db.query(SegmentProgress)
        .join(StudentUnitProgress, StudentUnitProgress.id == SegmentProgress.student_unit_id)
        .join(StudentCourse, StudentCourse.id == StudentUnitProgress.student_course_id)
        .filter(
            StudentCourse.student_id == student_id,
            SegmentProgress.status == ProgressStatus.COMPLETED,
        )
        .count()
    )
    units_completed = (
        db.query(StudentUnitProgress)
        .join(StudentCourse, StudentCourse.id == StudentUnitProgress.student_course_id)
        .filter(
            StudentCourse.student_id == student_id,
            StudentUnitProgress.status == ProgressStatus.COMPLETED,
        )
        .count()
    )
    courses_completed = (
        db.query(StudentCourse)
        .filter(StudentCourse.student_id == student_id, StudentCourse.status == "completed")
        .count()
    )
    streak_days = calculate_streak_days(db, student_id)

    metrics = {
        "lessons_completed": lessons_completed,
        "units_completed": units_completed,
        "courses_completed": courses_completed,
        "streak_days": streak_days,
    }

    awarded = []
    for rule in BADGE_RULES:
        if metrics.get(rule["metric"], 0) < rule["threshold"]:
            continue
        badge = get_or_create_badge(db, rule["title"], rule["description"])
        existing = (
            db.query(StudentBadge)
            .filter_by(student_id=student_id, badge_id=badge.id)
            .first()
        )
        if existing:
            awarded.append(existing)
            continue
        student_badge = StudentBadge(student_id=student_id, badge_id=badge.id)
        db.add(student_badge)
        db.commit()
        db.refresh(student_badge)
        awarded.append(student_badge)

    return awarded
