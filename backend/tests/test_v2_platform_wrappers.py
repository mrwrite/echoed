import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import analytics, courses, v2_platform
from app.database import get_db
from app.deps import get_current_user
from app.enum import ProgressStatus
from app.enum import OrganizationType
from app.models import (
    AccessGrant,
    Artifact,
    Course,
    GenerationRun,
    KnowledgeSource,
    Lesson,
    Organization,
    OrganizationMembership,
    Product,
    Project,
    SegmentProgress,
    Source,
    StudentCourse,
    StudentUnitProgress,
    Unit,
    User,
    Workspace,
)


def _admin_user() -> User:
    return User(
        id=uuid.uuid4(),
        firstname="Admin",
        lastname="User",
        username=f"admin_{uuid.uuid4().hex[:8]}",
        email=f"admin_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        role="admin",
    )


def test_v2_wrapper_models_preserve_existing_course_lesson_relationships(db_session):
    organization = Organization(
        id=uuid.uuid4(),
        name="Acme Learning",
        type=OrganizationType.SCHOOL,
    )
    course = Course(
        id=uuid.uuid4(),
        title="Existing Course",
        description="Existing runtime course",
        organization=organization,
    )
    unit = Unit(
        id=uuid.uuid4(),
        course=course,
        title="Existing Unit",
        content="Runtime content",
        order=1,
    )
    lesson = Lesson(
        id=uuid.uuid4(),
        unit=unit,
        title="Existing Lesson",
        objective="Keep runtime behavior intact",
    )
    source = Source(
        id=uuid.uuid4(),
        lesson=lesson,
        citation="Existing source",
        url="https://example.com/source",
    )
    workspace = Workspace(
        id=uuid.uuid4(),
        organization=organization,
        name="Acme Workspace",
    )
    project = Project(
        id=uuid.uuid4(),
        workspace=workspace,
        name="Onboarding Project",
    )
    product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=course,
        product_type="course",
        title=course.title,
        description=course.description,
        status="active",
    )
    knowledge_source = KnowledgeSource(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        source=source,
        title="Existing source as knowledge",
        source_type="lesson_source",
        citation=source.citation,
    )
    generation_run = GenerationRun(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        product=product,
        status="completed",
        provider="test-provider",
        model_name="test-model",
        prompt="Generate onboarding material",
        output_summary="Generated an outline",
    )
    artifact = Artifact(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        product=product,
        generation_run=generation_run,
        knowledge_source=knowledge_source,
        artifact_type="guide",
        title="Implementation Guide",
        body="Reviewable generated content",
    )

    db_session.add_all([
        organization,
        course,
        unit,
        lesson,
        source,
        workspace,
        project,
        product,
        knowledge_source,
        generation_run,
        artifact,
    ])
    db_session.commit()
    db_session.expire_all()

    saved_course = db_session.query(Course).filter_by(id=course.id).one()
    assert saved_course.units[0].lessons[0].title == "Existing Lesson"
    assert saved_course.products[0].title == "Existing Course"

    saved_project = db_session.query(Project).filter_by(id=project.id).one()
    assert saved_project.workspace.name == "Acme Workspace"
    assert saved_project.products[0].course_id == course.id
    assert saved_project.knowledge_sources[0].source_id == source.id
    assert saved_project.generation_runs[0].artifacts[0].title == "Implementation Guide"


