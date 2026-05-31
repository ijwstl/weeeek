"""rbac foundation

Revision ID: 20260530_0002
Revises: 20260530_0001
Create Date: 2026-05-30
"""
from collections.abc import Sequence
from uuid import NAMESPACE_URL, uuid5

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from app.permissions.catalog import PERMISSION_CATALOG

revision: str = "20260530_0002"
down_revision: str | None = "20260530_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ROLE_DEFINITIONS = (
    (
        "workspace_owner",
        "工作区拥有者",
        "拥有工作区内全部权限",
        False,
        [definition.code for definition in PERMISSION_CATALOG],
    ),
    (
        "workspace_admin",
        "工作区管理员",
        "管理工作区、成员、部门、项目、模板、集成和审计",
        False,
        [
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
    ),
    (
        "integration_admin",
        "集成管理员",
        "管理工作区级数据源、认证和通知集成",
        True,
        ["datasource.provider.manage", "notification.channel.manage", "workspace.setting.manage"],
    ),
    (
        "department_admin",
        "部门管理员",
        "管理作用域内部门配置、成员、填报规则和模板",
        True,
        [
            "department.read",
            "department.update",
            "department.member.manage",
            "department.rule.manage",
            "department.template.manage",
        ],
    ),
    (
        "department_lead",
        "部门负责人",
        "查看作用域内部门报告、提交状态和汇总",
        True,
        [
            "department.read",
            "department.report.view",
            "department.report.summary",
            "ai.summary.space",
        ],
    ),
    (
        "project_admin",
        "项目管理员",
        "管理项目团队、成员、规则、模板、进度和汇总",
        True,
        [
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
    ),
    (
        "project_member",
        "项目成员",
        "填写自己的项目进度并查看项目汇总",
        True,
        ["project.read", "report.read.own", "report.submit.own", "report.update.own"],
    ),
    (
        "member",
        "普通成员",
        "填写自己的报告并管理个人数据源和 AI 草稿",
        True,
        [
            "report.read.own",
            "report.submit.own",
            "report.update.own",
            "datasource.manage.own",
            "ai.generate.own",
        ],
    ),
)


def uuid_for(value: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"weeeek:{value}"))


def timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("resource_type", sa.String(length=64), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("code", name="uq_permissions_code"),
    )

    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=False, server_default=""),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_editable", sa.Boolean(), nullable=False, server_default=sa.true()),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.UniqueConstraint("workspace_id", "code", name="uq_roles_workspace_code"),
    )
    op.create_index("ix_roles_workspace_id", "roles", ["workspace_id"])

    op.create_table(
        "role_permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"]),
        sa.UniqueConstraint(
            "workspace_id",
            "role_id",
            "permission_id",
            name="uq_role_permissions_workspace_role_permission",
        ),
    )
    op.create_index("ix_role_permissions_workspace_id", "role_permissions", ["workspace_id"])

    op.create_table(
        "member_role_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("scope_type", sa.String(length=40), nullable=False),
        sa.Column("scope_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_by_member_id", postgresql.UUID(as_uuid=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.UniqueConstraint(
            "workspace_id",
            "member_id",
            "role_id",
            "scope_type",
            "scope_id",
            name="uq_member_role_assignments_scope",
        ),
    )
    op.create_index(
        "ix_member_role_assignments_workspace_id",
        "member_role_assignments",
        ["workspace_id"],
    )
    op.create_index(
        "ix_member_role_assignments_member_id",
        "member_role_assignments",
        ["member_id"],
    )

    permissions_table = sa.table(
        "permissions",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("category", sa.String),
        sa.column("resource_type", sa.String),
        sa.column("action", sa.String),
        sa.column("is_system", sa.Boolean),
    )
    roles_table = sa.table(
        "roles",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("workspace_id", postgresql.UUID(as_uuid=True)),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
        sa.column("is_builtin", sa.Boolean),
        sa.column("is_editable", sa.Boolean),
    )
    role_permissions_table = sa.table(
        "role_permissions",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("workspace_id", postgresql.UUID(as_uuid=True)),
        sa.column("role_id", postgresql.UUID(as_uuid=True)),
        sa.column("permission_id", postgresql.UUID(as_uuid=True)),
    )

    permission_rows = [
        {
            "id": uuid_for(f"permission:{definition.code}"),
            "code": definition.code,
            "name": definition.name,
            "description": definition.description,
            "category": definition.category,
            "resource_type": definition.resource_type,
            "action": definition.action,
            "is_system": True,
        }
        for definition in PERMISSION_CATALOG
    ]
    op.bulk_insert(permissions_table, permission_rows)

    role_rows = [
        {
            "id": uuid_for(f"role:{code}"),
            "workspace_id": None,
            "code": code,
            "name": name,
            "description": description,
            "is_builtin": True,
            "is_editable": is_editable,
        }
        for code, name, description, is_editable, _permissions in ROLE_DEFINITIONS
    ]
    op.bulk_insert(roles_table, role_rows)

    role_permission_rows = []
    for role_code, _name, _description, _is_editable, permission_codes in ROLE_DEFINITIONS:
        for permission_code in permission_codes:
            role_permission_rows.append(
                {
                    "id": uuid_for(f"role_permission:{role_code}:{permission_code}"),
                    "workspace_id": None,
                    "role_id": uuid_for(f"role:{role_code}"),
                    "permission_id": uuid_for(f"permission:{permission_code}"),
                }
            )
    op.bulk_insert(role_permissions_table, role_permission_rows)


def downgrade() -> None:
    op.drop_index("ix_member_role_assignments_member_id", table_name="member_role_assignments")
    op.drop_index("ix_member_role_assignments_workspace_id", table_name="member_role_assignments")
    op.drop_table("member_role_assignments")
    op.drop_index("ix_role_permissions_workspace_id", table_name="role_permissions")
    op.drop_table("role_permissions")
    op.drop_index("ix_roles_workspace_id", table_name="roles")
    op.drop_table("roles")
    op.drop_table("permissions")
