from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.modules.tenancy.application.security import Permission, Role


class AuthContextResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str
    tenant_id: UUID
    roles: list[Role]
    permissions: list[Permission]
