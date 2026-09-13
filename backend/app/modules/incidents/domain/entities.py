from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class IncidentSeverity(StrEnum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class IncidentImpactType(StrEnum):
    OUTAGE = "OUTAGE"
    DEGRADATION = "DEGRADATION"


class IncidentStatus(StrEnum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    MONITORING = "MONITORING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class IncidentEventType(StrEnum):
    CREATED = "INCIDENT_CREATED"
    UPDATED = "INCIDENT_UPDATED"
    NORMALIZED = "INCIDENT_NORMALIZED"


@dataclass(frozen=True, slots=True)
class Incident:
    id: UUID
    tenant_id: UUID
    title: str
    affected_resource: str
    severity: IncidentSeverity
    impact_type: IncidentImpactType
    symptoms: str
    status: IncidentStatus
    started_at: datetime
    created_by_subject: str
    created_at: datetime
    updated_at: datetime
    version: int


@dataclass(frozen=True, slots=True)
class IncidentEvent:
    id: UUID
    tenant_id: UUID
    incident_id: UUID
    event_type: IncidentEventType
    message: str | None
    actor_subject: str
    occurred_at: datetime
