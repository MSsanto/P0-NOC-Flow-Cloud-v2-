import json
import logging
import re

from fastapi.testclient import TestClient

from app.main import app


def test_request_id_is_propagated_and_logged_without_sensitive_headers(caplog) -> None:
    caplog.set_level(logging.INFO, logger="nocflow.http")
    client = TestClient(app)

    response = client.get(
        "/api/v1/health/live",
        headers={
            "X-Request-ID": "sprint5-request-001",
            "Authorization": "Bearer super-secret-token",
            "Cookie": "session=secret-cookie",
        },
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "sprint5-request-001"

    record = next(
        json.loads(item.message)
        for item in caplog.records
        if item.name == "nocflow.http" and '"event":"http_request"' in item.message
    )
    assert record["request_id"] == "sprint5-request-001"
    assert record["method"] == "GET"
    assert record["path"] == "/api/v1/health/live"
    assert record["status_code"] == 200
    assert "super-secret-token" not in caplog.text
    assert "secret-cookie" not in caplog.text


def test_invalid_request_id_is_replaced() -> None:
    client = TestClient(app)
    response = client.get(
        "/api/v1/health/live",
        headers={"X-Request-ID": "invalid request id"},
    )

    assert response.status_code == 200
    request_id = response.headers["X-Request-ID"]
    assert request_id != "invalid request id"
    assert re.fullmatch(r"[0-9a-f-]{36}", request_id)
