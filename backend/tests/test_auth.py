from fastapi.testclient import TestClient


def test_register(client: TestClient):
    res = client.post("/api/auth/register", json={
        "email": "new@test.com",
        "password": "password123",
        "full_name": "New User",
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client: TestClient):
    client.post("/api/auth/register", json={
        "email": "dup@test.com", "password": "password123", "full_name": "User",
    })
    res = client.post("/api/auth/register", json={
        "email": "dup@test.com", "password": "password123", "full_name": "User",
    })
    assert res.status_code == 400


def test_register_short_password(client: TestClient):
    res = client.post("/api/auth/register", json={
        "email": "short@test.com", "password": "123", "full_name": "User",
    })
    assert res.status_code == 422


def test_login(client: TestClient):
    client.post("/api/auth/register", json={
        "email": "login@test.com", "password": "password123", "full_name": "User",
    })
    res = client.post("/api/auth/login", json={
        "email": "login@test.com", "password": "password123",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client: TestClient):
    client.post("/api/auth/register", json={
        "email": "wrong@test.com", "password": "password123", "full_name": "User",
    })
    res = client.post("/api/auth/login", json={
        "email": "wrong@test.com", "password": "wrongpass",
    })
    assert res.status_code == 401


def test_me_no_token(client: TestClient):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_with_token(client: TestClient, user_headers: dict):
    res = client.get("/api/auth/me", headers=user_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "user@test.com"


def test_admin_check_employee_forbidden(client: TestClient, user_headers: dict):
    res = client.get("/api/admin/check", headers=user_headers)
    assert res.status_code == 403


def test_admin_check_allowed(client: TestClient, admin_headers: dict):
    res = client.get("/api/admin/check", headers=admin_headers)
    assert res.status_code == 200
