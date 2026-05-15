import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user, require_roles, require_org_roles
from app.enum import MembershipStatus
from app.enum import CourseVersionStatus
from app.api.routes.analytics import build_course_continuation_guidance
from app.lesson_governance import (
    evaluate_course_competency_evidence_integrity,
    evaluate_course_safe_publish,
    evaluate_course_publish_readiness,
    evaluate_lesson_readiness,
    resolve_review_fields,
    serialize_course,
)
from app.models import (
    Course,
    CourseVersion,
    Unit,
    Lesson,
    Assessment,
    Activity,
    StorybookPage,
    StudentCourse,
    StudentAssessmentAttempt,
    Source,
    OrganizationMembership,
)
from app.crud.progress import resolve_governed_progression
from app.schemas import (
    CourseDto,
    CourseResponse,
    StudentCourseWithDetails,
    CourseCreateRequest,
    CourseVersionCreateRequest,
    CourseVersionResponse,
    CourseCompetencyEvidenceIntegrityResponse,
    CompetencyEvidenceAffectedAssessmentResponse,
    CoursePublishReadinessResponse,
    CourseSafePublishValidationResponse,
    CourseSummaryResponse,
    PublishReadinessIssueResponse,
)
router = APIRouter()


def _can_view_course_publish_readiness(db: Session, current_user, course: Course) -> bool:
    if current_user.role in {"admin", "teacher"}:
        return True

    if course.organization_id is None:
        return False

    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == course.organization_id,
            OrganizationMembership.user_id == current_user.id,
        )
        .first()
    )
    if membership is None:
        return False

    membership_role = getattr(membership.role, "value", membership.role)
    membership_status = getattr(membership.status, "value", membership.status)
    return membership_role in {"content_admin", "org_admin"} and membership_status == MembershipStatus.ACTIVE.value


def _serialize_publish_readiness_issue(issue) -> PublishReadinessIssueResponse:
    return PublishReadinessIssueResponse(
        entity_type=issue.entity_type,
        entity_id=issue.entity_id,
        entity_title=issue.entity_title,
        code=issue.code,
        message=issue.message,
    )


def _serialize_affected_assessment(context) -> CompetencyEvidenceAffectedAssessmentResponse:
    return CompetencyEvidenceAffectedAssessmentResponse(
        assessment_id=context.assessment_id,
        assessment_title=context.assessment_title,
        competency_identifiers=list(context.competency_identifiers),
    )


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
    for sc in sorted(
        student_courses,
        key=lambda row: (
            row.enrolled_on or datetime.min,
            (row.course.title if row.course else ""),
            str(row.id),
        ),
    ):
        progression_state = resolve_governed_progression(db, sc.id)
        unit_progress_id = progression_state.get("unit_progress_id")

        results.append(
            {
                "id": sc.id,
                "student_id": sc.student_id,
                "course_id": sc.course_id,
                "enrolled_on": sc.enrolled_on,
                "status": sc.status,
                "course": serialize_course(sc.course, viewer_role=current_user.role),
                "unit_progress_id": unit_progress_id,
                "continuation_guidance": build_course_continuation_guidance(
                    db,
                    sc.course,
                    current_user.id,
                    educator_visible=False,
                ),
            }
        )

    return results


