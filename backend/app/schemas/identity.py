from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import OrmModel


class WorkspaceRead(OrmModel):
    id: UUID | str
    name: str
    slug: str
    deployment_mode: str
    default_locale: str
    timezone: str
    department_max_depth: int
    status: str


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    timezone: str | None = Field(default=None, max_length=64)
    department_max_depth: int | None = Field(default=None, ge=1, le=8)


class UserRead(OrmModel):
    id: UUID | str
    display_name: str
    email: str | None = None
    avatar_url: str | None = None
    status: str


class MemberRead(OrmModel):
    id: UUID | str
    workspace_id: UUID | str
    user_id: UUID | str
    department_id: UUID | str | None = None
    display_name: str
    email: str | None = None
    employee_no: str | None = None
    avatar_url: str | None = None
    status: str


class MemberCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=120)
    email: str | None = Field(default=None, max_length=255)
    employee_no: str | None = Field(default=None, max_length=80)
    department_id: UUID | None = None


class MemberUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    email: str | None = Field(default=None, max_length=255)
    employee_no: str | None = Field(default=None, max_length=80)
    department_id: UUID | None = None
    status: str | None = None


class CurrentPrincipalRead(BaseModel):
    user: UserRead
    member: MemberRead
    workspace: WorkspaceRead
    permissions: list[str]
    roles: list[str]


class LdapLoginRequest(BaseModel):
    username: str
    password: str


class AuthProviderConfigRead(BaseModel):
    id: str
    workspace_id: str
    provider_type: str
    name: str
    enabled: bool
    config_public: dict[str, object]
    bind_password_configured: bool = False


class AuthProviderConfigUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    enabled: bool | None = None
    config_public: dict[str, object] | None = None
    bind_password: str | None = None


class AuthProviderTestResult(BaseModel):
    ok: bool
    status: str
    message: str


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
