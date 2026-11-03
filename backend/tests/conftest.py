from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.api.routes import analysis, upload
from backend.main import app
from backend.services import database


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setattr(database, "DATABASE_PATH", tmp_path / "nyayasetu-test.sqlite3")
    monkeypatch.setattr(database, "DOCUMENT_STORAGE_DIR", tmp_path / "uploads")
    monkeypatch.setattr(upload, "DOCUMENT_STORAGE_DIR", tmp_path / "uploads")
    monkeypatch.setattr(analysis, "DOCUMENT_STORAGE_DIR", tmp_path / "uploads")
    with TestClient(app) as test_client:
        yield test_client
