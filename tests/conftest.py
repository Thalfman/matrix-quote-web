"""Shared test fixtures.

Every test runs against a fresh tmp DATA_DIR so the master parquet, upload
log, and model artifacts from one test never leak into another.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def _clean_settings_cache(monkeypatch, tmp_path):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setenv("ADMIN_PASSWORD", "test-password")
    monkeypatch.setenv("ADMIN_JWT_SECRET", "test-secret-at-least-32-chars-long!!")
    monkeypatch.setenv("ADMIN_TOKEN_EXPIRY_HOURS", "1")
    from backend.app.deps import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    from backend.app.main import create_app
    return TestClient(create_app())


@pytest.fixture
def admin_client(client: TestClient) -> TestClient:
    resp = client.post("/api/admin/login", json={"password": "test-password"})
    assert resp.status_code == 200, resp.text
    token = resp.json()["token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
