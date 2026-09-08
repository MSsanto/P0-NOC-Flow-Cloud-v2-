from fastapi import APIRouter, Query
from fastapi.testclient import TestClient

from app.main import create_app


def test_request_validation_uses_problem_details_contract() -> None:
    app = create_app()
    router = APIRouter()

    @router.get("/_test/validation")
    def validation(value: int = Query(ge=1)) -> dict[str, int]:
        return {"value": value}

    app.include_router(router, prefix="/api/v1")
    client = TestClient(app)

    response = client.get("/api/v1/_test/validation?value=0")

    assert response.status_code == 400
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["status"] == 400
    assert body["type"] == "https://nocflow.example/problems/request-validation"
    assert body["code"] == "REQUEST_VALIDATION_ERROR"
    assert body["request_id"] == response.headers["X-Request-ID"]
    assert body["errors"][0]["field"] == "value"
    assert body["errors"][0]["code"]
    assert body["errors"][0]["message"]
