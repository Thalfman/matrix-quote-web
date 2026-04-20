import pytest
from fastapi.testclient import TestClient


def test_login_rejects_wrong_password(client: TestClient) -> None:
    resp = client.post("/api/admin/login", json={"password": "wrong"})
    assert resp.status_code == 401


def test_login_issues_token(client: TestClient) -> None:
    resp = client.post("/api/admin/login", json={"password": "test-password"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["token"]
    assert body["expires_at"]


def test_admin_routes_require_bearer_token(client: TestClient) -> None:
    # Any admin route — pick one that's stubbed with 501 so we prove the
    # 401 comes from the auth layer, not the handler.
    resp = client.get("/api/admin/overview")
    assert resp.status_code == 401


def test_admin_routes_accept_valid_token(admin_client: TestClient) -> None:
    # With a valid token, the stubbed handler returns 501 (not 401).
    resp = admin_client.get("/api/admin/overview")
    assert resp.status_code == 501


def test_empty_jwt_secret_refuses_startup(monkeypatch):
    """Production startup must abort when ADMIN_JWT_SECRET is blank."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("ADMIN_PASSWORD", "x" * 12)
    monkeypatch.setenv("ADMIN_JWT_SECRET", "")
    from backend.app.deps import get_settings
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="ADMIN_JWT_SECRET"):
        get_settings()
    get_settings.cache_clear()


def test_short_jwt_secret_refuses_startup(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("ADMIN_PASSWORD", "x" * 12)
    monkeypatch.setenv("ADMIN_JWT_SECRET", "short")
    from backend.app.deps import get_settings
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="at least 32"):
        get_settings()
    get_settings.cache_clear()


def test_empty_admin_password_refuses_startup(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("ADMIN_PASSWORD", "")
    monkeypatch.setenv("ADMIN_JWT_SECRET", "x" * 40)
    from backend.app.deps import get_settings
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="ADMIN_PASSWORD"):
        get_settings()
    get_settings.cache_clear()


def test_login_accepts_display_name_and_claim_round_trips(client):
    resp = client.post(
        "/api/admin/login",
        json={"password": "test-password", "name": "Alice"},
    )
    assert resp.status_code == 200
    token = resp.json()["token"]

    from jose import jwt
    claims = jwt.decode(token, "test-secret-at-least-32-chars-long!!", algorithms=["HS256"])
    assert claims["sub"] == "admin"
    assert claims["name"] == "Alice"


def test_login_without_name_falls_back_to_admin(client):
    resp = client.post("/api/admin/login", json={"password": "test-password"})
    assert resp.status_code == 200
    token = resp.json()["token"]
    from jose import jwt
    claims = jwt.decode(token, "test-secret-at-least-32-chars-long!!", algorithms=["HS256"])
    assert claims["name"] == "admin"


def test_admin_login_rate_limit_kicks_in(client):
    """6th wrong-password attempt in a minute returns 429, not 401."""
    for _ in range(5):
        r = client.post("/api/admin/login", json={"password": "wrong"})
        assert r.status_code == 401
    r = client.post("/api/admin/login", json={"password": "wrong"})
    assert r.status_code == 429
