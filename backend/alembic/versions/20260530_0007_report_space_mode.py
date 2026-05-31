"""report space mode

Revision ID: 20260530_0007
Revises: 20260530_0006
Create Date: 2026-05-31
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260530_0007"
down_revision: str | None = "20260530_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "report_spaces",
        sa.Column(
            "report_mode",
            sa.String(length=40),
            nullable=False,
            server_default="weekly",
        ),
    )


def downgrade() -> None:
    op.drop_column("report_spaces", "report_mode")
