# tests/integration/test_calculation_endpoints.py

import pytest
from fastapi.testclient import TestClient
from main import app
from app.database import get_db


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Register a user and return a valid Authorization header."""
    client.post("/auth/register", json={
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "username": "johndoe",
        "password": "SecurePass1!",
        "confirm_password": "SecurePass1!"
    })
    response = client.post("/auth/login", json={
        "username": "johndoe",
        "password": "SecurePass1!"
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def calc_payload():
    return {"a": 10, "b": 5, "operation": "add"}

# ------------------------------------------------------------------------------
# Add tests
# ------------------------------------------------------------------------------

def test_add_calculation(client, auth_headers, calc_payload):
    response = client.post("/calculations", json=calc_payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["result"] == 15.0
    assert data["operation"] == "add"
    assert "id" in data
    assert "user_id" in data


def test_add_calculation_divide_by_zero(client, auth_headers):
    response = client.post("/calculations", json={"a": 10, "b": 0, "operation": "divide"}, headers=auth_headers)
    assert response.status_code == 400


def test_add_calculation_unauthenticated(client, calc_payload):
    response = client.post("/calculations", json=calc_payload)
    assert response.status_code == 401


# ------------------------------------------------------------------------------
# Browse tests
# ------------------------------------------------------------------------------

def test_browse_calculations(client, auth_headers, calc_payload):
    client.post("/calculations", json=calc_payload, headers=auth_headers)
    client.post("/calculations", json={"a": 3, "b": 2, "operation": "multiply"}, headers=auth_headers)
    response = client.get("/calculations", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_browse_calculations_empty(client, auth_headers):
    response = client.get("/calculations", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


# ------------------------------------------------------------------------------
# Read tests
# ------------------------------------------------------------------------------

def test_read_calculation(client, auth_headers, calc_payload):
    created = client.post("/calculations", json=calc_payload, headers=auth_headers).json()
    response = client.get(f"/calculations/{created['id']}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_read_calculation_not_found(client, auth_headers):
    response = client.get("/calculations/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert response.status_code == 404


# ------------------------------------------------------------------------------
# Edit tests
# ------------------------------------------------------------------------------

def test_edit_calculation(client, auth_headers, calc_payload):
    created = client.post("/calculations", json=calc_payload, headers=auth_headers).json()
    response = client.put(
        f"/calculations/{created['id']}",
        json={"a": 20, "b": 5, "operation": "subtract"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 15.0
    assert data["operation"] == "subtract"


def test_edit_calculation_not_found(client, auth_headers):
    response = client.put(
        "/calculations/00000000-0000-0000-0000-000000000000",
        json={"a": 1, "b": 1, "operation": "add"},
        headers=auth_headers
    )
    assert response.status_code == 404


# ------------------------------------------------------------------------------
# Delete tests
# ------------------------------------------------------------------------------

def test_delete_calculation(client, auth_headers, calc_payload):
    created = client.post("/calculations", json=calc_payload, headers=auth_headers).json()
    response = client.delete(f"/calculations/{created['id']}", headers=auth_headers)
    assert response.status_code == 204
    # Verify it's gone
    response = client.get(f"/calculations/{created['id']}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_calculation_not_found(client, auth_headers):
    response = client.delete("/calculations/00000000-0000-0000-0000-000000000000", headers=auth_headers)
    assert response.status_code == 404
