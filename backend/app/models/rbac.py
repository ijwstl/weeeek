from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class PermissionModel(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "permissions"

    code: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Role(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("workspace_id", "code", name="uq_roles_workspace_code"),)

    workspace_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True, index=True
    )
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False, default="")
    is_builtin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_editable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class RolePermission(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "role_id",
            "permission_id",
            name="uq_role_permissions_workspace_role_permission",
        ),
    )

    workspace_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=True, index=True
    )
    role_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    permission_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("permissions.id"), nullable=False
    )


class MemberRoleAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "member_role_assignments"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "member_id",
            "role_id",
            "scope_type",
            "scope_id",
            name="uq_member_role_assignments_scope",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False, index=True
    )
    member_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("members.id"), nullable=False, index=True
    )
    role_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("roles.id"), nullable=False
    )
    scope_type: Mapped[str] = mapped_column(String(40), nullable=False)
    scope_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
    created_by_member_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True), nullable=True)
