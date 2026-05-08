from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from uuid import UUID

from app.crud.badges import BADGE_RULES, calculate_streak_days, get_or_create_badge
from app.database import get_db
from app.deps import require_roles, require_org_roles
from app.enum import ProgressStatus
from app.models import (
    Assessment,
    StudentAssessmentAttempt,
    Course,
    Lesson,
    SegmentProgress,
    StudentBadge,
    StudentCourse,
    StudentUnitProgress,
    Unit,
    User,
    Enrollment,
)
from app.schemas import (
    AssessmentEvidenceSummaryResponse,
    AssessmentReportingSummaryResponse,
    MasteryObjectiveSummaryResponse,
    MasterySummaryResponse,
    ReportingProgressSnapshotResponse,
)

router = APIRouter()


def _latest_attempt_for_assessment(assessment: Assessment, student_id):
    attempts = [
        attempt
        for attempt in assessment.attempts
        if attempt.student_id == student_id
    ]
    if not attempts:
        return None
    return max(attempts, key=lambda attempt: (attempt.submitted_at, str(attempt.id)))


def _latest_event_metadata(attempt: StudentAssessmentAttempt) -> dict:
    scored_events = [event for event in attempt.events if event.event_type == "attempt_scored"]
    latest_event = scored_events[-1] if scored_events else (attempt.events[-1] if attempt.events else None)
    return dict(latest_event.event_metadata or {}) if latest_event else {}


def _build_mastery_summary(
    assessments: list[Assessment],
    student_id,
    *,
    lesson_id=None,
    unit_id=None,
    course_id=None,
    program_id=None,
) -> MasterySummaryResponse:
    totals: dict[str, dict[str, object]] = {}

    for assessment in assessments:
        if not assessment.competency_alignments:
            continue
        latest_attempt = _latest_attempt_for_assessment(assessment, student_id)
        if latest_attempt is None:
            continue
        evidence_weight = 1.0 if latest_attempt.passed else 0.0
        for alignment in assessment.competency_alignments:
            bucket = totals.setdefault(
                alignment.objective_key,
                {
                    "objective_key": alignment.objective_key,
                    "objective_title": alignment.objective_title,
                    "objective_type": alignment.objective_type,
                    "mastery_threshold": alignment.mastery_threshold,
                    "total_weight": 0.0,
                    "passed_weight": 0.0,
                    "assessments_considered": set(),
                    "attempts_considered": 0,
                    "latest_attempt_at": None,
                },
            )
            bucket["objective_title"] = bucket["objective_title"] or alignment.objective_title
            bucket["objective_type"] = alignment.objective_type
            bucket["mastery_threshold"] = max(float(bucket["mastery_threshold"]), alignment.mastery_threshold)
            bucket["total_weight"] = float(bucket["total_weight"]) + alignment.weight
            bucket["passed_weight"] = float(bucket["passed_weight"]) + (alignment.weight * evidence_weight)
            bucket["assessments_considered"].add(assessment.id)
            bucket["attempts_considered"] = int(bucket["attempts_considered"]) + 1
            latest_attempt_at = bucket["latest_attempt_at"]
            if latest_attempt_at is None or latest_attempt.submitted_at > latest_attempt_at:
                bucket["latest_attempt_at"] = latest_attempt.submitted_at

    objective_rows = []
    for bucket in sorted(totals.values(), key=lambda item: item["objective_key"]):
        total_weight = float(bucket["total_weight"])
        passed_weight = float(bucket["passed_weight"])
        mastery_percentage = round((passed_weight / total_weight) * 100, 1) if total_weight else 0.0
        mastery_threshold = float(bucket["mastery_threshold"])
        objective_rows.append(
            MasteryObjectiveSummaryResponse(
                objective_key=bucket["objective_key"],
                objective_title=bucket["objective_title"],
                objective_type=bucket["objective_type"],
                mastery_threshold=mastery_threshold,
                total_weight=total_weight,
                passed_weight=passed_weight,
                mastery_percentage=mastery_percentage,
                mastered=mastery_percentage >= mastery_threshold,
                assessments_considered=len(bucket["assessments_considered"]),
                attempts_considered=int(bucket["attempts_considered"]),
                latest_attempt_at=bucket["latest_attempt_at"],
            )
        )

    return MasterySummaryResponse(
        student_id=student_id,
        lesson_id=lesson_id,
        unit_id=unit_id,
        course_id=course_id,
        program_id=program_id,
        objectives=objective_rows,
    )


def _build_progress_snapshot(db: Session, student_id: UUID) -> ReportingProgressSnapshotResponse:
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
    last_activity_at = (
        db.query(StudentCourse.last_activity_at)
        .filter(StudentCourse.student_id == student_id)
        .order_by(StudentCourse.last_activity_at.desc())
        .first()
    )
    return ReportingProgressSnapshotResponse(
        lessons_completed=lessons_completed,
        units_completed=units_completed,
        courses_completed=courses_completed,
        last_activity_at=last_activity_at[0] if last_activity_at else None,
    )


