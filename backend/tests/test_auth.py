"""
Unit tests for Authentication, JWT, and User management.
"""

from middleware import decode_jwt


def test_register_first_user_is_admin(client):
    payload = {
        "email": "first@example.com",
        "password": "Password123!",
        "display_name": "First Admin",
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["email"] == "first@example.com"
    assert data["user"]["role"] == "admin"
    assert "token" in data

    # Verify JWT validity
    decoded = decode_jwt(data["token"])
    assert decoded["sub"] == data["user"]["id"]
    assert decoded["role"] == "admin"


def test_register_second_user_is_regular(client, admin_user):
    # admin_user already exists
    payload = {
        "email": "second@example.com",
        "password": "Password123!",
        "display_name": "Second User",
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["role"] == "user"


def test_register_duplicate_email_rejected(client, regular_user):
    user, _ = regular_user
    payload = {
        "email": user.email,
        "password": "Password123!",
        "display_name": "Duplicate",
    }
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 409


def test_login_invalid_password(client, regular_user):
    user, _ = regular_user
    resp = client.post("/api/auth/login", json={"email": user.email, "password": "WrongPassword"})
    assert resp.status_code == 401


def test_login_nonexistent_email(client):
    resp = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "Password123!"})
    assert resp.status_code == 401


def test_get_current_user_profile(client, regular_user):
    user, headers = regular_user
    resp = client.get("/api/auth/me", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == user.id
    assert data["email"] == user.email


def test_logout_revokes_token(client, regular_user):
    _, headers = regular_user
    resp_logout = client.post("/api/auth/logout", headers=headers)
    assert resp_logout.status_code == 200

    # Once revoked, /api/auth/me should reject with 401
    resp_me = client.get("/api/auth/me", headers=headers)
    assert resp_me.status_code == 401
