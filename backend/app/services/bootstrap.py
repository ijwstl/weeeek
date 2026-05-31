from app.permissions.constants import Permission

DEMO_WORKSPACE = {
    "id": "00000000-0000-0000-0000-000000000001",
    "name": "研发协作空间",
    "slug": "engineering",
    "deployment_mode": "private",
    "default_locale": "zh-CN",
    "timezone": "Asia/Shanghai",
    "department_max_depth": 5,
    "status": "active",
}

DEMO_USER = {
    "id": "00000000-0000-0000-0000-000000000101",
    "display_name": "王启",
    "email": "wangqi@example.com",
    "avatar_url": None,
    "status": "active",
}

DEMO_MEMBER = {
    "id": "00000000-0000-0000-0000-000000000201",
    "workspace_id": DEMO_WORKSPACE["id"],
    "user_id": DEMO_USER["id"],
    "department_id": None,
    "display_name": "王启",
    "email": "wangqi@example.com",
    "employee_no": "E0001",
    "avatar_url": None,
    "status": "active",
}

DEMO_ROLES = ["workspace_owner", "member"]
DEMO_PERMISSIONS = [permission.value for permission in Permission]


def get_demo_principal() -> dict[str, object]:
    return {
        "user": DEMO_USER,
        "member": DEMO_MEMBER,
        "workspace": DEMO_WORKSPACE,
        "permissions": DEMO_PERMISSIONS,
        "roles": DEMO_ROLES,
    }

