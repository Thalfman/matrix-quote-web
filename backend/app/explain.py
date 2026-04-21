"""Per-quote explainability: driver contributions and nearest neighbors.

Read-only over the service-trained model bundles and the master parquet.
Does NOT modify any vendored module.

NOTE: Models are sklearn GradientBoostingRegressor bundles (not LightGBM/XGBoost),
so pred_contrib is not available.  The shap fallback is always used.

Joblib bundles are cached in-process by _load_bundle_cached (keyed on path +
mtime_ns) so repeated requests skip disk I/O.  A retrain automatically
invalidates the cache because the mtime changes.
"""

from __future__ import annotations

import logging
from functools import cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from core.config import QUOTE_CAT_FEATURES, QUOTE_NUM_FEATURES

from . import storage
from .paths import models_dir
from .schemas_api import (
    DriverContribution,
    NeighborProject,
    OperationDrivers,
    QuoteInput,
)

logger = logging.getLogger(__name__)

# Human-readable labels for raw feature names.
FEATURE_LABELS: dict[str, str] = {
    "stations_count":           "Stations",
    "robot_count":              "Robots",
    "fixture_sets":             "Fixture sets",
    "part_types":               "Part types",
    "servo_axes":               "Servo axes",
    "pneumatic_devices":        "Pneumatic devices",
    "safety_doors":             "Safety doors",
    "weldment_perimeter_ft":    "Weldment perimeter (ft)",
    "fence_length_ft":          "Fence length (ft)",
    "conveyor_length_ft":       "Conveyor length (ft)",
    "product_familiarity_score":"Product familiarity",
    "product_rigidity":         "Product rigidity",
    "is_product_deformable":    "Deformable product",
    "is_bulk_product":          "Bulk product",
    "bulk_rigidity_score":      "Bulk rigidity",
    "has_tricky_packaging":     "Tricky packaging",
    "process_uncertainty_score":"Process uncertainty",
    "changeover_time_min":      "Changeover time (min)",
    "safety_devices_count":     "Safety devices",
    "custom_pct":               "Custom scope %",
    "duplicate":                "Duplicate",
    "has_controls":             "Has controls",
    "has_robotics":             "Has robotics",
    "Retrofit":                 "Retrofit",
    "complexity_score_1_5":     "Complexity",
    "vision_systems_count":     "Vision systems",
    "panel_count":              "Panels",
    "drive_count":              "Drives",
    "stations_robot_index":     "Stations/robot index",
    "mech_complexity_index":    "Mech complexity index",
    "controls_complexity_index":"Controls complexity index",
    "physical_scale_index":     "Physical scale index",
    "log_quoted_materials_cost":"Log(materials cost)",
    "industry_segment":         "Industry",
    "system_category":          "System category",
    "automation_level":         "Automation level",
    "plc_family":               "PLC family",
    "hmi_family":               "HMI family",
    "vision_type":               "Vision type",
}


def _humanize(feature: str) -> str:
    return FEATURE_LABELS.get(feature, feature.replace("_", " ").title())


@cache
def _load_bundle_cached(op_path: Path, mtime_ns: int) -> dict[str, Any]:
    """Cache the joblib bundle keyed on path + mtime so a retrain invalidates it."""
    return joblib.load(op_path)


def _load_bundle(op_path: Path) -> dict[str, Any]:
    return _load_bundle_cached(op_path, op_path.stat().st_mtime_ns)


def _discover_bundles() -> list[tuple[str, Path]]:
    """Return (op_name, path) pairs for all trained joblib bundles.

    Models are saved as ``{target}_v1.joblib`` by core.models.train_one_op,
    where target is e.g. ``me10_actual_hours``.  The op name returned strips
    the ``_actual_hours`` suffix (matching predict_lib convention), e.g. ``me10``.
    """
    md = models_dir()
    if not md.exists():
        return []
    bundles: list[tuple[str, Path]] = []
    for p in sorted(md.glob("*_actual_hours_v1.joblib")):
        # stem: "me10_actual_hours_v1"  -> strip "_v1" -> "me10_actual_hours"
        # then strip "_actual_hours" -> "me10"
        stem = p.stem  # e.g. "me10_actual_hours_v1"
        target = stem.removesuffix("_v1")          # "me10_actual_hours"
        op = target.replace("_actual_hours", "")   # "me10"
        bundles.append((op, p))
    return bundles


def _input_row(inputs: QuoteInput) -> pd.DataFrame:
    """Convert a QuoteInput into a 1-row DataFrame with all model features."""
    row = inputs.model_dump()
    # Fill missing optional numerics with 0.0 — identical to training default.
    for col in QUOTE_NUM_FEATURES:
        row.setdefault(col, 0.0)
        if row.get(col) is None:
            row[col] = 0.0
    for col in QUOTE_CAT_FEATURES:
        row.setdefault(col, "")
    return pd.DataFrame([row])


