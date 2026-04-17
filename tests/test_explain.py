"""Unit tests for backend/app/explain.py."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parent / "fixtures" / "tiny_models"


@pytest.fixture(autouse=True)
def _fixture_data_dir(monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(FIXTURE_DIR))
    yield


def _sample_input():
    from backend.app.schemas_api import QuoteInput
    return QuoteInput(
        industry_segment="Automotive",
        system_category="Machine Tending",
        automation_level="Robotic",
        plc_family="AB Compact Logix",
        hmi_family="AB PanelView Plus",
        vision_type="2D",
        stations_count=8,
        robot_count=2,
        conveyor_length_ft=120.0,
    )


def test_compute_drivers_returns_one_entry_per_trained_op():
    from backend.app.explain import compute_drivers

    result = compute_drivers(_sample_input(), top_n=3)

    assert isinstance(result, list)
    assert len(result) >= 1, "at least one operation should produce drivers"
    for op in result:
        assert op.operation
        if op.available:
            assert 1 <= len(op.drivers) <= 3
            for d in op.drivers:
                assert d.feature
                assert isinstance(d.contribution, float)
                assert d.value


def test_compute_drivers_graceful_when_one_model_errors(monkeypatch):
    from backend.app import explain

    calls = {"n": 0}
    original = explain._contributions_for_op

    def flaky(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise RuntimeError("simulated bad model")
        return original(*args, **kwargs)

    monkeypatch.setattr(explain, "_contributions_for_op", flaky)

    result = explain.compute_drivers(_sample_input(), top_n=3)

    unavailable = [op for op in result if not op.available]
    available   = [op for op in result if op.available]
    assert unavailable, "the flaky op should be marked unavailable"
    assert available,   "other ops should still return data"


def test_compute_neighbors_returns_up_to_k():
    from backend.app.explain import compute_neighbors

    result = compute_neighbors(_sample_input(), k=5)

    assert len(result) <= 5
    for n in result:
        assert n.project_name
        assert n.industry_segment
        assert n.automation_level
        assert 0.0 <= n.similarity <= 1.0 + 1e-9  # cosine
        assert n.actual_hours >= 0


def test_compute_neighbors_empty_when_master_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_DIR", str(tmp_path))  # no master parquet here
    from importlib import reload

    from backend.app import explain, storage
    reload(storage)
    reload(explain)

    result = explain.compute_neighbors(_sample_input(), k=5)
    assert result == []
