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


_ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.ADMIN: frozenset(Permission),
    Role.SUPERVISOR: frozenset(
        {
            Permission.INCIDENT_READ,
            Permission.INCIDENT_CREATE,
            Permission.INCIDENT_UPDATE,
            Permission.INCIDENT_NORMALIZE,
        }
    ),
    Role.OPERATOR: frozenset(
        {
            Permission.INCIDENT_READ,
            Permission.INCIDENT_CREATE,
            Permission.INCIDENT_UPDATE,
            Permission.INCIDENT_NORMALIZE,
        }
    ),
    Role.VIEWER: frozenset({Permission.INCIDENT_READ}),
}


def permissions_for_roles(roles: frozenset[Role]) -> frozenset[Permission]:
    permissions: set[Permission] = set()
    for role in roles:
        permissions.update(_ROLE_PERMISSIONS[role])
    return frozenset(permissions)
