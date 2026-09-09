from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_liveness_returns_ok_and_request_id() -> None:
    response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


def test_request_id_is_preserved_when_valid() -> None:
    response = client.get(
        "/api/v1/health/live",
        headers={"X-Request-ID": "noc-test-123"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "noc-test-123"


def test_invalid_request_id_is_replaced() -> None:
    response = client.get(
        "/api/v1/health/live",
        headers={"X-Request-ID": "not valid because spaces"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] != "not valid because spaces"


def test_readiness_checks_database() -> None:
    response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "checks": {"database": "up"}}
