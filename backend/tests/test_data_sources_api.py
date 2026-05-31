from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_data_sources() -> None:
    response = client.get("/api/v1/data-sources")
    assert response.status_code == 200
    body = response.json()["data"]
    assert {item["source_type"] for item in body} >= {"gitlab", "github", "jira"}
    assert body[0]["scope_config"]


def test_update_and_test_data_source() -> None:
    list_response = client.get("/api/v1/data-sources")
    connection_id = list_response.json()["data"][0]["id"]

    update_response = client.patch(
        f"/api/v1/data-sources/{connection_id}",
        json={"enabled": False},
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["enabled"] is False

    test_response = client.post(f"/api/v1/data-sources/{connection_id}/test")
    assert test_response.status_code == 200
    assert test_response.json()["data"]["ok"] is False
