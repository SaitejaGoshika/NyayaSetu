from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_current_user
from backend.models.schemas import AnalysisResponse
from backend.services.analyzer import RULES_VERSION, analyze_text
from backend.services.database import DOCUMENT_STORAGE_DIR, get_db
from backend.services.errors import ExtractionError
from backend.services.extractor import extract_text

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


@router.post(
    "/analyze/{document_id}",
    response_model=AnalysisResponse,
    responses={
        400: {"description": "Corrupt or unreadable document"},
        401: {"description": "Invalid or missing local session"},
        404: {"description": "Document not found"},
        415: {"description": "Unsupported document type"},
        500: {"description": "Local storage or database unavailable"},
    },
)
def analyze_document(
    document_id: str,
    force: bool = False,
    current_user: dict[str, Any] = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> AnalysisResponse:
    uid = str(current_user["uid"])
    record = db.execute(
        "SELECT document_id, filename, storage_name, status FROM documents WHERE document_id = ? AND owner_uid = ?",
        (document_id, uid),
    ).fetchone()
    if record is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "document_not_found", "message": "The requested document was not found."},
        )

    root = DOCUMENT_STORAGE_DIR.resolve()
    document_path = (root / str(record["storage_name"])).resolve()
    if document_path.parent != root:
        raise HTTPException(
            status_code=404,
            detail={"code": "document_not_found", "message": "The requested document was not found."},
        )
    try:
        existing = db.execute(
            "SELECT id, rules_version, extracted_text, findings_json FROM analyses WHERE document_id = ? AND owner_uid = ? ORDER BY created_at DESC LIMIT 1",
            (document_id, uid),
        ).fetchone()
        if not force and existing is not None and existing["rules_version"] == RULES_VERSION:
            findings = json.loads(existing["findings_json"])
            return AnalysisResponse(
                document_id=document_id,
                filename=str(record["filename"]),
                extracted_text=existing["extracted_text"],
                findings=findings,
                rules_version=RULES_VERSION,
            )

        extension = Path(str(record["filename"])).suffix.lower()
        extracted_text = extract_text(document_path, extension)
        findings = analyze_text(extracted_text)
        findings_json = json.dumps([finding.model_dump(mode="json", by_alias=True) for finding in findings], ensure_ascii=False)
        created_at = datetime.now(timezone.utc).isoformat()
        if existing is not None and existing["rules_version"] == RULES_VERSION:
            db.execute(
                "UPDATE analyses SET created_at = ?, extracted_text = ?, findings_json = ? WHERE id = ?",
                (created_at, extracted_text, findings_json, existing["id"]),
            )
        else:
            db.execute(
                "INSERT INTO analyses (id, document_id, owner_uid, rules_version, created_at, extracted_text, findings_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (uuid.uuid4().hex, document_id, uid, RULES_VERSION, created_at, extracted_text, findings_json),
            )
        db.execute("UPDATE documents SET status = ? WHERE document_id = ? AND owner_uid = ?", ("analyzed", document_id, uid))
        db.commit()
        return AnalysisResponse(
            document_id=document_id,
            filename=str(record["filename"]),
            extracted_text=extracted_text,
            findings=findings,
            rules_version=RULES_VERSION,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail={"code": "document_file_missing", "message": "The local document file could not be found."},
        ) from exc
    except ExtractionError:
        raise
    except sqlite3.Error as exc:
        logger.exception("Local document metadata update failed")
        raise HTTPException(
            status_code=500,
            detail={"code": "database_operation_failed", "message": "Document analysis could not be recorded."},
        ) from exc
