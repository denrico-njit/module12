# tests/integration/test_auth_endpoints.py

import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import get_db


@pytest.fixture
def client(db_session):
    """TestClient wired to the test DB session."""
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def register_payload():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "username": "johndoe",
        "password": "SecurePass1!",
        "confirm_password": "SecurePass1!"
    }

# Register tests
def test_register_success(client, register_payload):
    response = client.post("/auth/register", json=register_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "johndoe"
    assert data["email"] == "john@example.com"
    assert "id" in data
    assert "password" not in data


def test_register_duplicate(client, register_payload):
    client.post("/auth/register", json=register_payload)
    response = client.post("/auth/register", json=register_payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["error"]


def test_register_password_mismatch(client, register_payload):
    register_payload["confirm_password"] = "DifferentPass1!"
    response = client.post("/auth/register", json=register_payload)
    assert response.status_code == 400
    assert "Passwords do not match" in response.json()["error"]


def test_register_weak_password(client, register_payload):
    register_payload["password"] = "weakpassword"
    register_payload["confirm_password"] = "weakpassword"
    response = client.post("/auth/register", json=register_payload)
    assert response.status_code == 400

# Login tests
def test_login_success(client, register_payload):
    client.post("/auth/register", json=register_payload)
    response = client.post("/auth/login", json={
        "username": "johndoe",
        "password": "SecurePass1!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["username"] == "johndoe"
    assert data["email"] == "john@example.com"
    assert "password" not in data


def test_login_wrong_password(client, register_payload):
    client.post("/auth/register", json=register_payload)
    response = client.post("/auth/login", json={
        "username": "johndoe",
        "password": "WrongPass1!"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={
        "username": "nobody",
        "password": "SecurePass1!"
    })
    assert response.status_code == 401


def test_login_with_email(client, register_payload):
    client.post("/auth/register", json=register_payload)
    response = client.post("/auth/login", json={
        "username": "john@example.com",
        "password": "SecurePass1!"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
