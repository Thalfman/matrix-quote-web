"""Tests for auth-gating of telemetry endpoints (S-7).

After gating:
  - /api/metrics, /api/metrics/history, /api/metrics/calibration,
    /api/metrics/headline, /api/catalog/dropdowns, /api/demo/status,
    /api/insights/overview  → 401 without a bearer token
  - /api/health             → 200 (remains public)
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.parametrize("path", [
    "/api/metrics",
    "/api/metrics/history",
    "/api/metrics/calibration",
    "/api/metrics/headline",
    "/api/catalog/dropdowns",
    "/api/demo/status",
    "/api/insights/overview",
])
def test_gated_endpoints_return_401_without_token(client: TestClient, path: str) -> None:
    """Every telemetry endpoint must reject unauthenticated requests."""
    resp = client.get(path)
    assert resp.status_code == 401, (
        f"{path} returned {resp.status_code}; expected 401. "
        "Did you add require_admin to this route?"
    )


@pytest.mark.parametrize("path", [
    "/api/metrics",
    "/api/metrics/history",
    "/api/metrics/calibration",
    "/api/metrics/headline",
    "/api/catalog/dropdowns",
    "/api/demo/status",
    "/api/insights/overview",
])
def test_gated_endpoints_return_200_with_admin_token(admin_client: TestClient, path: str) -> None:
    """Every telemetry endpoint must succeed for an authenticated admin."""
    resp = admin_client.get(path)
    assert resp.status_code == 200, (
        f"{path} returned {resp.status_code} for admin; expected 200."
    )


def test_health_stays_public(client: TestClient) -> None:
    """/api/health must remain public — no bearer token required."""
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
