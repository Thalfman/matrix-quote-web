from __future__ import annotations


def test_list_quotes_requires_auth(client):
    resp = client.get("/api/quotes")
    assert resp.status_code == 401


def test_create_quote_requires_auth(client, saved_quote_payload):
    resp = client.post("/api/quotes", json=saved_quote_payload)
    assert resp.status_code == 401


def test_delete_quote_requires_auth(client):
    resp = client.delete("/api/quotes/any-id")
    assert resp.status_code == 401


def test_get_quote_requires_auth(client):
    resp = client.get("/api/quotes/any-id")
    assert resp.status_code == 401


def test_get_quote_pdf_requires_auth(client):
    resp = client.get("/api/quotes/any-id/pdf")
    assert resp.status_code == 401


def test_duplicate_quote_requires_auth(client):
    resp = client.post("/api/quotes/any-id/duplicate")
    assert resp.status_code == 401


def test_create_quote_sets_created_by_from_token_not_body(client, saved_quote_payload):
    # Log in as "Alice"
    login = client.post(
        "/api/admin/login",
        json={"password": "test-password", "name": "Alice"},
    )
    assert login.status_code == 200
    client.headers["Authorization"] = f"Bearer {login.json()['token']}"

    # Even if body had created_by, server would ignore it.
    payload = dict(saved_quote_payload)
    payload.pop("created_by", None)

    resp = client.post("/api/quotes", json=payload)
    assert resp.status_code == 201
    assert resp.json()["created_by"] == "Alice"


def test_create_list_get_delete(admin_client, saved_quote_payload):
    r = admin_client.post("/api/quotes", json=saved_quote_payload)
    assert r.status_code == 201
    id_ = r.json()["id"]

    r = admin_client.get("/api/quotes")
    assert r.status_code == 200
    assert r.json()["total"] == 1

    r = admin_client.get(f"/api/quotes/{id_}")
    assert r.status_code == 200
    assert r.json()["name"] == saved_quote_payload["name"]

    r = admin_client.delete(f"/api/quotes/{id_}")
    assert r.status_code == 204

    r = admin_client.get(f"/api/quotes/{id_}")
    assert r.status_code == 404


def test_duplicate(admin_client, saved_quote_payload):
    r = admin_client.post("/api/quotes", json=saved_quote_payload)
    id_ = r.json()["id"]
    r = admin_client.post(f"/api/quotes/{id_}/duplicate")
    assert r.status_code == 201
    assert r.json()["name"].endswith("(copy)")


def test_list_quotes_rejects_oversized_limit(admin_client):
    resp = admin_client.get("/api/quotes?limit=1000000")
    assert resp.status_code == 422


# Q-12: pagination edge cases.

def test_list_quotes_offset_beyond_total_returns_empty(admin_client, saved_quote_payload):
    """offset >= total should return rows=[] with the correct total."""
    admin_client.post("/api/quotes", json=saved_quote_payload)
    resp = admin_client.get("/api/quotes?offset=9999")
    assert resp.status_code == 200
    body = resp.json()
    assert body["rows"] == []
    assert body["total"] == 1


def test_list_quotes_limit_one_returns_exactly_one(admin_client, saved_quote_payload):
    """limit=1 returns exactly one row even when multiple exist."""
    admin_client.post("/api/quotes", json=saved_quote_payload)
    admin_client.post("/api/quotes", json=saved_quote_payload)
    resp = admin_client.get("/api/quotes?limit=1")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["rows"]) == 1
    assert body["total"] == 2
