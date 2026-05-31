from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.audit.decorator import audit_log
from app.db.session import get_db
from app.schemas.common import APIResponse
from app.schemas.identity import (
    AuthProviderConfigRead,
    AuthProviderConfigUpdate,
    AuthProviderTestResult,
    CurrentPrincipalRead,
    LdapLoginRequest,
    TokenRead,
)
from app.services.auth_providers import (
    get_ldap_provider,
    test_ldap_provider,
    update_ldap_provider,
)
from app.services.bootstrap import get_demo_principal

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/ldap/login", response_model=APIResponse[TokenRead])
def ldap_login(payload: LdapLoginRequest) -> APIResponse[TokenRead]:
    # Real LDAP binding and login-time sync will be implemented in the auth milestone.
    token = f"dev-token-for-{payload.username}"
    return APIResponse(data=TokenRead(access_token=token))


@router.get("/providers/ldap", response_model=APIResponse[AuthProviderConfigRead])
def get_ldap_config(db: DbSession) -> APIResponse[AuthProviderConfigRead]:
    return APIResponse(data=AuthProviderConfigRead.model_validate(get_ldap_provider(db)))


@router.patch("/providers/ldap", response_model=APIResponse[AuthProviderConfigRead])
@audit_log("auth_provider.ldap.update", "auth_provider")
def update_ldap_config(
    payload: AuthProviderConfigUpdate,
    db: DbSession,
) -> APIResponse[AuthProviderConfigRead]:
    provider = update_ldap_provider(payload.model_dump(exclude_none=True), db)
    return APIResponse(data=AuthProviderConfigRead.model_validate(provider))


@router.post("/providers/ldap/test", response_model=APIResponse[AuthProviderTestResult])
@audit_log("auth_provider.ldap.test", "auth_provider")
def test_ldap_config(db: DbSession) -> APIResponse[AuthProviderTestResult]:
    return APIResponse(data=AuthProviderTestResult.model_validate(test_ldap_provider(db)))


@router.post("/feishu/start", response_model=APIResponse[dict[str, str]])
def feishu_start() -> APIResponse[dict[str, str]]:
    return APIResponse(data={"authorize_url": "/api/v1/auth/feishu/callback?dev=1"})


@router.get("/feishu/callback", response_model=APIResponse[TokenRead])
def feishu_callback() -> APIResponse[TokenRead]:
    return APIResponse(data=TokenRead(access_token="dev-feishu-token"))


@router.post("/logout", response_model=APIResponse[dict[str, bool]])
def logout() -> APIResponse[dict[str, bool]]:
    return APIResponse(data={"ok": True})


@router.post("/refresh", response_model=APIResponse[TokenRead])
def refresh() -> APIResponse[TokenRead]:
    return APIResponse(data=TokenRead(access_token="dev-refreshed-token"))


@router.get("/me", response_model=APIResponse[CurrentPrincipalRead])
def me() -> APIResponse[CurrentPrincipalRead]:
    return APIResponse(data=CurrentPrincipalRead.model_validate(get_demo_principal()))


@router.get("/workspaces", response_model=APIResponse[list[dict[str, object]]])
def workspaces() -> APIResponse[list[dict[str, object]]]:
    principal = get_demo_principal()
    return APIResponse(data=[principal["workspace"]])


@router.post("/workspaces/switch", response_model=APIResponse[dict[str, bool]])
def switch_workspace() -> APIResponse[dict[str, bool]]:
    return APIResponse(data={"ok": True})
