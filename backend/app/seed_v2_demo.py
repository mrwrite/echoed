from __future__ import annotations

from datetime import datetime

from app import seed_demo
from app.database import SessionLocal
from app.models import (
    AccessGrant,
    Artifact,
    Course,
    GenerationRun,
    KnowledgeSource,
    Product,
    Project,
    StudentCourse,
    Unit,
    User,
    Workspace,
)


DEMO_WORKSPACE_SLUG = "echoed-v2-demo-workspace"
DEMO_PROJECT_NAME = "EchoEd V2 Platform Evolution Dogfood"
DEMO_OPERATOR_PRODUCT_TITLE = "EchoEd V2 Operator Walkthrough"
DEMO_REVIEW_PRODUCT_TITLE = "EchoEd Governance Review Pack"
DEMO_COURSE_PRODUCT_TITLE = "Introduction to Africa Governed Course Product"


def _utcnow() -> datetime:
    return datetime.utcnow()


def _merge_metadata(current: dict | None, updates: dict) -> dict:
    merged = dict(current or {})
    merged.update(updates)
    return merged


def _ensure_demo_identity(db) -> tuple[Workspace, dict[str, User]]:
    org = seed_demo._get_or_create_demo_org(db)
    users = {
        key: seed_demo._upsert_demo_user(db, profile)
        for key, profile in seed_demo.DEMO_USERS.items()
    }
    for key, role in seed_demo.MEMBERSHIP_MAP.items():
        seed_demo._ensure_membership(db, org, users[key], role)

    workspace = (
        db.query(Workspace)
        .filter(Workspace.organization_id == org.id)
        .first()
    )
    if workspace is None:
        workspace = Workspace(
            organization_id=org.id,
            name="EchoEd Demo Workspace",
            slug=DEMO_WORKSPACE_SLUG,
        )
        db.add(workspace)
        db.flush()

    workspace.name = "EchoEd Demo Workspace"
    workspace.slug = DEMO_WORKSPACE_SLUG
    workspace.description = (
        "Dogfooding workspace that shows how EchoEd turns source knowledge into reviewable artifacts, "
        "products, governed learner access, and analytics."
    )
    workspace.status = "active"
    workspace.workspace_metadata = _merge_metadata(
        workspace.workspace_metadata,
        {
            "demo": True,
            "demo_phase": "8.6",
            "story": "Workspace -> Project -> Sources -> Artifacts -> Products -> Review -> Learners -> Analytics",
        },
    )
    workspace.updated_at = _utcnow()
    db.flush()
    return workspace, users


def _ensure_project(db, workspace: Workspace) -> Project:
    project = (
        db.query(Project)
        .filter(Project.workspace_id == workspace.id, Project.name == DEMO_PROJECT_NAME)
        .first()
    )
    if project is None:
        project = Project(workspace_id=workspace.id, name=DEMO_PROJECT_NAME)
        db.add(project)
        db.flush()

    project.description = (
        "A realistic EchoEd-in-EchoEd project used to explain V2 platform evolution during demos."
    )
    project.status = "active"
    project.project_metadata = _merge_metadata(
        project.project_metadata,
        {
            "demo": True,
            "demo_phase": "8.6",
            "pipeline": ["sources", "generation_runs", "artifacts", "products"],
        },
    )
    project.updated_at = _utcnow()
    db.flush()
    return project


def _ensure_source(db, workspace: Workspace, project: Project, *, title: str, source_type: str, citation: str) -> KnowledgeSource:
    source = (
        db.query(KnowledgeSource)
        .filter(KnowledgeSource.project_id == project.id, KnowledgeSource.title == title)
        .first()
    )
    if source is None:
        source = KnowledgeSource(workspace_id=workspace.id, project_id=project.id, title=title)
        db.add(source)
        db.flush()

    source.workspace_id = workspace.id
    source.project_id = project.id
    source.source_type = source_type
    source.uri = None
    source.citation = citation
    source.content_hash = f"demo-phase-8-6-{title.lower().replace(' ', '-')}"
    source.status = "available"
    source.source_metadata = _merge_metadata(
        source.source_metadata,
        {
            "demo": True,
            "demo_phase": "8.6",
            "runtime_impact": "metadata_only",
        },
    )
    source.updated_at = _utcnow()
    db.flush()
    return source


