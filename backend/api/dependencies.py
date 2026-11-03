from __future__ import annotations

import sqlite3
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from jwt import InvalidTokenError

from backend.services.database import get_db
from backend.services.security import SESSION_COOKIE_NAME, decode_session_token


def get_current_user(
    request: Request,
    db: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        authorization = request.headers.get("authorization", "")
        scheme, _, credentials = authorization.partition(" ")
        if scheme.lower() == "bearer" and credentials:
            token = credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "missing_session", "message": "Sign in to access this workspace."},
        )

    try:
        payload = decode_session_token(token)
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_session", "message": "Your session expired. Sign in again."},
        ) from exc

    user_id = payload.get("sub")
    user = db.execute(
        "SELECT id, email, display_name FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_session", "message": "Your account is unavailable. Sign in again."},
        )
    return {"uid": str(user["id"]), "email": str(user["email"]), "display_name": str(user["display_name"])}
