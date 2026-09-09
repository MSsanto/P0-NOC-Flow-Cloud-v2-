from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi_is_exposed_under_v1() -> None:
    response = client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    body = response.json()
    assert body["info"]["title"] == "NOC Flow Cloud API"
    assert "/api/v1/health/live" in body["paths"]
    assert "/api/v1/health/ready" in body["paths"]
    assert "503" in body["paths"]["/api/v1/health/ready"]["get"]["responses"]
