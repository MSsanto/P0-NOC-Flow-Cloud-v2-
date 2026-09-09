from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import get_session_factory
from app.main import app
from app.modules.incidents.infrastructure.models import IncidentModel
from app.modules.tenancy.infrastructure.models import TenantModel


@pytest.fixture(autouse=True)
def clean_database():
    factory = get_session_factory()
    with factory() as session:
        session.execute(delete(IncidentModel))
        session.execute(delete(TenantModel))
        session.commit()

    yield

    with factory() as session:
        session.execute(delete(IncidentModel))
        session.execute(delete(TenantModel))
        session.commit()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _payload(*, minutes_ago: int = 1) -> dict[str, object]:
    return {
        "title": "WAN indisponível",
        "affected_resource": "WAN Loja 001",
        "severity": "HIGH",
        "impact_type": "OUTAGE",
        "symptoms": "Conectividade indisponível para a unidade.",
        "started_at": (datetime.now(UTC) - timedelta(minutes=minutes_ago)).isoformat(),
    }


def test_create_list_and_get_incident(client: TestClient) -> None:
    create_response = client.post("/api/v1/incidents", json=_payload())

    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "OPEN"
    assert created["title"] == "WAN indisponível"
    assert "tenant_id" not in created
    assert "created_by_subject" not in created

    list_response = client.get("/api/v1/incidents")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/incidents/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]


def test_list_orders_newest_incident_first(client: TestClient) -> None:
    older = client.post("/api/v1/incidents", json=_payload(minutes_ago=10)).json()
    newer = client.post("/api/v1/incidents", json=_payload(minutes_ago=1)).json()

    response = client.get("/api/v1/incidents")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [newer["id"], older["id"]]


def test_create_rejects_future_start_and_authority_fields(client: TestClient) -> None:
    future_payload = _payload()
    future_payload["started_at"] = (datetime.now(UTC) + timedelta(minutes=5)).isoformat()

    future_response = client.post("/api/v1/incidents", json=future_payload)
    assert future_response.status_code == 422

    forged_payload = _payload()
    forged_payload["tenant_id"] = "00000000-0000-4000-8000-000000000999"

    forged_response = client.post("/api/v1/incidents", json=forged_payload)
    assert forged_response.status_code == 422


def test_get_unknown_incident_returns_404(client: TestClient) -> None:
    response = client.get(
        "/api/v1/incidents/00000000-0000-4000-8000-000000000999"
    )

    assert response.status_code == 404
