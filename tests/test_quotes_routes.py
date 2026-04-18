# tests/test_quotes_routes.py
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from importlib import reload

    from backend.app import main, paths
    reload(paths)
    reload(main)
    return TestClient(main.app)


def _create_body():
    return {
        "name": "Draft A",
        "project_name": "Acme Line 3",
        "client_name": None,
        "notes": None,
        "created_by": "Tester",
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


def test_create_list_get_delete(client):
    r = client.post("/api/quotes", json=_create_body())
    assert r.status_code == 201
    id_ = r.json()["id"]

    r = client.get("/api/quotes")
    assert r.status_code == 200
    assert r.json()["total"] == 1

    r = client.get(f"/api/quotes/{id_}")
    assert r.status_code == 200
    assert r.json()["name"] == "Draft A"

    r = client.delete(f"/api/quotes/{id_}")
    assert r.status_code == 204

    r = client.get(f"/api/quotes/{id_}")
    assert r.status_code == 404


def test_duplicate(client):
    r = client.post("/api/quotes", json=_create_body())
    id_ = r.json()["id"]
    r = client.post(f"/api/quotes/{id_}/duplicate")
    assert r.status_code == 201
    assert r.json()["name"].endswith("(copy)")
