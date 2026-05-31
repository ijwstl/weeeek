from collections.abc import Callable

from fastapi import Depends, HTTPException, status

from app.permissions.constants import Permission


class CurrentPrincipal:
    """Temporary principal used until auth/RBAC persistence is implemented."""

    def __init__(self) -> None:
        self.member_id = "demo-member"
        self.workspace_id = "demo-workspace"
        self.permissions = {permission.value for permission in Permission}


def get_current_principal() -> CurrentPrincipal:
    return CurrentPrincipal()


CURRENT_PRINCIPAL_DEP = Depends(get_current_principal)


def require_permission(
    permission: Permission | str,
) -> Callable[[CurrentPrincipal], CurrentPrincipal]:
    permission_code = permission.value if isinstance(permission, Permission) else permission

    def dependency(
        principal: CurrentPrincipal = CURRENT_PRINCIPAL_DEP,
    ) -> CurrentPrincipal:
        if permission_code not in principal.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission_code}",
            )
        return principal

    return dependency
