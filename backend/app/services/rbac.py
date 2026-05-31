from app.permissions.catalog import PERMISSION_CATALOG, PermissionDefinition

BUILTIN_ROLE_DEFINITIONS: tuple[dict[str, object], ...] = (
    {
        "id": "builtin-workspace-owner",
        "code": "workspace_owner",
        "name": "工作区拥有者",
        "description": "拥有工作区内全部权限",
        "is_builtin": True,
        "is_editable": False,
        "permissions": [definition.code for definition in PERMISSION_CATALOG],
    },
    {
        "id": "builtin-workspace-admin",
        "code": "workspace_admin",
        "name": "工作区管理员",
        "description": "管理工作区、成员、部门、项目、模板、集成和审计",
        "is_builtin": True,
        "is_editable": False,
        "permissions": [
            "department.read",
            "department.create",
            "department.update",
            "department.delete",
            "department.member.manage",
            "department.rule.manage",
            "department.template.manage",
            "department.report.summary",
            "project.read",
            "project.create",
            "project.update",
            "project.archive",
            "project.member.manage",
            "project.rule.manage",
            "project.template.manage",
            "project.summary.view",
            "template.create",
            "template.update",
            "template.publish",
            "datasource.provider.manage",
            "workspace.member.manage",
            "workspace.role.manage",
            "workspace.setting.manage",
            "workspace.audit.view",
            "notification.channel.manage",
            "notification.rule.manage",
        ],
    },
    {
        "id": "builtin-integration-admin",
        "code": "integration_admin",
        "name": "集成管理员",
        "description": "管理工作区级数据源、认证和通知集成",
        "is_builtin": True,
        "is_editable": True,
        "permissions": [
            "datasource.provider.manage",
            "notification.channel.manage",
            "workspace.setting.manage",
        ],
    },
    {
        "id": "builtin-department-admin",
        "code": "department_admin",
        "name": "部门管理员",
        "description": "管理作用域内部门配置、成员、填报规则和模板",
        "is_builtin": True,
        "is_editable": True,
        "permissions": [
            "department.read",
            "department.update",
            "department.member.manage",
            "department.rule.manage",
            "department.template.manage",
        ],
    },
    {
        "id": "builtin-department-lead",
        "code": "department_lead",
        "name": "部门负责人",
        "description": "查看作用域内部门报告、提交状态和汇总",
        "is_builtin": True,
        "is_editable": True,
        "permissions": [
            "department.read",
            "department.report.view",
            "department.report.summary",
            "ai.summary.space",
        ],
    },
    {
        "id": "builtin-project-admin",
        "code": "project_admin",
        "name": "项目管理员",
        "description": "管理项目团队、成员、规则、模板、进度和汇总",
        "is_builtin": True,
        "is_editable": True,
        "permissions": [
            "project.read",
            "project.update",
            "project.archive",
            "project.member.manage",
            "project.rule.manage",
            "project.template.manage",
            "project.progress.view",
            "project.summary.view",
            "ai.summary.space",
        ],
    },
    {
        "id": "builtin-project-member",
        "code": "project_member",
        "name": "项目成员",
        "description": "填写自己的项目进度并查看项目汇总",
        "is_builtin": True,
        "is_editable": True,
        "permissions": [
            "project.read",
            "report.read.own",
            "report.submit.own",
            "report.update.own",
        ],
    },
    {
        "id": "builtin-member",
        "code": "member",
        "name": "普通成员",
        "description": "填写自己的报告并管理个人数据源和 AI 草稿",
        "is_builtin": True,
        "is_editable": True,
        "permissions": [
            "report.read.own",
            "report.submit.own",
            "report.update.own",
            "datasource.manage.own",
            "ai.generate.own",
        ],
    },
)


def list_permission_definitions() -> list[PermissionDefinition]:
    return list(PERMISSION_CATALOG)


def list_builtin_roles() -> list[dict[str, object]]:
    return [dict(role) for role in BUILTIN_ROLE_DEFINITIONS]


def get_builtin_role(role_id: str) -> dict[str, object] | None:
    return next((role for role in list_builtin_roles() if role["id"] == role_id), None)

