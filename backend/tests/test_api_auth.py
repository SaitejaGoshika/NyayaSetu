from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.ml.predictor import CasePredictor, case_predictor
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


def test_prediction_status_explains_missing_model_after_sign_in(client: TestClient) -> None:
    signup = client.post(
        "/api/auth/signup",
        json={"display_name": "Test User", "email": "predict@example.com", "password": "correct-horse-42"},
    )
    assert signup.status_code == 201

    status_response = client.get("/api/predict/status")

    assert status_response.status_code == 200
    assert status_response.json()["available"] is False
    assert "No approved case prediction model is installed" in status_response.json()["message"]

    prediction_response = client.post(
        "/api/predict",
        json={"features": {"contract_value_inr": 250000, "days_overdue": 45, "has_written_agreement": 1}},
    )

    assert prediction_response.status_code == 503
    assert prediction_response.json()["detail"]["code"] == "model_unavailable"


def test_prediction_status_requires_sign_in(client: TestClient) -> None:
    response = client.get("/api/predict/status")

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "missing_session"


def test_legacy_model_path_setting_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CASE_MODEL_PATH", raising=False)
    monkeypatch.setenv("ML_MODEL_PATH", "ml/models/case_predictor.joblib")

    predictor = CasePredictor()

    assert predictor.model_path == Path("ml/models/case_predictor.joblib")


def test_prediction_uses_configured_model_feature_order(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class TestModel:
        feature_names_in_ = ["days_overdue", "has_written_agreement", "contract_value_inr"]
        classes_ = ["review", "resolved"]

        def predict_proba(self, rows: list[list[float]]) -> list[list[float]]:
            assert rows == [[45.0, 1.0, 250000.0]]
            return [[0.35, 0.65]]

    signup = client.post(
        "/api/auth/signup",
        json={"display_name": "Test User", "email": "model@example.com", "password": "correct-horse-42"},
    )
    assert signup.status_code == 201
    monkeypatch.setattr(case_predictor, "_model", TestModel())

    status_response = client.get("/api/predict/status")
    prediction_response = client.post(
        "/api/predict",
        json={"features": {"contract_value_inr": 250000, "days_overdue": 45, "has_written_agreement": 1}},
    )

    assert status_response.json()["available"] is True
    assert prediction_response.status_code == 200
    assert prediction_response.json() == {
        "classes": ["review", "resolved"],
        "probabilities": [0.35, 0.65],
    }
