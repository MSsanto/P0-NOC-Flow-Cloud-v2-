from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError

from app.db.session import get_session_factory
from app.main import app
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Role
from app.modules.tenancy.presentation.dependencies import get_request_context
from app.modules.incidents.infrastructure.models import IncidentEventModel, IncidentModel
from app.modules.operations.infrastructure.models import HandoverItemModel, HandoverModel
from app.modules.tenancy.infrastructure.models import TenantMembershipModel, TenantModel


@pytest.fixture(autouse=True)
def clean_database():
    factory = get_session_factory()
    with factory() as session:
        session.execute(delete(HandoverItemModel))
        session.execute(delete(HandoverModel))
        session.execute(delete(IncidentEventModel))
        session.execute(delete(IncidentModel))
        session.execute(delete(TenantMembershipModel))
        session.execute(delete(TenantModel))
        session.commit()
    yield
    with factory() as session:
        session.execute(delete(HandoverItemModel))
        session.execute(delete(HandoverModel))
        session.execute(delete(IncidentEventModel))
        session.execute(delete(IncidentModel))
        session.execute(delete(TenantMembershipModel))
        session.execute(delete(TenantModel))
        session.commit()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def _incident_payload(severity: str = "HIGH") -> dict[str, object]:
    return {
        "title": "Incidente Sprint 4",
        "affected_resource": "DEMO-S4-EDGE-01",
        "severity": severity,
        "impact_type": "OUTAGE",
        "symptoms": "Incidente sintético para validar dashboard e handover.",
        "started_at": (datetime.now(UTC) - timedelta(minutes=20)).isoformat(),
    }


def test_dashboard_preview_finalize_history_and_snapshot_immutability(
    client: TestClient,
) -> None:
    created = client.post("/api/v1/incidents", json=_incident_payload("CRITICAL"))
    assert created.status_code == 201
    incident_id = created.json()["id"]

    update = client.post(
        f"/api/v1/incidents/{incident_id}/updates",
        json={"message": "Operadora sintética acionada."},
    )
    assert update.status_code == 200

    dashboard = client.get("/api/v1/dashboard/summary")
    assert dashboard.status_code == 200
    body = dashboard.json()
    assert body["active_count"] == 1
    assert body["critical_active_count"] == 1
    assert body["items"][0]["id"] == incident_id

    preview = client.get("/api/v1/handovers/preview")
    assert preview.status_code == 200
    assert [item["incident_id"] for item in preview.json()["items"]] == [incident_id]

    forged = client.post(
        "/api/v1/handovers",
        json={
            "observations": "Tentativa forjada.",
            "tenant_id": "00000000-0000-4000-8000-000000000999",
        },
    )
    assert forged.status_code == 422

    finalized = client.post(
        "/api/v1/handovers",
        json={"observations": "Pendência acompanhada pelo próximo turno."},
    )
    assert finalized.status_code == 201
    handover = finalized.json()
    assert handover["version"] == 1
    assert handover["items"][0]["status"] == "OPEN"
    assert handover["items"][0]["last_event_message"] == "Operadora sintética acionada."

    history = client.get("/api/v1/handovers")
    assert history.status_code == 200
    assert history.json()["total"] == 1
    assert history.json()["items"][0]["id"] == handover["id"]

    latest = client.get("/api/v1/handovers/latest")
    assert latest.status_code == 200
    assert latest.json()["id"] == handover["id"]

    normalize = client.post(
        f"/api/v1/incidents/{incident_id}/normalize",
        json={"note": "Normalizado após a passagem."},
    )
    assert normalize.status_code == 200

    historical = client.get(f"/api/v1/handovers/{handover['id']}")
    assert historical.status_code == 200
    assert historical.json()["items"][0]["status"] == "OPEN"

    dashboard_after = client.get("/api/v1/dashboard/summary")
    assert dashboard_after.status_code == 200
    assert dashboard_after.json()["active_count"] == 0
    assert dashboard_after.json()["resolved_in_shift_count"] >= 1


def test_empty_handover_is_valid_and_versions_are_monotonic(client: TestClient) -> None:
    first = client.post("/api/v1/handovers", json={})
    second = client.post("/api/v1/handovers", json={"observations": "Turno sem incidentes."})

    assert first.status_code == 201
    assert first.json()["items"] == []
    assert first.json()["version"] == 1
    assert second.status_code == 201
    assert second.json()["version"] == 2


def test_viewer_can_read_but_cannot_finalize_handover(client: TestClient) -> None:
    seed = client.get("/api/v1/dashboard/summary")
    assert seed.status_code == 200

    viewer_context = RequestContext(
        tenant_id=UUID("00000000-0000-4000-8000-000000000001"),
        actor_subject="viewer@example.test",
        roles=frozenset({Role.VIEWER}),
    )
    app.dependency_overrides[get_request_context] = lambda: viewer_context
    try:
        preview = client.get("/api/v1/handovers/preview")
        finalize = client.post(
            "/api/v1/handovers",
            json={"observations": "Viewer cannot finalize."},
        )
    finally:
        app.dependency_overrides.pop(get_request_context, None)

    assert preview.status_code == 200
    assert finalize.status_code == 403


def test_handover_id_from_another_tenant_is_hidden(client: TestClient) -> None:
    assert client.get("/api/v1/dashboard/summary").status_code == 200

    other_tenant_id = uuid4()
    other_handover_id = uuid4()
    now = datetime.now(UTC)
    factory = get_session_factory()
    with factory() as session:
        session.add(
            TenantModel(
                id=other_tenant_id,
                slug=f"tenant-{other_tenant_id.hex[:8]}",
                name="Other Tenant",
                timezone="UTC",
                is_active=True,
            )
        )
        session.flush()
        session.add(
            HandoverModel(
                id=other_handover_id,
                tenant_id=other_tenant_id,
                window_start=now - timedelta(hours=12),
                window_end=now,
                version=1,
                observations=None,
                finalized_by_subject="other@example.test",
                finalized_at=now,
            )
        )
        session.commit()

    response = client.get(f"/api/v1/handovers/{other_handover_id}")
    assert response.status_code == 404
    assert response.json()["code"] == "HANDOVER_NOT_FOUND"


def test_database_prevents_duplicate_handover_version(client: TestClient) -> None:
    assert client.get("/api/v1/dashboard/summary").status_code == 200
    tenant_id = UUID("00000000-0000-4000-8000-000000000001")
    now = datetime.now(UTC)
    start = now - timedelta(hours=12)

    factory = get_session_factory()
    with factory() as session:
        session.add_all(
            [
                HandoverModel(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    window_start=start,
                    window_end=now,
                    version=1,
                    observations=None,
                    finalized_by_subject="operator-a@example.test",
                    finalized_at=now,
                ),
                HandoverModel(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    window_start=start,
                    window_end=now,
                    version=1,
                    observations=None,
                    finalized_by_subject="operator-b@example.test",
                    finalized_at=now,
                ),
            ]
        )
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
