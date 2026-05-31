"""report space template bindings

Revision ID: 20260530_0008
Revises: 20260530_0007
Create Date: 2026-05-31
"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260530_0008"
down_revision: str | None = "20260530_0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "report_spaces",
        sa.Column(
            "template_bindings",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )


def downgrade() -> None:
    op.drop_column("report_spaces", "template_bindings")
