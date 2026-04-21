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


def test_batch_preview_rejects_non_xlsx_with_400(client):
    resp = client.post(
        "/api/quote/batch/preview",
        files={"file": ("garbage.xlsx", b"not an excel file", "application/vnd.ms-excel")},
    )
    assert resp.status_code == 400
    assert "Could not parse" in resp.json()["detail"]


def test_batch_rejects_non_xlsx_extension(client):
    resp = client.post(
        "/api/quote/batch",
        files={"file": ("data.exe", b"MZ\x90\x00", "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert "extension" in resp.json()["detail"].lower()


def test_batch_preview_rejects_non_xlsx_extension(client):
    resp = client.post(
        "/api/quote/batch/preview",
        files={"file": ("data.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400


# Q-12: 413 for > 10 MB upload.

def test_batch_preview_413_on_oversized_upload(client):
    """A file larger than 10 MB must return 413."""
    big_content = b"x" * (10 * 1024 * 1024 + 1)
    resp = client.post(
        "/api/quote/batch/preview",
        files={"file": ("data.xlsx", big_content,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert resp.status_code == 413
    assert "10 MB" in resp.json()["detail"]


def test_batch_413_on_oversized_upload(client):
    """batch/preview also returns 413 when upload exceeds 10 MB (batch guards models first)."""
    big_content = b"x" * (10 * 1024 * 1024 + 1)
    # Use preview endpoint because /batch checks models-ready before reading the body.
    resp = client.post(
        "/api/quote/batch/preview",
        files={"file": ("data.xlsx", big_content,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert resp.status_code == 413
