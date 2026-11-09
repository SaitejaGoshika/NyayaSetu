from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient

from backend.services import database


def create_docx_bytes(text: str | None = None) -> bytes:
    document = Document()
    document.add_paragraph(text or "Payment shall be made within 60 days. A 12-month lock-in period applies.")
    stream = BytesIO()
    document.save(stream)
    return stream.getvalue()


def test_upload_streams_to_local_disk_and_analysis_is_account_scoped(client: TestClient) -> None:
    signup = client.post(
        "/api/auth/signup",
        json={"display_name": "First User", "email": "first@example.com", "password": "correct-horse-42"},
    )
    assert signup.status_code == 201

    upload = client.post(
        "/api/upload",
        files={"file": ("agreement.docx", create_docx_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert upload.status_code == 201
    document_id = upload.json()["documentId"]
    connection = database.connect_database()
    try:
        row = connection.execute(
            "SELECT storage_name, owner_uid FROM documents WHERE document_id = ?",
            (document_id,),
        ).fetchone()
    finally:
        connection.close()
    assert row is not None
    assert row["owner_uid"] == signup.json()["user"]["uid"]
    assert (database.DOCUMENT_STORAGE_DIR / row["storage_name"]).is_file()

    analysis = client.post(f"/api/analyze/{document_id}")
    assert analysis.status_code == 200
    assert "payment shall be made within 60 days" in analysis.json()["extractedText"].lower()
    assert [finding["riskLevel"] for finding in analysis.json()["findings"]] == ["high", "medium"]
    assert analysis.json()["rulesVersion"]

    client.post("/api/auth/logout")
    other_signup = client.post(
        "/api/auth/signup",
        json={"display_name": "Second User", "email": "second@example.com", "password": "correct-horse-42"},
    )
    assert other_signup.status_code == 201
    assert client.get("/api/documents").json() == []
    assert client.post(f"/api/analyze/{document_id}").status_code == 404


def test_analysis_is_stored_and_reused_for_current_rules_version(client: TestClient) -> None:
    signup = client.post(
        "/api/auth/signup",
        json={"display_name": "First User", "email": "stored@example.com", "password": "correct-horse-42"},
    )
    document = client.post(
        "/api/upload",
        files={"file": ("agreement.docx", create_docx_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    document_id = document.json()["documentId"]

    first = client.post(f"/api/analyze/{document_id}")
    second = client.post(f"/api/analyze/{document_id}")

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["extractedText"] == first.json()["extractedText"]
    assert second.json()["findings"] == first.json()["findings"]


def test_analysis_reanalyzes_when_rules_version_changes(client: TestClient) -> None:
    signup = client.post(
        "/api/auth/signup",
        json={"display_name": "First User", "email": "version@example.com", "password": "correct-horse-42"},
    )
    document = client.post(
        "/api/upload",
        files={"file": ("agreement.docx", create_docx_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    document_id = document.json()["documentId"]
    first = client.post(f"/api/analyze/{document_id}")
    assert first.status_code == 200

    connection = database.connect_database()
    try:
        connection.execute("UPDATE analyses SET rules_version = ? WHERE document_id = ?", ("stale-rules", document_id))
        connection.commit()
    finally:
        connection.close()

    second = client.post(f"/api/analyze/{document_id}")
    assert second.status_code == 200
    assert second.json()["rulesVersion"]


def test_document_delete_removes_file_and_related_analysis(client: TestClient) -> None:
    signup = client.post(
        "/api/auth/signup",
        json={"display_name": "First User", "email": "delete@example.com", "password": "correct-horse-42"},
    )
    document = client.post(
        "/api/upload",
        files={"file": ("agreement.docx", create_docx_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    document_id = document.json()["documentId"]
    client.post(f"/api/analyze/{document_id}")

    connection = database.connect_database()
    try:
        storage_name = connection.execute("SELECT storage_name FROM documents WHERE document_id = ?", (document_id,)).fetchone()["storage_name"]
    finally:
        connection.close()

    response = client.delete(f"/api/documents/{document_id}")
    assert response.status_code == 204
    assert client.get("/api/documents").json() == []
    assert not (database.DOCUMENT_STORAGE_DIR / storage_name).exists()
    connection = database.connect_database()
    try:
        assert connection.execute("SELECT COUNT(*) FROM analyses WHERE document_id = ?", (document_id,)).fetchone()[0] == 0
    finally:
        connection.close()


def test_compare_route_returns_changed_findings_and_clauses(client: TestClient) -> None:
    client.post(
        "/api/auth/signup",
        json={"display_name": "First User", "email": "compare@example.com", "password": "correct-horse-42"},
    )

    first = client.post(
        "/api/upload",
        files={"file": ("v1.docx", create_docx_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    second = client.post(
        "/api/upload",
        files={"file": ("v2.docx", create_docx_bytes("The agreement states the parties will work together respectfully."), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )

    first_id = first.json()["documentId"]
    second_id = second.json()["documentId"]
    client.post(f"/api/analyze/{first_id}")
    client.post(f"/api/analyze/{second_id}")

    response = client.post("/api/compare", json={"primaryDocumentId": first_id, "secondaryDocumentId": second_id})
    assert response.status_code == 200
    payload = response.json()
    assert payload["removedFindings"]
    assert payload["changedClauses"]


def test_report_export_returns_document_bytes(client: TestClient) -> None:
    client.post(
        "/api/auth/signup",
        json={"display_name": "First User", "email": "report@example.com", "password": "correct-horse-42"},
    )
    document = client.post(
        "/api/upload",
        files={"file": ("agreement.docx", create_docx_bytes(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    document_id = document.json()["documentId"]
    client.post(f"/api/analyze/{document_id}")

    response = client.get(f"/api/analyze/{document_id}/report?format=docx")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    assert "agreement.docx".lower() in response.headers["content-disposition"].lower()
