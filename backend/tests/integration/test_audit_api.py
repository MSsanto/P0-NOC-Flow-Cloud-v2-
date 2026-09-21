from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.db.session import get_session_factory
from app.main import app
from app.modules.audit.infrastructure.models import AuditEventModel
from app.modules.tenancy.application.context import RequestContext
from app.modules.tenancy.application.security import Role
from app.modules.tenancy.presentation.dependencies import get_request_context


def _payload() -> dict[str, object]:
    return {
        "title": "Auditoria Sprint 5",
        "affected_resource": "DEMO-S5-EDGE-01",
        "severity": "HIGH",
        "impact_type": "OUTAGE",
        "symptoms": "Incidente sintético para validar trilha de auditoria.",
        "started_at": (datetime.now(UTC) - timedelta(minutes=10)).isoformat(),
    }


def test_critical_mutations_are_audited_and_query_is_restricted() -> None:
    client = TestClient(app)

    created = client.post(
        "/api/v1/incidents",
        json=_payload(),
        headers={"X-Request-ID": "audit-create-001"},
    )
    assert created.status_code == 201
    incident_id = created.json()["id"]

    updated = client.post(
        f"/api/v1/incidents/{incident_id}/updates",
        json={"message": "Atualização sintética para auditoria."},
        headers={"X-Request-ID": "audit-update-001"},
    )
    assert updated.status_code == 200

    normalized = client.post(
        f"/api/v1/incidents/{incident_id}/normalize",
        json={"note": "Normalização sintética."},
        headers={"X-Request-ID": "audit-normalize-001"},
    )
    assert normalized.status_code == 200

    page = client.get("/api/v1/audit-events?page_size=100")
    assert page.status_code == 200
    items = page.json()["items"]
    incident_items = [item for item in items if item["resource_id"] == incident_id]
    assert {item["action"] for item in incident_items} == {
        "incident.created",
        "incident.updated",
        "incident.normalized",
    }
    assert {item["request_id"] for item in incident_items} == {
        "audit-create-001",
        "audit-update-001",
        "audit-normalize-001",
    }

    operator_context = RequestContext(
        tenant_id=UUID("00000000-0000-4000-8000-000000000001"),
        actor_subject="operator@example.test",
        roles=frozenset({Role.OPERATOR}),
    )
    app.dependency_overrides[get_request_context] = lambda: operator_context
    try:
        forbidden = client.get("/api/v1/audit-events")
    finally:
        app.dependency_overrides.pop(get_request_context, None)
    assert forbidden.status_code == 403


def test_failed_mutation_does_not_create_audit_event() -> None:
    client = TestClient(app)
    created = client.post("/api/v1/incidents", json=_payload())
    assert created.status_code == 201
    incident_id = created.json()["id"]
    assert client.post(f"/api/v1/incidents/{incident_id}/normalize", json={}).status_code == 200

    factory = get_session_factory()
    with factory() as session:
        before = session.scalar(select(AuditEventModel).where(
            AuditEventModel.resource_id == UUID(incident_id),
            AuditEventModel.action == "incident.updated",
        ))
    failed = client.post(
        f"/api/v1/incidents/{incident_id}/updates",
        json={"message": "Não deve ser auditado porque a mutação falha."},
    )
    assert failed.status_code == 409
    with factory() as session:
        after = session.scalar(select(AuditEventModel).where(
            AuditEventModel.resource_id == UUID(incident_id),
            AuditEventModel.action == "incident.updated",
        ))
    assert before is None
    assert after is None


def test_audit_filter_does_not_expose_payload_content() -> None:
    client = TestClient(app)
    created = client.post("/api/v1/incidents", json=_payload())
    assert created.status_code == 201

    page = client.get("/api/v1/audit-events?action=incident.created")
    assert page.status_code == 200
    serialized = str(page.json())
    assert "Incidente sintético para validar trilha de auditoria." not in serialized
    assert "symptoms" not in serialized
