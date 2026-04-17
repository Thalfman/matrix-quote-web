# tests/test_pdf_export.py
from __future__ import annotations

import pytest

# WeasyPrint requires native pango/gobject libs that are not present on Windows dev boxes.
# On those machines the import raises OSError. Skip the entire module rather than fail.
try:
    import weasyprint as _wp  # noqa: F401
except OSError:
    pytest.skip(
        "WeasyPrint native libs (pango/gobject) not available on this platform",
        allow_module_level=True,
    )

from fastapi.testclient import TestClient  # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from importlib import reload
    from backend.app import main, paths
    reload(paths); reload(main)
    return TestClient(main.app)


def _create_body():
    return {
        "name": "Draft A",
        "project_name": "Acme Line 3",
        "client_name": "Acme Industrial",
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
            "ops": {"mechanical_hours": {"p50":100,"p10":80,"p90":120,"std":10,"rel_width":0.4,"confidence":"medium"}},
            "total_p50": 1200, "total_p10": 1000, "total_p90": 1400,
            "sales_buckets": {
                "mechanical":  {"p50":500,"p10":450,"p90":560,"rel_width":0.2,"confidence":"medium"},
                "electrical":  {"p50":420,"p10":380,"p90":470,"rel_width":0.2,"confidence":"medium"},
                "controls":    {"p50":280,"p10":240,"p90":320,"rel_width":0.3,"confidence":"low"},
            },
        },
    }


def test_saved_quote_pdf_download(client):
    created = client.post("/api/quotes", json=_create_body()).json()
    r = client.get(f"/api/quotes/{created['id']}/pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 5000  # non-trivial body
    disp = r.headers["content-disposition"]
    assert "Matrix-Quote-Acme-Line-3" in disp


def test_adhoc_pdf(client):
    r = client.post("/api/quote/pdf", json={
        "name": "Draft", "project_name": "Ad Hoc",
        "created_by": "Tester",
        "inputs":     _create_body()["inputs"],
        "prediction": _create_body()["prediction"],
    })
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 5000


def test_saved_quote_pdf_404_when_missing(client):
    r = client.get("/api/quotes/does-not-exist/pdf")
    assert r.status_code == 404
