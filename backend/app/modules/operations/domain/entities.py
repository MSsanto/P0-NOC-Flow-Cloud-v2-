from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.modules.incidents.domain.entities import IncidentSeverity, IncidentStatus


@dataclass(frozen=True, slots=True)
class ShiftWindow:
    window_start: datetime
    window_end: datetime


@dataclass(frozen=True, slots=True)
class DashboardItem:
    id: UUID
    title: str
    affected_resource: str
    severity: IncidentSeverity
    status: IncidentStatus
    started_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class DashboardSummary:
    active_count: int
    critical_active_count: int
    resolved_in_shift_count: int
    shift: ShiftWindow
    items: list[DashboardItem]


@dataclass(frozen=True, slots=True)
class HandoverItem:
    incident_id: UUID
    title: str
    affected_resource: str
    severity: IncidentSeverity
    status: IncidentStatus
    started_at: datetime
    last_event_message: str | None
    last_event_at: datetime | None


@dataclass(frozen=True, slots=True)
class HandoverPreview:
    window_start: datetime
    window_end: datetime
    generated_at: datetime
    items: list[HandoverItem]


@dataclass(frozen=True, slots=True)
class Handover:
    id: UUID
    version: int
    window_start: datetime
    window_end: datetime
    observations: str | None
    finalized_by_subject: str
    finalized_at: datetime
    items: list[HandoverItem]


@dataclass(frozen=True, slots=True)
class HandoverListItem:
    id: UUID
    version: int
    window_start: datetime
    window_end: datetime
    finalized_by_subject: str
    finalized_at: datetime


@dataclass(frozen=True, slots=True)
class HandoverPage:
    items: list[HandoverListItem]
    page: int
    page_size: int
    total: int
