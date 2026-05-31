"""report instances drafts submissions

Revision ID: 20260530_0006
Revises: 20260530_0005
Create Date: 2026-05-30
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260530_0006"
down_revision: str | None = "20260530_0005"
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
        "report_instances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("report_space_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("report_type", sa.String(length=40), nullable=False),
        sa.Column("assignee_member_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="pending"),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("template_version_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("latest_draft_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("latest_submission_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("submitted_late", sa.Boolean(), nullable=False, server_default=sa.false()),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["report_space_id"], ["report_spaces.id"]),
        sa.ForeignKeyConstraint(["assignee_member_id"], ["members.id"]),
        sa.UniqueConstraint(
            "workspace_id",
            "report_space_id",
            "report_type",
            "assignee_member_id",
            "period_start",
            "period_end",
            name="uq_report_instances_period_assignee",
        ),
    )
    op.create_index("ix_report_instances_workspace_id", "report_instances", ["workspace_id"])
    op.create_index("ix_report_instances_report_space_id", "report_instances", ["report_space_id"])
    op.create_index(
        "ix_report_instances_assignee_member_id",
        "report_instances",
        ["assignee_member_id"],
    )

    op.create_table(
        "report_drafts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("report_instance_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "content_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("ai_generated", sa.Boolean(), nullable=False, server_default=sa.false()),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["report_instance_id"], ["report_instances.id"]),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"]),
    )
    op.create_index("ix_report_drafts_workspace_id", "report_drafts", ["workspace_id"])
    op.create_index("ix_report_drafts_report_instance_id", "report_drafts", ["report_instance_id"])
    op.create_index("ix_report_drafts_member_id", "report_drafts", ["member_id"])

    op.create_table(
        "report_submissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("report_instance_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column(
            "content_snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("change_reason", sa.String(length=500), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["report_instance_id"], ["report_instances.id"]),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"]),
        sa.UniqueConstraint(
            "report_instance_id",
            "version_no",
            name="uq_report_submissions_instance_version",
        ),
    )
    op.create_index("ix_report_submissions_workspace_id", "report_submissions", ["workspace_id"])
    op.create_index(
        "ix_report_submissions_report_instance_id",
        "report_submissions",
        ["report_instance_id"],
    )
    op.create_index("ix_report_submissions_member_id", "report_submissions", ["member_id"])


def downgrade() -> None:
    op.drop_index("ix_report_submissions_member_id", table_name="report_submissions")
    op.drop_index("ix_report_submissions_report_instance_id", table_name="report_submissions")
    op.drop_index("ix_report_submissions_workspace_id", table_name="report_submissions")
    op.drop_table("report_submissions")
    op.drop_index("ix_report_drafts_member_id", table_name="report_drafts")
    op.drop_index("ix_report_drafts_report_instance_id", table_name="report_drafts")
    op.drop_index("ix_report_drafts_workspace_id", table_name="report_drafts")
    op.drop_table("report_drafts")
    op.drop_index("ix_report_instances_assignee_member_id", table_name="report_instances")
    op.drop_index("ix_report_instances_report_space_id", table_name="report_instances")
    op.drop_index("ix_report_instances_workspace_id", table_name="report_instances")
    op.drop_table("report_instances")