def _ensure_product(
    db,
    workspace: Workspace,
    project: Project,
    *,
    title: str,
    product_type: str,
    status: str,
    review_state: str,
    access_state: str,
    description: str,
    visibility: str = "private",
    pricing_model: str = "internal",
    price_placeholder: str | None = None,
    category: str | None = None,
    audience: str | None = None,
    estimated_duration: str | None = None,
    featured: bool = False,
    course: Course | None = None,
) -> Product:
    if course is not None:
        product = db.query(Product).filter(Product.course_id == course.id).first()
    else:
        product = None

    if product is None:
        product = (
            db.query(Product)
            .filter(Product.workspace_id == workspace.id, Product.title == title)
            .first()
        )

    if product is None:
        product = Product(workspace_id=workspace.id, title=title)
        db.add(product)
        db.flush()

    product.workspace_id = workspace.id
    product.project_id = project.id
    product.course_id = course.id if course is not None else None
    product.product_type = product_type
    product.title = title
    product.subtitle = product.subtitle or "EchoEd V2 commercial-readiness preview"
    product.slug = product.slug or title.lower().replace(" ", "-")
    product.description = description
    product.status = status
    product.review_state = review_state
    product.access_state = access_state
    product.visibility = visibility
    product.pricing_model = pricing_model
    product.price_placeholder = price_placeholder
    product.currency = "USD" if pricing_model == "paid" else product.currency
    product.audience = audience
    product.difficulty = product.difficulty or "Operator"
    product.estimated_duration = estimated_duration
    product.tags = product.tags or ["demo", "echoed-v2", "commercial-readiness"]
    product.category = category
    product.version = product.version or "v2-demo"
    product.language = product.language or "en"
    product.last_updated = _utcnow()
    product.certificate_available = product.certificate_available or False
    product.featured = featured
    product.product_metadata = _merge_metadata(
        product.product_metadata,
        {
            "demo": True,
            "demo_phase": "8.6",
            "governance_note": "Product wrapper status does not override lesson readiness or runtime publication rules.",
        },
    )
    product.published_at = _utcnow() if status == "published" and product.published_at is None else product.published_at
    product.updated_at = _utcnow()
    db.flush()
    return product


def _ensure_generation_run(db, workspace: Workspace, project: Project, product: Product) -> GenerationRun:
    run = (
        db.query(GenerationRun)
        .filter(
            GenerationRun.project_id == project.id,
            GenerationRun.product_id == product.id,
            GenerationRun.provider == "demo_seed",
        )
        .first()
    )
    if run is None:
        run = GenerationRun(workspace_id=workspace.id, project_id=project.id, product_id=product.id)
        db.add(run)
        db.flush()

    run.workspace_id = workspace.id
    run.project_id = project.id
    run.product_id = product.id
    run.status = "completed"
    run.provider = "demo_seed"
    run.model_name = "not-executed-demo-placeholder"
    run.prompt = "Seeded walkthrough metadata only; no AI generation execution was run."
    run.output_summary = "Demo artifacts were inserted as reviewable V2 wrapper records."
    run.input_metadata = {
        "demo": True,
        "source": "Phase 8.6 dogfooding seed",
        "execution": "not_run",
    }
    run.output_metadata = {
        "artifact_count": 3,
        "runtime_content_created": False,
    }
    if run.started_at is None:
        run.started_at = _utcnow()
    if run.completed_at is None:
        run.completed_at = _utcnow()
    db.flush()
    return run


def _ensure_artifact(
    db,
    workspace: Workspace,
    project: Project,
    product: Product,
    generation_run: GenerationRun,
    knowledge_source: KnowledgeSource,
    *,
    title: str,
    artifact_type: str,
    status: str,
    review_state: str,
    body: str,
) -> Artifact:
    artifact = (
        db.query(Artifact)
        .filter(Artifact.project_id == project.id, Artifact.title == title)
        .first()
    )
    if artifact is None:
        artifact = Artifact(workspace_id=workspace.id, project_id=project.id, title=title)
        db.add(artifact)
        db.flush()

    artifact.workspace_id = workspace.id
    artifact.project_id = project.id
    artifact.product_id = product.id
    artifact.generation_run_id = generation_run.id
    artifact.knowledge_source_id = knowledge_source.id
    artifact.artifact_type = artifact_type
    artifact.body = body
    artifact.uri = None
    artifact.status = status
    artifact.review_state = review_state
    artifact.artifact_metadata = _merge_metadata(
        artifact.artifact_metadata,
        {
            "demo": True,
            "demo_phase": "8.6",
            "learner_runtime_generated": False,
        },
    )
    artifact.updated_at = _utcnow()
    db.flush()
    return artifact


def _ensure_access_grant(db, workspace: Workspace, project: Project, product: Product, learner: User) -> AccessGrant:
    grant = (
        db.query(AccessGrant)
        .filter(
            AccessGrant.user_id == learner.id,
            AccessGrant.product_id == product.id,
            AccessGrant.grant_type == "manual",
        )
        .first()
    )
    if grant is None:
        grant = AccessGrant(
            user_id=learner.id,
            product_id=product.id,
            workspace_id=workspace.id,
            project_id=project.id,
            grant_type="manual",
        )
        db.add(grant)
        db.flush()

    grant.workspace_id = workspace.id
    grant.project_id = project.id
    grant.status = "active"
    grant.source = "demo_seed"
    grant.starts_at = grant.starts_at or _utcnow()
    grant.expires_at = None
    grant.revoked_at = None
    grant.grant_metadata = _merge_metadata(
        grant.grant_metadata,
        {
            "demo": True,
            "demo_phase": "8.6",
            "access_note": "Product-level access only; governed lessons still require existing runtime eligibility.",
        },
    )
    grant.updated_at = _utcnow()
    db.flush()
    return grant


