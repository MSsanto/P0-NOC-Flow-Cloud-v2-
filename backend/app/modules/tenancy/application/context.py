from dataclasses import dataclass
from uuid import UUID

from app.modules.tenancy.application.security import Permission, Role, permissions_for_roles


@dataclass(frozen=True, slots=True)
class RequestContext:
    tenant_id: UUID
    actor_subject: str
    roles: frozenset[Role]

    def has_permission(self, permission: Permission) -> bool:
        return permission in permissions_for_roles(self.roles)
