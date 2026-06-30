from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.enum import MembershipStatus
from app.models import (
    Artifact,
    GenerationRun,
    KnowledgeSource,
    OrganizationMembership,
    Product,
    Course,
    Program,
    Project,
    Source,
    User,
    Workspace,
)
from app.schemas import (
    ArtifactCreateRequest,
    ArtifactResponse,
    GenerationRunResponse,
    KnowledgeSourceCreateRequest,
    KnowledgeSourceResponse,
    ProductCreateRequest,
    ProductResponse,
    ProjectCreateRequest,
    ProjectResponse,
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
