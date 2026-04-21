"""Tests for S-11: /docs, /redoc, and /openapi.json are hidden when ENV=prod.

When the SPA dist is present, FastAPI's /openapi.json and /docs routes are
disabled (openapi_url=None, docs_url=None) and the SPA catch-all serves
index.html instead. The test therefore asserts that the response is NOT the
OpenAPI schema JSON — not that it is a 404 — because the SPA fallback
intercepts the path with a 200+HTML.

In dev (default) the endpoints must return 200 application/json / HTML docs.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def prod_client(monkeypatch) -> TestClient:
    """TestClient built from an app instance created under ENV=prod."""
    monkeypatch.setenv("ENV", "prod")
    from backend.app.main import create_app
    return TestClient(create_app())


@pytest.fixture
def dev_client(monkeypatch) -> TestClient:
    """TestClient built under the default dev environment (ENV unset)."""
    monkeypatch.delenv("ENV", raising=False)
    from backend.app.main import create_app
    return TestClient(create_app())


# ---------------------------------------------------------------------------
# prod: /openapi.json must NOT expose the schema (content-type is not JSON
# and body does not contain the "openapi" field).
# ---------------------------------------------------------------------------

def test_openapi_schema_not_exposed_in_prod(prod_client: TestClient) -> None:
    """ENV=prod must not serve the OpenAPI schema at /openapi.json."""
    resp = prod_client.get("/openapi.json")
    # Two valid "hidden" topologies:
    #   - API-only (no SPA dist): FastAPI returns 404 with a JSON error body.
    #     Content-Type is application/json but the payload is {"detail":"..."},
    #     not a schema — the status-code check is what proves hidden.
    #   - SPA-mounted: catch-all returns 200 with index.html. Confirm the body
    #     does not carry the OpenAPI "openapi" key.
    assert resp.status_code in (200, 404), (
        f"Expected 200 (SPA fallback) or 404 (no SPA); got {resp.status_code}"
    )
    if resp.status_code == 200:
        assert '"openapi"' not in resp.text, (
            "OpenAPI schema content leaked in prod response body"
        )


def test_swagger_docs_not_exposed_in_prod(prod_client: TestClient) -> None:
    """ENV=prod must not serve Swagger UI at /docs."""
    resp = prod_client.get("/docs")
    # Swagger UI HTML would contain 'swagger-ui'; the SPA index.html will not.
    if resp.status_code == 200:
        assert "swagger-ui" not in resp.text.lower(), (
            "Swagger UI must not be exposed in prod"
        )


def test_redoc_not_exposed_in_prod(prod_client: TestClient) -> None:
    """ENV=prod must not serve ReDoc at /redoc."""
    resp = prod_client.get("/redoc")
    if resp.status_code == 200:
        assert "redoc" not in resp.text.lower() or "ReDoc" not in resp.text, (
            "ReDoc must not be exposed in prod"
        )


def test_app_openapi_url_is_none_in_prod(monkeypatch) -> None:
    """create_app() under ENV=prod sets openapi_url=None on the FastAPI instance."""
    monkeypatch.setenv("ENV", "prod")
    from backend.app.main import create_app
    app = create_app()
    assert app.openapi_url is None, "openapi_url must be None in prod"
    assert app.docs_url is None, "docs_url must be None in prod"
    assert app.redoc_url is None, "redoc_url must be None in prod"


# ---------------------------------------------------------------------------
# dev (default): schema must be reachable as application/json
# ---------------------------------------------------------------------------

def test_openapi_json_available_in_dev(dev_client: TestClient) -> None:
    resp = dev_client.get("/openapi.json")
    assert resp.status_code == 200
    assert "application/json" in resp.headers.get("content-type", "")


def test_swagger_docs_available_in_dev(dev_client: TestClient) -> None:
    resp = dev_client.get("/docs")
    assert resp.status_code == 200
