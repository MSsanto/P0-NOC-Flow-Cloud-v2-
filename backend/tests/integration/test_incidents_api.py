from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from app.db.session import get_session_factory
from app.main import app
from app.modules.incidents.infrastructure.models import IncidentEventModel, IncidentModel
from app.modules.tenancy.infrastructure.models import TenantModel


@pytest.fixture(autouse=True)
def clean_database():
    factory = get_session_factory()
    with factory() as session:
        session.execute(delete(IncidentEventModel))
        session.execute(delete(IncidentModel))
        session.execute(delete(TenantModel))
        session.commit()

    yield

    with factory() as session:
        session.execute(delete(IncidentEventModel))
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


def _create(client: TestClient) -> dict[str, object]:
    response = client.post("/api/v1/incidents", json=_payload())
    assert response.status_code == 201
    return response.json()


def test_create_list_get_and_created_timeline(client: TestClient) -> None:
    created = _create(client)
    assert created["status"] == "OPEN"
    assert "tenant_id" not in created
    assert "created_by_subject" not in created

    list_response = client.get("/api/v1/incidents")
    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [created["id"]]

    detail_response = client.get(f"/api/v1/incidents/{created['id']}")
    assert detail_response.status_code == 200

    timeline_response = client.get(f"/api/v1/incidents/{created['id']}/timeline")
    assert timeline_response.status_code == 200
    timeline = timeline_response.json()
    assert [item["event_type"] for item in timeline] == ["INCIDENT_CREATED"]
    assert timeline[0]["incident_id"] == created["id"]


def test_update_normalize_and_negative_transitions(client: TestClient) -> None:
    created = _create(client)
    incident_id = created["id"]

    update_response = client.post(
        f"/api/v1/incidents/{incident_id}/updates",
        json={"message": "Operadora acionada; protocolo DEMO-123."},
    )
    assert update_response.status_code == 200
    assert update_response.json()["version"] == 2

    normalize_response = client.post(
        f"/api/v1/incidents/{incident_id}/normalize",
        json={"note": "Conectividade restabelecida."},
    )
    assert normalize_response.status_code == 200
    assert normalize_response.json()["status"] == "RESOLVED"
    assert normalize_response.json()["version"] == 3

    second_normalize = client.post(
        f"/api/v1/incidents/{incident_id}/normalize",
        json={},
    )
    assert second_normalize.status_code == 409

    update_after_resolve = client.post(
        f"/api/v1/incidents/{incident_id}/updates",
        json={"message": "Atualização não permitida."},
    )
    assert update_after_resolve.status_code == 409

    timeline_response = client.get(f"/api/v1/incidents/{incident_id}/timeline")
    assert timeline_response.status_code == 200
    assert [item["event_type"] for item in timeline_response.json()] == [
        "INCIDENT_CREATED",
        "INCIDENT_UPDATED",
        "INCIDENT_NORMALIZED",
    ]


def test_action_payloads_reject_forged_authority_fields(client: TestClient) -> None:
    created = _create(client)
    incident_id = created["id"]

    forged_update = client.post(
        f"/api/v1/incidents/{incident_id}/updates",
        json={
            "message": "Operadora acionada.",
            "tenant_id": "00000000-0000-4000-8000-000000000999",
        },
    )
    assert forged_update.status_code == 422

    forged_normalize = client.post(
        f"/api/v1/incidents/{incident_id}/normalize",
        json={
            "note": "Serviço restabelecido.",
            "actor_subject": "forged-actor",
        },
    )
    assert forged_normalize.status_code == 422


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


def test_unknown_incident_and_timeline_return_404(client: TestClient) -> None:
    incident_id = "00000000-0000-4000-8000-000000000999"

    detail = client.get(f"/api/v1/incidents/{incident_id}")
    timeline = client.get(f"/api/v1/incidents/{incident_id}/timeline")

    assert detail.status_code == 404
    assert timeline.status_code == 404