def test_v2_read_apis_list_wrappers_without_replacing_course_api(db_session):
    admin = _admin_user()
    organization = Organization(
        id=uuid.uuid4(),
        name="Runtime Org",
        type=OrganizationType.SCHOOL,
    )
    course = Course(
        id=uuid.uuid4(),
        title="Runtime Course",
        description="Still served by /api/courses",
        organization=organization,
    )
    unit = Unit(
        id=uuid.uuid4(),
        course=course,
        title="Runtime Unit",
        content="Existing unit",
        order=1,
    )
    lesson = Lesson(
        id=uuid.uuid4(),
        unit=unit,
        title="Runtime Lesson",
        objective="Existing lesson",
    )
    workspace = Workspace(
        id=uuid.uuid4(),
        organization=organization,
        name="Runtime Workspace",
    )
    project = Project(
        id=uuid.uuid4(),
        workspace=workspace,
        name="Runtime Project",
    )
    product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=course,
        product_type="course",
        title=course.title,
        description=course.description,
        status="active",
    )

    db_session.add_all([admin, organization, course, unit, lesson, workspace, project, product])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(v2_platform.router, prefix="/api")
    test_app.include_router(courses.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: admin

    client = TestClient(test_app)

    products_response = client.get("/api/products")
    assert products_response.status_code == 200
    products_payload = products_response.json()
    assert len(products_payload) == 1
    assert products_payload[0]["course_id"] == str(course.id)
    assert products_payload[0]["title"] == "Runtime Course"

    courses_response = client.get(f"/api/courses/{course.id}")
    assert courses_response.status_code == 200
    course_payload = courses_response.json()
    assert course_payload["id"] == str(course.id)
    assert course_payload["units"][0]["lessons"][0]["title"] == "Runtime Lesson"
    assert "products" not in course_payload


def test_v2_create_project_and_product_shells_are_additive(db_session):
    admin = _admin_user()
    organization = Organization(
        id=uuid.uuid4(),
        name="Studio Org",
        type=OrganizationType.SCHOOL,
    )
    course = Course(
        id=uuid.uuid4(),
        title="Course Runtime",
        description="Existing runtime remains untouched",
        organization=organization,
    )
    unit = Unit(
        id=uuid.uuid4(),
        course=course,
        title="Runtime Unit",
        content="Existing unit",
        order=1,
    )
    lesson = Lesson(
        id=uuid.uuid4(),
        unit=unit,
        title="Runtime Lesson",
        objective="Existing lesson",
    )
    workspace = Workspace(
        id=uuid.uuid4(),
        organization=organization,
        name="Studio Workspace",
    )
    db_session.add_all([admin, organization, course, unit, lesson, workspace])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(v2_platform.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: admin

    client = TestClient(test_app)

    project_response = client.post(
        "/api/projects",
        json={
            "workspace_id": str(workspace.id),
            "name": "Studio Project",
            "description": "Project shell only",
        },
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    product_response = client.post(
        "/api/products",
        json={
            "workspace_id": str(workspace.id),
            "project_id": project_id,
            "course_id": str(course.id),
            "product_type": "course",
            "title": "Course Runtime Product",
            "description": "Wrapper only",
        },
    )
    assert product_response.status_code == 201
    payload = product_response.json()
    assert payload["course_id"] == str(course.id)
    assert payload["project_id"] == project_id

    db_session.expire_all()
    assert db_session.query(Course).filter(Course.id == course.id).count() == 1
    assert db_session.query(Unit).filter(Unit.id == unit.id).count() == 1
    assert db_session.query(Lesson).filter(Lesson.id == lesson.id).count() == 1
    assert db_session.query(Project).filter(Project.id == uuid.UUID(project_id)).count() == 1
    assert db_session.query(Product).filter(Product.course_id == course.id).count() == 1


def test_v2_create_product_reuses_existing_course_backed_wrapper(db_session):
    admin = _admin_user()
    organization = Organization(
        id=uuid.uuid4(),
        name="Reuse Org",
        type=OrganizationType.SCHOOL,
    )
    course = Course(
        id=uuid.uuid4(),
        title="Reusable Course",
        description="Existing course",
        organization=organization,
    )
    workspace = Workspace(
        id=uuid.uuid4(),
        organization=organization,
        name="Reuse Workspace",
    )
    existing_product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        course=course,
        product_type="course",
        title=course.title,
        description=course.description,
        status="active",
    )
    db_session.add_all([admin, organization, course, workspace, existing_product])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(v2_platform.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: admin

    client = TestClient(test_app)
    response = client.post(
        "/api/products",
        json={
            "workspace_id": str(workspace.id),
            "course_id": str(course.id),
            "product_type": "course",
            "title": "Duplicate wrapper request",
        },
    )

    assert response.status_code == 201
    assert response.json()["id"] == str(existing_product.id)
    assert db_session.query(Product).count() == 1


def test_v2_creates_knowledge_source_and_artifact_links_without_changing_runtime(db_session):
    admin = _admin_user()
    organization = Organization(
        id=uuid.uuid4(),
        name="Pipeline Org",
        type=OrganizationType.SCHOOL,
    )
    course = Course(
        id=uuid.uuid4(),
        title="Pipeline Course",
        description="Existing runtime course",
        organization=organization,
    )
    unit = Unit(
        id=uuid.uuid4(),
        course=course,
        title="Runtime Unit",
        content="Existing unit",
        order=1,
    )
    lesson = Lesson(
        id=uuid.uuid4(),
        unit=unit,
        title="Runtime Lesson",
        objective="Runtime objective",
    )
    source = Source(
        id=uuid.uuid4(),
        lesson=lesson,
        citation="Runtime source",
        url="https://example.com/runtime-source",
    )
    workspace = Workspace(
        id=uuid.uuid4(),
        organization=organization,
        name="Pipeline Workspace",
    )
    project = Project(
        id=uuid.uuid4(),
        workspace=workspace,
        name="Pipeline Project",
    )
    product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=course,
        product_type="course",
        title="Pipeline Product",
    )
    generation_run = GenerationRun(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        product=product,
        status="completed",
        provider="placeholder",
        model_name="future-model",
        prompt="Draft a guide",
        output_summary="Placeholder output only",
    )
    db_session.add_all([
        admin,
        organization,
        course,
        unit,
        lesson,
        source,
        workspace,
        project,
        product,
        generation_run,
    ])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(v2_platform.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: admin
    client = TestClient(test_app)

    source_response = client.post(
        "/api/knowledge-sources",
        json={
            "workspace_id": str(workspace.id),
            "project_id": str(project.id),
            "source_id": str(source.id),
            "title": "Wrapped runtime source",
            "source_type": "lesson_source",
            "uri": source.url,
            "citation": source.citation,
            "metadata": {"wrapped_from": "lesson_source"},
        },
    )
    assert source_response.status_code == 201
    knowledge_source_id = source_response.json()["id"]
    assert source_response.json()["source_id"] == str(source.id)

    artifact_response = client.post(
        "/api/artifacts",
        json={
            "workspace_id": str(workspace.id),
            "project_id": str(project.id),
            "product_id": str(product.id),
            "generation_run_id": str(generation_run.id),
            "knowledge_source_id": knowledge_source_id,
            "artifact_type": "guide",
            "title": "Implementation Guide",
            "body": "Reviewable artifact content",
        },
    )
    assert artifact_response.status_code == 201
    artifact_payload = artifact_response.json()
    assert artifact_payload["status"] == "draft"
    assert artifact_payload["review_state"] == "review_required"
    assert artifact_payload["product_id"] == str(product.id)
    assert artifact_payload["generation_run_id"] == str(generation_run.id)
    assert artifact_payload["knowledge_source_id"] == knowledge_source_id

    assert client.get(f"/api/projects/{project.id}/knowledge-sources").json()[0]["id"] == knowledge_source_id
    assert client.get(f"/api/projects/{project.id}/artifacts").json()[0]["id"] == artifact_payload["id"]
    assert client.get(f"/api/projects/{project.id}/generation-runs").json()[0]["id"] == str(generation_run.id)
    assert client.get(f"/api/projects/{project.id}/products").json()[0]["id"] == str(product.id)

    db_session.expire_all()
    assert db_session.query(Source).filter(Source.id == source.id).one().citation == "Runtime source"
    assert db_session.query(Course).filter(Course.id == course.id).count() == 1
    assert db_session.query(Lesson).filter(Lesson.id == lesson.id).count() == 1


def test_v2_rejects_unsupported_source_and_artifact_types(db_session):
    admin = _admin_user()
    organization = Organization(
        id=uuid.uuid4(),
        name="Validation Org",
        type=OrganizationType.SCHOOL,
    )
    workspace = Workspace(
        id=uuid.uuid4(),
        organization=organization,
        name="Validation Workspace",
    )
    project = Project(
        id=uuid.uuid4(),
        workspace=workspace,
        name="Validation Project",
    )
    db_session.add_all([admin, organization, workspace, project])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(v2_platform.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: admin
    client = TestClient(test_app)

    source_response = client.post(
        "/api/knowledge-sources",
        json={
            "workspace_id": str(workspace.id),
            "project_id": str(project.id),
            "title": "Unsupported source",
            "source_type": "unknown",
        },
    )
    assert source_response.status_code == 400

    artifact_response = client.post(
        "/api/artifacts",
        json={
            "workspace_id": str(workspace.id),
            "project_id": str(project.id),
            "artifact_type": "unknown",
            "title": "Unsupported artifact",
        },
    )
    assert artifact_response.status_code == 400


def test_review_center_lists_v2_wrappers_and_existing_governance_items(db_session):
    admin = _admin_user()
    organization = Organization(
        id=uuid.uuid4(),
        name="Review Org",
        type=OrganizationType.SCHOOL,
    )
    course = Course(
        id=uuid.uuid4(),
        title="Blocked Runtime Course",
        description="Existing course remains governed",
        organization=organization,
    )
    unit = Unit(id=uuid.uuid4(), course=course, title="Runtime Unit", content="Runtime", order=1)
    lesson = Lesson(
        id=uuid.uuid4(),
        unit=unit,
        title="Draft Runtime Lesson",
        objective="Needs source and approval",
        order=1,
        review_status="draft",
    )
    workspace = Workspace(id=uuid.uuid4(), organization=organization, name="Review Workspace")
    project = Project(id=uuid.uuid4(), workspace=workspace, name="Review Project")
    product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=course,
        product_type="course",
        title="Draft Product",
        status="draft",
    )
    artifact = Artifact(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        product=product,
        artifact_type="lesson_draft",
        title="Pending Lesson Draft",
        body="Reviewable wrapper content",
        status="in_review",
    )
    db_session.add_all([admin, organization, course, unit, lesson, workspace, project, product, artifact])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(v2_platform.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: admin
    client = TestClient(test_app)

    response = client.get("/api/review-center")

    assert response.status_code == 200
    payload = response.json()
    assert payload["pending_artifacts"][0]["id"] == str(artifact.id)
    assert payload["pending_artifacts"][0]["status"] == "in_review"
    assert payload["draft_products"][0]["id"] == str(product.id)
    assert payload["draft_products"][0]["status"] == "draft"
    assert payload["lesson_governance_items"][0]["id"] == str(course.id)
    assert payload["lesson_governance_items"][0]["status"] == "blocked"
    assert payload["recent_activity"][0]["id"] == "review-activity-placeholder"


def test_review_status_updates_only_change_v2_wrapper_records(db_session):
    admin = _admin_user()
    organization = Organization(
        id=uuid.uuid4(),
        name="Status Org",
        type=OrganizationType.SCHOOL,
    )
    course = Course(
        id=uuid.uuid4(),
        title="Runtime Status Course",
        description="Runtime course",
        organization=organization,
        published_at=None,
    )
    unit = Unit(id=uuid.uuid4(), course=course, title="Runtime Unit", content="Runtime", order=1)
    lesson = Lesson(id=uuid.uuid4(), unit=unit, title="Runtime Lesson", objective="Draft", review_status="draft")
    workspace = Workspace(id=uuid.uuid4(), organization=organization, name="Status Workspace")
    project = Project(id=uuid.uuid4(), workspace=workspace, name="Status Project")
    product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=course,
        product_type="course",
        title="Status Product",
        status="draft",
        review_state="not_reviewed",
    )
    artifact = Artifact(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        product=product,
        artifact_type="guide",
        title="Status Artifact",
        status="draft",
        review_state="review_required",
    )
    db_session.add_all([admin, organization, course, unit, lesson, workspace, project, product, artifact])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(v2_platform.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: admin
    client = TestClient(test_app)

    artifact_response = client.patch(
        f"/api/artifacts/{artifact.id}/review-status",
        json={"status": "approved"},
    )
    product_response = client.patch(
        f"/api/products/{product.id}/review-status",
        json={"status": "approved"},
    )
    invalid_response = client.patch(
        f"/api/artifacts/{artifact.id}/review-status",
        json={"status": "published"},
    )

    assert artifact_response.status_code == 200
    assert artifact_response.json()["status"] == "approved"
    assert artifact_response.json()["review_state"] == "approved"
    assert product_response.status_code == 200
    assert product_response.json()["status"] == "approved"
    assert product_response.json()["review_state"] == "approved"
    assert invalid_response.status_code == 400

    db_session.expire_all()
    saved_course = db_session.query(Course).filter(Course.id == course.id).one()
    saved_lesson = db_session.query(Lesson).filter(Lesson.id == lesson.id).one()
    assert saved_course.published_at is None
    assert saved_lesson.review_status == "draft"


def test_approved_artifact_does_not_make_draft_lesson_learner_visible(db_session):
    admin = _admin_user()
    learner = User(
        id=uuid.uuid4(),
        firstname="Learner",
        lastname="User",
        username=f"learner_{uuid.uuid4().hex[:8]}",
        email=f"learner_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        role="student",
    )
    organization = Organization(
        id=uuid.uuid4(),
        name="Learner Safety Org",
        type=OrganizationType.SCHOOL,
    )
    course = Course(
        id=uuid.uuid4(),
        title="Learner Safety Course",
        description="Existing governed course",
        organization=organization,
    )
    unit = Unit(id=uuid.uuid4(), course=course, title="Runtime Unit", content="Runtime", order=1)
    lesson = Lesson(
        id=uuid.uuid4(),
        unit=unit,
        title="Unapproved Runtime Lesson",
        objective="Still draft",
        review_status="draft",
        order=1,
    )
    workspace = Workspace(id=uuid.uuid4(), organization=organization, name="Learner Safety Workspace")
    project = Project(id=uuid.uuid4(), workspace=workspace, name="Learner Safety Project")
    product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=course,
        product_type="course",
        title="Learner Safety Product",
    )
    artifact = Artifact(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        product=product,
        artifact_type="lesson_draft",
        title="Approved Wrapper Only",
        status="approved",
        review_state="approved",
    )
    db_session.add_all([admin, learner, organization, course, unit, lesson, workspace, project, product, artifact])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(courses.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: learner
    client = TestClient(test_app)

    response = client.get(f"/api/courses/{course.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["units"][0]["learner_availability"] == "no_approved_content"
    assert payload["units"][0]["lessons"] == []


def test_learner_portal_products_use_enrollments_and_active_grants(db_session):
    learner = User(
        id=uuid.uuid4(),
        firstname="Learner",
        lastname="Portal",
        username=f"learner_{uuid.uuid4().hex[:8]}",
        email=f"learner_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        role="student",
    )
    organization = Organization(
        id=uuid.uuid4(),
        name="Learner Product Org",
        type=OrganizationType.SCHOOL,
    )
    membership = OrganizationMembership(
        id=uuid.uuid4(),
        organization=organization,
        user=learner,
        role="student",
        status="active",
    )
    workspace = Workspace(id=uuid.uuid4(), organization=organization, name="Learner Product Workspace")
    project = Project(id=uuid.uuid4(), workspace=workspace, name="Learner Product Project")
    enrolled_course = Course(
        id=uuid.uuid4(),
        title="Enrolled Course",
        description="Existing runtime enrollment",
        organization=organization,
    )
    available_course = Course(
        id=uuid.uuid4(),
        title="Available Course",
        description="Approved wrapper",
        organization=organization,
    )
    draft_course = Course(
        id=uuid.uuid4(),
        title="Draft Wrapper Course",
        description="Should not be available through learner products",
        organization=organization,
    )
    enrollment = StudentCourse(
        id=uuid.uuid4(),
        student=learner,
        course=enrolled_course,
        status="active",
    )
    enrolled_product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=enrolled_course,
        product_type="course",
        title="Draft Enrolled Product",
        status="draft",
        review_state="draft",
    )
    available_product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=available_course,
        product_type="course",
        title="Approved Available Product",
        status="approved",
        review_state="approved",
    )
    available_grant = AccessGrant(
        id=uuid.uuid4(),
        user=learner,
        product=available_product,
        workspace=workspace,
        project=project,
        grant_type="manual",
        status="active",
        source="manual",
    )
    draft_product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=draft_course,
        product_type="course",
        title="Hidden Draft Product",
        status="draft",
        review_state="draft",
    )
    db_session.add_all([
        learner,
        organization,
        membership,
        workspace,
        project,
        enrolled_course,
        available_course,
        draft_course,
        enrollment,
        enrolled_product,
        available_product,
            draft_product,
            available_grant,
        ])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(v2_platform.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: learner
    client = TestClient(test_app)

    response = client.get("/api/learner-portal/products")

    assert response.status_code == 200
    payload = response.json()
    titles = {item["title"] for item in payload}
    assert "Draft Enrolled Product" in titles
    assert "Approved Available Product" in titles
    assert "Hidden Draft Product" not in titles

    enrolled = next(item for item in payload if item["title"] == "Draft Enrolled Product")
    available = next(item for item in payload if item["title"] == "Approved Available Product")
    assert enrolled["is_enrolled"] is True
    assert enrolled["product_status"] == "draft"
    assert enrolled["learner_visibility"].startswith("Existing enrollment controls access")
    assert available["is_enrolled"] is False
    assert available["product_status"] == "approved"
    assert available["access_grant_id"] == str(available_grant.id)


def test_access_grant_create_revoke_and_learner_visibility_are_additive(db_session):
    admin = _admin_user()
    learner = User(
        id=uuid.uuid4(),
        firstname="Grant",
        lastname="Learner",
        username=f"grant_learner_{uuid.uuid4().hex[:8]}",
        email=f"grant_learner_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        role="student",
    )
    organization = Organization(
        id=uuid.uuid4(),
        name="Grant Org",
        type=OrganizationType.SCHOOL,
    )
    workspace = Workspace(id=uuid.uuid4(), organization=organization, name="Grant Workspace")
    project = Project(id=uuid.uuid4(), workspace=workspace, name="Grant Project")
    course = Course(
        id=uuid.uuid4(),
        title="Grant Course",
        description="Access grant backed course",
        organization=organization,
    )
    unit = Unit(id=uuid.uuid4(), course=course, title="Grant Unit", content="Runtime", order=1)
    lesson = Lesson(
        id=uuid.uuid4(),
        unit=unit,
        title="Grant Draft Lesson",
        objective="Still governed",
        review_status="draft",
        order=1,
    )
    product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=course,
        product_type="course",
        title="Grant Product",
        status="approved",
        review_state="approved",
    )
    db_session.add_all([admin, learner, organization, workspace, project, course, unit, lesson, product])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(v2_platform.router, prefix="/api")
    test_app.include_router(courses.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: admin
    admin_client = TestClient(test_app)

    create_response = admin_client.post(
        "/api/access-grants",
        json={
            "user_id": str(learner.id),
            "product_id": str(product.id),
            "grant_type": "manual",
            "source": "manual",
            "metadata": {"reason": "phase7-test"},
        },
    )
    assert create_response.status_code == 201
    grant_payload = create_response.json()
    grant_id = grant_payload["id"]
    assert grant_payload["status"] == "active"
    assert grant_payload["workspace_id"] == str(workspace.id)
    assert db_session.query(StudentCourse).filter(StudentCourse.student_id == learner.id).count() == 0

    list_response = admin_client.get("/api/access-grants")
    assert list_response.status_code == 200
    assert list_response.json()[0]["id"] == grant_id

    test_app.dependency_overrides[get_current_user] = lambda: learner
    learner_client = TestClient(test_app)
    learner_products_response = learner_client.get("/api/learner-portal/products")
    assert learner_products_response.status_code == 200
    learner_products = learner_products_response.json()
    assert learner_products[0]["title"] == "Grant Product"
    assert learner_products[0]["access_grant_id"] == grant_id
    assert learner_products[0]["is_enrolled"] is False
    assert learner_products[0]["learner_visibility"].startswith("Active access grant")

    course_response = learner_client.get(f"/api/courses/{course.id}")
    assert course_response.status_code == 200
    course_payload = course_response.json()
    assert course_payload["units"][0]["learner_availability"] == "no_approved_content"
    assert course_payload["units"][0]["lessons"] == []

    test_app.dependency_overrides[get_current_user] = lambda: admin
    revoke_response = admin_client.patch(f"/api/access-grants/{grant_id}/revoke")
    assert revoke_response.status_code == 200
    assert revoke_response.json()["status"] == "revoked"

    test_app.dependency_overrides[get_current_user] = lambda: learner
    after_revoke_response = learner_client.get("/api/learner-portal/products")
    assert after_revoke_response.status_code == 200
    assert after_revoke_response.json() == []


def test_access_grant_does_not_expose_unapproved_product_to_learner_portal(db_session):
    admin = _admin_user()
    learner = User(
        id=uuid.uuid4(),
        firstname="Draft",
        lastname="Learner",
        username=f"draft_learner_{uuid.uuid4().hex[:8]}",
        email=f"draft_learner_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        role="student",
    )
    organization = Organization(
        id=uuid.uuid4(),
        name="Draft Grant Org",
        type=OrganizationType.SCHOOL,
    )
    workspace = Workspace(id=uuid.uuid4(), organization=organization, name="Draft Grant Workspace")
    product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        product_type="resource_pack",
        title="Draft Granted Product",
        status="draft",
        review_state="draft",
    )
    grant = AccessGrant(
        id=uuid.uuid4(),
        user=learner,
        product=product,
        workspace=workspace,
        grant_type="manual",
        status="active",
        source="manual",
    )
    db_session.add_all([admin, learner, organization, workspace, product, grant])
    db_session.commit()

    test_app = FastAPI()
    test_app.include_router(v2_platform.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: learner
    client = TestClient(test_app)

    response = client.get("/api/learner-portal/products")

    assert response.status_code == 200
    assert response.json() == []


def test_analytics_v2_reports_wrapper_and_runtime_state_read_only(db_session):
    admin = _admin_user()
    learner = User(
        id=uuid.uuid4(),
        firstname="Metric",
        lastname="Learner",
        username=f"metric_learner_{uuid.uuid4().hex[:8]}",
        email=f"metric_learner_{uuid.uuid4().hex[:8]}@example.com",
        hashed_password="hashed",
        role="student",
    )
    organization = Organization(
        id=uuid.uuid4(),
        name="Analytics Org",
        type=OrganizationType.SCHOOL,
    )
    course = Course(
        id=uuid.uuid4(),
        title="Analytics Course",
        description="Runtime course for analytics",
        organization=organization,
    )
    unit = Unit(
        id=uuid.uuid4(),
        course=course,
        title="Analytics Unit",
        content="Runtime unit",
        order=1,
    )
    lesson = Lesson(
        id=uuid.uuid4(),
        unit=unit,
        title="Analytics Lesson",
        objective="Track existing progress",
    )
    enrollment = StudentCourse(
        id=uuid.uuid4(),
        student=learner,
        course=course,
        status="active",
    )
    unit_progress = StudentUnitProgress(
        id=uuid.uuid4(),
        student_course=enrollment,
        unit=unit,
        status=ProgressStatus.COMPLETED,
    )
    segment_progress = SegmentProgress(
        id=uuid.uuid4(),
        student_unit=unit_progress,
        lesson=lesson,
        status=ProgressStatus.COMPLETED,
    )
    workspace = Workspace(id=uuid.uuid4(), organization=organization, name="Analytics Workspace")
    project = Project(id=uuid.uuid4(), workspace=workspace, name="Analytics Project")
    product = Product(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        course=course,
        product_type="course",
        title="Analytics Product",
        status="published",
        review_state="approved",
    )
    knowledge_source = KnowledgeSource(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        title="Analytics Source",
        source_type="lesson_source",
        status="available",
    )
    generation_run = GenerationRun(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        product=product,
        status="completed",
    )
    artifact = Artifact(
        id=uuid.uuid4(),
        workspace=workspace,
        project=project,
        product=product,
        knowledge_source=knowledge_source,
        generation_run=generation_run,
        artifact_type="guide",
        title="Analytics Artifact",
        status="needs_changes",
        review_state="needs_changes",
    )
    access_grant = AccessGrant(
        id=uuid.uuid4(),
        user=learner,
        product=product,
        workspace=workspace,
        grant_type="manual",
        status="active",
        source="manual",
    )
    db_session.add_all([
        admin,
        learner,
        organization,
        course,
        unit,
        lesson,
        enrollment,
        unit_progress,
        segment_progress,
        workspace,
        project,
        product,
        knowledge_source,
        generation_run,
        artifact,
        access_grant,
    ])
    db_session.commit()

    initial_enrollment_count = db_session.query(StudentCourse).count()
    test_app = FastAPI()
    test_app.include_router(analytics.router, prefix="/api")

    def override_get_db():
        yield db_session

    test_app.dependency_overrides[get_db] = override_get_db
    test_app.dependency_overrides[get_current_user] = lambda: admin
    client = TestClient(test_app)

    workspace_response = client.get("/api/analytics/workspace")
    products_response = client.get("/api/analytics/products")
    learners_response = client.get("/api/analytics/learners")
    pipeline_response = client.get("/api/analytics/knowledge-pipeline")

    assert workspace_response.status_code == 200
    workspace_payload = workspace_response.json()
    assert workspace_payload["totals"]["total_products"] == 1
    assert workspace_payload["totals"]["total_projects"] == 1
    assert workspace_payload["totals"]["total_knowledge_sources"] == 1
    assert workspace_payload["totals"]["total_artifacts"] == 1
    assert workspace_payload["totals"]["total_access_grants"] == 1
    assert workspace_payload["products_by_type"]["course"] == 1
    assert workspace_payload["products_by_status"]["published"] == 1
    assert workspace_payload["artifacts_by_status"]["needs_changes"] == 1
    assert workspace_payload["access_grants_by_type"]["manual"] == 1
    assert workspace_payload["learner_engagement"]["lesson_completion_count"] == 1
    assert workspace_payload["event_tracking"]["status"] == "unavailable"

    assert products_response.status_code == 200
    products_payload = products_response.json()
    assert products_payload["course_backed_product_count"] == 1
    assert products_payload["products"][0]["enrollment_count"] == 1
    assert products_payload["products"][0]["artifact_count"] == 1

    assert learners_response.status_code == 200
    learners_payload = learners_response.json()
    assert learners_payload["summary"]["learner_count"] == 1
    assert learners_payload["enrollments_by_status"]["active"] == 1

    assert pipeline_response.status_code == 200
    pipeline_payload = pipeline_response.json()
    assert pipeline_payload["total_generation_runs"] == 1
    assert pipeline_payload["source_coverage"]["artifacts_with_knowledge_source"] == 1

    assert db_session.query(StudentCourse).count() == initial_enrollment_count
