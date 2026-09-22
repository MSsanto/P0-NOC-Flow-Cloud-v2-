import json
import logging

from fastapi.testclient import TestClient

from app.core import middleware
from app.core.config import get_settings
from app.core.logging import JsonFormatter
from app.main import app


def test_json_formatter_emits_structured_safe_fields() -> None:
    formatter = JsonFormatter(get_settings())
    record = logging.LogRecord(
        name="nocflow.http",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="http_request",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-123"
    record.route = "/api/v1/health/live"
    record.method = "GET"
    record.status_code = 200
    record.duration_ms = 1.25

    payload = json.loads(formatter.format(record))

    assert payload["level"] == "INFO"
    assert payload["environment"] == "test"
    assert payload["request_id"] == "req-123"
    assert payload["route"] == "/api/v1/health/live"
    assert payload["method"] == "GET"
    assert payload["status_code"] == 200
    assert payload["duration_ms"] == 1.25
    assert "authorization" not in formatter.format(record).lower()


def test_request_log_correlates_request_and_trace_without_headers(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def capture(message: str, *, extra: dict[str, object]) -> None:
        captured["message"] = message
        captured["extra"] = extra

    monkeypatch.setattr(middleware.logger, "info", capture)
    trace_id = "0af7651916cd43dd8448eb211c80319c"

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/health/live",
            headers={
                "X-Request-ID": "req-observability-1",
                "traceparent": f"00-{trace_id}-b7ad6b7169203331-01",
                "Authorization": "Bearer must-not-be-logged",
            },
        )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "req-observability-1"
    assert captured["message"] == "http_request"
    extra = captured["extra"]
    assert isinstance(extra, dict)
    assert extra["request_id"] == "req-observability-1"
    assert extra["trace_id"] == trace_id
    assert extra["route"] == "/health/live"
    assert extra["method"] == "GET"
    assert extra["status_code"] == 200
    assert "must-not-be-logged" not in repr(extra)
