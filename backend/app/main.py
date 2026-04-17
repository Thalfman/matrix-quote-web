"""FastAPI application entrypoint.

- Mounts the three router modules under /api.
- Serves the built Vite SPA from frontend/dist when present.
- Configures CORS for local dev (same-origin in prod).
"""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import demo
from .deps import get_settings
from .paths import ensure_runtime_dirs
from .routes import admin, insights, metrics, quote, quotes


def create_app() -> FastAPI:
    settings = get_settings()
    ensure_runtime_dirs()
    demo.seed_if_enabled()

    app = FastAPI(
        title="Matrix Quote Web",
        version="0.1.0",
        description="Wraps the Matrix per-operation quoting engine for customer-facing estimation.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
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
