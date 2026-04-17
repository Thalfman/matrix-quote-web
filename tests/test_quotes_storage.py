# tests/test_quotes_storage.py
from __future__ import annotations
from datetime import datetime

import pytest


@pytest.fixture(autouse=True)
def _isolated_data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    from backend.app import paths, quotes_storage
    paths.ensure_runtime_dirs()
    yield


def _make_create():
    from backend.app.schemas_api import SavedQuoteCreate, QuoteInput, QuotePrediction
    from core.schemas import OpPrediction, SalesBucketPrediction
    return SavedQuoteCreate(
        name="Draft A",
        project_name="Acme Line 3",
        client_name=None,
        created_by="T. Halfman",
        inputs=QuoteInput(
            industry_segment="Automotive",
            system_category="Machine Tending",
            automation_level="Robotic",
            plc_family="AB Compact Logix",
            hmi_family="AB PanelView Plus",
            vision_type="2D",
            stations_count=8,
        ),
        prediction=QuotePrediction(
            ops={"mechanical_hours": OpPrediction(p50=100, p10=80, p90=120, std=10, rel_width=0.4, confidence="medium")},
            total_p50=100.0, total_p10=80.0, total_p90=120.0,
            sales_buckets={"mechanical": SalesBucketPrediction(p50=100, p10=80, p90=120, rel_width=0.4, confidence="medium")},
        ),
    )


def test_create_then_list_then_get_then_delete():
    from backend.app import quotes_storage

    created = quotes_storage.create(_make_create())
    assert created.id
    assert isinstance(created.created_at, datetime)

    listing = quotes_storage.list_all()
    assert listing.total == 1
    assert listing.rows[0].id == created.id
    assert listing.rows[0].hours == 100.0

    full = quotes_storage.get(created.id)
    assert full is not None
    assert full.name == "Draft A"

    deleted = quotes_storage.delete(created.id)
    assert deleted is True
    assert quotes_storage.get(created.id) is None


def test_delete_returns_false_when_missing():
    from backend.app import quotes_storage
    assert quotes_storage.delete("does-not-exist") is False


def test_atomic_replace_leaves_no_tmp_files(tmp_path):
    from backend.app import quotes_storage
    quotes_storage.create(_make_create())
    parents = list(tmp_path.rglob("quotes.parquet.tmp"))
    assert parents == []
