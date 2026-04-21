"""API-layer Pydantic models.

Core request/response types (QuoteInput, QuotePrediction, OpPrediction,
SalesBucketPrediction) are re-exported from core.schemas so the API
contract stays in lockstep with the vendored ML library.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from core.schemas import (  # re-export
    OpPrediction,
    QuoteInput,
    QuotePrediction,
    SalesBucketPrediction,
)
from pydantic import BaseModel, Field

__all__ = [
    "OpPrediction",
    "QuoteInput",
    "QuotePrediction",
    "SalesBucketPrediction",
    "HealthResponse",
    "DropdownOptions",
    "MetricRow",
    "MetricsSummary",
    "LoginRequest",
    "LoginResponse",
    "TrainPreviewResponse",
    "TrainResponse",
    "DatasetFacets",
    "DatasetScatterPoint",
    "DatasetPage",
    "DriverFeature",
    "DriversResponse",
    "SimilarRequest",
    "SimilarResponse",
    "UploadLogRow",
    "OverviewResponse",
    "ResetPrepareResponse",
    "ResetRequest",
    "DriverContribution",
    "OperationDrivers",
    "NeighborProject",
    "ExplainedQuoteResponse",
    "SavedQuoteCreateBody",
    "SavedQuoteCreate",
    "SavedQuote",
    "SavedQuoteSummary",
    "SavedQuoteList",
    "AdHocPdfRequest",
    "CalibrationPoint",
    "TrainingRunRow",
    "PerformanceHeadline",
    "InsightsOverview",
    "DemoStatus",
    "DemoLoadResponse",
]


class HealthResponse(BaseModel):
    status: str = "ok"
    models_ready: bool


class DropdownOptions(BaseModel):
    industry_segment: list[str]
    system_category: list[str]
    automation_level: list[str]
    plc_family: list[str]
    hmi_family: list[str]
    vision_type: list[str]


class MetricRow(BaseModel):
    target: str
    version: str | None = None
    rows: int | None = None
    mae: float | None = None
    r2: float | None = None
    model_path: str | None = None


class MetricsSummary(BaseModel):
    models_ready: bool
    metrics: list[MetricRow]


class LoginRequest(BaseModel):
    password: str
    name: str | None = Field(default=None, max_length=120)


class LoginResponse(BaseModel):
    token: str
    expires_at: datetime


class TrainPreviewResponse(BaseModel):
    sheets: list[str]
    columns_per_sheet: dict[str, list[str]]


class TrainResponse(BaseModel):
    rows_raw: int
    rows_train: int
    rows_master_total: int
    metrics: list[MetricRow]
    trained_targets: list[str]
    skipped_targets: list[str]
    models_ready: bool


class DatasetFacets(BaseModel):
    industry_segment: list[str]
    system_category: list[str]
    ops_with_data: list[str]


class DatasetScatterPoint(BaseModel):
    project_id: str | None = None
    robot_count: float | None = None
    hours: float | None = None


class DatasetPage(BaseModel):
    total: int
    filtered_total: int
    columns: list[str]
    rows: list[dict[str, Any]]
    facets: DatasetFacets
    scatter: list[DatasetScatterPoint] | None = None


class DriverFeature(BaseModel):
    feature: str
    importance: float


class DriversResponse(BaseModel):
    op: str
    has_model: bool
    features: list[DriverFeature] = Field(default_factory=list)
    nonzero_count: int = 0


class SimilarRequest(BaseModel):
    industry_segment: str | None = None
    system_category: str | None = None
    min_robots: int = 0
    max_robots: int = 10
    limit: int = 50


class SimilarResponse(BaseModel):
    count: int
    rows: list[dict[str, Any]]


class UploadLogRow(BaseModel):
    rows_raw: int | None = None
    rows_train: int | None = None
    rows_master_total: int | None = None


class OverviewResponse(BaseModel):
    n_projects: int
    n_ops_modeled: int
    avg_mae: float | None = None
    avg_r2: float | None = None
    models_ready: bool
    recent_uploads: list[UploadLogRow]
    metrics: list[MetricRow]


class ResetPrepareResponse(BaseModel):
    confirm_token: str
    expires_at: datetime


class ResetRequest(BaseModel):
    confirm_token: str


class DriverContribution(BaseModel):
    """One feature's signed contribution to a single operation's hours."""

    feature: str           # humanized label ("Stations", "Industry: Automotive")
    contribution: float    # signed hours (+62.0, -22.0)
    value: str             # displayed input value ("12", "Automotive", "180 ft")


class OperationDrivers(BaseModel):
    """Top-N drivers for one operation model."""

    operation: str         # e.g. "mechanical_hours"
    drivers: list[DriverContribution] = Field(default_factory=list)
    available: bool = True
    reason: str | None = None   # populated only when available=False


class NeighborProject(BaseModel):
    """A historical project similar to the current quote input."""

    project_name: str
    year: int | None = None
    industry_segment: str
    automation_level: str
    stations: int | None = None
    actual_hours: float
    similarity: float      # 0..1 (1 = identical after preprocessing)


class ExplainedQuoteResponse(BaseModel):
    """Wrapper returned by POST /api/quote/single.

    Nests the vendored QuotePrediction so we don't edit core/schemas.py.
    """

    prediction: QuotePrediction
    drivers: list[OperationDrivers] | None = None
    neighbors: list[NeighborProject] | None = None


class SavedQuoteCreateBody(BaseModel):
    """Public request schema — `created_by` is derived server-side from the JWT."""
    name: str = Field(min_length=1, max_length=120)
    project_name: str = Field(min_length=1, max_length=200)
    client_name: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=1000)
    inputs: QuoteInput
    prediction: QuotePrediction
    quoted_hours_by_bucket: dict[str, float] | None = None


class SavedQuoteCreate(SavedQuoteCreateBody):
    """Internal write model — includes trusted `created_by` from the token."""
    created_by: str = Field(min_length=1, max_length=120)


class SavedQuote(SavedQuoteCreate):
    id: str                  # uuid4 hex
    created_at: datetime


class SavedQuoteSummary(BaseModel):
    id: str
    name: str
    project_name: str
    client_name: str | None = None
    industry_segment: str
    hours: float              # prediction.total_p50
    range_low: float
    range_high: float
    created_at: datetime
    created_by: str


class SavedQuoteList(BaseModel):
    total: int
    rows: list[SavedQuoteSummary]


class AdHocPdfRequest(BaseModel):
    name: str = "Draft"
    project_name: str = "Untitled project"
    client_name: str | None = None
    created_by: str = "Anonymous"
    inputs: QuoteInput
    prediction: QuotePrediction


class CalibrationPoint(BaseModel):
    predicted_low: float
    predicted_high: float
    actual: float
    inside_band: bool


class TrainingRunRow(BaseModel):
    run_id: str
    trained_at: datetime
    rows: int
    overall_mape: float


class PerformanceHeadline(BaseModel):
    overall_mape: float | None = None
    within_10_pct: float | None = None
    within_20_pct: float | None = None
    last_trained_at: datetime | None = None
    rows_at_train: int | None = None


class InsightsOverview(BaseModel):
    active_quotes_30d: int
    models_trained: int
    models_target: int
    overall_mape: float | None
    calibration_within_band_pct: float | None
    quotes_activity: list[tuple[str, int]]   # (iso week start, count)
    latest_quotes: list[SavedQuoteSummary]
    accuracy_heatmap: list[list[float | None]]   # rows = operations, cols = quarters
    operations: list[str]
    quarters: list[str]


class DemoStatus(BaseModel):
    is_demo: bool = False
    enabled_env: bool = False
    has_real_data: bool = False


class DemoLoadResponse(BaseModel):
    loaded: bool
    reason: str | None = None