def _build_assessment_evidence_summary(
    assessments: list[Assessment],
    student_id: UUID,
) -> list[AssessmentEvidenceSummaryResponse]:
    rows: list[AssessmentEvidenceSummaryResponse] = []
    for assessment in assessments:
        if assessment.assessment_state != "published" or assessment.availability_state != "available":
            continue
        attempts = sorted(
            [attempt for attempt in assessment.attempts if attempt.student_id == student_id],
            key=lambda attempt: (attempt.submitted_at, str(attempt.id)),
        )
        if not attempts:
            continue

        latest_attempt = attempts[-1]
        latest_event_metadata = _latest_event_metadata(latest_attempt)
        submitted_event_count = sum(
            1 for attempt in attempts for event in attempt.events if event.event_type == "attempt_submitted"
        )
        scored_event_count = sum(
            1 for attempt in attempts for event in attempt.events if event.event_type == "attempt_scored"
        )
        rows.append(
            AssessmentEvidenceSummaryResponse(
                assessment_id=assessment.id,
                assessment_title=assessment.title,
                assessment_scope=assessment.assessment_scope or (
                    "unit"
                    if assessment.unit_id
                    else "lesson"
                    if assessment.lesson_id
                    else "course"
                    if assessment.course_id
                    else "program"
                ),
                assessment_state=assessment.assessment_state or "published",
                availability_state=assessment.availability_state or "available",
                question_count=len(assessment.questions or []),
                attempt_count=len(attempts),
                passed_attempt_count=sum(1 for attempt in attempts if attempt.passed),
                latest_attempt_id=latest_attempt.id,
                latest_attempt_at=latest_attempt.submitted_at,
                latest_score=latest_attempt.score,
                latest_max_score=latest_attempt.max_score,
                latest_percentage=(latest_attempt.score / latest_attempt.max_score * 100) if latest_attempt.max_score else 0.0,
                latest_passed=latest_attempt.passed,
                submitted_event_count=submitted_event_count,
                scored_event_count=scored_event_count,
                latest_event_metadata=latest_event_metadata,
            )
        )
    rows.sort(key=lambda row: (row.latest_attempt_at or row.assessment_title, row.assessment_title))
    return rows


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


@router.get("/sections/{section_id}/analytics/summary")
def get_section_summary(
    section_id: str,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("teacher", "org_admin", "instructor")),
):
    total_enrolled = (
        db.query(Enrollment)
        .filter(Enrollment.section_id == section_id)
        .count()
    )
    completed_lessons = (
        db.query(SegmentProgress)
        .filter(
            SegmentProgress.section_id == section_id,
            SegmentProgress.status == ProgressStatus.COMPLETED,
        )
        .count()
    )
    completed_units = (
        db.query(StudentUnitProgress)
        .filter(
            StudentUnitProgress.section_id == section_id,
            StudentUnitProgress.status == ProgressStatus.COMPLETED,
        )
        .count()
    )
    return {
        "section_id": section_id,
        "totals": {
            "enrolled": total_enrolled,
            "lessons_completed": completed_lessons,
            "units_completed": completed_units,
        },
    }


@router.get("/analytics/mastery-summary", response_model=MasterySummaryResponse)
def get_mastery_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
    student_id: UUID | None = None,
    lesson_id: UUID | None = None,
    unit_id: UUID | None = None,
    course_id: UUID | None = None,
    program_id: UUID | None = None,
):
    scope_count = sum(value is not None for value in (lesson_id, unit_id, course_id, program_id))
    if scope_count != 1:
        raise HTTPException(status_code=400, detail="Mastery summary must target exactly one of lesson, unit, course, or program.")

    target_student_id = current_user.id
    if student_id is not None:
        if current_user.role not in {"admin", "teacher"}:
            raise HTTPException(status_code=403, detail="Only educators can request mastery summaries for other students.")
        target_student_id = student_id

    query = db.query(Assessment).options(
        selectinload(Assessment.competency_alignments),
        selectinload(Assessment.attempts),
    )
    if lesson_id is not None:
        query = query.filter(Assessment.lesson_id == lesson_id)
    if unit_id is not None:
        query = query.filter(Assessment.unit_id == unit_id)
    if course_id is not None:
        query = query.filter(Assessment.course_id == course_id)
    if program_id is not None:
        query = query.filter(Assessment.program_id == program_id)

    assessments = query.all()
    return _build_mastery_summary(
        assessments,
        target_student_id,
        lesson_id=lesson_id,
        unit_id=unit_id,
        course_id=course_id,
        program_id=program_id,
    )


@router.get("/analytics/reporting-summary", response_model=AssessmentReportingSummaryResponse)
def get_reporting_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
    student_id: UUID | None = None,
    lesson_id: UUID | None = None,
    unit_id: UUID | None = None,
    course_id: UUID | None = None,
    program_id: UUID | None = None,
):
    scope_count = sum(value is not None for value in (lesson_id, unit_id, course_id, program_id))
    if scope_count != 1:
        raise HTTPException(status_code=400, detail="Reporting summary must target exactly one of lesson, unit, course, or program.")

    target_student_id = current_user.id
    if student_id is not None:
        if current_user.role not in {"admin", "teacher"}:
            raise HTTPException(status_code=403, detail="Only educators can request reporting summaries for other students.")
        target_student_id = student_id

    query = db.query(Assessment).options(
        selectinload(Assessment.questions),
        selectinload(Assessment.attempts).selectinload(StudentAssessmentAttempt.events),
        selectinload(Assessment.competency_alignments),
    )
    if lesson_id is not None:
        query = query.filter(Assessment.lesson_id == lesson_id)
    if unit_id is not None:
        query = query.filter(Assessment.unit_id == unit_id)
    if course_id is not None:
        query = query.filter(Assessment.course_id == course_id)
    if program_id is not None:
        query = query.filter(Assessment.program_id == program_id)

    assessments = query.all()
    return AssessmentReportingSummaryResponse(
        student_id=target_student_id,
        lesson_id=lesson_id,
        unit_id=unit_id,
        course_id=course_id,
        program_id=program_id,
        progress=_build_progress_snapshot(db, target_student_id),
        assessment_evidence=_build_assessment_evidence_summary(assessments, target_student_id),
        mastery_summary=_build_mastery_summary(
            assessments,
            target_student_id,
            lesson_id=lesson_id,
            unit_id=unit_id,
            course_id=course_id,
            program_id=program_id,
        ),
    )
