from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    actor_subject: str
    action: str
    resource_type: str
    resource_id: UUID | None
    request_id: str
    occurred_at: datetime


class AuditEventPage(BaseModel):
    items: list[AuditEventResponse]
    page: int
    page_size: int
    total: int
