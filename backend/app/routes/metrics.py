"""Public metrics, health, and dropdown-catalog routes."""

from __future__ import annotations

import pandas as pd
from fastapi import APIRouter

from .. import storage
from ..paths import calibration_path, metrics_history_path
from ..schemas_api import (
    CalibrationPoint,
    DropdownOptions,
    HealthResponse,
    MapeRow,
    MetricRow,
    MetricsSummary,
    PerformanceHeadline,
    TrainingRunRow,
)

router = APIRouter(prefix="/api", tags=["public"])


DEFAULT_DROPDOWNS: dict[str, list[str]] = {
    "industry_segment": ["Automotive", "Food & Beverage", "General Industry"],
    "system_category": [
        "Machine Tending",
        "End of Line Automation",
        "Robotic Metal Finishing",
        "Engineered Manufacturing Systems",
        "Other",
    ],
    "automation_level": ["Semi-Automatic", "Robotic", "Hard Automation"],
    "plc_family": ["AB Compact Logix", "AB Control Logix", "Siemens S7"],
    "hmi_family": ["AB PanelView Plus", "Siemens Comfort Panel"],
    "vision_type": ["None", "2D", "3D"],
}


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", models_ready=storage.models_ready())


@router.get("/metrics", response_model=MetricsSummary)
def metrics() -> MetricsSummary:
    df = storage.read_metrics()
    if df is None or df.empty:
        return MetricsSummary(models_ready=False, metrics=[])
    rows = [MetricRow(**r) for r in storage.df_to_jsonable_records(df)]
    return MetricsSummary(models_ready=True, metrics=rows)


@router.get("/catalog/dropdowns", response_model=DropdownOptions)
def dropdowns() -> DropdownOptions:
    df = storage.read_master()
    result: dict[str, list[str]] = {}
    for field, fallback in DEFAULT_DROPDOWNS.items():
        if df is not None and field in df.columns:
            values = sorted(str(v) for v in df[field].dropna().unique() if str(v).strip())
            result[field] = values or fallback
        else:
            result[field] = fallback
    return DropdownOptions(**result)


@router.get("/metrics/history", response_model=list[TrainingRunRow])
def metrics_history() -> list[TrainingRunRow]:
    path = metrics_history_path()
    if not path.exists():
        return []
    df = pd.read_parquet(path)
    rows: list[TrainingRunRow] = []
    for r in df.sort_values("trained_at").to_dict(orient="records"):
        rows.append(TrainingRunRow(
            run_id=str(r.get("run_id", "")),
            trained_at=pd.to_datetime(r["trained_at"]).to_pydatetime(),
            rows=int(r.get("rows", 0) or 0),
            overall_mape=float(r.get("overall_mape", 0) or 0),
        ))
    return rows


@router.get("/metrics/calibration", response_model=list[CalibrationPoint])
def metrics_calibration() -> list[CalibrationPoint]:
    path = calibration_path()
    if not path.exists():
        return []
    df = pd.read_parquet(path)
    out: list[CalibrationPoint] = []
    for r in df.to_dict(orient="records"):
        low = float(r.get("predicted_low", 0) or 0)
        high = float(r.get("predicted_high", 0) or 0)
        actual = float(r.get("actual", 0) or 0)
        out.append(CalibrationPoint(
            predicted_low=low,
            predicted_high=high,
            actual=actual,
            inside_band=(low <= actual <= high),
        ))
    return out


@router.get("/metrics/headline", response_model=PerformanceHeadline)
def metrics_headline() -> PerformanceHeadline:
    head = PerformanceHeadline()
    cur = storage.read_metrics()
    if cur is not None and not cur.empty:
        if "mape" in cur.columns and cur["mape"].notna().any():
            head.overall_mape = float(cur["mape"].mean())
    path = calibration_path()
    if path.exists():
        df = pd.read_parquet(path)
        if not df.empty and {"predicted_low", "predicted_high", "actual"}.issubset(df.columns):
            within_10 = ((df["actual"] - ((df["predicted_low"] + df["predicted_high"]) / 2)).abs()
                         / df["actual"].replace(0, pd.NA)).dropna().lt(0.10).mean()
            within_20 = ((df["actual"] - ((df["predicted_low"] + df["predicted_high"]) / 2)).abs()
                         / df["actual"].replace(0, pd.NA)).dropna().lt(0.20).mean()
            head.within_10_pct = float(within_10 * 100) if pd.notna(within_10) else None
            head.within_20_pct = float(within_20 * 100) if pd.notna(within_20) else None
    hist_path = metrics_history_path()
    if hist_path.exists():
        hdf = pd.read_parquet(hist_path)
        if not hdf.empty and "trained_at" in hdf.columns:
            last = pd.to_datetime(hdf["trained_at"]).max()
            head.last_trained_at = last.to_pydatetime()
    return head
