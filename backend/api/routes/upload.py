from __future__ import annotations

import logging
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

import anyio
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from backend.api.dependencies import get_current_user
from backend.models.schemas import DocumentUploadResponse
from backend.services.database import DOCUMENT_STORAGE_DIR, get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")
MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
CHUNK_BYTES = 1024 * 1024
ALLOWED_EXTENSIONS = {".pdf": "application/pdf", ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}


def _safe_filename(filename: str | None) -> str:
    normalized = (filename or "document").replace("\\", "/").split("/")[-1]
    normalized = re.sub(r"[^A-Za-z0-9._ -]", "_", normalized).strip(" .")
    return (normalized or "document")[:200]


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Invalid file"},
        401: {"description": "Invalid or missing local session"},
        413: {"description": "File exceeds 10 MiB"},
        415: {"description": "Unsupported or mismatched file type"},
        500: {"description": "Local storage or database unavailable"},
    },
)
async def upload_document(
    file: UploadFile = File(...),
    current_user: dict[str, Any] = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> DocumentUploadResponse:
    filename = _safe_filename(file.filename)
    extension = os.path.splitext(filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail={"code": "unsupported_media_type", "message": "Only PDF and DOCX files are supported."},
        )

    signature = await file.read(8)
    await file.seek(0)
    valid_signature = signature.startswith(b"%PDF-") if extension == ".pdf" else signature.startswith(b"PK")
    if not valid_signature:
        raise HTTPException(
            status_code=415,
            detail={"code": "file_type_mismatch", "message": "The file contents do not match its extension."},
        )

    uid = str(current_user["uid"])
    document_id = uuid.uuid4().hex
    storage_name = f"{document_id}{extension}"
    local_path = DOCUMENT_STORAGE_DIR / storage_name
    created_at = datetime.now(timezone.utc)
    size = 0
    try:
        DOCUMENT_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        async with await anyio.open_file(local_path, "wb") as destination:
            while chunk := await file.read(CHUNK_BYTES):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise HTTPException(
                        status_code=413,
                        detail={"code": "file_too_large", "message": "The maximum upload size is 10 MiB."},
                    )
                await destination.write(chunk)

        db.execute(
            "INSERT INTO documents (document_id, owner_uid, filename, storage_name, content_type, size_bytes, created_at, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (document_id, uid, filename, storage_name, ALLOWED_EXTENSIONS[extension], size, created_at.isoformat(), "uploaded"),
        )
        db.commit()
    except HTTPException:
        local_path.unlink(missing_ok=True)
        raise
    except Exception as exc:
        db.rollback()
        local_path.unlink(missing_ok=True)
        logger.exception("Local document upload failed")
        raise HTTPException(
            status_code=500,
            detail={"code": "upload_failed", "message": "The document could not be stored locally."},
        ) from exc
    finally:
        await file.close()

    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        created_at=created_at.isoformat(),
    )
