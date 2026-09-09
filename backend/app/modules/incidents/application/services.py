from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.modules.incidents.application.ports import IncidentRepository
from app.modules.incidents.domain.entities import (
    Incident,
    IncidentImpactType,
    IncidentSeverity,
    IncidentStatus,
)


class IncidentStartedAtInFutureError(ValueError):
    pass


class IncidentService:
    def __init__(self, repository: IncidentRepository) -> None:
        self.repository = repository

    def list_incidents(self, tenant_id: UUID) -> list[Incident]:
        return self.repository.list_for_tenant(tenant_id)

    def get_incident(self, tenant_id: UUID, incident_id: UUID) -> Incident | None:
        return self.repository.get_for_tenant(tenant_id, incident_id)

    def create_incident(
        self,
        *,
        tenant_id: UUID,
        actor_subject: str,
        title: str,
        affected_resource: str,
        severity: IncidentSeverity,
        impact_type: IncidentImpactType,
        symptoms: str,
        started_at: datetime,
    ) -> Incident:
        now = datetime.now(UTC)
        normalized_started_at = (
            started_at.replace(tzinfo=UTC)
            if started_at.tzinfo is None
            else started_at.astimezone(UTC)
        )
        if normalized_started_at > now:
            raise IncidentStartedAtInFutureError("Incident start time cannot be in the future.")

        incident = Incident(
            id=uuid4(),
            tenant_id=tenant_id,
            title=title,
            affected_resource=affected_resource,
            severity=severity,
            impact_type=impact_type,
            symptoms=symptoms,
            status=IncidentStatus.OPEN,
            started_at=normalized_started_at,
            created_by_subject=actor_subject,
            created_at=now,
            updated_at=now,
            version=1,
        )
        return self.repository.create(incident)
