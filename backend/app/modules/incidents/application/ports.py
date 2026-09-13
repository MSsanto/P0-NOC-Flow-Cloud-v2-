from typing import Protocol
from uuid import UUID

from app.modules.incidents.domain.entities import Incident, IncidentEvent


class IncidentRepository(Protocol):
    def list_for_tenant(self, tenant_id: UUID) -> list[Incident]: ...

    def get_for_tenant(self, tenant_id: UUID, incident_id: UUID) -> Incident | None: ...

    def create(self, incident: Incident, event: IncidentEvent) -> Incident: ...

    def save_with_event(self, incident: Incident, event: IncidentEvent) -> Incident: ...

    def list_events_for_incident(
        self,
        tenant_id: UUID,
        incident_id: UUID,
    ) -> list[IncidentEvent]: ...
