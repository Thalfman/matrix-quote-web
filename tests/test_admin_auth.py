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
