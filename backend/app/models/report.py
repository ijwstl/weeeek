from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ReportInstance(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "report_instances"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "report_space_id",
            "report_type",
            "assignee_member_id",
            "period_start",
            "period_end",
            name="uq_report_instances_period_assignee",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    report_space_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("report_spaces.id"), nullable=False, index=True
    )
    report_type: Mapped[str] = mapped_column(String(40), nullable=False)
    assignee_member_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="pending")
    template_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    template_version_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    latest_draft_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    latest_submission_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_late: Mapped[bool] = mapped_column(default=False, nullable=False)


class ReportDraft(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "report_drafts"

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    report_instance_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("report_instances.id"), nullable=False, index=True
    )
    member_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    content_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    ai_generated: Mapped[bool] = mapped_column(default=False, nullable=False)


class ReportSubmission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "report_submissions"
    __table_args__ = (
        UniqueConstraint(
            "report_instance_id",
            "version_no",
            name="uq_report_submissions_instance_version",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    report_instance_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("report_instances.id"), nullable=False, index=True
    )
    member_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    content_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    change_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

