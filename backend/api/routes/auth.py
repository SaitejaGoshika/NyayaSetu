from __future__ import annotations

import re
import sqlite3
import uuid
import os
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response, status

from backend.api.dependencies import get_current_user
from backend.models.schemas import AuthSessionResponse, AuthUser, LoginRequest, SignupRequest
from backend.services.database import get_db
from backend.services.security import SESSION_COOKIE_NAME, SESSION_TTL_SECONDS, create_session_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _user_response(user: sqlite3.Row) -> AuthUser:
    return AuthUser(uid=str(user["id"]), email=str(user["email"]), display_name=str(user["display_name"]))


def _set_session(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=create_session_token(user_id),
        max_age=SESSION_TTL_SECONDS,
        httponly=True,
        secure=os.getenv("NYAYASETU_ENV", "development").lower() == "production",
        samesite="lax",
        path="/",
    )


def _validate_email(email: str) -> str:
    normalized = email.strip().lower()
    if not EMAIL_PATTERN.fullmatch(normalized):
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_email", "message": "Enter a valid email address."},
        )
    return normalized


@router.post("/signup", response_model=AuthSessionResponse, status_code=status.HTTP_201_CREATED)
def signup(
    request: SignupRequest,
    response: Response,
    db: sqlite3.Connection = Depends(get_db),
) -> AuthSessionResponse:
    email = _validate_email(request.email)
    display_name = request.display_name.strip()
    if not display_name:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_display_name", "message": "Enter your name."},
        )

    user_id = uuid.uuid4().hex
    try:
        db.execute(
            "INSERT INTO users (id, email, display_name, password_hash, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, email, display_name, hash_password(request.password), datetime.now(timezone.utc).isoformat()),
        )
        db.commit()
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "account_exists", "message": "An account already exists for this email. Sign in instead."},
        ) from exc

    user = db.execute("SELECT id, email, display_name FROM users WHERE id = ?", (user_id,)).fetchone()
    if user is None:
        raise HTTPException(status_code=500, detail={"code": "account_creation_failed", "message": "The account could not be created."})
    _set_session(response, user_id)
    return AuthSessionResponse(user=_user_response(user))


@router.post("/login", response_model=AuthSessionResponse)
def login(
    request: LoginRequest,
    response: Response,
    db: sqlite3.Connection = Depends(get_db),
) -> AuthSessionResponse:
    email = _validate_email(request.email)
    user = db.execute(
        "SELECT id, email, display_name, password_hash FROM users WHERE email = ? COLLATE NOCASE",
        (email,),
    ).fetchone()
    if user is None or not verify_password(request.password, str(user["password_hash"])):
        raise HTTPException(
            status_code=401,
            detail={"code": "invalid_credentials", "message": "The email or password is incorrect."},
        )

    _set_session(response, str(user["id"]))
    return AuthSessionResponse(user=_user_response(user))


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.delete_cookie(key=SESSION_COOKIE_NAME, path="/", httponly=True, samesite="lax")
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.get("/me", response_model=AuthUser)
def current_session(current_user: dict[str, Any] = Depends(get_current_user)) -> AuthUser:
    return AuthUser(
        uid=str(current_user["uid"]),
        email=str(current_user["email"]),
        display_name=str(current_user["display_name"]),
    )
