from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.incidents.domain.entities import IncidentSeverity, IncidentStatus


class ShiftResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    window_start: datetime
    window_end: datetime


class DashboardItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    title: str
    affected_resource: str
    severity: IncidentSeverity
    status: IncidentStatus
    started_at: datetime
    updated_at: datetime


class DashboardResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    active_count: int
    critical_active_count: int
    resolved_in_shift_count: int
    shift: ShiftResponse
    items: list[DashboardItemResponse]


class HandoverItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    incident_id: UUID
    title: str
    affected_resource: str
    severity: IncidentSeverity
    status: IncidentStatus
    started_at: datetime
    last_event_message: str | None
    last_event_at: datetime | None


class HandoverPreviewResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    window_start: datetime
    window_end: datetime
    generated_at: datetime
    items: list[HandoverItemResponse]


class HandoverFinalizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    observations: str | None = Field(default=None, max_length=4000)

    @field_validator("observations")
    @classmethod
    def validate_observations(cls, value: str | None) -> str | None:
        if value == "":
            return None
        if value is not None and len(value) < 3:
            raise ValueError("observations must contain at least 3 characters")
        return value


class HandoverResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    version: int
    window_start: datetime
    window_end: datetime
    observations: str | None
    finalized_by_subject: str
    finalized_at: datetime
    items: list[HandoverItemResponse]


class HandoverListItemResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    version: int
    window_start: datetime
    window_end: datetime
    finalized_by_subject: str
    finalized_at: datetime


class HandoverListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    items: list[HandoverListItemResponse]
    page: int
    page_size: int
    total: int
