"""Pure-function aggregators used by the insights routes.

All functions tolerate missing data (return empty/None) so the frontend
can render empty-states while training-pipeline persistence is being wired.
"""

from __future__ import annotations

import pandas as pd


def weekly_quotes_activity(
    quotes: pd.DataFrame,
    weeks: int = 26,
    end: pd.Timestamp | None = None,
) -> list[tuple[str, int]]:
    """Return (ISO-week-label, count) tuples for the last `weeks` calendar weeks.

    Always returns exactly `weeks` entries; weeks with no saves get a zero count.
    Labels are ISO-8601 week strings, e.g. '2026-W04'.
    """
    end = pd.Timestamp(end) if end is not None else pd.Timestamp.utcnow()
    end_week = end.to_period("W-SUN")
    start_week = end_week - (weeks - 1)
    all_weeks = [(start_week + i).to_timestamp().strftime("%G-W%V") for i in range(weeks)]

    if quotes.empty or "created_at" not in quotes.columns:
        return [(w, 0) for w in all_weeks]

    s = pd.to_datetime(quotes["created_at"], errors="coerce").dropna()
    labels = s.dt.strftime("%G-W%V")
    counts = labels.value_counts().to_dict()
    return [(w, int(counts.get(w, 0))) for w in all_weeks]


def active_quotes_last_n_days(quotes: pd.DataFrame, n: int = 30) -> int:
    """Count quotes created within the last `n` days (UTC). Returns 0 when the store is empty."""
    if quotes.empty or "created_at" not in quotes.columns:
        return 0
    s = pd.to_datetime(quotes["created_at"], errors="coerce").dropna()
    cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=n)
    return int((s >= cutoff).sum())


def accuracy_heatmap(
    history: pd.DataFrame | None,
) -> tuple[list[str], list[str], list[list[float | None]]]:
    """Build a rows=operation x cols=quarter matrix of MAPE values.

    Expects history with columns `operation`, `quarter` (e.g. '2026Q1'), `mape`.
    When the history source is missing or empty, returns empty lists.
    """
    if history is None or history.empty:
        return [], [], []

    required = {"operation", "quarter", "mape"}
    if not required.issubset(history.columns):
        return [], [], []

    ops = sorted(history["operation"].dropna().unique().tolist())
    quarters = sorted(history["quarter"].dropna().unique().tolist())
    matrix: list[list[float | None]] = []
    for op in ops:
        row_vals: list[float | None] = []
        for q in quarters:
            cell = history[(history["operation"] == op) & (history["quarter"] == q)]
            row_vals.append(float(cell["mape"].mean()) if not cell.empty else None)
        matrix.append(row_vals)
    return ops, quarters, matrix


def calibration_within_band_pct(calibration: pd.DataFrame | None) -> float | None:
    """Return the percentage of predictions whose actual value falls inside the predicted band.

    Returns None when the calibration parquet is absent — the frontend should show a dash
    rather than 0% until the training pipeline begins persisting this file.
    """
    if calibration is None or calibration.empty:
        return None
    inside = calibration["inside_band"].mean() if "inside_band" in calibration.columns else None
    return float(inside * 100) if inside is not None else None
