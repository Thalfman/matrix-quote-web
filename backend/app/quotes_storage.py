# backend/app/quotes_storage.py
"""CRUD for saved quotes persisted as data/master/quotes.parquet.

Inputs and predictions are stored as JSON strings so evolving QuoteInput
doesn't churn the parquet schema.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from .paths import ensure_runtime_dirs, quotes_parquet_path
from .schemas_api import (
    QuoteInput,
    QuotePrediction,
    SavedQuote,
    SavedQuoteCreate,
    SavedQuoteList,
    SavedQuoteSummary,
)

COLUMNS = [
    "id", "name", "project_name", "client_name", "notes",
    "created_by", "created_at",
    "industry_segment", "hours", "range_low", "range_high",
    "inputs_json", "prediction_json", "quoted_hours_by_bucket_json",
]


def _load() -> pd.DataFrame:
    path = quotes_parquet_path()
    if not path.exists():
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_parquet(path)


def _atomic_write(df: pd.DataFrame) -> None:
    ensure_runtime_dirs()
    path = quotes_parquet_path()
    tmp = path.with_suffix(path.suffix + ".tmp")
    df.to_parquet(tmp, index=False)
    os.replace(tmp, path)


def _row_from(create: SavedQuoteCreate, id_: str, created_at: datetime) -> dict[str, Any]:
    return {
        "id": id_,
        "name": create.name,
        "project_name": create.project_name,
        "client_name": create.client_name,
        "notes": create.notes,
        "created_by": create.created_by,
        "created_at": created_at.isoformat(),
        "industry_segment": create.inputs.industry_segment,
        "hours": float(create.prediction.total_p50),
        "range_low": float(create.prediction.total_p10),
        "range_high": float(create.prediction.total_p90),
        "inputs_json": create.inputs.model_dump_json(),
        "prediction_json": create.prediction.model_dump_json(),
        "quoted_hours_by_bucket_json": json.dumps(create.quoted_hours_by_bucket or {}),
    }


def create(payload: SavedQuoteCreate) -> SavedQuote:
    df = _load()
    id_ = uuid.uuid4().hex
    created_at = datetime.now(UTC)
    row = _row_from(payload, id_, created_at)
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    _atomic_write(df)
    return SavedQuote(id=id_, created_at=created_at, **payload.model_dump())


def list_all(
    project: str | None = None,
    industry: str | None = None,
    search: str | None = None,
    limit: int = 200,
    offset: int = 0,
) -> SavedQuoteList:
    df = _load()
    if project:
        df = df[df["project_name"] == project]
    if industry:
        df = df[df["industry_segment"] == industry]
    if search:
        needle = search.lower()
        df = df[df["name"].str.lower().str.contains(needle, na=False)
                | df["project_name"].str.lower().str.contains(needle, na=False)
                | df["client_name"].fillna("").str.lower().str.contains(needle, na=False)]
    df = df.sort_values("created_at", ascending=False)
    total = int(len(df))
    df = df.iloc[offset:offset + limit]
    rows = [
        SavedQuoteSummary(
            id=r["id"],
            name=r["name"],
            project_name=r["project_name"],
            client_name=r["client_name"],
            industry_segment=r["industry_segment"],
            hours=float(r["hours"]),
            range_low=float(r["range_low"]),
            range_high=float(r["range_high"]),
            created_at=datetime.fromisoformat(r["created_at"]),
            created_by=r["created_by"],
        )
        for r in df.to_dict(orient="records")
    ]
    return SavedQuoteList(total=total, rows=rows)


def get(id_: str) -> SavedQuote | None:
    df = _load()
    match = df[df["id"] == id_]
    if match.empty:
        return None
    r = match.iloc[0].to_dict()
    return SavedQuote(
        id=r["id"],
        name=r["name"],
        project_name=r["project_name"],
        client_name=r["client_name"],
        notes=r.get("notes"),
        created_by=r["created_by"],
        created_at=datetime.fromisoformat(r["created_at"]),
        inputs=QuoteInput.model_validate_json(r["inputs_json"]),
        prediction=QuotePrediction.model_validate_json(r["prediction_json"]),
        quoted_hours_by_bucket=json.loads(r["quoted_hours_by_bucket_json"] or "{}") or None,
    )


def delete(id_: str) -> bool:
    df = _load()
    before = len(df)
    df = df[df["id"] != id_]
    if len(df) == before:
        return False
    _atomic_write(df)
    return True


def duplicate(id_: str, created_by: str | None = None) -> SavedQuote | None:
    src = get(id_)
    if src is None:
        return None
    copy_payload = SavedQuoteCreate(
        name=f"{src.name} (copy)",
        project_name=src.project_name,
        client_name=src.client_name,
        notes=src.notes,
        created_by=created_by or src.created_by,
        inputs=src.inputs,
        prediction=src.prediction,
        quoted_hours_by_bucket=src.quoted_hours_by_bucket,
    )
    return create(copy_payload)