def _contributions_for_op(
    bundle: dict[str, Any], row: pd.DataFrame, top_n: int
) -> list[DriverContribution]:
    """Return the top-N signed contributions for a single op model.

    Uses shap.TreeExplainer as the fallback because sklearn GradientBoostingRegressor
    does not support pred_contrib (that is a LightGBM/XGBoost-only parameter).
    """
    pipeline = bundle["pipeline"]  # sklearn Pipeline of (preprocessor, estimator)
    X = pipeline[:-1].transform(row)
    est = pipeline[-1]

    try:
        # LightGBM / XGB / CatBoost native — not used for sklearn GBR,
        # but kept so the code degrades gracefully if the model type changes.
        contribs = est.predict(X, pred_contrib=True)
        contrib_vec = np.asarray(contribs).ravel()[:-1]  # drop bias term
    except TypeError:
        import shap
        explainer = shap.TreeExplainer(est)
        vals = explainer.shap_values(X)
        contrib_vec = np.asarray(vals).ravel()

    feature_names = _output_feature_names(pipeline[:-1])
    if len(feature_names) != len(contrib_vec):
        # Safety: if the preprocessor produced a different width than we
        # can name, bail so callers mark op unavailable.
        raise ValueError(
            f"feature name/contribution length mismatch "
            f"({len(feature_names)} vs {len(contrib_vec)})"
        )

    pairs = sorted(
        zip(feature_names, contrib_vec, strict=False),
        key=lambda p: abs(p[1]),
        reverse=True,
    )[:top_n]

    displayed = row.iloc[0].to_dict()
    drivers: list[DriverContribution] = []
    for feat, contrib in pairs:
        # Feature names from ColumnTransformer look like "num__stations_count"
        # or "cat__industry_segment_Automotive".
        raw, value_label = _split_feature_name(feat, displayed)
        drivers.append(
            DriverContribution(
                feature=_humanize(raw),
                contribution=float(contrib),
                value=value_label,
            )
        )
    return drivers


def _output_feature_names(preprocessor) -> list[str]:
    try:
        return list(preprocessor.get_feature_names_out())
    except Exception:
        logger.exception("get_feature_names_out failed; falling back to config feature list")
        # Fall back to best-effort: numerics then categoricals by config.
        return QUOTE_NUM_FEATURES + QUOTE_CAT_FEATURES


def _split_feature_name(name: str, row_values: dict[str, Any]) -> tuple[str, str]:
    """From 'num__stations_count' -> ('stations_count', '8')
       From 'cat__industry_segment_Automotive' -> ('industry_segment', 'Automotive')."""
    if "__" in name:
        _, rest = name.split("__", 1)
    else:
        rest = name
    # Try matching against known cat features first.
    for cat in QUOTE_CAT_FEATURES:
        if rest.startswith(cat + "_"):
            return cat, rest[len(cat) + 1:]
    if rest in QUOTE_NUM_FEATURES:
        val = row_values.get(rest)
        return rest, str(val) if val is not None else ""
    return rest, ""


def compute_drivers(inputs: QuoteInput, top_n: int = 3) -> list[OperationDrivers]:
    bundles = _discover_bundles()
    row = _input_row(inputs)
    out: list[OperationDrivers] = []
    for op, path in bundles:
        try:
            bundle = _load_bundle(path)
            drivers = _contributions_for_op(bundle, row, top_n)
            out.append(OperationDrivers(operation=op, drivers=drivers, available=True))
        except Exception as exc:  # noqa: BLE001 — graceful degrade, reason captured
            out.append(
                OperationDrivers(
                    operation=op,
                    drivers=[],
                    available=False,
                    reason=str(exc)[:200],
                )
            )
    return out


def compute_neighbors(inputs: QuoteInput, k: int = 5) -> list[NeighborProject]:
    df = storage.read_master()
    if df is None or df.empty:
        return []

    bundles = _discover_bundles()
    if not bundles:
        return []

    # Use any bundle's preprocessor to map both the live input and the
    # master dataset into the same encoded vector space.
    _op, first_path = bundles[0]
    preproc = _load_bundle(first_path)["pipeline"][:-1]
    X_master = preproc.transform(df)
    X_live = preproc.transform(_input_row(inputs))

    # Cosine similarity. Normalize, multiply.
    def _normalize(a):
        n = np.linalg.norm(a, axis=1, keepdims=True)
        n[n == 0] = 1.0
        return a / n

    X_master_n = _normalize(np.asarray(X_master))
    X_live_n = _normalize(np.asarray(X_live))
    sims = (X_master_n @ X_live_n.T).ravel()

    idx = np.argsort(-sims)[:k]
    out: list[NeighborProject] = []
    for i in idx:
        row = df.iloc[int(i)]
        actual = _row_total_hours(row)
        out.append(
            NeighborProject(
                project_name=str(row.get("project_id") or f"Project #{int(i)}"),
                year=_maybe_year(row),
                industry_segment=str(row.get("industry_segment", "")),
                automation_level=str(row.get("automation_level", "")),
                stations=_maybe_int(row.get("stations_count")),
                actual_hours=float(actual),
                similarity=float(sims[int(i)]),
            )
        )
    return out


def _row_total_hours(row) -> float:
    cols = [c for c in row.index if c.endswith("_hours")]
    vals = [row[c] for c in cols if pd.notna(row[c])]
    return float(sum(vals)) if vals else 0.0


def _maybe_year(row) -> int | None:
    for col in ("year", "quote_year", "project_year"):
        if col in row.index and pd.notna(row[col]):
            try:
                return int(row[col])
            except (TypeError, ValueError):
                return None
    return None


def _maybe_int(v) -> int | None:
    if v is None or pd.isna(v):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None