def seed_echoed_v2_demo(db) -> dict[str, str]:
    workspace, users = _ensure_demo_identity(db)
    project = _ensure_project(db, workspace)

    sources = [
        _ensure_source(
            db,
            workspace,
            project,
            title="EchoEd V2 OpenSpec Phase Plan",
            source_type="openspec",
            citation="echoed-v2-platform-evolution proposal, design, and phase tasks",
        ),
        _ensure_source(
            db,
            workspace,
            project,
            title="Governed Runtime Preservation Notes",
            source_type="governance_note",
            citation="Existing Course, Lesson, progress, readiness, and governance behavior",
        ),
        _ensure_source(
            db,
            workspace,
            project,
            title="Learner Portal Access Walkthrough",
            source_type="demo_script",
            citation="Phase 6 Learner Portal V2 and Phase 7 Access Grant demo flow",
        ),
    ]

    existing_course = db.query(Course).filter(Course.title == seed_demo.DEMO_COURSE_TITLE).first()
    if existing_course is not None:
        _ensure_product(
            db,
            workspace,
            project,
            title=DEMO_COURSE_PRODUCT_TITLE,
            product_type="course",
            status="published",
            review_state="approved",
            access_state="enrollment_backed",
            description="A course-backed product proving V2 wraps the existing governed lesson runtime without replacing it.",
            visibility="workspace",
            pricing_model="internal",
            category="Governed course",
            audience="Demo learners",
            estimated_duration="45 minutes",
            course=existing_course,
        )

    operator_product = _ensure_product(
        db,
        workspace,
        project,
        title=DEMO_OPERATOR_PRODUCT_TITLE,
        product_type="playbook",
        status="published",
        review_state="approved",
        access_state="grant_required",
        description="A dogfooding product that explains EchoEd V2 using EchoEd's own workspace, source, artifact, review, access, learner, and analytics layers.",
        visibility="public",
        pricing_model="free",
        price_placeholder="Free preview - checkout not connected",
        category="Platform operations",
        audience="Knowledge product operators",
        estimated_duration="5 minutes",
        featured=True,
    )
    review_product = _ensure_product(
        db,
        workspace,
        project,
        title=DEMO_REVIEW_PRODUCT_TITLE,
        product_type="resource_pack",
        status="in_review",
        review_state="in_review",
        access_state="private",
        description="A reviewable product shell used to demonstrate trust, governance, and non-runtime artifact approval.",
        visibility="workspace",
        pricing_model="internal",
        category="Governance",
        audience="Reviewers",
        estimated_duration="10 minutes",
    )
    generation_run = _ensure_generation_run(db, workspace, project, operator_product)

    _ensure_artifact(
        db,
        workspace,
        project,
        operator_product,
        generation_run,
        sources[0],
        title="EchoEd V2 Workspace Storyboard",
        artifact_type="outline",
        status="approved",
        review_state="approved",
        body="Demo outline: Workspace -> Projects -> Sources -> Artifacts -> Products -> Review -> Access -> Learner Portal -> Analytics.",
    )
    _ensure_artifact(
        db,
        workspace,
        project,
        review_product,
        generation_run,
        sources[1],
        title="Review Center Governance Checklist",
        artifact_type="checklist",
        status="in_review",
        review_state="in_review",
        body="Confirms artifact approval and product approval do not publish learner-visible lessons.",
    )
    _ensure_artifact(
        db,
        workspace,
        project,
        operator_product,
        generation_run,
        sources[2],
        title="Learner Portal Access Explainer",
        artifact_type="implementation_guide",
        status="needs_changes",
        review_state="needs_changes",
        body="Explains active access grants for product visibility while runtime lesson access remains governed by existing enrollment and readiness rules.",
    )

    _ensure_access_grant(db, workspace, project, operator_product, users["normal_student"])

    db.commit()
    return {
        "workspace_id": str(workspace.id),
        "project_id": str(project.id),
        "operator_product_id": str(operator_product.id),
        "review_product_id": str(review_product.id),
        "runtime_student_course_count": str(db.query(StudentCourse).count()),
        "runtime_unit_count": str(db.query(Unit).count()),
    }


def run() -> dict[str, str]:
    db = SessionLocal()
    try:
        result = seed_echoed_v2_demo(db)
        print("Seeded EchoEd V2 dogfooding demo workspace.")
        print(f"Workspace: {DEMO_WORKSPACE_SLUG}")
        print(f"Project: {DEMO_PROJECT_NAME}")
        print(f"Published product: {DEMO_OPERATOR_PRODUCT_TITLE}")
        print(f"Review product: {DEMO_REVIEW_PRODUCT_TITLE}")
        return result
    finally:
        db.close()


if __name__ == "__main__":
    run()
