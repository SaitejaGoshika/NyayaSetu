import pytest
from fastapi.testclient import TestClient

from backend.services.security import create_session_token


def test_api_root_reports_backend_status(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"service": "NyayaSetu API", "status": "ok"}


def test_document_history_requires_local_session(client: TestClient) -> None:
    response = client.get("/api/documents")

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "missing_session"


def test_signup_login_and_logout_use_http_only_session(client: TestClient) -> None:
    signup = client.post(
        "/api/auth/signup",
        json={"display_name": "Test User", "email": "Test@Example.com", "password": "correct-horse-42"},
    )
    assert signup.status_code == 201
    assert signup.json()["user"]["email"] == "test@example.com"
    assert "httponly" in signup.headers["set-cookie"].lower()
    assert client.get("/api/auth/me").json()["displayName"] == "Test User"
    assert client.get("/api/documents").json() == []

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 204
    assert client.get("/api/auth/me").status_code == 401

    login = client.post("/api/auth/login", json={"email": "test@example.com", "password": "correct-horse-42"})
    assert login.status_code == 200
    assert client.get("/api/auth/me").json()["uid"] == signup.json()["user"]["uid"]


def test_login_rejects_wrong_password(client: TestClient) -> None:
    client.post(
        "/api/auth/signup",
        json={"display_name": "Test User", "email": "test@example.com", "password": "correct-horse-42"},
    )

    response = client.post("/api/auth/login", json={"email": "test@example.com", "password": "wrong-password"})

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "invalid_credentials"


def test_production_requires_configured_session_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NYAYASETU_ENV", "production")
    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        create_session_token("user-id")
