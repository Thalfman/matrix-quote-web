"""API-layer Pydantic models.

Core request/response types (QuoteInput, QuotePrediction, OpPrediction,
SalesBucketPrediction) are re-exported from core.schemas so the API
contract stays in lockstep with the vendored ML library.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from core.schemas import (  # re-export
    OpPrediction,
    QuoteInput,
    QuotePrediction,
    SalesBucketPrediction,
)

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
