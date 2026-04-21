"""FastAPI application entrypoint.

- Mounts the three router modules under /api.
- Serves the built Vite SPA from frontend/dist when present.
- Configures CORS for local dev (same-origin in prod).
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from . import demo
from .deps import get_settings, limiter
from .logging_config import configure_logging
from .middleware import SecurityHeadersMiddleware
from .paths import ensure_runtime_dirs
from .routes import admin, insights, metrics, quote, quotes


def create_app() -> FastAPI:
    configure_logging()
    settings = get_settings()

    if "*" in settings.cors_origins_list and not os.environ.get("PYTEST_CURRENT_TEST"):
        raise RuntimeError(
            "CORS_ALLOW_ORIGINS=* is incompatible with allow_credentials=True. "
            "Set an explicit origin list in production."
        )

    ensure_runtime_dirs()
    demo.seed_if_enabled()

    is_prod = os.environ.get("ENV", "dev").lower() == "prod"
    app = FastAPI(
        title="Matrix Quote Web",
        version="0.1.0",
        description="Wraps the Matrix per-operation quoting engine for customer-facing estimation.",
        docs_url=None if is_prod else "/docs",
        redoc_url=None if is_prod else "/redoc",
        openapi_url=None if is_prod else "/openapi.json",
    )

    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    )

    app.include_router(metrics.router)
    app.include_router(quote.router)
    app.include_router(admin.router)
    app.include_router(quotes.router)
    app.include_router(insights.router)

    _mount_frontend(app)
    return app


def _mount_frontend(app: FastAPI) -> None:
    """Mount frontend/dist at /. Safe to call before the build exists."""
    dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
    if not dist.exists():
        return

    assets = dist / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    index = dist / "index.html"

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str) -> FileResponse:  # noqa: ARG001
        # Any non-/api path falls back to the SPA index so client-side
        # routing (React Router) works on refresh.
        return FileResponse(index)


app = create_app()
