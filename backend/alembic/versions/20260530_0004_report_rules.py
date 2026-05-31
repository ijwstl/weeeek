"""report rules

Revision ID: 20260530_0004
Revises: 20260530_0003
Create Date: 2026-05-30
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260530_0004"
down_revision: str | None = "20260530_0003"
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
        "report_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("report_space_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("report_type", sa.String(length=40), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("frequency", sa.String(length=40), nullable=False),
        sa.Column("interval_value", sa.Integer(), nullable=True),
        sa.Column("week_start_day", sa.Integer(), nullable=True),
        sa.Column("reminder_day", sa.Integer(), nullable=True),
        sa.Column("reminder_time", sa.String(length=16), nullable=True),
        sa.Column("due_type", sa.String(length=40), nullable=False, server_default="same_day"),
        sa.Column("due_day", sa.Integer(), nullable=True),
        sa.Column("due_time", sa.String(length=16), nullable=True),
        sa.Column("skip_weekends", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "notification_channels",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default='["in_app", "feishu"]',
        ),
        sa.Column(
            "overdue_policy",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "extra_config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["report_space_id"], ["report_spaces.id"]),
        sa.UniqueConstraint(
            "workspace_id",
            "report_space_id",
            "report_type",
            name="uq_report_rules_space_type",
        ),
    )
    op.create_index("ix_report_rules_workspace_id", "report_rules", ["workspace_id"])
    op.create_index("ix_report_rules_report_space_id", "report_rules", ["report_space_id"])


def downgrade() -> None:
    op.drop_index("ix_report_rules_report_space_id", table_name="report_rules")
    op.drop_index("ix_report_rules_workspace_id", table_name="report_rules")
    op.drop_table("report_rules")

