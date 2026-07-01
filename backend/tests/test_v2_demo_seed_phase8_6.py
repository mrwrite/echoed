from sqlalchemy.orm import sessionmaker

from app import seed_demo, seed_v2_demo
from app.models import AccessGrant, Artifact, Course, GenerationRun, KnowledgeSource, Product, Project, StudentCourse, Unit, User, Workspace


def _build_session_factory(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


def test_v2_demo_seed_adds_dogfooding_wrapper_story_without_runtime_changes(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    monkeypatch.setattr(seed_demo, "SessionLocal", session_factory)
    seed_demo.run()

    session = session_factory()
    try:
        runtime_counts_before = {
            "courses": session.query(Course).count(),
            "student_courses": session.query(StudentCourse).count(),
            "units": session.query(Unit).count(),
        }
    finally:
        session.close()

    session = session_factory()
    try:
        result = seed_v2_demo.seed_echoed_v2_demo(session)
        assert result["workspace_id"]
    finally:
        session.close()

    session = session_factory()
    try:
        assert session.query(Workspace).filter(Workspace.slug == seed_v2_demo.DEMO_WORKSPACE_SLUG).count() == 1
        assert session.query(Project).filter(Project.name == seed_v2_demo.DEMO_PROJECT_NAME).count() == 1
        assert session.query(KnowledgeSource).count() >= 3
        assert session.query(Artifact).count() >= 3
        assert session.query(GenerationRun).count() == 1

        products = {
            product.title: product
            for product in session.query(Product).filter(
                Product.title.in_(
                    [
                        seed_v2_demo.DEMO_OPERATOR_PRODUCT_TITLE,
                        seed_v2_demo.DEMO_REVIEW_PRODUCT_TITLE,
                        seed_v2_demo.DEMO_COURSE_PRODUCT_TITLE,
                    ]
                )
            )
        }
        assert products[seed_v2_demo.DEMO_OPERATOR_PRODUCT_TITLE].status == "published"
        assert products[seed_v2_demo.DEMO_OPERATOR_PRODUCT_TITLE].review_state == "approved"
        assert products[seed_v2_demo.DEMO_REVIEW_PRODUCT_TITLE].status == "in_review"

        normal_student = session.query(User).filter(User.username == "normalstudent").one()
        operator_product = products[seed_v2_demo.DEMO_OPERATOR_PRODUCT_TITLE]
        grant = (
            session.query(AccessGrant)
            .filter(
                AccessGrant.user_id == normal_student.id,
                AccessGrant.product_id == operator_product.id,
                AccessGrant.grant_type == "manual",
            )
            .one()
        )
        assert grant.status == "active"
        assert grant.source == "demo_seed"

        assert session.query(Course).count() == runtime_counts_before["courses"]
        assert session.query(StudentCourse).count() == runtime_counts_before["student_courses"]
        assert session.query(Unit).count() == runtime_counts_before["units"]
    finally:
        session.close()


def test_v2_demo_seed_is_idempotent(db_engine, monkeypatch):
    session_factory = _build_session_factory(db_engine)
    monkeypatch.setattr(seed_demo, "SessionLocal", session_factory)
    seed_demo.run()

    for _ in range(2):
        session = session_factory()
        try:
            seed_v2_demo.seed_echoed_v2_demo(session)
        finally:
            session.close()

    session = session_factory()
    try:
        assert session.query(Workspace).filter(Workspace.slug == seed_v2_demo.DEMO_WORKSPACE_SLUG).count() == 1
        assert session.query(Project).filter(Project.name == seed_v2_demo.DEMO_PROJECT_NAME).count() == 1
        assert session.query(Product).filter(Product.title == seed_v2_demo.DEMO_OPERATOR_PRODUCT_TITLE).count() == 1
        assert session.query(Product).filter(Product.title == seed_v2_demo.DEMO_REVIEW_PRODUCT_TITLE).count() == 1
        assert session.query(Artifact).filter(Artifact.title == "Review Center Governance Checklist").count() == 1
        assert session.query(AccessGrant).count() == 1
    finally:
        session.close()
