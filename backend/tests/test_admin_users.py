import uuid

from fastapi.testclient import TestClient

from app.auth import get_current_user
from app.database import get_db
from app.main import app
from app.models import User


def _user(role: str, prefix: str) -> User:
    suffix = uuid.uuid4().hex[:8]
    return User(
        id=uuid.uuid4(),
        firstname=prefix.title(),
        lastname="User",
        username=f"{prefix}_{suffix}",
        email=f"{prefix}_{suffix}@example.test",
        hashed_password="unchanged-password-hash",
        role=role,
    )


def _client(db_session, current_user: User) -> TestClient:
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_current_user] = lambda: current_user
    return TestClient(app)


def test_admin_can_fetch_user_detail_by_uuid_on_sqlite(db_session):
    admin = _user("admin", "admin")
    student = _user("student", "student")
    db_session.add_all([admin, student])
    db_session.commit()

    client = _client(db_session, admin)
    try:
        response = client.get(f"/api/users/{student.id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == str(student.id)
    assert response.json()["role"] == "student"


def test_admin_can_update_user_role_by_uuid_without_changing_password(db_session):
    admin = _user("admin", "admin")
    student = _user("student", "student")
    db_session.add_all([admin, student])
    db_session.commit()

    client = _client(db_session, admin)
    try:
        response = client.put(
            f"/api/users/{student.id}",
            json={
                "firstname": student.firstname,
                "lastname": student.lastname,
                "username": student.username,
                "email": student.email,
                "password": "",
                "role": "teacher",
            },
        )
    finally:
        app.dependency_overrides.clear()

    db_session.refresh(student)
    assert response.status_code == 200
    assert student.role == "teacher"
    assert student.hashed_password == "unchanged-password-hash"


def test_static_student_list_route_is_not_shadowed_by_user_detail(db_session):
    teacher = _user("teacher", "teacher")
    student = _user("student", "student")
    db_session.add_all([teacher, student])
    db_session.commit()

    client = _client(db_session, teacher)
    try:
        response = client.get("/api/users/students")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [str(student.id)]
