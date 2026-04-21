# backend/app/demo.py
"""Seed DATA_DIR with synthetic assets so the app is demoable without a real dataset.

Never seeds when real data already exists.
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from .paths import (
    demo_assets_dir,
    ensure_runtime_dirs,
    master_data_path,
    metrics_path,
    models_dir,
    status_json_path,
)


def is_enabled_via_env() -> bool:
    return os.environ.get("ENABLE_DEMO", "").strip() in ("1", "true", "yes")


def has_real_data() -> bool:
    return master_data_path().exists() or metrics_path().exists()


def read_status() -> dict:
    path = status_json_path()
    if not path.exists():
        return {"is_demo": False}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"is_demo": False}


def write_status(payload: dict) -> None:
    """Write a status dict to the status JSON file (UTF-8)."""
    path = status_json_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_status(is_demo: bool) -> None:
    write_status({"is_demo": is_demo})


def _copy_tree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            _copy_tree(item, target)
        else:
            shutil.copy2(item, target)


def _seed() -> None:
    ensure_runtime_dirs()
    src = demo_assets_dir()
    if not src.exists():
        raise FileNotFoundError(
            "demo_assets/ is missing. Run scripts/generate_demo_assets.py."
        )
    # Copy data + models side of demo_assets into DATA_DIR.
    _copy_tree(src / "data", master_data_path().parent.parent)
    _copy_tree(src / "models", models_dir())
    _write_status(is_demo=True)


def seed_if_enabled() -> None:
    """Startup hook: seeds only when ENABLE_DEMO=1 and DATA_DIR has no real data."""
    if not is_enabled_via_env():
        return
    if has_real_data():
        return
    _seed()


def seed_on_demand() -> tuple[bool, str | None]:
    """Admin-button path. Refuses to clobber real data."""
    if has_real_data():
        return False, "Real data is already present; demo seed would clobber it."
    _seed()
    return True, None
