ROLE_PERMISSIONS = {
    "super_admin": {
        "overview:read", "accounts:read", "accounts:status_write",
        "recruiters:read", "jobs:read", "jobs:moderate",
        "applications:read", "commands:read", "commands:retry",
        "audit:read", "administrators:manage",
    },
    "operator": {
        "overview:read", "accounts:read", "accounts:status_write", "recruiters:read",
        "jobs:read", "jobs:moderate", "applications:read", "commands:read", "audit:read",
    },
    "auditor": {
        "overview:read", "accounts:read", "recruiters:read", "jobs:read",
        "applications:read", "commands:read", "audit:read",
    },
}


def can(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
