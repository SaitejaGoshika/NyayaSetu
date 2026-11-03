from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

SESSION_COOKIE_NAME = "nyayasetu_session"
SESSION_TTL_SECONDS = 8 * 60 * 60
_DEVELOPMENT_SECRET = secrets.token_urlsafe(32)


def _session_secret() -> str:
    configured_secret = os.getenv("JWT_SECRET_KEY", "").strip()
    is_production = os.getenv("NYAYASETU_ENV", "development").lower() == "production"
    if is_production and len(configured_secret) < 32:
        raise RuntimeError("Set JWT_SECRET_KEY to a random secret of at least 32 characters in production.")
    return configured_secret or _DEVELOPMENT_SECRET


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    derived_key = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return "scrypt$16384$8$1${}${}".format(
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(derived_key).decode("ascii"),
    )


def verify_password(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, n_value, r_value, p_value, salt_value, hash_value = encoded_hash.split("$", maxsplit=5)
        if algorithm != "scrypt" or (n_value, r_value, p_value) != ("16384", "8", "1"):
            return False
        salt = base64.urlsafe_b64decode(salt_value.encode("ascii"))
        expected = base64.urlsafe_b64decode(hash_value.encode("ascii"))
        actual = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=len(expected))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_session_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": user_id, "iat": now, "exp": now + timedelta(seconds=SESSION_TTL_SECONDS)},
        _session_secret(),
        algorithm="HS256",
    )


def decode_session_token(token: str) -> dict[str, object]:
    return jwt.decode(token, _session_secret(), algorithms=["HS256"], options={"require": ["sub", "exp"]})
