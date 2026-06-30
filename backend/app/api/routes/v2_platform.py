from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.deps import get_current_user
from app.enum import MembershipStatus
from app.lesson_governance import evaluate_course_publish_readiness
from app.models import (
    AccessGrant,
    Artifact,
    GenerationRun,
    KnowledgeSource,
    OrganizationMembership,
    Product,
    Course,
    Lesson,
    Program,
    Project,
    Source,
    StudentCourse,
    Unit,
    User,
    Workspace,
)
from app.schemas import (
    AccessGrantCreateRequest,
    AccessGrantResponse,
    ArtifactCreateRequest,
    ArtifactResponse,
    GenerationRunResponse,
    KnowledgeSourceCreateRequest,
    KnowledgeSourceResponse,
    ProductCreateRequest,
    ProductResponse,
    ProjectCreateRequest,
    ProjectResponse,
    LearnerProductResponse,
    ReviewCenterActivityResponse,
    ReviewCenterItemResponse,
    ReviewCenterResponse,
    ReviewStatusUpdateRequest,
    WorkspaceResponse,
)

router = APIRouter()

CREATOR_ROLES = {"admin", "teacher", "content_admin", "org_admin", "instructor", "super_admin"}
SUPPORTED_PRODUCT_TYPES = {
    "course",
    "learning_path",
    "documentation_pack",
    "onboarding_track",
    "implementation_playbook",
    "knowledge_portal",
    "certification",
    "resource_pack",
}
SUPPORTED_KNOWLEDGE_SOURCE_TYPES = {
    "repository",
    "document",
    "pdf",
    "url",
    "transcript",
    "upload",
    "manual_note",
    "lesson_source",
}
SUPPORTED_ARTIFACT_TYPES = {
    "outline",
    "documentation",
    "guide",
    "checklist",
    "source_map",
    "export_bundle",
    "assessment_seed",
    "lesson_draft",
}
SUPPORTED_ARTIFACT_REVIEW_STATUSES = {"draft", "in_review", "approved", "rejected", "needs_changes"}
SUPPORTED_PRODUCT_REVIEW_STATUSES = {"draft", "in_review", "approved", "published", "archived"}
LEARNER_VISIBLE_PRODUCT_STATUSES = {"approved", "published"}
SUPPORTED_ACCESS_GRANT_TYPES = {"manual", "enrollment", "membership", "purchase", "organization", "invitation"}
SUPPORTED_ACCESS_GRANT_STATUSES = {"active", "pending", "expired", "revoked"}


def _visible_workspace_ids(db: Session, current_user: User) -> list[UUID] | None:
    if current_user.role in {"admin", "super_admin"}:
        return None

    active_status = MembershipStatus.ACTIVE.value
    memberships = (
        db.query(OrganizationMembership)
        .filter(OrganizationMembership.user_id == current_user.id)
        .all()
    )
    organization_ids = [
        membership.organization_id
        for membership in memberships
        if getattr(membership.status, "value", membership.status) == active_status
    ]
    if not organization_ids:
        return []

    return [
        workspace.id
        for workspace in db.query(Workspace.id)
        .filter(Workspace.organization_id.in_(organization_ids))
        .all()
    ]


def _scope_workspace_query(query, db: Session, current_user: User):
    visible_workspace_ids = _visible_workspace_ids(db, current_user)
    if visible_workspace_ids is None:
        return query
    if not visible_workspace_ids:
        return query.filter(False)
    return query.filter(Workspace.id.in_(visible_workspace_ids))


def _scope_platform_query(query, model, db: Session, current_user: User):
    visible_workspace_ids = _visible_workspace_ids(db, current_user)
    if visible_workspace_ids is None:
        return query
    if not visible_workspace_ids:
        return query.filter(False)
    return query.filter(model.workspace_id.in_(visible_workspace_ids))


def _visible_organization_ids(db: Session, current_user: User) -> list[UUID] | None:
    if current_user.role in {"admin", "teacher", "super_admin"}:
        return None

    visible_workspace_ids = _visible_workspace_ids(db, current_user)
    if visible_workspace_ids is None:
        return None
    if not visible_workspace_ids:
        return []

    return [
        organization_id
        for (organization_id,) in db.query(Workspace.organization_id)
        .filter(Workspace.id.in_(visible_workspace_ids), Workspace.organization_id.isnot(None))
        .all()
    ]


