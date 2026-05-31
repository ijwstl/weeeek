from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_permissions() -> None:
    response = client.get("/api/v1/permissions")
    assert response.status_code == 200
    body = response.json()["data"]
    codes = {item["code"] for item in body}
    assert "workspace.role.manage" in codes
    assert "department.report.view" in codes


def test_list_roles() -> None:
    response = client.get("/api/v1/roles")
    assert response.status_code == 200
    body = response.json()["data"]
    roles = {item["code"]: item for item in body}
    assert "workspace_owner" in roles
    assert "workspace.role.manage" in roles["workspace_owner"]["permissions"]
    assert roles["workspace_owner"]["is_editable"] is False


def test_locked_role_cannot_be_updated() -> None:
    response = client.patch(
        "/api/v1/roles/builtin-workspace-owner",
        json={"name": "Owner"},
    )
    assert response.status_code == 400


def test_list_member_role_assignments() -> None:
    response = client.get(
        "/api/v1/members/00000000-0000-0000-0000-000000000201/role-assignments"
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body[0]["role_code"] == "workspace_owner"

