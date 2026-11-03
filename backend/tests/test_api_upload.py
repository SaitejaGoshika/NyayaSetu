from io import BytesIO

from docx import Document
from fastapi.testclient import TestClient

from backend.services import database


def create_docx_bytes() -> bytes:
    document = Document()
    document.add_paragraph("Payment shall be made within 60 days. A 12-month lock-in period applies.")
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

    client.post("/api/auth/logout")
    other_signup = client.post(
        "/api/auth/signup",
        json={"display_name": "Second User", "email": "second@example.com", "password": "correct-horse-42"},
    )
    assert other_signup.status_code == 201
    assert client.get("/api/documents").json() == []
    assert client.post(f"/api/analyze/{document_id}").status_code == 404
