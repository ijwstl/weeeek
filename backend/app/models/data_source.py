from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class DataSourceConnection(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "data_source_connections"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "member_id",
            "source_type",
            "name",
            name="uq_data_source_connections_member_source_name",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    member_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    source_type: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    account_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="connected")
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    scope_config: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    auth_config_encrypted: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
