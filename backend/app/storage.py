"""File I/O wrappers around the master parquet, upload log, and metrics CSV.

These helpers centralize path resolution (so the rest of the backend never
touches `os.path.join`) and normalize NaN → None for JSON-safe responses.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .paths import (
    ensure_runtime_dirs,
    master_data_path,
    metrics_path,
    models_dir,
    uploads_log_path,
)


def read_master() -> pd.DataFrame | None:
    path = master_data_path()
    if not path.exists():
        return None
    return pd.read_parquet(path)


def write_master(df: pd.DataFrame) -> None:
    ensure_runtime_dirs()
    df.to_parquet(master_data_path(), index=False)


def read_metrics() -> pd.DataFrame | None:
    path = metrics_path()
    if not path.exists():
        return None
    return pd.read_csv(path)


def write_metrics(df: pd.DataFrame) -> None:
    ensure_runtime_dirs()
    df.to_csv(metrics_path(), index=False)


def read_uploads_log() -> pd.DataFrame | None:
    path = uploads_log_path()
    if not path.exists():
        return None
    return pd.read_csv(path)


def log_upload(rows_raw: int, rows_train: int, rows_master_total: int) -> None:
    ensure_runtime_dirs()
    path = uploads_log_path()
    row = pd.DataFrame(
        [{
            "rows_raw": rows_raw,
            "rows_train": rows_train,
            "rows_master_total": rows_master_total,
        }]
    )
    if path.exists():
        existing = pd.read_csv(path)
        combined = pd.concat([existing, row], ignore_index=True)
    else:
        combined = row
    combined.to_csv(path, index=False)


def models_ready() -> bool:
    df = read_metrics()
    return df is not None and not df.empty


def reset_all() -> None:
    for path in (master_data_path(), uploads_log_path(), metrics_path()):
        if path.exists():
            path.unlink()
    md = models_dir()
    if md.exists():
        for joblib_file in md.glob("*.joblib"):
            try:
                joblib_file.unlink()
            except OSError:
                pass


def df_to_jsonable_records(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Convert a DataFrame to JSON-safe records (NaN -> None)."""
    return df.replace({np.nan: None}).to_dict(orient="records")
