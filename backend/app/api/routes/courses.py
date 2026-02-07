import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_roles, require_org_roles
from app.enum import CourseVersionStatus
from app.models import Course, CourseVersion, Unit, Lesson, Activity, Media, StorybookPage, StudentCourse
from app.schemas import (
    CourseDto,
    CourseResponse,
    UnitResponse,
    LessonResponse,
    ActivityResponse,
    MediaResponse,
    StorybookPageResponse,
    StudentCourseWithDetails,
    CourseCreateRequest,
    CourseVersionCreateRequest,
    CourseVersionResponse,
    CourseSummaryResponse,
)
from app.enum import ProgressStatus

router = APIRouter()


@router.get("/courses", response_model=list[CourseSummaryResponse])
def get_courses(
    subject: str | None = Query(default=None),
    age_min: int | None = Query(default=None),
    age_max: int | None = Query(default=None),
    locale: str | None = Query(default=None),
    org_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    query = db.query(Course)
    if subject:
        query = query.filter(Course.subject == subject)
    if age_min is not None:
        query = query.filter(Course.age_band_min <= age_min)
    if age_max is not None:
        query = query.filter(Course.age_band_max >= age_max)
    if locale:
        query = query.filter(Course.default_locale == locale)
    if org_id:
        query = query.filter(Course.organization_id == org_id)
    return query.all()


@router.get("/student-courses", response_model=list[StudentCourseWithDetails])
def get_student_courses(
    db: Session = Depends(get_db), current_user=Depends(require_roles("student"))
):
    student_courses = (
        db.query(StudentCourse)
        .options(joinedload(StudentCourse.course).joinedload(Course.units))
        .filter(StudentCourse.student_id == current_user.id)
        .all()
    )

    results = []
    for sc in student_courses:
        active_progress = next(
            (up for up in sc.unit_progress if up.status == ProgressStatus.IN_PROGRESS),
            None,
        )
        unit_progress_id = (
            active_progress.id
            if active_progress
            else (sc.unit_progress[0].id if sc.unit_progress else None)
        )

        results.append(
            {
                "id": sc.id,
                "student_id": sc.student_id,
                "course_id": sc.course_id,
                "enrolled_on": sc.enrolled_on,
                "status": sc.status,
                "course": CourseResponse.from_orm(sc.course),
                "unit_progress_id": unit_progress_id,
            }
        )

    return results


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course_by_id(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course_data = CourseResponse(
        id=course.id,
        title=course.title,
        description=course.description,
        units=[
            UnitResponse(
                id=unit.id,
                title=unit.title,
                content=unit.content,
                order=unit.order,
                lessons=[
                    LessonResponse(
                        id=lesson.id,
                        title=lesson.title,
                        objective=lesson.objective,
                        order=lesson.order,
                        duration_minutes=lesson.duration_minutes,
                        activities=[
                            ActivityResponse(
                                id=activity.id,
                                type=activity.type,
                                title=activity.title,
                                content=activity.content,
                                order=activity.order,
                                media=(
                                    MediaResponse(
                                        id=activity.media.id,
                                        type=activity.media.type,
                                        title=activity.media.title,
                                        url=activity.media.url,
                                        description=activity.media.description,
                                    )
                                    if activity.media
                                    else None
                                ),
                                pages=[
                                    StorybookPageResponse.from_orm(p)
                                    for p in activity.storybook_pages
                                ],
                            )
                            for activity in lesson.activities
                        ],
                    )
                    for lesson in unit.lessons
                ],
            )
            for unit in course.units
        ],
    )

    return course_data


@router.post("/courses")
def create_course(
    course: CourseDto,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    new_course = Course(title=course.title, description=course.description)
    db.add(new_course)
    db.flush()

    for unit_data in course.units:
        new_unit = Unit(
            title=unit_data.title,
            content=unit_data.content,
            order=unit_data.order,
            course_id=new_course.id,
        )
        db.add(new_unit)
        db.flush()

        for lesson_data in unit_data.lessons:
            new_lesson = Lesson(
                title=lesson_data.title,
                objective=lesson_data.objective,
                order=lesson_data.order,
                duration_minutes=lesson_data.duration_minutes,
                unit_id=new_unit.id,
            )
            db.add(new_lesson)
            db.flush()

            for activity_data in lesson_data.activities:
                new_activity = Activity(
                    type=activity_data.type,
                    title=activity_data.title,
                    content=activity_data.content,
                    order=activity_data.order,
                    lesson_id=new_lesson.id,
                )
                db.add(new_activity)
                db.flush()

                if activity_data.type == "storybook":
                    for page in getattr(activity_data, "pages", []):
                        db.add(
                            StorybookPage(
                                activity_id=new_activity.id,
                                image_url=page.image_url,
                                order=page.order,
                            )
                        )

    db.commit()

    return {
        "message": "Course with units, lessons, and activities created successfully!"
    }


@router.post("/courses/authoring", response_model=CourseSummaryResponse)
def create_course_authoring(
    course: CourseCreateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_org_roles("content_admin", "org_admin")),
):
    new_course = Course(
        title=course.title,
        description=course.description,
        subject=course.subject,
        age_band_min=course.age_band_min,
        age_band_max=course.age_band_max,
        default_locale=course.default_locale,
        created_by=current_user.id,
        organization_id=membership.organization_id,
    )
    db.add(new_course)
    db.flush()

    version = CourseVersion(
        course_id=new_course.id,
        version_number=1,
        status=CourseVersionStatus.DRAFT,
        changelog="Initial draft",
    )
    db.add(version)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.post("/courses/{course_id}/versions", response_model=CourseVersionResponse)
def create_course_version(
    course_id: str,
    payload: CourseVersionCreateRequest,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("content_admin", "org_admin")),
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    latest_version = (
        db.query(CourseVersion)
        .filter(CourseVersion.course_id == course.id)
        .order_by(CourseVersion.version_number.desc())
        .first()
    )
    next_version = 1 if not latest_version else latest_version.version_number + 1
    new_version = CourseVersion(
        course_id=course.id,
        version_number=next_version,
        status=CourseVersionStatus.DRAFT,
        changelog=payload.changelog,
    )
    db.add(new_version)
    db.commit()
    db.refresh(new_version)
    return new_version


@router.put("/course-versions/{version_id}", response_model=CourseVersionResponse)
def update_course_version(
    version_id: str,
    payload: CourseVersionCreateRequest,
    db: Session = Depends(get_db),
    membership=Depends(require_org_roles("content_admin", "org_admin")),
):
    version = db.query(CourseVersion).filter(CourseVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Course version not found")
    if version.status != CourseVersionStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Only drafts can be edited")

    version.changelog = payload.changelog
    db.commit()
    db.refresh(version)
    return version


@router.post("/course-versions/{version_id}/publish", response_model=CourseVersionResponse)
def publish_course_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    membership=Depends(require_org_roles("content_admin", "org_admin")),
):
    version = db.query(CourseVersion).filter(CourseVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Course version not found")
    if version.status != CourseVersionStatus.DRAFT:
        raise HTTPException(status_code=400, detail="Version is not a draft")

    version.status = CourseVersionStatus.PUBLISHED
    version.published_at = datetime.utcnow()
    version.published_by = current_user.id
    db.commit()
    db.refresh(version)
    return version


@router.put("/courses/{course_id}")
def update_course(
    course_id: str,
    course_dto: CourseDto,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    try:
        cid = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    existing_course = db.query(Course).filter(Course.id == cid).first()
    if not existing_course:
        raise HTTPException(status_code=404, detail="Course not found")

    try:
        existing_course.title = course_dto.title
        existing_course.description = course_dto.description

        for unit in list(existing_course.units):
            db.delete(unit)
        db.flush()

        for unit_dto in course_dto.units:
            new_unit = Unit(
                title=unit_dto.title,
                content=unit_dto.content,
                order=unit_dto.order,
                course_id=existing_course.id,
            )
            db.add(new_unit)
            db.flush()

            for lesson_dto in unit_dto.lessons:
                new_lesson = Lesson(
                    title=lesson_dto.title,
                    objective=lesson_dto.objective,
                    order=lesson_dto.order,
                    duration_minutes=lesson_dto.duration_minutes,
                    unit_id=new_unit.id,
                )
                db.add(new_lesson)
                db.flush()

                for activity_dto in lesson_dto.activities:
                    new_activity = Activity(
                        title=activity_dto.title,
                        type=activity_dto.type,
                        content=activity_dto.content,
                        order=activity_dto.order,
                        lesson_id=new_lesson.id,
                    )
                    db.add(new_activity)
                    db.flush()

                    if activity_dto.type == "storybook":
                        for page in getattr(activity_dto, "pages", []):
                            db.add(
                                StorybookPage(
                                    activity_id=new_activity.id,
                                    image_url=page.image_url,
                                    order=page.order,
                                )
                            )

        db.commit()
        db.refresh(existing_course)
    except Exception as e:
        db.rollback()
        raise e

    return {"message": "Course updated successfully"}


@router.delete("/courses/{course_id}")
def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    try:
        cid = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")
    course = db.query(Course).filter(Course.id == cid).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}
