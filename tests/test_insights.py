# tests/test_insights.py
from __future__ import annotations

import pandas as pd


def test_weekly_quotes_empty_returns_zero_weeks():
    from backend.app.insights import weekly_quotes_activity
    out = weekly_quotes_activity(pd.DataFrame(columns=["created_at"]), weeks=26)
    assert len(out) == 26
    assert all(count == 0 for _, count in out)


def test_weekly_quotes_counts_rows_per_week():
    from backend.app.insights import weekly_quotes_activity
    df = pd.DataFrame({
        "created_at": [
            "2026-04-07T00:00:00", "2026-04-08T00:00:00",  # same ISO week
            "2026-04-14T00:00:00",
        ],
    })
    out = weekly_quotes_activity(df, weeks=4, end=pd.Timestamp("2026-04-17"))
    counts = dict(out)
    assert counts.get("2026-W15", 0) == 2
    assert counts.get("2026-W16", 0) == 1


def test_accuracy_heatmap_handles_missing_history():
    from backend.app.insights import accuracy_heatmap
    ops, quarters, matrix = accuracy_heatmap(None)
    assert ops == []
    assert quarters == []
    assert matrix == []


def test_overview_endpoint_degrades_when_nothing_exists(admin_client):
    r = admin_client.get("/api/insights/overview")
    assert r.status_code == 200
    body = r.json()
    assert body["active_quotes_30d"] == 0
    assert body["quotes_activity"] and len(body["quotes_activity"]) == 26
    assert body["latest_quotes"] == []
    assert body["accuracy_heatmap"] == []