def _can_manage_workspace(db: Session, current_user: User, workspace: Workspace) -> bool:
    if current_user.role in {"admin", "teacher", "super_admin"}:
        return True
    if current_user.role in {"content_admin", "org_admin", "instructor"}:
        return True
    if workspace.organization_id is None:
        return False

    membership = (
        db.query(OrganizationMembership)
        .filter(
            OrganizationMembership.organization_id == workspace.organization_id,
            OrganizationMembership.user_id == current_user.id,
        )
        .first()
    )
    if not membership:
        return False
    membership_role = getattr(membership.role, "value", membership.role)
    membership_status = getattr(membership.status, "value", membership.status)
    return (
        membership_role in {"content_admin", "org_admin", "teacher", "instructor"}
        and membership_status == MembershipStatus.ACTIVE.value
    )


def _require_manage_workspace(db: Session, current_user: User, workspace_id: UUID) -> Workspace:
    workspace = _scope_workspace_query(
        db.query(Workspace).filter(Workspace.id == workspace_id),
        db,
        current_user,
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    if current_user.role not in CREATOR_ROLES or not _can_manage_workspace(db, current_user, workspace):
        raise HTTPException(status_code=403, detail="You do not have permission to manage this workspace.")
    return workspace


def _get_visible_project(db: Session, current_user: User, project_id: UUID) -> Project:
    project = _scope_platform_query(
        db.query(Project).filter(Project.id == project_id),
        Project,
        db,
        current_user,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def _require_project_in_workspace(
    db: Session,
    current_user: User,
    workspace_id: UUID,
    project_id: UUID,
) -> Project:
    _require_manage_workspace(db, current_user, workspace_id)
    project = (
        db.query(Project)
        .filter(Project.id == project_id, Project.workspace_id == workspace_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=400, detail="Project does not belong to the selected workspace.")
    return project


def _get_visible_artifact(db: Session, current_user: User, artifact_id: UUID) -> Artifact:
    artifact = _scope_platform_query(
        db.query(Artifact).filter(Artifact.id == artifact_id),
        Artifact,
        db,
        current_user,
    ).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


def _get_visible_product(db: Session, current_user: User, product_id: UUID) -> Product:
    product = _scope_platform_query(
        db.query(Product).filter(Product.id == product_id),
        Product,
        db,
        current_user,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def _require_manage_platform_record(db: Session, current_user: User, workspace_id: UUID) -> Workspace:
    return _require_manage_workspace(db, current_user, workspace_id)


def _scope_access_grant_query(query, db: Session, current_user: User):
    visible_workspace_ids = _visible_workspace_ids(db, current_user)
    if visible_workspace_ids is None:
        return query
    if not visible_workspace_ids:
        return query.filter(False)
    return query.filter(AccessGrant.workspace_id.in_(visible_workspace_ids))


def _grant_is_active(grant: AccessGrant, now: datetime | None = None) -> bool:
    now = now or datetime.utcnow()
    if grant.status != "active" or grant.revoked_at is not None:
        return False
    if grant.starts_at is not None and grant.starts_at > now:
        return False
    if grant.expires_at is not None and grant.expires_at <= now:
        return False
    return True


def _source_coverage_for_artifact(artifact: Artifact) -> str:
    if artifact.knowledge_source_id:
        return "Linked knowledge source"
    if artifact.generation_run_id:
        return "Generation run linked; source coverage pending"
    return "No source link"


def _artifact_required_decision(artifact: Artifact) -> str:
    if artifact.status in {"approved", "rejected"}:
        return "No decision required"
    if artifact.status == "needs_changes":
        return "Revise or reject artifact wrapper"
    return "Review artifact wrapper"


def _product_required_decision(product: Product) -> str:
    if product.status == "published":
        return "Monitor existing runtime governance"
    if product.status == "archived":
        return "No decision required"
    if product.status == "approved":
        return "Confirm existing governance before learner delivery"
    return "Review product wrapper"


def _review_item_for_artifact(artifact: Artifact) -> ReviewCenterItemResponse:
    return ReviewCenterItemResponse(
        id=artifact.id,
        item_type="artifact",
        title=artifact.title,
        status=artifact.status,
        review_state=artifact.review_state,
        owner=None,
        source_coverage=_source_coverage_for_artifact(artifact),
        readiness="Wrapper review only; not learner-deliverable",
        required_decision=_artifact_required_decision(artifact),
        blocked=artifact.status in {"rejected", "needs_changes"},
        detail_route=f"/workspace/artifacts/{artifact.id}",
        governance_route=None,
        updated_at=artifact.updated_at,
    )


def _review_item_for_product(product: Product) -> ReviewCenterItemResponse:
    linked_runtime = "Course-backed runtime link" if product.course_id else "No runtime course link"
    return ReviewCenterItemResponse(
        id=product.id,
        item_type="product",
        title=product.title,
        status=product.status,
        review_state=product.review_state,
        owner=None,
        source_coverage=linked_runtime,
        readiness="Existing lesson governance remains authoritative",
        required_decision=_product_required_decision(product),
        blocked=product.status == "archived",
        detail_route=f"/workspace/products/{product.id}",
        governance_route=(
            f"/workspace/product-studio/courses/{product.course_id}/edit"
            if product.course_id
            else None
        ),
        updated_at=product.updated_at,
    )


def _review_item_for_course(course: Course) -> ReviewCenterItemResponse | None:
    readiness = evaluate_course_publish_readiness(course)
    if readiness.is_ready and not readiness.warnings:
        return None

    issue_count = len(readiness.blocking_issues)
    warning_count = len(readiness.warnings)
    if issue_count:
        status = "blocked"
        required_decision = "Resolve lesson governance blockers"
    else:
        status = "approved"
        required_decision = "Review readiness warnings"

    return ReviewCenterItemResponse(
        id=course.id,
        item_type="lesson_governance",
        title=course.title,
        status=status,
        review_state="existing_governance",
        owner=None,
        source_coverage=f"{issue_count} blocking issue(s), {warning_count} warning(s)",
        readiness="Ready" if readiness.is_ready else "Blocked",
        required_decision=required_decision,
        blocked=not readiness.is_ready,
        detail_route=f"/workspace/product-studio/courses/{course.id}/edit",
        governance_route=f"/workspace/product-studio/courses/{course.id}/edit",
        updated_at=course.updated_at,
    )


def _review_center_course_query(db: Session, current_user: User):
    query = db.query(Course).options(
        joinedload(Course.units).joinedload(Unit.lessons).joinedload(Lesson.sources),
    )
    visible_organization_ids = _visible_organization_ids(db, current_user)
    if visible_organization_ids is None:
        return query
    if not visible_organization_ids:
        return query.filter(False)
    return query.filter(Course.organization_id.in_(visible_organization_ids))


def _learner_product_from_enrollment(
    enrollment: StudentCourse,
    product: Product | None,
) -> LearnerProductResponse:
    course = enrollment.course
    return LearnerProductResponse(
        id=product.id if product else course.id,
        product_id=product.id if product else None,
        course_id=course.id,
        title=product.title if product else course.title,
        description=(product.description if product else course.description),
        product_type=product.product_type if product else "course",
        product_status=product.status if product else None,
        review_state=product.review_state if product else None,
        access_state=product.access_state if product else None,
        enrollment_id=enrollment.id,
        enrollment_status=enrollment.status,
        enrolled_on=enrollment.enrolled_on,
        access_grant_id=None,
        access_grant_status=None,
        is_enrolled=True,
        source="product_wrapper" if product else "runtime_course",
        learner_visibility="Existing enrollment controls access; lesson governance controls content.",
        next_action="Continue governed course runtime",
    )


def _learner_product_from_grant(grant: AccessGrant) -> LearnerProductResponse:
    product = grant.product
    course = product.course
    return LearnerProductResponse(
        id=product.id,
        product_id=product.id,
        course_id=course.id if course else None,
        title=product.title,
        description=product.description or (course.description if course else None),
        product_type=product.product_type,
        product_status=product.status,
        review_state=product.review_state,
        access_state=product.access_state,
        enrollment_id=None,
        enrollment_status=None,
        enrolled_on=None,
        access_grant_id=grant.id,
        access_grant_status=grant.status,
        is_enrolled=False,
        source="product_wrapper",
        learner_visibility="Active access grant permits product-level access; lesson governance still controls runtime content.",
        next_action=(
            "Continue governed course runtime"
            if course is not None
            else "Product access available; learner runtime is not implemented for this product type yet"
        ),
    )


@router.get("/review-center", response_model=ReviewCenterResponse)
def get_review_center(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pending_artifacts = [
        _review_item_for_artifact(artifact)
        for artifact in _scope_platform_query(db.query(Artifact), Artifact, db, current_user)
        .filter(Artifact.status.in_(["draft", "in_review", "needs_changes"]))
        .order_by(Artifact.updated_at.desc(), Artifact.created_at.desc())
        .all()
    ]
    draft_products = [
        _review_item_for_product(product)
        for product in _scope_platform_query(db.query(Product), Product, db, current_user)
        .filter(Product.status.in_(["draft", "in_review", "approved"]))
        .order_by(Product.updated_at.desc(), Product.created_at.desc())
        .all()
    ]
    lesson_governance_items = [
        item
        for item in (
            _review_item_for_course(course)
            for course in _review_center_course_query(db, current_user)
            .order_by(Course.updated_at.desc(), Course.created_at.desc())
            .all()
        )
        if item is not None
    ]

    return ReviewCenterResponse(
        pending_artifacts=pending_artifacts,
        draft_products=draft_products,
        lesson_governance_items=lesson_governance_items,
        recent_activity=[
            ReviewCenterActivityResponse(
                id="review-activity-placeholder",
                message="Review activity history will appear here after audit records are introduced.",
                created_at=None,
            )
        ],
    )


@router.patch("/artifacts/{artifact_id}/review-status", response_model=ArtifactResponse)
def update_artifact_review_status(
    artifact_id: UUID,
    payload: ReviewStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.status not in SUPPORTED_ARTIFACT_REVIEW_STATUSES:
        raise HTTPException(status_code=400, detail="Unsupported artifact review status.")

    artifact = _get_visible_artifact(db, current_user, artifact_id)
    _require_manage_platform_record(db, current_user, artifact.workspace_id)

    artifact.status = payload.status
    artifact.review_state = payload.status
    db.commit()
    db.refresh(artifact)
    return artifact


@router.patch("/products/{product_id}/review-status", response_model=ProductResponse)
def update_product_review_status(
    product_id: UUID,
    payload: ReviewStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.status not in SUPPORTED_PRODUCT_REVIEW_STATUSES:
        raise HTTPException(status_code=400, detail="Unsupported product review status.")

    product = _get_visible_product(db, current_user, product_id)
    _require_manage_platform_record(db, current_user, product.workspace_id)

    product.status = payload.status
    product.review_state = payload.status
    db.commit()
    db.refresh(product)
    return product


@router.get("/learner-portal/products", response_model=list[LearnerProductResponse])
def list_learner_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    enrolled_courses = (
        db.query(StudentCourse)
        .options(joinedload(StudentCourse.course))
        .filter(StudentCourse.student_id == current_user.id)
        .order_by(StudentCourse.enrolled_on.desc(), StudentCourse.id.asc())
        .all()
    )
    enrolled_course_ids = [enrollment.course_id for enrollment in enrolled_courses]
    products_by_course_id = {
        product.course_id: product
        for product in db.query(Product)
        .filter(Product.course_id.in_(enrolled_course_ids))
        .all()
        if product.course_id is not None
    } if enrolled_course_ids else {}

    learner_products = [
        _learner_product_from_enrollment(
            enrollment,
            products_by_course_id.get(enrollment.course_id),
        )
        for enrollment in enrolled_courses
        if enrollment.course is not None
    ]

    granted_products_query = (
        db.query(AccessGrant)
        .options(joinedload(AccessGrant.product).joinedload(Product.course))
        .join(Product, AccessGrant.product_id == Product.id)
        .filter(
            AccessGrant.user_id == current_user.id,
            AccessGrant.status == "active",
            AccessGrant.revoked_at.is_(None),
            Product.status.in_(LEARNER_VISIBLE_PRODUCT_STATUSES),
        )
        .order_by(Product.title.asc())
    )
    if enrolled_course_ids:
        granted_products_query = granted_products_query.filter(
            (Product.course_id.is_(None)) | (~Product.course_id.in_(enrolled_course_ids))
        )

    now = datetime.utcnow()
    learner_products.extend(
        _learner_product_from_grant(grant)
        for grant in granted_products_query.all()
        if grant.product is not None and _grant_is_active(grant, now)
    )

    return learner_products


@router.get("/access-grants", response_model=list[AccessGrantResponse])
def list_access_grants(
    workspace_id: UUID | None = Query(default=None),
    product_id: UUID | None = Query(default=None),
    user_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _scope_access_grant_query(db.query(AccessGrant), db, current_user)
    if current_user.role not in CREATOR_ROLES:
        query = query.filter(AccessGrant.user_id == current_user.id)
    if workspace_id:
        query = query.filter(AccessGrant.workspace_id == workspace_id)
    if product_id:
        query = query.filter(AccessGrant.product_id == product_id)
    if user_id:
        query = query.filter(AccessGrant.user_id == user_id)
    return query.order_by(AccessGrant.created_at.desc(), AccessGrant.id.asc()).all()


@router.post("/access-grants", response_model=AccessGrantResponse, status_code=201)
def create_access_grant(
    payload: AccessGrantCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.grant_type not in SUPPORTED_ACCESS_GRANT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported access grant type.")
    if payload.status not in SUPPORTED_ACCESS_GRANT_STATUSES:
        raise HTTPException(status_code=400, detail="Unsupported access grant status.")
    if payload.status == "revoked":
        raise HTTPException(status_code=400, detail="Create active or pending grants, then revoke explicitly.")

    product = _get_visible_product(db, current_user, payload.product_id)
    _require_manage_platform_record(db, current_user, product.workspace_id)
    if payload.workspace_id and payload.workspace_id != product.workspace_id:
        raise HTTPException(status_code=400, detail="Access grant workspace must match the product workspace.")
    if payload.project_id and payload.project_id != product.project_id:
        raise HTTPException(status_code=400, detail="Access grant project must match the product project.")

    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(AccessGrant)
        .filter(
            AccessGrant.user_id == payload.user_id,
            AccessGrant.product_id == payload.product_id,
            AccessGrant.grant_type == payload.grant_type,
        )
        .first()
    )
    if existing:
        existing.status = payload.status
        existing.source = payload.source
        existing.workspace_id = product.workspace_id
        existing.project_id = product.project_id
        existing.starts_at = payload.starts_at
        existing.expires_at = payload.expires_at
        existing.revoked_at = None
        existing.grant_metadata = payload.metadata
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    grant = AccessGrant(
        user_id=payload.user_id,
        product_id=product.id,
        workspace_id=product.workspace_id,
        project_id=product.project_id,
        grant_type=payload.grant_type,
        status=payload.status,
        source=payload.source,
        starts_at=payload.starts_at,
        expires_at=payload.expires_at,
        grant_metadata=payload.metadata,
    )
    db.add(grant)
    db.commit()
    db.refresh(grant)
    return grant


@router.patch("/access-grants/{grant_id}/revoke", response_model=AccessGrantResponse)
def revoke_access_grant(
    grant_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    grant = _scope_access_grant_query(
        db.query(AccessGrant).filter(AccessGrant.id == grant_id),
        db,
        current_user,
    ).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Access grant not found")

    _require_manage_platform_record(db, current_user, grant.workspace_id)
    grant.status = "revoked"
    grant.revoked_at = datetime.utcnow()
    grant.updated_at = grant.revoked_at
    db.commit()
    db.refresh(grant)
    return grant


@router.get("/workspaces", response_model=list[WorkspaceResponse])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _scope_workspace_query(db.query(Workspace), db, current_user)
    return query.order_by(Workspace.created_at.asc(), Workspace.name.asc()).all()


@router.get("/workspaces/{workspace_id}", response_model=WorkspaceResponse)
def get_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = _scope_workspace_query(
        db.query(Workspace).filter(Workspace.id == workspace_id),
        db,
        current_user,
    ).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return workspace


@router.get("/projects", response_model=list[ProjectResponse])
def list_projects(
    workspace_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _scope_platform_query(db.query(Project), Project, db, current_user)
    if workspace_id:
        query = query.filter(Project.workspace_id == workspace_id)
    return query.order_by(Project.created_at.asc(), Project.name.asc()).all()


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = _scope_platform_query(
        db.query(Project).filter(Project.id == project_id),
        Project,
        db,
        current_user,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/projects", response_model=ProjectResponse, status_code=201)
def create_project(
    payload: ProjectCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_manage_workspace(db, current_user, payload.workspace_id)
    project = Project(
        workspace_id=payload.workspace_id,
        name=payload.name,
        description=payload.description,
        status=payload.status,
        project_metadata=payload.metadata,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/products", response_model=list[ProductResponse])
def list_products(
    workspace_id: UUID | None = Query(default=None),
    project_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _scope_platform_query(db.query(Product), Product, db, current_user)
    if workspace_id:
        query = query.filter(Product.workspace_id == workspace_id)
    if project_id:
        query = query.filter(Product.project_id == project_id)
    return query.order_by(Product.created_at.asc(), Product.title.asc()).all()


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = _scope_platform_query(
        db.query(Product).filter(Product.id == product_id),
        Product,
        db,
        current_user,
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(
    payload: ProductCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.product_type not in SUPPORTED_PRODUCT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported product type.")

    _require_manage_workspace(db, current_user, payload.workspace_id)

    if payload.project_id:
        _require_project_in_workspace(db, current_user, payload.workspace_id, payload.project_id)

    if payload.course_id:
        course = db.query(Course).filter(Course.id == payload.course_id).first()
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        existing_product = db.query(Product).filter(Product.course_id == payload.course_id).first()
        if existing_product:
            return existing_product

    if payload.program_id:
        program = db.query(Program).filter(Program.id == payload.program_id).first()
        if not program:
            raise HTTPException(status_code=404, detail="Program not found")
        existing_product = db.query(Product).filter(Product.program_id == payload.program_id).first()
        if existing_product:
            return existing_product

    product = Product(
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        course_id=payload.course_id,
        program_id=payload.program_id,
        product_type=payload.product_type,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        review_state=payload.review_state,
        access_state=payload.access_state,
        product_metadata=payload.metadata,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/projects/{project_id}/products", response_model=list[ProductResponse])
def list_project_products(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_visible_project(db, current_user, project_id)
    return (
        _scope_platform_query(db.query(Product), Product, db, current_user)
        .filter(Product.project_id == project_id)
        .order_by(Product.created_at.asc(), Product.title.asc())
        .all()
    )


@router.get("/knowledge-sources", response_model=list[KnowledgeSourceResponse])
def list_knowledge_sources(
    project_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _scope_platform_query(db.query(KnowledgeSource), KnowledgeSource, db, current_user)
    if project_id:
        query = query.filter(KnowledgeSource.project_id == project_id)
    return query.order_by(KnowledgeSource.created_at.asc(), KnowledgeSource.title.asc()).all()


@router.get("/projects/{project_id}/knowledge-sources", response_model=list[KnowledgeSourceResponse])
def list_project_knowledge_sources(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_visible_project(db, current_user, project_id)
    return (
        _scope_platform_query(db.query(KnowledgeSource), KnowledgeSource, db, current_user)
        .filter(KnowledgeSource.project_id == project_id)
        .order_by(KnowledgeSource.created_at.asc(), KnowledgeSource.title.asc())
        .all()
    )


@router.post("/knowledge-sources", response_model=KnowledgeSourceResponse, status_code=201)
def create_knowledge_source(
    payload: KnowledgeSourceCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.source_type not in SUPPORTED_KNOWLEDGE_SOURCE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported knowledge source type.")

    _require_project_in_workspace(db, current_user, payload.workspace_id, payload.project_id)

    if payload.source_id:
        source = db.query(Source).filter(Source.id == payload.source_id).first()
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")

    knowledge_source = KnowledgeSource(
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        source_id=payload.source_id,
        title=payload.title,
        source_type=payload.source_type,
        uri=payload.uri,
        citation=payload.citation,
        content_hash=payload.content_hash,
        status=payload.status,
        source_metadata=payload.metadata,
    )
    db.add(knowledge_source)
    db.commit()
    db.refresh(knowledge_source)
    return knowledge_source


@router.get("/artifacts", response_model=list[ArtifactResponse])
def list_artifacts(
    project_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _scope_platform_query(db.query(Artifact), Artifact, db, current_user)
    if project_id:
        query = query.filter(Artifact.project_id == project_id)
    return query.order_by(Artifact.created_at.asc(), Artifact.title.asc()).all()


@router.get("/projects/{project_id}/artifacts", response_model=list[ArtifactResponse])
def list_project_artifacts(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_visible_project(db, current_user, project_id)
    return (
        _scope_platform_query(db.query(Artifact), Artifact, db, current_user)
        .filter(Artifact.project_id == project_id)
        .order_by(Artifact.created_at.asc(), Artifact.title.asc())
        .all()
    )


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
def get_artifact(
    artifact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    artifact = _scope_platform_query(
        db.query(Artifact).filter(Artifact.id == artifact_id),
        Artifact,
        db,
        current_user,
    ).first()
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return artifact


@router.post("/artifacts", response_model=ArtifactResponse, status_code=201)
def create_artifact(
    payload: ArtifactCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if payload.artifact_type not in SUPPORTED_ARTIFACT_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported artifact type.")

    _require_project_in_workspace(db, current_user, payload.workspace_id, payload.project_id)

    if payload.product_id:
        product = (
            db.query(Product)
            .filter(
                Product.id == payload.product_id,
                Product.workspace_id == payload.workspace_id,
                Product.project_id == payload.project_id,
            )
            .first()
        )
        if not product:
            raise HTTPException(status_code=400, detail="Product does not belong to the selected project.")

    if payload.knowledge_source_id:
        knowledge_source = (
            db.query(KnowledgeSource)
            .filter(
                KnowledgeSource.id == payload.knowledge_source_id,
                KnowledgeSource.workspace_id == payload.workspace_id,
                KnowledgeSource.project_id == payload.project_id,
            )
            .first()
        )
        if not knowledge_source:
            raise HTTPException(status_code=400, detail="Knowledge source does not belong to the selected project.")

    if payload.generation_run_id:
        generation_run = (
            db.query(GenerationRun)
            .filter(
                GenerationRun.id == payload.generation_run_id,
                GenerationRun.workspace_id == payload.workspace_id,
                GenerationRun.project_id == payload.project_id,
            )
            .first()
        )
        if not generation_run:
            raise HTTPException(status_code=400, detail="Generation run does not belong to the selected project.")

    artifact = Artifact(
        workspace_id=payload.workspace_id,
        project_id=payload.project_id,
        product_id=payload.product_id,
        generation_run_id=payload.generation_run_id,
        knowledge_source_id=payload.knowledge_source_id,
        artifact_type=payload.artifact_type,
        title=payload.title,
        body=payload.body,
        uri=payload.uri,
        status=payload.status,
        review_state=payload.review_state,
        artifact_metadata=payload.metadata,
    )
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


@router.get("/generation-runs", response_model=list[GenerationRunResponse])
def list_generation_runs(
    project_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = _scope_platform_query(db.query(GenerationRun), GenerationRun, db, current_user)
    if project_id:
        query = query.filter(GenerationRun.project_id == project_id)
    return query.order_by(GenerationRun.created_at.desc()).all()


@router.get("/projects/{project_id}/generation-runs", response_model=list[GenerationRunResponse])
def list_project_generation_runs(
    project_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _get_visible_project(db, current_user, project_id)
    return (
        _scope_platform_query(db.query(GenerationRun), GenerationRun, db, current_user)
        .filter(GenerationRun.project_id == project_id)
        .order_by(GenerationRun.created_at.desc())
        .all()
    )


@router.get("/generation-runs/{generation_run_id}", response_model=GenerationRunResponse)
def get_generation_run(
    generation_run_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    generation_run = _scope_platform_query(
        db.query(GenerationRun).filter(GenerationRun.id == generation_run_id),
        GenerationRun,
        db,
        current_user,
    ).first()
    if not generation_run:
        raise HTTPException(status_code=404, detail="Generation run not found")
    return generation_run
