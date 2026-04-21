"""Unit tests for S-10: _scoped_url_fetcher in backend/app/pdf.py.

The fetcher must:
- Allow a file:// URL that resolves inside TEMPLATES_DIR (delegated to
  default_url_fetcher — verified with a monkeypatch sentinel).
- Raise PermissionError for a file:// URL that resolves *outside* TEMPLATES_DIR.
- Raise PermissionError for http:// and https:// remote URLs.

WeasyPrint requires native pango/gobject libs absent on Windows dev boxes.
The import inside _scoped_url_fetcher crashes before the guard logic can run
in that scenario, so these tests are skipped when WeasyPrint is not importable
(same pattern as test_pdf_export.py).
"""

from __future__ import annotations

import pytest

try:
    import weasyprint as _wp  # noqa: F401
except OSError:
    pytest.skip(
        "WeasyPrint native libs (pango/gobject) not available on this platform",
        allow_module_level=True,
    )

from backend.app.pdf import TEMPLATES_DIR, _scoped_url_fetcher


def test_url_fetcher_blocks_path_traversal_outside_templates(tmp_path):
    """A file:// URL pointing outside TEMPLATES_DIR raises PermissionError."""
    outside = tmp_path / "passwd"
    outside.write_text("root:x:0:0:root:/root:/bin/bash")
    url = "file://" + str(outside.resolve())
    with pytest.raises(PermissionError, match="outside templates dir"):
        _scoped_url_fetcher(url)


def test_url_fetcher_blocks_etc_passwd_style_escape():
    """Canonical path-traversal attack: file:///etc/passwd."""
    with pytest.raises(PermissionError, match="outside templates dir"):
        _scoped_url_fetcher("file:///etc/passwd")


def test_url_fetcher_blocks_http():
    """http:// remote URLs are blocked unconditionally."""
    with pytest.raises(PermissionError, match="Remote URL fetch blocked"):
        _scoped_url_fetcher("http://example.com/logo.png")


def test_url_fetcher_blocks_https():
    """https:// remote URLs are blocked unconditionally."""
    with pytest.raises(PermissionError, match="Remote URL fetch blocked"):
        _scoped_url_fetcher("https://malicious.example/evil.css")


def test_url_fetcher_allows_file_inside_templates(monkeypatch):
    """A file:// URL resolving inside TEMPLATES_DIR is delegated to default_url_fetcher."""
    sentinel = object()

    import weasyprint
    monkeypatch.setattr(weasyprint, "default_url_fetcher", lambda url: sentinel)

    url = "file://" + str(TEMPLATES_DIR.resolve())
    result = _scoped_url_fetcher(url)
    assert result is sentinel, "Expected delegation to default_url_fetcher for in-scope URL"
