from enum import StrEnum


class Role(StrEnum):
    ADMIN = "Admin"
    SUPERVISOR = "Supervisor"
    OPERATOR = "Operator"
    VIEWER = "Viewer"


class Permission(StrEnum):
    INCIDENT_READ = "incident:read"
    INCIDENT_CREATE = "incident:create"
    INCIDENT_UPDATE = "incident:update"
    INCIDENT_NORMALIZE = "incident:normalize"
    HANDOVER_READ = "handover:read"
    HANDOVER_FINALIZE = "handover:finalize"
    AUDIT_READ = "audit:read"


_ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),
    Role.SUPERVISOR: frozenset(
        {
            Permission.AUDIT_READ,
            Permission.INCIDENT_READ,
            Permission.INCIDENT_CREATE,
            Permission.INCIDENT_UPDATE,
            Permission.INCIDENT_NORMALIZE,
            Permission.HANDOVER_READ,
            Permission.HANDOVER_FINALIZE,
        }
    ),
    Role.OPERATOR: frozenset(
        {
            Permission.INCIDENT_READ,
            Permission.INCIDENT_CREATE,
            Permission.INCIDENT_UPDATE,
            Permission.INCIDENT_NORMALIZE,
            Permission.HANDOVER_READ,
            Permission.HANDOVER_FINALIZE,
        }
    ),
    Role.VIEWER: frozenset({Permission.INCIDENT_READ, Permission.HANDOVER_READ}),
}


def permissions_for_roles(roles: frozenset[Role]) -> frozenset[Permission]:
    permissions: set[Permission] = set()
    for role in roles:
        permissions.update(_ROLE_PERMISSIONS[role])
    return frozenset(permissions)
