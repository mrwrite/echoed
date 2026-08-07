from __future__ import annotations

from dataclasses import asdict, dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.enum import MembershipStatus
from app.models import Course, OrganizationMembership, User


@dataclass(frozen=True)
class CourseAuthoringCapabilities:
    can_create: bool = False
    can_view_draft: bool = False
    can_edit: bool = False
    can_duplicate: bool = False
    can_preview: bool = False
    can_submit_review: bool = False
    can_review: bool = False
    can_publish: bool = False

    def model_payload(self) -> dict[str, bool]:
        return asdict(self)


def _enum_value(value) -> str | None:
    return getattr(value, "value", value)


def _active_membership(
    db: Session,
    user_id: UUID,
    organization_id: UUID | None,
) -> OrganizationMembership | None:
    if organization_id is None:
        return None
    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == organization_id,
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.status == MembershipStatus.ACTIVE,
        )
        .first()
    )
    return membership


def resolve_course_authoring_capabilities(
    db: Session,
    current_user: User,
    *,
    active_organization_id: UUID | None = None,
    course: Course | None = None,
) -> CourseAuthoringCapabilities:
    """Resolve bounded authoring actions; every mutation must re-check these.

    Platform administrators retain broad authority for migration compatibility.
    Organization roles are evaluated against the course organization for item
    actions and against the active organization for collection actions.
    """

    platform_role = _enum_value(current_user.role)
    if platform_role in {"admin", "super_admin"}:
        return CourseAuthoringCapabilities(
            can_create=True,
            can_view_draft=True,
            can_edit=True,
            can_duplicate=True,
            can_preview=True,
            can_submit_review=True,
            can_review=True,
            can_publish=True,
        )

    organization_id = course.organization_id if course is not None else active_organization_id
    authoring_state = (course.revision_metadata or {}).get("authoring_state", "draft") if course else "draft"
    author_editable = authoring_state in {"draft", "changes_requested", "published"}
    membership = _active_membership(db, current_user.id, organization_id)
    membership_role = _enum_value(membership.role) if membership else None

    if membership_role in {"org_admin", "super_admin"}:
        independent_reviewer = course is None or course.created_by != current_user.id
        return CourseAuthoringCapabilities(
            can_create=True,
            can_view_draft=True,
            can_edit=author_editable,
            can_duplicate=True,
            can_preview=True,
            can_submit_review=author_editable,
            can_review=independent_reviewer,
            can_publish=independent_reviewer,
        )

    if membership_role == "content_admin":
        return CourseAuthoringCapabilities(
            can_create=True,
            can_view_draft=True,
            can_edit=author_editable,
            can_duplicate=True,
            can_preview=True,
            can_submit_review=author_editable,
        )

    if membership_role in {"teacher", "instructor"}:
        owns_draft = course is not None and course.created_by == current_user.id
        is_editable = owns_draft and author_editable
        return CourseAuthoringCapabilities(
            can_create=False,
            can_view_draft=is_editable,
            can_edit=is_editable,
            can_duplicate=True,
            can_preview=is_editable,
            can_submit_review=is_editable,
        )

    # Preserve the legacy unscoped teacher authoring contract during migration.
    if platform_role in {"teacher", "instructor"} and (
        active_organization_id is None and (course is None or course.organization_id is None)
    ):
        owns_or_legacy = course is None or course.created_by in {None, current_user.id}
        return CourseAuthoringCapabilities(
            can_create=course is None,
            can_view_draft=owns_or_legacy,
            can_edit=owns_or_legacy,
            can_duplicate=True,
            can_preview=owns_or_legacy,
            can_submit_review=owns_or_legacy,
        )

    return CourseAuthoringCapabilities()


def require_course_authoring_capability(
    capabilities: CourseAuthoringCapabilities,
    action: str,
) -> None:
    attribute = f"can_{action}"
    if not hasattr(capabilities, attribute) or not getattr(capabilities, attribute):
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this course-authoring action.",
        )
