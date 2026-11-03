from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_current_user
from backend.models.schemas import AnalysisResponse
from backend.services.analyzer import analyze_text
from backend.services.errors import ExtractionError
from backend.services.extractor import extract_text
from backend.services.database import DOCUMENT_STORAGE_DIR, get_db

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
        extension = Path(str(record["filename"])).suffix.lower()
        extracted_text = extract_text(document_path, extension)
        db.execute("UPDATE documents SET status = ? WHERE document_id = ? AND owner_uid = ?", ("analyzed", document_id, uid))
        db.commit()
        return AnalysisResponse(
            document_id=document_id,
            filename=str(record["filename"]),
            extracted_text=extracted_text,
            findings=analyze_text(extracted_text),
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
