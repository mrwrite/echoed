from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_roles
from app.crud.certifications import get_program_completion, sync_student_program_progress
from app.models import Course, Program, ProgramCourse, StudentCourse, StudentProgramProgress, User
from app.schemas import (
    CourseSummaryResponse,
    ProgramCreateRequest,
    ProgramCourseResponse,
    ProgramResponse,
    StudentProgramProgressResponse,
)

router = APIRouter()


def _serialize_course_summary(course: Course) -> CourseSummaryResponse:
    return CourseSummaryResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        subject=course.subject,
        age_band_min=course.age_band_min,
        age_band_max=course.age_band_max,
        default_locale=course.default_locale,
        learning_objectives=course.learning_objectives,
        skill_tags=course.skill_tags or [],
        standards_metadata=course.standards_metadata or {},
        created_by=course.created_by,
        organization_id=course.organization_id,
    )


def _serialize_program(program: Program, db: Session, student_id) -> ProgramResponse:
    progress = (
        db.query(StudentProgramProgress)
        .filter(
            StudentProgramProgress.program_id == program.id,
            StudentProgramProgress.student_id == student_id,
        )
        .first()
    )
    progress = sync_student_program_progress(
        db,
        program=program,
        student_id=student_id,
        progress=progress,
    )
    completed_courses, total_courses, percentage, _ = get_program_completion(db, program, student_id)

    return ProgramResponse(
        id=program.id,
        title=program.title,
        description=program.description,
        organization_id=program.organization_id,
        created_by=program.created_by,
        created_at=program.created_at,
        updated_at=program.updated_at,
        courses=[
                ProgramCourseResponse(
                    id=link.id,
                    course_id=link.course_id,
                    order=link.order,
                    is_required=link.is_required,
                    course=_serialize_course_summary(link.course),
                )
            for link in sorted(program.courses, key=lambda course_link: course_link.order)
        ],
        progress=(
            StudentProgramProgressResponse(
                id=progress.id,
                student_id=progress.student_id,
                program_id=progress.program_id,
                status=progress.status,
                enrolled_on=progress.enrolled_on,
                last_activity_at=progress.last_activity_at,
                completed_at=progress.completed_at,
                completion_percentage=percentage,
                completed_courses=completed_courses,
                total_courses=total_courses,
            )
            if progress
            else None
        ),
    )


@router.get("/programs", response_model=list[ProgramResponse])
def list_programs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    programs = (
        db.query(Program)
        .options(joinedload(Program.courses).joinedload(ProgramCourse.course))
        .order_by(Program.created_at.desc())
        .all()
    )
    return [_serialize_program(program, db, current_user.id) for program in programs]


@router.get("/programs/{program_id}", response_model=ProgramResponse)
def get_program(
    program_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    program = (
        db.query(Program)
        .options(joinedload(Program.courses).joinedload(ProgramCourse.course))
        .filter(Program.id == program_id)
        .first()
    )
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    return _serialize_program(program, db, current_user.id)


@router.post("/programs", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    payload: ProgramCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "teacher")),
):
    if not payload.course_links:
        raise HTTPException(status_code=400, detail="Programs must include at least one course.")

    course_ids = [link.course_id for link in payload.course_links]
    courses = db.query(Course).filter(Course.id.in_(course_ids)).all()
    if len(courses) != len(set(course_ids)):
        raise HTTPException(status_code=404, detail="One or more courses were not found.")

    program = Program(
        title=payload.title,
        description=payload.description,
        created_by=current_user.id,
    )
    db.add(program)
    db.flush()

    for link in payload.course_links:
        db.add(
            ProgramCourse(
                program_id=program.id,
                course_id=link.course_id,
                order=link.order,
                is_required=link.is_required,
            )
        )

    db.commit()
    db.refresh(program)

    program = (
        db.query(Program)
        .options(joinedload(Program.courses).joinedload(ProgramCourse.course))
        .filter(Program.id == program.id)
        .first()
    )
    return _serialize_program(program, db, current_user.id)


@router.post("/programs/{program_id}/enroll", response_model=StudentProgramProgressResponse)
def enroll_in_program(
    program_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student")),
):
    program = (
        db.query(Program)
        .options(joinedload(Program.courses))
        .filter(Program.id == program_id)
        .first()
    )
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    progress = (
        db.query(StudentProgramProgress)
        .filter(
            StudentProgramProgress.program_id == program.id,
            StudentProgramProgress.student_id == current_user.id,
        )
        .first()
    )
    if not progress:
        progress = StudentProgramProgress(
            student_id=current_user.id,
            program_id=program.id,
        )
        db.add(progress)
        db.flush()

    for link in program.courses:
        student_course = (
            db.query(StudentCourse)
            .filter(
                StudentCourse.student_id == current_user.id,
                StudentCourse.course_id == link.course_id,
            )
            .first()
        )
        if not student_course:
            db.add(
                StudentCourse(
                    student_id=current_user.id,
                    course_id=link.course_id,
                    enrolled_on=datetime.utcnow(),
                    status="active",
                )
            )

    db.commit()
    db.refresh(progress)
    progress = sync_student_program_progress(
        db,
        program=program,
        student_id=current_user.id,
        progress=progress,
    )
    completed_courses, total_courses, percentage, _ = get_program_completion(db, program, current_user.id)
    return StudentProgramProgressResponse(
        id=progress.id,
        student_id=progress.student_id,
        program_id=progress.program_id,
        status=progress.status,
        enrolled_on=progress.enrolled_on,
        last_activity_at=progress.last_activity_at,
        completed_at=progress.completed_at,
        completion_percentage=percentage,
        completed_courses=completed_courses,
        total_courses=total_courses,
    )
