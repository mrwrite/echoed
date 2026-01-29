from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud.badges import BADGE_RULES, calculate_streak_days, get_or_create_badge
from app.database import get_db
from app.deps import require_roles
from app.enum import ProgressStatus
from app.models import Course, Lesson, SegmentProgress, StudentBadge, StudentCourse, StudentUnitProgress, Unit, User

router = APIRouter()


@router.get("/analytics/overview")
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin")),
):
    total_students = db.query(User).filter(User.role == "student").count()
    total_teachers = db.query(User).filter(User.role == "teacher").count()
    total_courses = db.query(Course).count()
    total_enrollments = db.query(StudentCourse).count()
    active_students = db.query(StudentCourse.student_id).distinct().count()
    lessons_completed = db.query(SegmentProgress).filter(
        SegmentProgress.status == ProgressStatus.COMPLETED
    ).count()
    units_completed = db.query(StudentUnitProgress).filter(
        StudentUnitProgress.status == ProgressStatus.COMPLETED
    ).count()
    courses_completed = db.query(StudentCourse).filter(
        StudentCourse.status == "completed"
    ).count()
    completion_rate = (
        round((courses_completed / total_enrollments) * 100, 1)
        if total_enrollments
        else 0
    )
    pending_enrollments = total_enrollments - courses_completed

    return {
        "totals": {
            "students": total_students,
            "teachers": total_teachers,
            "courses": total_courses,
            "active_students": active_students,
            "total_enrollments": total_enrollments,
            "pending_enrollments": pending_enrollments,
        },
        "progress": {
            "lessons_completed": lessons_completed,
            "units_completed": units_completed,
            "courses_completed": courses_completed,
            "course_completion_rate": completion_rate,
        },
    }


@router.get("/analytics/teacher-summary")
def get_teacher_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher")),
):
    courses = db.query(Course).all()
    course_lesson_counts = {}
    for course in courses:
        lesson_count = (
            db.query(Lesson)
            .join(Unit, Unit.id == Lesson.unit_id)
            .filter(Unit.course_id == course.id)
            .count()
        )
        course_lesson_counts[course.id] = lesson_count

    enrollments = (
        db.query(StudentCourse)
        .join(User, User.id == StudentCourse.student_id)
        .all()
    )
    results = []
    for enrollment in enrollments:
        completed_lessons = (
            db.query(SegmentProgress)
            .join(StudentUnitProgress, StudentUnitProgress.id == SegmentProgress.student_unit_id)
            .filter(
                StudentUnitProgress.student_course_id == enrollment.id,
                SegmentProgress.status == ProgressStatus.COMPLETED,
            )
            .count()
        )
        total_lessons = course_lesson_counts.get(enrollment.course_id, 0)
        progress = round((completed_lessons / total_lessons) * 100, 1) if total_lessons else 0
        results.append(
            {
                "student_name": f"{enrollment.student.firstname} {enrollment.student.lastname}",
                "course_title": enrollment.course.title,
                "progress": progress,
                "last_active": enrollment.last_activity_at,
                "status": enrollment.status,
            }
        )
    return results


@router.get("/analytics/student-progress")
def get_student_progress(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    student_id = current_user.id

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

    progress_cards = []
    for rule in BADGE_RULES:
        badge = get_or_create_badge(db, rule["title"], rule["description"])
        current_value = {
            "lessons_completed": lessons_completed,
            "units_completed": units_completed,
            "courses_completed": courses_completed,
            "streak_days": streak_days,
        }.get(rule["metric"], 0)
        progress_cards.append(
            {
                "title": rule["title"],
                "description": rule["description"],
                "current": current_value,
                "target": rule["threshold"],
                "earned": bool(
                    db.query(StudentBadge)
                    .filter_by(student_id=student_id, badge_id=badge.id)
                    .first()
                ),
            }
        )

    return {
        "metrics": {
            "lessons_completed": lessons_completed,
            "units_completed": units_completed,
            "courses_completed": courses_completed,
            "streak_days": streak_days,
        },
        "badge_progress": progress_cards,
    }
