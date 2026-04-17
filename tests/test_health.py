from fastapi.testclient import TestClient


def test_health_returns_ok_with_untrained_state(client: TestClient) -> None:
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["models_ready"] is False


def test_metrics_is_empty_when_untrained(client: TestClient) -> None:
    resp = client.get("/api/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert body["models_ready"] is False
    assert body["metrics"] == []


def test_dropdowns_returns_fallbacks_without_master(client: TestClient) -> None:
    resp = client.get("/api/catalog/dropdowns")
    assert resp.status_code == 200
    body = resp.json()
    assert "Automotive" in body["industry_segment"]
    assert body["automation_level"]
