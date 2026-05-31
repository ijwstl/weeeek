from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ReportTemplate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "report_templates"

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    template_scope: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    created_by_member_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)


class ReportTemplateVersion(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "report_template_versions"
    __table_args__ = (
        UniqueConstraint("template_id", "version_no", name="uq_template_versions_no"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    template_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("report_templates.id"), nullable=False, index=True
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    schema_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    published_by_member_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

