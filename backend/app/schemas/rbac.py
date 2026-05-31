from pydantic import BaseModel, Field


class PermissionRead(BaseModel):
    code: str
    name: str
    description: str
    category: str
    resource_type: str
    action: str
    is_system: bool = True


class RoleRead(BaseModel):
    id: str
    code: str
    name: str
    description: str
    is_builtin: bool
    is_editable: bool
    permissions: list[str]


class RoleCreate(BaseModel):
    code: str = Field(min_length=2, max_length=80)
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    permissions: list[str] = Field(default_factory=list)


class RoleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    permissions: list[str] | None = None


class RolePermissionUpdate(BaseModel):
    permissions: list[str]


class MemberRoleAssignmentRead(BaseModel):
    id: str
    member_id: str
    role_id: str
    role_code: str
    scope_type: str
    scope_id: str | None = None


class MemberRoleAssignmentCreate(BaseModel):
    role_id: str
    scope_type: str
    scope_id: str | None = None

