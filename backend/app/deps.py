"""Settings, auth dependencies, and shared helpers."""

from __future__ import annotations

import hmac
import os
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status
from jwt import PyJWTError
from pydantic_settings import BaseSettings, SettingsConfigDict
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=[])


class Settings(BaseSettings):
    admin_password: str = ""
    admin_jwt_secret: str = ""
    admin_token_expiry_hours: int = 12
    cors_allow_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_allow_origins.split(",") if o.strip()]


def _in_test_env() -> bool:
    return bool(os.environ.get("PYTEST_CURRENT_TEST"))


def _assert_production_secrets(s: Settings) -> None:
    if _in_test_env():
        return
    if not s.admin_password:
        raise RuntimeError(
            "ADMIN_PASSWORD must be set (non-empty) outside the test env."
        )
    if not s.admin_jwt_secret:
        raise RuntimeError(
            "ADMIN_JWT_SECRET must be set (non-empty) outside the test env."
        )
    if len(s.admin_jwt_secret) < 32:
        raise RuntimeError(
            "ADMIN_JWT_SECRET must be at least 32 characters."
        )


@lru_cache
def get_settings() -> Settings:
    s = Settings()
    _assert_production_secrets(s)
    return s


JWT_ALGORITHM = "HS256"


def create_admin_token(
    settings: Settings, display_name: str = "admin"
) -> tuple[str, datetime]:
    expires_at = datetime.now(UTC) + timedelta(
        hours=settings.admin_token_expiry_hours
    )
    claims = {
        "sub": "admin",
        "name": display_name or "admin",
        "iat": datetime.now(UTC),
        "iss": "matrix-quote-web",
        "exp": expires_at,
    }
    token = jwt.encode(claims, settings.admin_jwt_secret, algorithm=JWT_ALGORITHM)
    return token, expires_at


def verify_admin_password(settings: Settings, supplied: str) -> bool:
    if not settings.admin_password:
        return False
    return hmac.compare_digest(settings.admin_password, supplied)


def require_admin(
    authorization: Annotated[str | None, Header()] = None,
    settings: Annotated[Settings, Depends(get_settings)] = None,
) -> dict[str, str]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = authorization.split(" ", 1)[1]
    try:
        claims = jwt.decode(
            token,
            settings.admin_jwt_secret,
            algorithms=[JWT_ALGORITHM],
            issuer="matrix-quote-web",
        )
    except PyJWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if claims.get("sub") != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token subject",
        )
    return {"sub": "admin", "name": str(claims.get("name") or "admin")}
