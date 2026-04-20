"""Shared helpers for filename- and URL-safe quote identifiers."""

from __future__ import annotations

import re

_FILENAME_SAFE = re.compile(r"[^A-Za-z0-9_.-]+")


def safe_filename_part(value: str, max_len: int = 60) -> str:
    """Return a filename-segment-safe version of `value`.

    Replaces runs of unsafe characters with '-', strips leading/trailing '-',
    truncates to `max_len`. Returns the literal string "quote" if the result
    would be empty (e.g. all-whitespace input).
    """
    return _FILENAME_SAFE.sub("-", value).strip("-")[:max_len] or "quote"
