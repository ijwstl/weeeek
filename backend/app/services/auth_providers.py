from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.identity import AuthProviderConfig
from app.services.bootstrap import DEMO_MEMBER
from app.services.reports import ensure_demo_report_seed

WORKSPACE_ID = UUID(str(DEMO_MEMBER["workspace_id"]))

DEFAULT_LDAP_PUBLIC_CONFIG: dict[str, object] = {
    "server_url": "ldap://ldap.example.local:389",
    "use_ssl": False,
    "base_dn": "dc=example,dc=local",
    "bind_dn": "cn=readonly,dc=example,dc=local",
    "user_filter": "(uid={username})",
    "department_sync_enabled": True,
    "attribute_mapping": {
        "display_name": "cn",
        "email": "mail",
        "employee_no": "employeeNumber",
        "department": "department",
    },
}


def ensure_ldap_provider(db: Session) -> AuthProviderConfig:
    ensure_demo_report_seed(db)
    provider = db.scalar(
        select(AuthProviderConfig).where(
            AuthProviderConfig.workspace_id == WORKSPACE_ID,
            AuthProviderConfig.provider_type == "ldap",
        )
    )
    if provider is not None:
        return provider

    provider = AuthProviderConfig(
        workspace_id=WORKSPACE_ID,
        provider_type="ldap",
        name="LDAP / Active Directory",
        enabled=False,
        config_public=dict(DEFAULT_LDAP_PUBLIC_CONFIG),
        config_encrypted={},
    )
    db.add(provider)
    db.commit()
    db.refresh(provider)
    return provider


def get_ldap_provider(db: Session) -> dict[str, object]:
    return serialize_provider(ensure_ldap_provider(db))


def update_ldap_provider(payload: dict[str, object], db: Session) -> dict[str, object]:
    provider = ensure_ldap_provider(db)
    if "name" in payload and payload["name"] is not None:
        provider.name = str(payload["name"])
    if "enabled" in payload and payload["enabled"] is not None:
        provider.enabled = bool(payload["enabled"])
    if "config_public" in payload and isinstance(payload["config_public"], dict):
        provider.config_public = {
            **provider.config_public,
            **payload["config_public"],
        }
    bind_password = payload.get("bind_password")
    if isinstance(bind_password, str) and bind_password:
        provider.config_encrypted = {
            **provider.config_encrypted,
            "bind_password": "***configured***",
        }
    db.commit()
    db.refresh(provider)
    return serialize_provider(provider)


def test_ldap_provider(db: Session) -> dict[str, object]:
    provider = ensure_ldap_provider(db)
    ok, message = validate_ldap_provider(provider)
    return {
        "ok": ok,
        "status": "connected" if ok else "invalid_config",
        "message": message,
    }


def validate_ldap_provider(provider: AuthProviderConfig) -> tuple[bool, str]:
    if not provider.enabled:
        return False, "LDAP 登录已停用"

    config = provider.config_public
    server_url = str(config.get("server_url") or "")
    base_dn = str(config.get("base_dn") or "")
    bind_dn = str(config.get("bind_dn") or "")
    user_filter = str(config.get("user_filter") or "")

    if not server_url.startswith(("ldap://", "ldaps://")):
        return False, "LDAP 服务器地址需要以 ldap:// 或 ldaps:// 开头"
    if not base_dn:
        return False, "Base DN 不能为空"
    if not bind_dn:
        return False, "绑定 DN 不能为空"
    if "{username}" not in user_filter:
        return False, "用户过滤器需要包含 {username}"
    if "bind_password" not in provider.config_encrypted:
        return False, "绑定密码尚未配置"
    return True, "LDAP 配置格式有效，真实网络绑定将在联调环境执行"


def serialize_provider(provider: AuthProviderConfig) -> dict[str, object]:
    return {
        "id": str(provider.id),
        "workspace_id": str(provider.workspace_id),
        "provider_type": provider.provider_type,
        "name": provider.name,
        "enabled": provider.enabled,
        "config_public": provider.config_public,
        "bind_password_configured": "bind_password" in provider.config_encrypted,
    }
