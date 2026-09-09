from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.incidents.domain.entities import (
    IncidentImpactType,
    IncidentSeverity,
    IncidentStatus,
)


class IncidentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=120)
    affected_resource: str = Field(min_length=2, max_length=120)
    severity: IncidentSeverity
    impact_type: IncidentImpactType
    symptoms: str = Field(min_length=10, max_length=2000)
    started_at: datetime


class IncidentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    title: str
    affected_resource: str
    severity: IncidentSeverity
    impact_type: IncidentImpactType
    symptoms: str
    status: IncidentStatus
    started_at: datetime
    created_at: datetime
    updated_at: datetime
    version: int
