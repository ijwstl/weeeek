"""organization and report spaces

Revision ID: 20260530_0003
Revises: 20260530_0002
Create Date: 2026-05-30
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260530_0003"
down_revision: str | None = "20260530_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


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
        "departments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("path", sa.String(length=1000), nullable=False),
        sa.Column("depth", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
    )
    op.create_index("ix_departments_workspace_id", "departments", ["workspace_id"])
    op.create_index("ix_departments_parent_id", "departments", ["parent_id"])

    op.create_table(
        "project_teams",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("goal", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="not_started"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("expected_end_date", sa.Date(), nullable=True),
        sa.Column("actual_end_date", sa.Date(), nullable=True),
        sa.Column("created_by_member_id", postgresql.UUID(as_uuid=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
    )
    op.create_index("ix_project_teams_workspace_id", "project_teams", ["workspace_id"])

    op.create_table(
        "project_team_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_team_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", sa.String(length=40), nullable=False, server_default="project_member"),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["project_team_id"], ["project_teams.id"]),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"]),
        sa.UniqueConstraint(
            "workspace_id",
            "project_team_id",
            "member_id",
            name="uq_project_team_members_member",
        ),
    )
    op.create_index(
        "ix_project_team_members_workspace_id",
        "project_team_members",
        ["workspace_id"],
    )
    op.create_index(
        "ix_project_team_members_project_team_id",
        "project_team_members",
        ["project_team_id"],
    )
    op.create_index(
        "ix_project_team_members_member_id",
        "project_team_members",
        ["member_id"],
    )

    op.create_table(
        "report_spaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("space_type", sa.String(length=40), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("project_team_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("report_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ai_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "allowed_data_source_types",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default='["git", "jira", "project_progress", "history"]',
        ),
        sa.Column(
            "member_visibility",
            sa.String(length=40),
            nullable=False,
            server_default="private",
        ),
        *timestamps(),
        sa.CheckConstraint(
            "(department_id IS NOT NULL AND project_team_id IS NULL) OR "
            "(department_id IS NULL AND project_team_id IS NOT NULL)",
            name="ck_report_spaces_report_space_exactly_one_owner",
        ),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"]),
        sa.ForeignKeyConstraint(["project_team_id"], ["project_teams.id"]),
        sa.UniqueConstraint("workspace_id", "department_id", name="uq_report_spaces_department"),
        sa.UniqueConstraint(
            "workspace_id",
            "project_team_id",
            name="uq_report_spaces_project_team",
        ),
    )
    op.create_index("ix_report_spaces_workspace_id", "report_spaces", ["workspace_id"])


def downgrade() -> None:
    op.drop_index("ix_report_spaces_workspace_id", table_name="report_spaces")
    op.drop_table("report_spaces")
    op.drop_index("ix_project_team_members_member_id", table_name="project_team_members")
    op.drop_index("ix_project_team_members_project_team_id", table_name="project_team_members")
    op.drop_index("ix_project_team_members_workspace_id", table_name="project_team_members")
    op.drop_table("project_team_members")
    op.drop_index("ix_project_teams_workspace_id", table_name="project_teams")
    op.drop_table("project_teams")
    op.drop_index("ix_departments_parent_id", table_name="departments")
    op.drop_index("ix_departments_workspace_id", table_name="departments")
    op.drop_table("departments")
