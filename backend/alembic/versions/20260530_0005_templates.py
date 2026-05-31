"""report templates

Revision ID: 20260530_0005
Revises: 20260530_0004
Create Date: 2026-05-30
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260530_0005"
down_revision: str | None = "20260530_0004"
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
        "report_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("template_scope", sa.String(length=40), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_by_member_id", postgresql.UUID(as_uuid=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
    )
    op.create_index("ix_report_templates_workspace_id", "report_templates", ["workspace_id"])

    op.create_table(
        "report_template_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="draft"),
        sa.Column(
            "schema_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("published_by_member_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["template_id"], ["report_templates.id"]),
        sa.UniqueConstraint("template_id", "version_no", name="uq_template_versions_no"),
    )
    op.create_index(
        "ix_report_template_versions_workspace_id",
        "report_template_versions",
        ["workspace_id"],
    )
    op.create_index(
        "ix_report_template_versions_template_id",
        "report_template_versions",
        ["template_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_report_template_versions_template_id", table_name="report_template_versions")
    op.drop_index("ix_report_template_versions_workspace_id", table_name="report_template_versions")
    op.drop_table("report_template_versions")
    op.drop_index("ix_report_templates_workspace_id", table_name="report_templates")
    op.drop_table("report_templates")

