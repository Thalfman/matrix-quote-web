from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "tiny_models"
FIXTURE_MODELS_DIR = str(FIXTURE_DIR / "models")


@pytest.fixture()
def trained_client(monkeypatch):
    """TestClient with DATA_DIR pointing to tiny_models and load_model patched
    to load from the fixture models directory.

    The conftest autouse fixture sets DATA_DIR to a tmp_path, which makes
    storage.models_ready() return False.  We override DATA_DIR here and also
    patch core.models.load_model so predict_quote finds the fixture bundles
    (core.models.load_model defaults to models_dir="models" which is the repo
    root models/ dir, not DATA_DIR — the two are independent paths).
    """
    monkeypatch.setenv("DATA_DIR", str(FIXTURE_DIR))

    import core.models as core_models
    import service.predict_lib as predict_lib

    original_load = core_models.load_model

    def _fixture_load(target, version="v1", models_dir=FIXTURE_MODELS_DIR):
        return original_load(target, version=version, models_dir=models_dir)

    # Patch both the module-level name and the imported name in predict_lib
    # (predict_lib does `from core.models import load_model`, creating its own binding).
    monkeypatch.setattr(core_models, "load_model", _fixture_load)
    monkeypatch.setattr(predict_lib, "load_model", _fixture_load)

    from backend.app.main import create_app
    return TestClient(create_app())


def test_single_quote_returns_explain_fields(trained_client):
    resp = trained_client.post(
        "/api/quote/single",
        json={
            "industry_segment": "Automotive",
            "system_category": "Machine Tending",
            "automation_level": "Robotic",
            "plc_family": "AB Compact Logix",
            "hmi_family": "AB PanelView Plus",
            "vision_type": "2D",
            "stations_count": 8,
            "robot_count": 2,
            "conveyor_length_ft": 120.0,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "prediction" in body
    assert "ops" in body["prediction"]
    assert "drivers" in body
    assert "neighbors" in body
    assert body["drivers"] is not None
    assert body["neighbors"] is not None
