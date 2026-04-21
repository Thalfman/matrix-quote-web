# backend/app/pdf.py
"""Render a saved-quote Jinja template to a PDF bytes payload."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .schemas_api import SavedQuote

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def _scoped_url_fetcher(url: str):
    """Only allow file:// URLs that resolve inside TEMPLATES_DIR; block remote."""
    from weasyprint import default_url_fetcher  # noqa: PLC0415

    if url.startswith("file://"):
        local = Path(url[len("file://"):]).resolve()
        tdir = TEMPLATES_DIR.resolve()
        if tdir not in local.parents and local != tdir:
            raise PermissionError(f"URL outside templates dir: {url}")
    elif url.startswith(("http://", "https://")):
        raise PermissionError(f"Remote URL fetch blocked: {url}")
    return default_url_fetcher(url)


BUCKET_LABELS = {
    "mechanical":    "Mechanical",
    "electrical":    "Electrical",
    "controls":      "Controls",
    "robotics":      "Robotics",
    "assembly":      "Assembly",
    "shipping":      "Shipping",
    "install":       "Install",
    "startup":       "Startup",
    "engineering":   "Engineering",
    "project_mgmt":  "Project management",
    "documentation": "Documentation",
    "misc":          "Misc",
}

INPUT_LABELS = {
    "industry_segment":       "Industry",
    "system_category":        "System category",
    "automation_level":       "Automation level",
    "plc_family":             "PLC family",
    "hmi_family":             "HMI family",
    "vision_type":            "Vision type",
    "stations_count":         "Stations",
    "robot_count":            "Robots",
    "conveyor_length_ft":     "Conveyor length (ft)",
    "fixture_sets":           "Fixture sets",
    "part_types":             "Part types",
    "servo_axes":             "Servo axes",
    "complexity_score_1_5":   "Complexity",
}


def _format_hours(n: float) -> str:
    return f"{round(n):,}"


def _humanize_bucket(key: str) -> str:
    return BUCKET_LABELS.get(key, key.replace("_", " ").title())


def _render_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    env.globals["format_hours"] = _format_hours
    env.globals["humanize_bucket"] = _humanize_bucket
    return env


def _input_rows(inputs: Any) -> list[tuple[str, str]]:
    data = inputs.model_dump() if hasattr(inputs, "model_dump") else dict(inputs)
    rows: list[tuple[str, str]] = []
    for key, label in INPUT_LABELS.items():
        if key in data and data[key] not in (None, ""):
            rows.append((label, str(data[key])))
    return rows


def render_quote_pdf(quote: SavedQuote, *, quote_number: str) -> bytes:
    # Lazy import: weasyprint requires native pango/gobject libs that are absent
    # on Windows dev boxes. Importing at call time means the module loads fine
    # without those libs; the OSError only surfaces when actually rendering.
    from weasyprint import HTML  # noqa: PLC0415

    env = _render_env()
    template = env.get_template("quote_pdf.html")
    html = template.render(
        quote=quote,
        quote_number=quote_number,
        prepared_on=datetime.utcnow().strftime("%b %d, %Y"),
        input_rows=_input_rows(quote.inputs),
    )
    pdf_bytes = HTML(
        string=html,
        base_url=str(TEMPLATES_DIR),
        url_fetcher=_scoped_url_fetcher,
    ).write_pdf()
    return pdf_bytes
