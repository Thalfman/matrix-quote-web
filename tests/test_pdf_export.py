# tests/test_pdf_export.py
from __future__ import annotations

import pytest

# WeasyPrint requires native pango/gobject libs that are not present on Windows dev boxes.
# On those machines the import raises OSError. Skip the entire module rather than fail.
try:
    import weasyprint as _wp  # noqa: F401
except OSError:
    pytest.skip(
        "WeasyPrint native libs (pango/gobject) not available on this platform",
        allow_module_level=True,
    )


def _adhoc_body(saved_quote_payload):
    return {
        "name": "Draft",
        "project_name": "Ad Hoc",
        "created_by": "Tester",
        "inputs": saved_quote_payload["inputs"],
        "prediction": saved_quote_payload["prediction"],
    }


def test_saved_quote_pdf_download(admin_client, saved_quote_payload):
    payload = {**saved_quote_payload, "project_name": "Acme Line 3"}
    created = admin_client.post("/api/quotes", json=payload).json()
    r = admin_client.get(f"/api/quotes/{created['id']}/pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 5000  # non-trivial body
    disp = r.headers["content-disposition"]
    assert "Matrix-Quote-Acme-Line-3" in disp


def test_adhoc_pdf(client, saved_quote_payload):
    # /api/quote/pdf is the ad-hoc (unauthenticated) PDF endpoint — different
    # from the gated /api/quotes/{id}/pdf route.
    r = client.post("/api/quote/pdf", json=_adhoc_body(saved_quote_payload))
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(r.content) > 5000


def test_saved_quote_pdf_404_when_missing(admin_client):
    r = admin_client.get("/api/quotes/does-not-exist/pdf")
    assert r.status_code == 404


def test_saved_quote_pdf_requires_auth(client):
    r = client.get("/api/quotes/any-id/pdf")
    assert r.status_code == 401


def test_adhoc_pdf_filename_is_header_safe(client, saved_quote_payload):
    # Inject quote + CRLF + semicolon into project_name to attempt header injection
    payload = {
        "name": "Draft",
        "project_name": 'Bad"Name;\r\nX-Injected: 1',
        "created_by": "Tester",
        "inputs": saved_quote_payload["inputs"],
        "prediction": saved_quote_payload["prediction"],
    }
    resp = client.post("/api/quote/pdf", json=payload)
    assert resp.status_code == 200
    cd = resp.headers["content-disposition"]
    # Must not contain raw quote/CRLF/semicolon/colon from the injected value
    assert "\r" not in cd and "\n" not in cd
    # Confirm the sanitized filename is interpolated (all suspect chars replaced)
    # The value must NOT contain an unescaped '"', ';', or embedded header.
    # Header format: 'attachment; filename="Matrix-Quote-<safe>-YYYYMMDD.pdf"'
    # There is exactly one ';' separating 'attachment' from 'filename='; no others.
    assert cd.count(";") == 1
    assert "X-Injected" not in cd
