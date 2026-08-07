import uuid
from time import perf_counter

import pytest
from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.database import SessionLocal
from app.enum import MembershipStatus, OrganizationRole, OrganizationType
from app.main import app
from app.lesson_governance import serialize_course
from app.models import Course, Organization, OrganizationMembership, User


client = TestClient(app)


@pytest.fixture
def draft_context():
    db = SessionLocal()
    suffix = uuid.uuid4()
    user = User(
        id=uuid.uuid4(),
        firstname="Content",
        lastname="Author",
        username=f"draft_author_{suffix}",
        email=f"draft_author_{suffix}@example.com",
        hashed_password="fake",
        role="content_admin",
    )
    organization = Organization(
        id=uuid.uuid4(),
        name=f"Draft Org {suffix}",
        type=OrganizationType.SCHOOL,
    )
    db.add_all([user, organization])
    db.flush()
    db.add(
        OrganizationMembership(
            organization_id=organization.id,
            user_id=user.id,
            role=OrganizationRole.CONTENT_ADMIN,
            status=MembershipStatus.ACTIVE,
        )
    )
    db.commit()
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        yield db, user, organization
    finally:
        app.dependency_overrides = {}
        db.close()


def _headers(organization, key="draft-key"):
    return {"X-Org-Id": str(organization.id), "Idempotency-Key": key}


def _payload(title="Durable course"):
    return {
        "title": title,
        "description": "A complete nested draft",
        "subject": "History",
        "age_band_min": 10,
        "age_band_max": 13,
        "default_locale": "en",
        "learning_objectives": "Compare historical sources.",
        "skill_tags": ["source-analysis"],
        "standards_metadata": {"framework": "local"},
        "units": [
            {
                "title": "Second in supplied metadata",
                "order": 9,
                "lessons": [
                    {
                        "title": "Source comparison",
                        "order": 8,
                        "duration_minutes": 30,
                        "teacher_notes": "Educator-only guidance",
                        "sources": [
                            {"citation": "Archive A", "url": "https://example.com/a"}
                        ],
                        "activities": [
                            {
                                "type": "text",
                                "title": "Read the accounts",
                                "content": "Account A and Account B",
                                "order": 6,
                            }
                        ],
                    }
                ],
            },
            {"title": "Second unit", "order": 2, "lessons": []},
        ],
    }


def test_idempotent_creation_persists_one_ordered_course_graph(draft_context):
    db, user, organization = draft_context
    first = client.post(
        "/api/courses/authoring",
        headers=_headers(organization, "same-request"),
        json=_payload(),
    )
    second = client.post(
        "/api/courses/authoring",
        headers=_headers(organization, "same-request"),
        json=_payload(),
    )

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert first.json()["id"] == second.json()["id"]
    assert db.query(Course).filter(Course.created_by == user.id).count() == 1
    payload = first.json()
    assert payload["revision_number"] == 1
    assert [unit["order"] for unit in payload["units"]] == [1, 2]
    assert payload["units"][0]["lessons"][0]["order"] == 1
    assert payload["units"][0]["lessons"][0]["activities"][0]["order"] == 1
    assert payload["current_version_id"]


def test_update_preserves_ids_and_rejects_stale_revision(draft_context):
    _, _, organization = draft_context
    created = client.post(
        "/api/courses/authoring",
        headers=_headers(organization, "revision-test"),
        json=_payload(),
    ).json()
    course_id = created["id"]
    original_ids = [unit["id"] for unit in created["units"]]
    update = _payload("Updated durable course")
    update["revision_number"] = created["revision_number"]
    update["units"] = list(reversed(created["units"]))

    saved = client.put(f"/api/courses/{course_id}/authoring-draft", json=update)
    assert saved.status_code == 200, saved.text
    saved_payload = saved.json()
    assert saved_payload["revision_number"] == 2
    assert [unit["id"] for unit in saved_payload["units"]] == list(reversed(original_ids))
    assert [unit["order"] for unit in saved_payload["units"]] == [1, 2]

    stale = client.put(f"/api/courses/{course_id}/authoring-draft", json=update)
    assert stale.status_code == 409
    assert stale.json()["detail"]["code"] == "course_authoring_revision_conflict"
    assert stale.json()["detail"]["current_revision"] == 2


