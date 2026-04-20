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


@pytest.fixture(autouse=True)
def _reset_limiter():
    from backend.app.deps import limiter
    limiter.reset()
    yield
    limiter.reset()


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


@pytest.fixture
def saved_quote_payload() -> dict:
    return {
        "name": "Draft A",
        "project_name": "Acme Line 3",
        "client_name": None,
        "notes": None,
        "inputs": {
            "industry_segment": "Automotive",
            "system_category": "Machine Tending",
            "automation_level": "Robotic",
            "plc_family": "AB Compact Logix",
            "hmi_family": "AB PanelView Plus",
            "vision_type": "2D",
            "stations_count": 8,
        },
        "prediction": {
            "ops": {
                "mechanical_hours": {
                    "p50": 100, "p10": 80, "p90": 120,
                    "std": 10, "rel_width": 0.4, "confidence": "medium",
                },
            },
            "total_p50": 100, "total_p10": 80, "total_p90": 120,
            "sales_buckets": {
                "mechanical": {
                    "p50": 100, "p10": 80, "p90": 120,
                    "rel_width": 0.4, "confidence": "medium",
                },
            },
        },
    }
