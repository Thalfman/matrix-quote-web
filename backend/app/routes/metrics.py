"""Public metrics, health, and dropdown-catalog routes."""

from __future__ import annotations

from fastapi import APIRouter

from .. import storage
from ..schemas_api import DropdownOptions, HealthResponse, MetricRow, MetricsSummary

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
