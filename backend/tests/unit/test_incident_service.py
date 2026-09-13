from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.modules.incidents.application.services import (
    IncidentAlreadyNormalizedError,
    IncidentCannotBeUpdatedError,
    IncidentNotFoundError,
    IncidentService,
    IncidentStartedAtInFutureError,
)
from app.modules.incidents.domain.entities import IncidentImpactType, IncidentSeverity


class InMemoryIncidentRepository:
    def __init__(self) -> None:
        self.items = []
        self.events = []

    def list_for_tenant(self, tenant_id: UUID):
        return [item for item in self.items if item.tenant_id == tenant_id]

    def get_for_tenant(self, tenant_id: UUID, incident_id: UUID):
        return next(
            (
                item
                for item in self.items
                if item.tenant_id == tenant_id and item.id == incident_id
            ),
            None,
        )

    def create(self, incident, event):
        self.items.append(incident)
        self.events.append(event)
        return incident

    def save_with_event(self, incident, event):
        self.items = [item for item in self.items if item.id != incident.id]
        self.items.append(incident)
        self.events.append(event)
        return incident

    def list_events_for_incident(self, tenant_id: UUID, incident_id: UUID):
        return [
            event
            for event in self.events
            if event.tenant_id == tenant_id and event.incident_id == incident_id
        ]


def _create(service: IncidentService, tenant_id: UUID):
    return service.create_incident(
        tenant_id=tenant_id,
        actor_subject="demo-operator",
        title="WAN outage",
        affected_resource="WAN",
        severity=IncidentSeverity.HIGH,
        impact_type=IncidentImpactType.OUTAGE,
        symptoms="Connectivity is unavailable",
        started_at=datetime.now(UTC) - timedelta(minutes=1),
    )


def test_create_list_get_and_timeline_are_tenant_scoped() -> None:
    repository = InMemoryIncidentRepository()
    service = IncidentService(repository)
    tenant_a = UUID("00000000-0000-4000-8000-000000000001")
    tenant_b = UUID("00000000-0000-4000-8000-000000000002")

    incident = _create(service, tenant_a)

    assert incident.status.value == "OPEN"
    assert service.list_incidents(tenant_a) == [incident]
    assert service.list_incidents(tenant_b) == []
    assert service.get_incident(tenant_a, incident.id) == incident
    assert service.get_incident(tenant_b, incident.id) is None

    timeline = service.list_timeline(tenant_a, incident.id)
    assert [event.event_type.value for event in timeline] == ["INCIDENT_CREATED"]
    with pytest.raises(IncidentNotFoundError):
        service.list_timeline(tenant_b, incident.id)


def test_update_then_normalize_appends_timeline_events() -> None:
    repository = InMemoryIncidentRepository()
    service = IncidentService(repository)
    tenant_id = UUID("00000000-0000-4000-8000-000000000001")
    incident = _create(service, tenant_id)

    updated = service.add_update(
        tenant_id=tenant_id,
        incident_id=incident.id,
        actor_subject="demo-operator",
        message="Operadora acionada; protocolo DEMO-123.",
    )
    normalized = service.normalize_incident(
        tenant_id=tenant_id,
        incident_id=incident.id,
        actor_subject="demo-operator",
        note="Conectividade restabelecida.",
    )

    assert updated.version == 2
    assert normalized.version == 3
    assert normalized.status.value == "RESOLVED"

    timeline = service.list_timeline(tenant_id, incident.id)
    assert [event.event_type.value for event in timeline] == [
        "INCIDENT_CREATED",
        "INCIDENT_UPDATED",
        "INCIDENT_NORMALIZED",
    ]
    assert timeline[1].message == "Operadora acionada; protocolo DEMO-123."
    assert timeline[2].message == "Conectividade restabelecida."


def test_resolved_incident_rejects_update_and_second_normalization() -> None:
    repository = InMemoryIncidentRepository()
    service = IncidentService(repository)
    tenant_id = UUID("00000000-0000-4000-8000-000000000001")
    incident = _create(service, tenant_id)

    service.normalize_incident(
        tenant_id=tenant_id,
        incident_id=incident.id,
        actor_subject="demo-operator",
    )

    with pytest.raises(IncidentCannotBeUpdatedError):
        service.add_update(
            tenant_id=tenant_id,
            incident_id=incident.id,
            actor_subject="demo-operator",
            message="Tentativa inválida de atualização.",
        )

    with pytest.raises(IncidentAlreadyNormalizedError):
        service.normalize_incident(
            tenant_id=tenant_id,
            incident_id=incident.id,
            actor_subject="demo-operator",
        )


def test_create_rejects_future_started_at() -> None:
    service = IncidentService(InMemoryIncidentRepository())

    with pytest.raises(IncidentStartedAtInFutureError):
        service.create_incident(
            tenant_id=UUID("00000000-0000-4000-8000-000000000001"),
            actor_subject="demo-operator",
            title="WAN outage",
            affected_resource="WAN",
            severity=IncidentSeverity.HIGH,
            impact_type=IncidentImpactType.OUTAGE,
            symptoms="Connectivity is unavailable",
            started_at=datetime.now(UTC) + timedelta(minutes=1),
        )
