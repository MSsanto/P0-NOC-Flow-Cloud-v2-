from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.modules.incidents.application.services import (
    IncidentService,
    IncidentStartedAtInFutureError,
)
from app.modules.incidents.domain.entities import IncidentImpactType, IncidentSeverity


class InMemoryIncidentRepository:
    def __init__(self) -> None:
        self.items = []

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

    def create(self, incident):
        self.items.append(incident)
        return incident


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


def test_create_list_and_get_are_tenant_scoped() -> None:
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
