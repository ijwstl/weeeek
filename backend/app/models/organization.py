from datetime import date
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Department(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "departments"

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    parent_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    path: Mapped[str] = mapped_column(String(1000), nullable=False)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")


class ProjectTeam(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_teams"

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    goal: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="not_started")
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expected_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_by_member_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)


class ProjectTeamMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "project_team_members"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "project_team_id",
            "member_id",
            name="uq_project_team_members_member",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    project_team_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("project_teams.id"), nullable=False, index=True
    )
    member_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(String(40), nullable=False, default="project_member")


class ReportSpace(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "report_spaces"
    __table_args__ = (
        CheckConstraint(
            "(department_id IS NOT NULL AND project_team_id IS NULL) OR "
            "(department_id IS NULL AND project_team_id IS NOT NULL)",
            name="report_space_exactly_one_owner",
        ),
        UniqueConstraint("workspace_id", "department_id", name="uq_report_spaces_department"),
        UniqueConstraint("workspace_id", "project_team_id", name="uq_report_spaces_project_team"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    space_type: Mapped[str] = mapped_column(String(40), nullable=False)
    department_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("departments.id"), nullable=True
    )
    project_team_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("project_teams.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    report_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    report_mode: Mapped[str] = mapped_column(String(40), nullable=False, default="weekly")
    ai_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    allowed_data_source_types: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=lambda: ["git", "jira", "project_progress", "history"]
    )
    template_bindings: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    member_visibility: Mapped[str] = mapped_column(String(40), nullable=False, default="private")


class ReportRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "report_rules"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "report_space_id",
            "report_type",
            name="uq_report_rules_space_type",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    report_space_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("report_spaces.id"), nullable=False, index=True
    )
    report_type: Mapped[str] = mapped_column(String(40), nullable=False)
    enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    frequency: Mapped[str] = mapped_column(String(40), nullable=False)
    interval_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    week_start_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reminder_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reminder_time: Mapped[str | None] = mapped_column(String(16), nullable=True)
    due_type: Mapped[str] = mapped_column(String(40), nullable=False, default="same_day")
    due_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    due_time: Mapped[str | None] = mapped_column(String(16), nullable=True)
    skip_weekends: Mapped[bool] = mapped_column(default=False, nullable=False)
    notification_channels: Mapped[list[str]] = mapped_column(
        JSONB, nullable=False, default=lambda: ["in_app", "feishu"]
    )
    overdue_policy: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    extra_config: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
