import uuid
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes import threads as threads_router, posts as posts_router
from app.database import get_db
from app.deps import get_current_user
from app.models import User, Thread

app = FastAPI()
app.include_router(threads_router.router, prefix="/api/forum")
app.include_router(posts_router.router, prefix="/api/forum")

@pytest.fixture
def test_db(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield db_session
    app.dependency_overrides = {}

@pytest.fixture
def user(test_db):
    u = User(
        id=uuid.uuid4(),
        firstname="Forum",
        lastname="User",
        username=f"user_{uuid.uuid4()}",
        email=f"user_{uuid.uuid4()}@example.com",
        hashed_password="x",
    )
    test_db.add(u)
    test_db.commit()
    return u

def test_create_and_list_threads(test_db, user):
    app.dependency_overrides[get_current_user] = lambda: user
    client = TestClient(app)
    resp = client.post(
        "/api/forum/threads",
        json={"title": "First"}
    )
    assert resp.status_code == 200
    thread_id = resp.json()["id"]

    resp = client.get("/api/forum/threads")
    assert resp.status_code == 200
    threads = resp.json()
    assert any(t["id"] == thread_id for t in threads)


def test_create_and_list_posts(test_db, user):
    t = Thread(id=uuid.uuid4(), user_id=user.id, title="T")
    test_db.add(t)
    test_db.commit()
    test_db.refresh(t)
    app.dependency_overrides[get_current_user] = lambda: user

    client = TestClient(app)
    resp = client.post(
        "/api/forum/posts",
        json={"thread_id": str(t.id), "content": "Hi"}
    )
    assert resp.status_code == 200
    post_id = resp.json()["id"]

    resp = client.get("/api/forum/posts")
    assert resp.status_code == 200
    posts = resp.json()
    assert any(p["id"] == post_id for p in posts)


def test_anonymous_forum_mutations_are_rejected(test_db, user):
    thread = Thread(id=uuid.uuid4(), user_id=user.id, title="Protected")
    test_db.add(thread)
    test_db.commit()
    client = TestClient(app)

    assert client.post("/api/forum/threads", json={"title": "No"}).status_code == 401
    assert client.put(f"/api/forum/threads/{thread.id}", json={"title": "No"}).status_code == 401
    assert client.delete(f"/api/forum/threads/{thread.id}").status_code == 401
    assert client.post(
        "/api/forum/posts", json={"thread_id": str(thread.id), "content": "No"}
    ).status_code == 401


def test_forum_ownership_is_immutable_and_non_owner_is_denied(test_db, user):
    other = User(
        id=uuid.uuid4(), firstname="Other", lastname="User",
        username=f"other_{uuid.uuid4()}", email=f"other_{uuid.uuid4()}@example.com",
        hashed_password="x", role="student",
    )
    thread = Thread(id=uuid.uuid4(), user_id=user.id, title="Owned")
    test_db.add_all([other, thread])
    test_db.commit()
    app.dependency_overrides[get_current_user] = lambda: other
    client = TestClient(app)

    denied = client.put(f"/api/forum/threads/{thread.id}", json={"title": "Stolen"})
    mass_assignment = client.put(
        f"/api/forum/threads/{thread.id}",
        json={"title": "Stolen", "user_id": str(other.id)},
    )

    assert denied.status_code == 403
    assert mass_assignment.status_code == 422
    test_db.refresh(thread)
    assert thread.user_id == user.id
    assert thread.title == "Owned"


def test_platform_moderator_can_delete_another_users_post(test_db, user):
    moderator = User(
        id=uuid.uuid4(), firstname="Forum", lastname="Moderator",
        username=f"moderator_{uuid.uuid4()}", email=f"moderator_{uuid.uuid4()}@example.com",
        hashed_password="x", role="admin",
    )
    thread = Thread(id=uuid.uuid4(), user_id=user.id, title="T")
    test_db.add_all([moderator, thread])
    test_db.flush()
    from app.models import Post
    post = Post(id=uuid.uuid4(), thread_id=thread.id, user_id=user.id, content="Moderate")
    test_db.add(post)
    test_db.commit()
    app.dependency_overrides[get_current_user] = lambda: moderator
    client = TestClient(app)

    response = client.delete(f"/api/forum/posts/{post.id}")

    assert response.status_code == 200
    assert test_db.query(Post).filter(Post.id == post.id).first() is None
