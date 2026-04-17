from fastapi.testclient import TestClient

VALID_QUOTE_INPUT = {
    "industry_segment": "Automotive",
    "system_category": "Machine Tending",
    "automation_level": "Robotic",
    "plc_family": "AB Compact Logix",
    "hmi_family": "AB PanelView Plus",
    "vision_type": "None",
}


def test_single_quote_returns_409_when_models_not_ready(client: TestClient) -> None:
    resp = client.post("/api/quote/single", json=VALID_QUOTE_INPUT)
    assert resp.status_code == 409
    assert "not trained" in resp.json()["detail"].lower()


def test_single_quote_rejects_missing_required_categorical(client: TestClient) -> None:
    bad = {k: v for k, v in VALID_QUOTE_INPUT.items() if k != "industry_segment"}
    resp = client.post("/api/quote/single", json=bad)
    assert resp.status_code == 422


def test_batch_quote_returns_409_when_models_not_ready(client: TestClient) -> None:
    # No file upload needed to hit the 409 — the guard runs first.
    resp = client.post(
        "/api/quote/batch",
        files={"file": ("q.csv", b"industry_segment\nAutomotive\n", "text/csv")},
    )
    assert resp.status_code == 409
