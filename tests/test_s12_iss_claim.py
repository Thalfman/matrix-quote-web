"""Tests for S-12: JWT iss claim validation in require_admin.

The login endpoint must embed iss='matrix-quote-web' in every token and the
require_admin guard must reject tokens whose iss does not match, even when the
signature is valid (same secret, different issuer).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from fastapi.testclient import TestClient

JWT_SECRET = "TEST-ONLY-test-secret-at-least-32-chars!!"
JWT_ALGORITHM = "HS256"


def _forge_token(iss: str, secret: str = JWT_SECRET) -> str:
    """Build a structurally valid, correctly signed JWT with an arbitrary iss."""
    claims = {
        "sub": "admin",
        "name": "admin",
        "iat": datetime.now(UTC),
        "iss": iss,
        "exp": datetime.now(UTC) + timedelta(hours=1),
    }
    return jwt.encode(claims, secret, algorithm=JWT_ALGORITHM)


# ---------------------------------------------------------------------------
# Happy path: token issued by the login endpoint contains expected claims.
# (Covered by test_login_accepts_display_name_and_claim_round_trips, re-stated
# here so S-12 coverage is self-contained.)
# ---------------------------------------------------------------------------

def test_login_token_contains_iat_and_correct_iss(client: TestClient) -> None:
    resp = client.post("/api/admin/login", json={"password": "test-password"})
    assert resp.status_code == 200
    token = resp.json()["token"]
    claims = jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        issuer="matrix-quote-web",
    )
    assert "iat" in claims, "iat claim must be present"
    assert claims["iss"] == "matrix-quote-web", "iss must be matrix-quote-web"


# ---------------------------------------------------------------------------
# Security: forged token with a different iss must be rejected with 401.
# ---------------------------------------------------------------------------

def test_require_admin_rejects_token_with_wrong_iss(client: TestClient) -> None:
    """A valid-signature token with iss='malicious' must return 401."""
    token = _forge_token(iss="malicious")
    resp = client.get(
        "/api/admin/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401, (
        f"Expected 401 for wrong-iss token, got {resp.status_code}"
    )


def test_require_admin_rejects_token_with_empty_iss(client: TestClient) -> None:
    """A valid-signature token with iss='' must also return 401."""
    token = _forge_token(iss="")
    resp = client.get(
        "/api/admin/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 401


def test_require_admin_accepts_token_with_correct_iss(client: TestClient) -> None:
    """A correctly issued token (iss=matrix-quote-web) must be accepted."""
    token = _forge_token(iss="matrix-quote-web")
    resp = client.get(
        "/api/admin/overview",
        headers={"Authorization": f"Bearer {token}"},
    )
    # The /overview stub returns 501 — confirms the auth layer passed.
    assert resp.status_code == 501, (
        f"Expected 501 (auth passed, stub handler), got {resp.status_code}"
    )