def test_invalid_nested_update_returns_issues_and_rolls_back(draft_context):
    db, _, organization = draft_context
    created = client.post(
        "/api/courses/authoring",
        headers=_headers(organization, "rollback-test"),
        json=_payload(),
    ).json()
    invalid = _payload("Changed but invalid")
    invalid["revision_number"] = created["revision_number"]
    invalid["units"][0]["lessons"][0]["title"] = ""

    response = client.put(
        f"/api/courses/{created['id']}/authoring-draft",
        json=invalid,
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "course_authoring_validation_failed"
    assert detail["issues"][0]["entity_type"] == "lesson"
    assert detail["issues"][0]["field"] == "title"
    db.expire_all()
    stored = db.query(Course).filter(Course.id == uuid.UUID(created["id"])).one()
    assert stored.title == "Durable course"
    assert stored.revision_number == 1


def test_course_and_nested_duplication_regenerate_ids_and_preserve_attribution(draft_context):
    _, _, organization = draft_context
    created = client.post(
        "/api/courses/authoring",
        headers=_headers(organization, "duplication-source"),
        json=_payload(),
    ).json()

    duplicated = client.post(
        f"/api/courses/{created['id']}/duplicate",
        headers={"Idempotency-Key": "duplication-copy"},
        json={"title": "Adapted copy"},
    )

    assert duplicated.status_code == 200, duplicated.text
    copy = duplicated.json()
    assert copy["id"] != created["id"]
    assert copy["title"] == "Adapted copy"
    assert copy["revision_status"] == "draft"
    assert copy["revision_metadata"]["derivative_source_course_id"] == created["id"]
    assert copy["units"][0]["id"] != created["units"][0]["id"]
    assert copy["units"][0]["lessons"][0]["id"] != created["units"][0]["lessons"][0]["id"]
    assert (
        copy["units"][0]["lessons"][0]["activities"][0]["id"]
        != created["units"][0]["lessons"][0]["activities"][0]["id"]
    )
    assert copy["units"][0]["lessons"][0]["sources"][0]["citation"] == "Archive A"
    assert "published_at" not in copy


def test_preview_review_and_safe_publish_are_separate_governed_actions(draft_context):
    db, author, organization = draft_context
    payload = _payload("Reviewable course")
    lesson = payload["units"][0]["lessons"][0]
    lesson.update({
        "objective": "Evaluate evidence.",
        "learning_objectives": "Explain a claim using evidence.",
        "key_concepts": ["evidence"],
        "hook": "Notice one surprising detail.",
        "content": "A complete learner-facing explanation.",
        "guided_practice": "Model one response.",
        "independent_practice": "Write one response.",
        "assessment": "A short evidence check.",
    })
    payload["units"] = [payload["units"][0]]
    created_response = client.post(
        "/api/courses/authoring",
        headers=_headers(organization, "review-workflow"),
        json=payload,
    )
    assert created_response.status_code == 200, created_response.text
    created = created_response.json()

    preview = client.get(f"/api/courses/{created['id']}/authoring-preview")
    assert preview.status_code == 200, preview.text
    assert preview.json()["units"][0]["lessons"][0]["teacher_notes"] is None
    assert preview.json()["units"][0]["lessons"][0]["title"] == "Source comparison"

    submitted = client.post(f"/api/courses/{created['id']}/submit-review")
    assert submitted.status_code == 200, submitted.text
    assert submitted.json()["lifecycle_state"] == "submitted"
    assert client.put(f"/api/courses/{created['id']}/authoring-draft", json={**payload, "revision_number": 1}).status_code == 403

    reviewer = User(
        id=uuid.uuid4(), firstname="Independent", lastname="Reviewer",
        username=f"reviewer_{uuid.uuid4()}", email=f"reviewer_{uuid.uuid4()}@example.com",
        hashed_password="fake", role="org_admin",
    )
    db.add(reviewer)
    db.flush()
    db.add(OrganizationMembership(
        organization_id=organization.id, user_id=reviewer.id,
        role=OrganizationRole.ORG_ADMIN, status=MembershipStatus.ACTIVE,
    ))
    db.commit()
    app.dependency_overrides[get_current_user] = lambda: reviewer

    returned = client.post(
        f"/api/courses/{created['id']}/review",
        json={"decision": "changes_requested", "feedback": "Clarify the learner directions."},
    )
    assert returned.status_code == 200, returned.text
    assert returned.json()["lifecycle_state"] == "changes_requested"

    app.dependency_overrides[get_current_user] = lambda: author
    payload["description"] = "A revised, complete nested draft"
    payload["revision_number"] = created["revision_number"]
    revised = client.put(f"/api/courses/{created['id']}/authoring-draft", json=payload)
    assert revised.status_code == 200, revised.text
    assert client.post(f"/api/courses/{created['id']}/submit-review").status_code == 200

    app.dependency_overrides[get_current_user] = lambda: reviewer
    reviewed = client.post(
        f"/api/courses/{created['id']}/review",
        json={"decision": "approved", "feedback": "Ready for learners."},
    )
    assert reviewed.status_code == 200, reviewed.text
    assert reviewed.json()["lifecycle_state"] == "approved"

    published = client.post(f"/api/course-versions/{created['current_version_id']}/publish")
    assert published.status_code == 200, published.text
    db.expire_all()
    stored = db.query(Course).filter(Course.id == uuid.UUID(created["id"])).one()
    assert stored.revision_metadata["authoring_state"] == "published"
    assert stored.revision_metadata["published_snapshot"]["title"] == "Reviewable course"

    app.dependency_overrides[get_current_user] = lambda: author
    later_edit = payload | {"description": "Unpublished second-edition changes", "revision_number": revised.json()["revision_number"]}
    later = client.put(f"/api/courses/{created['id']}/authoring-draft", json=later_edit)
    assert later.status_code == 200, later.text
    db.expire_all()
    stored = db.query(Course).filter(Course.id == uuid.UUID(created["id"])).one()
    published_versions = [version for version in stored.versions if version.status.value == "published"]
    draft_versions = [version for version in stored.versions if version.status.value == "draft"]
    assert len(published_versions) == 1
    assert len(draft_versions) == 1
    assert {unit.course_version_id for unit in stored.units} == {published_versions[0].id, draft_versions[0].id}
    learner_projection = serialize_course(stored, viewer_role="student")
    assert learner_projection.description == "A revised, complete nested draft"
    assert learner_projection.revision_metadata == {}


def test_representative_large_graph_stays_within_autosave_bounds(draft_context):
    _, _, organization = draft_context
    payload = {
        "title": "Large authoring graph",
        "description": "Performance fixture",
        "units": [
            {
                "title": f"Unit {unit_index + 1}",
                "lessons": [
                    {
                        "title": f"Lesson {unit_index + 1}.{lesson_index + 1}",
                        "activities": [
                            {"type": "reading", "title": f"Activity {activity_index + 1}", "content": "x" * 500}
                            for activity_index in range(3)
                        ],
                        "sources": [{"citation": "Representative source", "url": "https://example.com/source"}],
                    }
                    for lesson_index in range(5)
                ],
            }
            for unit_index in range(20)
        ],
    }
    started = perf_counter()
    created = client.post("/api/courses/authoring", headers=_headers(organization, "large-graph"), json=payload)
    create_seconds = perf_counter() - started
    assert created.status_code == 200, created.text
    assert create_seconds < 5
    assert len(created.content) < 1_500_000

    update = created.json()
    update["title"] = "Large authoring graph revised"
    started = perf_counter()
    saved = client.put(f"/api/courses/{created.json()['id']}/authoring-draft", json=update)
    save_seconds = perf_counter() - started
    assert saved.status_code == 200, saved.text
    assert save_seconds < 5
    assert len(saved.content) < 1_500_000
