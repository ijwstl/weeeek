from fastapi import APIRouter, HTTPException, status

from app.schemas.common import APIResponse
from app.schemas.rbac import (
    MemberRoleAssignmentCreate,
    MemberRoleAssignmentRead,
    PermissionRead,
    RoleCreate,
    RolePermissionUpdate,
    RoleRead,
    RoleUpdate,
)
from app.services.rbac import get_builtin_role, list_builtin_roles, list_permission_definitions

router = APIRouter()


@router.get("/permissions", response_model=APIResponse[list[PermissionRead]])
def list_permissions() -> APIResponse[list[PermissionRead]]:
    permissions = [
        PermissionRead(
            code=definition.code,
            name=definition.name,
            description=definition.description,
            category=definition.category,
            resource_type=definition.resource_type,
            action=definition.action,
        )
        for definition in list_permission_definitions()
    ]
    return APIResponse(data=permissions)


@router.get("/roles", response_model=APIResponse[list[RoleRead]])
def list_roles() -> APIResponse[list[RoleRead]]:
    return APIResponse(data=[RoleRead.model_validate(role) for role in list_builtin_roles()])


@router.post("/roles", response_model=APIResponse[RoleRead])
def create_role(payload: RoleCreate) -> APIResponse[RoleRead]:
    role = {
        "id": f"custom-{payload.code}",
        "code": payload.code,
        "name": payload.name,
        "description": payload.description,
        "is_builtin": False,
        "is_editable": True,
        "permissions": payload.permissions,
    }
    return APIResponse(data=RoleRead.model_validate(role))


@router.get("/roles/{role_id}", response_model=APIResponse[RoleRead])
def get_role(role_id: str) -> APIResponse[RoleRead]:
    role = get_builtin_role(role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return APIResponse(data=RoleRead.model_validate(role))


@router.patch("/roles/{role_id}", response_model=APIResponse[RoleRead])
def update_role(role_id: str, payload: RoleUpdate) -> APIResponse[RoleRead]:
    role = get_builtin_role(role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if not role["is_editable"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Builtin role is locked",
        )

    updated = {**role, **payload.model_dump(exclude_none=True)}
    return APIResponse(data=RoleRead.model_validate(updated))


@router.delete("/roles/{role_id}", response_model=APIResponse[dict[str, bool]])
def delete_role(role_id: str) -> APIResponse[dict[str, bool]]:
    role = get_builtin_role(role_id)
    if role is not None and not role["is_editable"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Builtin role is locked",
        )
    return APIResponse(data={"ok": True})


@router.put("/roles/{role_id}/permissions", response_model=APIResponse[RoleRead])
def update_role_permissions(
    role_id: str,
    payload: RolePermissionUpdate,
) -> APIResponse[RoleRead]:
    role = get_builtin_role(role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    if not role["is_editable"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Builtin role is locked",
        )

    updated = {**role, "permissions": payload.permissions}
    return APIResponse(data=RoleRead.model_validate(updated))


@router.get(
    "/members/{member_id}/role-assignments",
    response_model=APIResponse[list[MemberRoleAssignmentRead]],
)
def list_member_role_assignments(member_id: str) -> APIResponse[list[MemberRoleAssignmentRead]]:
    return APIResponse(
        data=[
            MemberRoleAssignmentRead(
                id="assignment-workspace-owner",
                member_id=member_id,
                role_id="builtin-workspace-owner",
                role_code="workspace_owner",
                scope_type="workspace",
                scope_id="00000000-0000-0000-0000-000000000001",
            ),
            MemberRoleAssignmentRead(
                id="assignment-member",
                member_id=member_id,
                role_id="builtin-member",
                role_code="member",
                scope_type="self",
                scope_id=member_id,
            ),
        ]
    )


@router.post(
    "/members/{member_id}/role-assignments",
    response_model=APIResponse[MemberRoleAssignmentRead],
)
def create_member_role_assignment(
    member_id: str,
    payload: MemberRoleAssignmentCreate,
) -> APIResponse[MemberRoleAssignmentRead]:
    role = get_builtin_role(payload.role_id)
    role_code = str(role["code"]) if role else payload.role_id
    return APIResponse(
        data=MemberRoleAssignmentRead(
            id=f"assignment-{member_id}-{payload.role_id}",
            member_id=member_id,
            role_id=payload.role_id,
            role_code=role_code,
            scope_type=payload.scope_type,
            scope_id=payload.scope_id,
        )
    )


@router.delete(
    "/members/{member_id}/role-assignments/{assignment_id}",
    response_model=APIResponse[dict[str, bool]],
)
def delete_member_role_assignment(
    member_id: str,
    assignment_id: str,
) -> APIResponse[dict[str, bool]]:
    _ = (member_id, assignment_id)
    return APIResponse(data={"ok": True})
