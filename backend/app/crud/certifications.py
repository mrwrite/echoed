from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.models import (
    Certification,
    Program,
    StudentAssessmentAttempt,
    StudentBadge,
    StudentCertification,
    StudentCourse,
    StudentProgramProgress,
)


def get_program_completion(db: Session, program: Program, student_id) -> tuple[int, int, float, datetime | None]:
    course_ids = [link.course_id for link in program.courses if link.is_required]
    if not course_ids:
        return 0, 0, 100.0, None

    student_courses = (
        db.query(StudentCourse)
        .filter(
            StudentCourse.student_id == student_id,
            StudentCourse.course_id.in_(course_ids),
        )
        .all()
    )
    completed = sum(1 for student_course in student_courses if student_course.status == "completed")
    total = len(course_ids)
    percentage = (completed / total) * 100 if total else 100.0
    last_activity = max(
        (student_course.last_activity_at for student_course in student_courses if student_course.last_activity_at),
        default=None,
    )
    return completed, total, percentage, last_activity


def sync_student_program_progress(
    db: Session,
    *,
    program: Program,
    student_id,
    progress: StudentProgramProgress | None = None,
) -> StudentProgramProgress | None:
    progress = progress or (
        db.query(StudentProgramProgress)
        .filter(
            StudentProgramProgress.student_id == student_id,
            StudentProgramProgress.program_id == program.id,
        )
        .first()
    )
    if not progress:
        return None

    completed, total, percentage, last_activity = get_program_completion(db, program, student_id)
    progress.last_activity_at = last_activity
    if total > 0 and completed == total:
        progress.status = "completed"
        progress.completed_at = progress.completed_at or datetime.utcnow()
    else:
        progress.status = "active"
        progress.completed_at = None
    db.commit()
    db.refresh(progress)
    return progress


def evaluate_certification(db: Session, certification: Certification, student_id) -> tuple[bool, list[str], StudentCertification | None]:
    missing_requirements: list[str] = []
    score_snapshot: float | None = None

    program_progress = sync_student_program_progress(
        db,
        program=certification.program,
        student_id=student_id,
    )

    for requirement in certification.requirements:
        if requirement.requirement_type == "course_completion":
            student_course = (
                db.query(StudentCourse)
                .filter(
                    StudentCourse.student_id == student_id,
                    StudentCourse.course_id == requirement.course_id,
                    StudentCourse.status == "completed",
                )
                .first()
            )
            if not student_course:
                missing_requirements.append(f"Course {requirement.course_id} must be completed.")
        elif requirement.requirement_type == "assessment_pass":
            attempts = (
                db.query(StudentAssessmentAttempt)
                .filter(
                    StudentAssessmentAttempt.student_id == student_id,
                    StudentAssessmentAttempt.assessment_id == requirement.assessment_id,
                    StudentAssessmentAttempt.passed.is_(True),
                )
                .order_by(StudentAssessmentAttempt.submitted_at.desc())
                .all()
            )
            matched_attempt = None
            for attempt in attempts:
                percentage = (attempt.score / attempt.max_score) * 100 if attempt.max_score else 0
                if requirement.minimum_score is None or percentage >= requirement.minimum_score:
                    matched_attempt = attempt
                    score_snapshot = max(score_snapshot or 0.0, percentage)
                    break
            if matched_attempt is None:
                threshold = requirement.minimum_score or certification.program.assessments[0].passing_score if certification.program.assessments else requirement.minimum_score
                if threshold is not None:
                    missing_requirements.append(
                        f"Assessment {requirement.assessment_id} requires a score of at least {threshold:.0f}%."
                    )
                else:
                    missing_requirements.append(f"Assessment {requirement.assessment_id} must be passed.")

    if program_progress and program_progress.status != "completed":
        missing_requirements.append("Program coursework is not yet complete.")

    existing = (
        db.query(StudentCertification)
        .filter(
            StudentCertification.student_id == student_id,
            StudentCertification.certification_id == certification.id,
        )
        .first()
    )

    if missing_requirements:
        return False, missing_requirements, existing

    if existing:
        return True, [], existing

    issued = StudentCertification(
        student_id=student_id,
        certification_id=certification.id,
        score_snapshot=score_snapshot,
    )
    db.add(issued)

    if certification.badge_id:
        existing_badge = (
            db.query(StudentBadge)
            .filter(
                StudentBadge.student_id == student_id,
                StudentBadge.badge_id == certification.badge_id,
            )
            .first()
        )
        if not existing_badge:
            db.add(StudentBadge(student_id=student_id, badge_id=certification.badge_id))

    db.commit()
    db.refresh(issued)
    return True, [], issued
