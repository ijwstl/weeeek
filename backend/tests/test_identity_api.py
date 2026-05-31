from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_current_principal() -> None:
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["workspace"]["name"] == "研发协作空间"
    assert "workspace.setting.manage" in body["permissions"]


def test_get_workspace() -> None:
    response = client.get("/api/v1/workspace")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["slug"] == "engineering"
    assert body["department_max_depth"] == 5


def test_list_members() -> None:
    response = client.get("/api/v1/members")
    assert response.status_code == 200
    body = response.json()["data"]
    assert len(body) == 1
    assert body[0]["display_name"] == "王启"


def test_update_and_test_ldap_provider_config() -> None:
    update_response = client.patch(
        "/api/v1/auth/providers/ldap",
        json={
            "enabled": True,
            "config_public": {
                "server_url": "ldap://ldap.internal:389",
                "base_dn": "dc=internal,dc=local",
                "bind_dn": "cn=readonly,dc=internal,dc=local",
                "user_filter": "(uid={username})",
            },
            "bind_password": "secret",
        },
    )
    assert update_response.status_code == 200
    body = update_response.json()["data"]
    assert body["provider_type"] == "ldap"
    assert body["bind_password_configured"] is True

    test_response = client.post("/api/v1/auth/providers/ldap/test")
    assert test_response.status_code == 200
    assert test_response.json()["data"]["ok"] is True
