"""Insights routes — executive-facing KPI snapshot.

Single endpoint: GET /api/insights/overview returns InsightsOverview with
aggregated quote activity, model readiness counts, MAPE, calibration band %, and
a 26-week activity time-series.  All fields that depend on optional parquet files
(accuracy_heatmap, calibration_within_band_pct) degrade gracefully to empty/None
until the training pipeline begins persisting metrics_history.parquet and
calibration.parquet.
"""
from __future__ import annotations

import pandas as pd
from fastapi import APIRouter

from .. import insights, quotes_storage, storage
from ..paths import calibration_path, metrics_history_path
from ..schemas_api import InsightsOverview


router = APIRouter(prefix="/api/insights", tags=["insights"])


MODELS_TARGET = 12


@router.get("/overview", response_model=InsightsOverview)
def overview() -> InsightsOverview:
    """Return the executive KPI snapshot.

    Fields sourced from optional parquet files return empty lists or None when
    those files do not yet exist on disk; callers should render empty-state UI
    rather than treating null as an error.
    """
    quotes_df = _quotes_as_df()

    calibration_df = pd.read_parquet(calibration_path()) if calibration_path().exists() else None
    history_df = pd.read_parquet(metrics_history_path()) if metrics_history_path().exists() else None

    cur = storage.read_metrics()
    overall_mape = None
    if cur is not None and not cur.empty and "mape" in cur.columns and cur["mape"].notna().any():
        overall_mape = float(cur["mape"].mean())

    models_trained = int(len(cur)) if cur is not None else 0

    ops, quarters, matrix = insights.accuracy_heatmap(history_df)

    latest = quotes_storage.list_all(limit=5, offset=0).rows

    return InsightsOverview(
        active_quotes_30d=insights.active_quotes_last_n_days(quotes_df, n=30),
        models_trained=models_trained,
        models_target=MODELS_TARGET,
        overall_mape=overall_mape,
        calibration_within_band_pct=insights.calibration_within_band_pct(calibration_df),
        quotes_activity=insights.weekly_quotes_activity(quotes_df, weeks=26),
        latest_quotes=latest,
        accuracy_heatmap=matrix,
        operations=ops,
        quarters=quarters,
    )


def _quotes_as_df() -> pd.DataFrame:
    from ..paths import quotes_parquet_path
    path = quotes_parquet_path()
    if not path.exists():
        return pd.DataFrame(columns=["created_at"])
    return pd.read_parquet(path)
