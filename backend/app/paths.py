"""Filesystem paths derived from DATA_DIR.

Mirrors the Streamlit app's layout (quote_app.py:36-38) so the vendored
core/ and service/ modules can read and write to the same on-disk files.
"""

from __future__ import annotations

import os
from pathlib import Path


def data_dir() -> Path:
    return Path(os.environ.get("DATA_DIR", ".")).resolve()


def master_data_path() -> Path:
    return data_dir() / "data" / "master" / "projects_master.parquet"


def uploads_log_path() -> Path:
    return data_dir() / "data" / "master" / "uploads_log.csv"


def models_dir() -> Path:
    return data_dir() / "models"


def metrics_path() -> Path:
    return models_dir() / "metrics_summary.csv"


def train_lock_path() -> Path:
    return data_dir() / ".train.lock"


def ensure_runtime_dirs() -> None:
    master_data_path().parent.mkdir(parents=True, exist_ok=True)
    models_dir().mkdir(parents=True, exist_ok=True)