@router.get("/courses/{course_id}", response_model=CourseResponse)
def get_course_by_id(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles("admin", "teacher", "student")),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    course = db.query(Course).filter(Course.id == parsed_course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return serialize_course(course, viewer_role=current_user.role)


@router.get("/courses/{course_id}/publish-readiness", response_model=CoursePublishReadinessResponse)
def get_course_publish_readiness(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    course = (
        db.query(Course)
        .options(
            joinedload(Course.units).joinedload(Unit.lessons).joinedload(Lesson.sources),
        )
        .filter(Course.id == parsed_course_id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if not _can_view_course_publish_readiness(db, current_user, course):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    readiness = evaluate_course_publish_readiness(course)
    blocking_issues = [_serialize_publish_readiness_issue(issue) for issue in readiness.blocking_issues]
    warnings = [_serialize_publish_readiness_issue(issue) for issue in readiness.warnings]

    return CoursePublishReadinessResponse(
        course_id=course.id,
        course_title=course.title,
        is_ready=readiness.is_ready,
        blocking_issue_count=len(blocking_issues),
        warning_count=len(warnings),
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


@router.get("/courses/{course_id}/safe-publish-validation", response_model=CourseSafePublishValidationResponse)
def get_course_safe_publish_validation(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    course = (
        db.query(Course)
        .options(
            joinedload(Course.student_courses),
            joinedload(Course.assessments).joinedload(Assessment.attempts),
            joinedload(Course.assessments).joinedload(Assessment.events),
            joinedload(Course.units)
            .joinedload(Unit.lessons)
            .joinedload(Lesson.sources),
            joinedload(Course.units)
            .joinedload(Unit.lessons)
            .joinedload(Lesson.assessments)
            .joinedload(Assessment.attempts),
            joinedload(Course.units)
            .joinedload(Unit.lessons)
            .joinedload(Lesson.assessments)
            .joinedload(Assessment.events),
            joinedload(Course.units)
            .joinedload(Unit.assessments)
            .joinedload(Assessment.attempts),
            joinedload(Course.units)
            .joinedload(Unit.assessments)
            .joinedload(Assessment.events),
        )
        .filter(Course.id == parsed_course_id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if not _can_view_course_publish_readiness(db, current_user, course):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    validation = evaluate_course_safe_publish(course)
    blocking_issues = [_serialize_publish_readiness_issue(issue) for issue in validation.blocking_issues]
    warnings = [_serialize_publish_readiness_issue(issue) for issue in validation.warnings]

    return CourseSafePublishValidationResponse(
        course_id=course.id,
        course_title=course.title,
        is_safe=validation.is_safe,
        blocking_issue_count=len(blocking_issues),
        warning_count=len(warnings),
        blocking_issues=blocking_issues,
        warnings=warnings,
    )


@router.get("/courses/{course_id}/competency-evidence-integrity", response_model=CourseCompetencyEvidenceIntegrityResponse)
def get_course_competency_evidence_integrity(
    course_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        parsed_course_id = uuid.UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid course id")

    course = (
        db.query(Course)
        .options(
            joinedload(Course.assessments)
            .joinedload(Assessment.attempts)
            .joinedload(StudentAssessmentAttempt.events),
            joinedload(Course.assessments).joinedload(Assessment.competency_alignments),
            joinedload(Course.units)
            .joinedload(Unit.assessments)
            .joinedload(Assessment.attempts)
            .joinedload(StudentAssessmentAttempt.events),
            joinedload(Course.units)
            .joinedload(Unit.assessments)
            .joinedload(Assessment.competency_alignments),
            joinedload(Course.units)
            .joinedload(Unit.lessons)
            .joinedload(Lesson.assessments)
            .joinedload(Assessment.attempts)
            .joinedload(StudentAssessmentAttempt.events),
            joinedload(Course.units)
            .joinedload(Unit.lessons)
            .joinedload(Lesson.assessments)
            .joinedload(Assessment.competency_alignments),
        )
        .filter(Course.id == parsed_course_id)
        .first()
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if not _can_view_course_publish_readiness(db, current_user, course):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource.",
        )

    integrity = evaluate_course_competency_evidence_integrity(course)
    blocking_issues = [_serialize_publish_readiness_issue(issue) for issue in integrity.blocking_issues]
    warnings = [_serialize_publish_readiness_issue(issue) for issue in integrity.warnings]
    affected_assessments = [_serialize_affected_assessment(context) for context in integrity.affected_assessments]

    return CourseCompetencyEvidenceIntegrityResponse(
        course_id=course.id,
        course_title=course.title,
        is_valid=integrity.is_valid,
        is_explainable=integrity.is_explainable,
        blocking_issue_count=len(blocking_issues),
        warning_count=len(warnings),
        blocking_issues=blocking_issues,
        warnings=warnings,
        affected_assessments=affected_assessments,
        affected_competency_identifiers=list(integrity.affected_competency_identifiers),
    )


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
    new_course.learning_objectives = course.learning_objectives
    new_course.skill_tags = course.skill_tags
    new_course.standards_metadata = course.standards_metadata
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
            readiness = evaluate_lesson_readiness(
                title=lesson_data.title,
                objective=lesson_data.objective,
                learning_objectives=lesson_data.learning_objectives,
                key_concepts=lesson_data.key_concepts,
                hook=lesson_data.hook,
                content=lesson_data.content,
                guided_practice=lesson_data.guided_practice,
                independent_practice=lesson_data.independent_practice,
                assessment=lesson_data.assessment,
                sources=lesson_data.sources,
            )
            review_status, reviewed_by = resolve_review_fields(
                db=db,
                current_user=current_user,
                requested_status=lesson_data.review_status,
                unit_id=new_unit.id,
                readiness=readiness,
            )
            new_lesson = Lesson(
                title=lesson_data.title,
                objective=lesson_data.objective,
                learning_objectives=lesson_data.learning_objectives,
                key_concepts=lesson_data.key_concepts,
                teacher_notes=lesson_data.teacher_notes,
                discussion_questions=lesson_data.discussion_questions,
                hook=lesson_data.hook,
                content=lesson_data.content,
                guided_practice=lesson_data.guided_practice,
                independent_practice=lesson_data.independent_practice,
                assessment=lesson_data.assessment,
                review_status=review_status,
                reviewed_by=reviewed_by,
                skill_tags=lesson_data.skill_tags,
                standards_metadata=lesson_data.standards_metadata,
                order=lesson_data.order,
                duration_minutes=lesson_data.duration_minutes,
                unit_id=new_unit.id,
            )
            db.add(new_lesson)
            db.flush()

            for source_data in lesson_data.sources:
                db.add(
                    Source(
                        lesson_id=new_lesson.id,
                        citation=source_data.citation,
                        url=source_data.url,
                    )
                )

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
        learning_objectives=course.learning_objectives,
        skill_tags=course.skill_tags,
        standards_metadata=course.standards_metadata,
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
        existing_course.learning_objectives = course_dto.learning_objectives
        existing_course.skill_tags = course_dto.skill_tags
        existing_course.standards_metadata = course_dto.standards_metadata

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
                readiness = evaluate_lesson_readiness(
                    title=lesson_dto.title,
                    objective=lesson_dto.objective,
                    learning_objectives=lesson_dto.learning_objectives,
                    key_concepts=lesson_dto.key_concepts,
                    hook=lesson_dto.hook,
                    content=lesson_dto.content,
                    guided_practice=lesson_dto.guided_practice,
                    independent_practice=lesson_dto.independent_practice,
                    assessment=lesson_dto.assessment,
                    sources=lesson_dto.sources,
                )
                review_status, reviewed_by = resolve_review_fields(
                    db=db,
                    current_user=current_user,
                    requested_status=lesson_dto.review_status,
                    unit_id=new_unit.id,
                    readiness=readiness,
                )
                new_lesson = Lesson(
                title=lesson_dto.title,
                objective=lesson_dto.objective,
                learning_objectives=lesson_dto.learning_objectives,
                key_concepts=lesson_dto.key_concepts,
                teacher_notes=lesson_dto.teacher_notes,
                discussion_questions=lesson_dto.discussion_questions,
                hook=lesson_dto.hook,
                content=lesson_dto.content,
                guided_practice=lesson_dto.guided_practice,
                independent_practice=lesson_dto.independent_practice,
                assessment=lesson_dto.assessment,
                review_status=review_status,
                reviewed_by=reviewed_by,
                skill_tags=lesson_dto.skill_tags,
                standards_metadata=lesson_dto.standards_metadata,
                order=lesson_dto.order,
                duration_minutes=lesson_dto.duration_minutes,
                unit_id=new_unit.id,
                )
                db.add(new_lesson)
                db.flush()

                for source_data in lesson_dto.sources:
                    db.add(
                        Source(
                            lesson_id=new_lesson.id,
                            citation=source_data.citation,
                            url=source_data.url,
                        )
                    )

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
