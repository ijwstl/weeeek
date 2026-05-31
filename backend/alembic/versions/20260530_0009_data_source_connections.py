"""data source connections

Revision ID: 20260530_0009
Revises: 20260530_0008
Create Date: 2026-05-31
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260530_0009"
down_revision: str | None = "20260530_0008"
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
        "data_source_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("member_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("account_name", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="connected"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "scope_config",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "auth_config_encrypted",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"]),
        sa.ForeignKeyConstraint(["member_id"], ["members.id"]),
        sa.UniqueConstraint(
            "workspace_id",
            "member_id",
            "source_type",
            "name",
            name="uq_data_source_connections_member_source_name",
        ),
    )
    op.create_index(
        "ix_data_source_connections_workspace_id",
        "data_source_connections",
        ["workspace_id"],
    )
    op.create_index(
        "ix_data_source_connections_member_id",
        "data_source_connections",
        ["member_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_data_source_connections_member_id", table_name="data_source_connections")
    op.drop_index("ix_data_source_connections_workspace_id", table_name="data_source_connections")
    op.drop_table("data_source_connections")
