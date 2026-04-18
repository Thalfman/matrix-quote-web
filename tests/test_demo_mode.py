# tests/test_demo_mode.py
"""Tests for the demo-mode seeding backend.

Tests cover:
- Startup seed when ENABLE_DEMO=1 and DATA_DIR is empty.
- No seed when ENABLE_DEMO is unset.
- seed_on_demand() refuses to clobber existing real data.
- Admin route requires a valid bearer token.
- Admin load succeeds when DATA_DIR is empty (no pre-existing data).
"""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

REPO_ROOT = Path(__file__).resolve().parents[1]
DEMO_ROOT = REPO_ROOT / "demo_assets"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reload_stack(monkeypatch, tmp_path, *, enable_demo: bool = False):
    """Reload paths → storage → demo → main in order after env changes.

    Returns a fresh TestClient wrapping the reloaded app. The conftest
    autouse fixture already sets DATA_DIR to a fresh tmp_path and clears
    the get_settings LRU cache, but creating a TestClient via create_app()
    at module level would miss those changes. Reloading the module stack
    picks up the new environment state for path-derived singletons.
    """
    from backend.app.deps import get_settings

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    if enable_demo:
        monkeypatch.setenv("ENABLE_DEMO", "1")
    else:
        monkeypatch.delenv("ENABLE_DEMO", raising=False)

    # Clear settings cache so create_app() sees the new DATA_DIR.
    get_settings.cache_clear()

    from backend.app import demo, main, paths, storage

    importlib.reload(paths)
    importlib.reload(storage)
    importlib.reload(demo)
    importlib.reload(main)

    return TestClient(main.app)


def _admin_token(client: TestClient) -> str:
    """Obtain a valid admin JWT using the test-password from conftest."""
    resp = client.post("/api/admin/login", json={"password": "test-password"})
    assert resp.status_code == 200, resp.text
    return resp.json()["token"]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

@pytest.mark.skipif(not DEMO_ROOT.exists(), reason="demo_assets/ not generated")
def test_startup_seeds_when_enabled(tmp_path, monkeypatch):
    """With ENABLE_DEMO=1 and an empty DATA_DIR, startup should seed demo data."""
    client = _reload_stack(monkeypatch, tmp_path, enable_demo=True)

    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["models_ready"] is True, "Models should be ready after demo seed"

    s = client.get("/api/demo/status").json()
    assert s["is_demo"] is True, "status.json should mark is_demo=true after seed"


def test_no_seed_without_env(tmp_path, monkeypatch):
    """Without ENABLE_DEMO, startup must not seed and models must be absent."""
    client = _reload_stack(monkeypatch, tmp_path, enable_demo=False)

    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["models_ready"] is False, "Models should be absent with no seed"

    s = client.get("/api/demo/status").json()
    assert s["is_demo"] is False
    assert s["enabled_env"] is False


def test_load_demo_refuses_when_real_data_present(tmp_path, monkeypatch):
    """seed_on_demand() must refuse (False, reason) if master parquet already exists."""
    import pandas as pd

    from backend.app.deps import get_settings

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.delenv("ENABLE_DEMO", raising=False)
    get_settings.cache_clear()

    from backend.app import paths
    importlib.reload(paths)

    # Plant a dummy parquet so has_real_data() returns True.
    paths.master_data_path().parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"x": [1]}).to_parquet(paths.master_data_path(), index=False)

    from backend.app import demo
    importlib.reload(demo)

    loaded, reason = demo.seed_on_demand()
    assert loaded is False
    assert reason is not None
    assert "clobber" in reason.lower(), f"Expected 'clobber' in reason, got: {reason!r}"


def test_admin_load_requires_auth(tmp_path, monkeypatch):
    """POST /api/admin/demo/load without a bearer token must return 401."""
    client = _reload_stack(monkeypatch, tmp_path, enable_demo=False)

    r = client.post("/api/admin/demo/load")
    assert r.status_code == 401, f"Expected 401, got {r.status_code}: {r.text}"


@pytest.mark.skipif(not DEMO_ROOT.exists(), reason="demo_assets/ not generated")
def test_admin_load_succeeds_when_empty(tmp_path, monkeypatch):
    """With a valid admin token and empty DATA_DIR, load endpoint seeds demo data."""
    client = _reload_stack(monkeypatch, tmp_path, enable_demo=False)

    token = _admin_token(client)

    r = client.post(
        "/api/admin/demo/load",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}: {r.text}"
    body = r.json()
    assert body["loaded"] is True
    assert body["reason"] is None

    # Verify status now reflects demo mode.
    s = client.get("/api/demo/status").json()
    assert s["is_demo"] is True, "Demo status should be true after admin load"
