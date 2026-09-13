from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.modules.incidents.application.ports import IncidentRepository
from app.modules.incidents.domain.entities import (
    Incident,
    IncidentEvent,
    IncidentEventType,
    IncidentImpactType,
    IncidentSeverity,
    IncidentStatus,
)


class IncidentStartedAtInFutureError(ValueError):
    pass


class IncidentNotFoundError(LookupError):
    pass


class IncidentCannotBeUpdatedError(ValueError):
    pass


class IncidentAlreadyNormalizedError(ValueError):
    pass


class IncidentService:
    def __init__(self, repository: IncidentRepository) -> None:
        self.repository = repository

    def list_incidents(self, tenant_id: UUID) -> list[Incident]:
        return self.repository.list_for_tenant(tenant_id)

    def get_incident(self, tenant_id: UUID, incident_id: UUID) -> Incident | None:
        return self.repository.get_for_tenant(tenant_id, incident_id)

    def _get_required_incident(self, tenant_id: UUID, incident_id: UUID) -> Incident:
        incident = self.repository.get_for_tenant(tenant_id, incident_id)
        if incident is None:
            raise IncidentNotFoundError(
                "The requested incident was not found in the active tenant."
            )
        return incident

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
            raise IncidentStartedAtInFutureError(
                "Incident start time cannot be in the future."
            )

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
        event = IncidentEvent(
            id=uuid4(),
            tenant_id=tenant_id,
            incident_id=incident.id,
            event_type=IncidentEventType.CREATED,
            message=None,
            actor_subject=actor_subject,
            occurred_at=now,
        )
        return self.repository.create(incident, event)

    def add_update(
        self,
        *,
        tenant_id: UUID,
        incident_id: UUID,
        actor_subject: str,
        message: str,
    ) -> Incident:
        incident = self._get_required_incident(tenant_id, incident_id)
        if incident.status in {IncidentStatus.RESOLVED, IncidentStatus.CLOSED}:
            raise IncidentCannotBeUpdatedError(
                "Resolved or closed incidents cannot receive operational updates."
            )

        now = datetime.now(UTC)
        updated_incident = replace(
            incident,
            updated_at=now,
            version=incident.version + 1,
        )
        event = IncidentEvent(
            id=uuid4(),
            tenant_id=tenant_id,
            incident_id=incident.id,
            event_type=IncidentEventType.UPDATED,
            message=message,
            actor_subject=actor_subject,
            occurred_at=now,
        )
        return self.repository.save_with_event(updated_incident, event)

    def normalize_incident(
        self,
        *,
        tenant_id: UUID,
        incident_id: UUID,
        actor_subject: str,
        note: str | None = None,
    ) -> Incident:
        incident = self._get_required_incident(tenant_id, incident_id)
        if incident.status in {IncidentStatus.RESOLVED, IncidentStatus.CLOSED}:
            raise IncidentAlreadyNormalizedError(
                "The incident is already normalized or closed."
            )

        now = datetime.now(UTC)
        normalized_incident = replace(
            incident,
            status=IncidentStatus.RESOLVED,
            updated_at=now,
            version=incident.version + 1,
        )
        event = IncidentEvent(
            id=uuid4(),
            tenant_id=tenant_id,
            incident_id=incident.id,
            event_type=IncidentEventType.NORMALIZED,
            message=note,
            actor_subject=actor_subject,
            occurred_at=now,
        )
        return self.repository.save_with_event(normalized_incident, event)

    def list_timeline(self, tenant_id: UUID, incident_id: UUID) -> list[IncidentEvent]:
        self._get_required_incident(tenant_id, incident_id)
        return self.repository.list_events_for_incident(tenant_id, incident_id)
