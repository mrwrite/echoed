import uuid
import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.routes import threads as threads_router, posts as posts_router
from app.database import get_db
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
    client = TestClient(app)
    resp = client.post(
        "/api/forum/threads",
        json={"user_id": str(user.id), "title": "First"}
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

    client = TestClient(app)
    resp = client.post(
        "/api/forum/posts",
        json={"thread_id": str(t.id), "user_id": str(user.id), "content": "Hi"}
    )
    assert resp.status_code == 200
    post_id = resp.json()["id"]

    resp = client.get("/api/forum/posts")
    assert resp.status_code == 200
    posts = resp.json()
    assert any(p["id"] == post_id for p in posts)
