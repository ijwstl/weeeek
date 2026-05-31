from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "users"

    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    memberships: Mapped[list["Member"]] = relationship(back_populates="user")


class Workspace(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    deployment_mode: Mapped[str] = mapped_column(String(32), nullable=False, default="saas")
    default_locale: Mapped[str] = mapped_column(String(32), nullable=False, default="zh-CN")
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Shanghai")
    department_max_depth: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    members: Mapped[list["Member"]] = relationship(back_populates="workspace")


class Member(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "members"
    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_members_workspace_user"),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    department_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    employee_no: Mapped[str | None] = mapped_column(String(80), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow
    )

    user: Mapped[User] = relationship(back_populates="memberships")
    workspace: Mapped[Workspace] = relationship(back_populates="members")


class UserIdentity(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "user_identities"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "provider_type",
            "provider_user_id",
            name="uq_user_identities_provider_user",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    member_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("members.id"), nullable=False
    )
    provider_type: Mapped[str] = mapped_column(String(32), nullable=False)
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_payload_snapshot: Mapped[dict[str, object]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuthProviderConfig(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "auth_provider_configs"

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    provider_type: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    config_public: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
    config_encrypted: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False, default=dict)
