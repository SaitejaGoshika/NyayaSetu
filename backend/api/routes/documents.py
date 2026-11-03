from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from backend.api.dependencies import get_current_user
from backend.models.schemas import DocumentRecord
from backend.services.database import get_db

router = APIRouter(prefix="/api")


@router.get("/documents", response_model=list[DocumentRecord])
def list_documents(
    current_user: dict[str, Any] = Depends(get_current_user),
    db: sqlite3.Connection = Depends(get_db),
) -> list[DocumentRecord]:
    rows = db.execute(
        "SELECT document_id, filename, created_at, status FROM documents WHERE owner_uid = ? ORDER BY created_at DESC",
        (str(current_user["uid"]),),
    ).fetchall()
    return [DocumentRecord(**dict(row)) for row in rows]
