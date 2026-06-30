import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import courses, v2_platform
from app.database import get_db
from app.deps import get_current_user
from app.enum import OrganizationType
from app.models import (
    Artifact,
    Course,
    GenerationRun,
    KnowledgeSource,
    Lesson,
    Organization,
    Product,
    Project,
    Source,
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
