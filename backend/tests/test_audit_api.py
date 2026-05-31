from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_audit_log_is_recorded_by_decorator() -> None:
    response = client.patch(
        "/api/v1/notifications/channels/channel-feishu-default",
        json={"enabled": True},
    )
    assert response.status_code == 200

    logs_response = client.get("/api/v1/audit/logs")
    assert logs_response.status_code == 200
    logs = logs_response.json()["data"]
    assert any(log["action"] == "notification.channel.update" for log in logs)


def test_audit_log_query_filters() -> None:
    update_response = client.patch(
        "/api/v1/notifications/channels/channel-feishu-default",
        json={"enabled": True},
    )
    assert update_response.status_code == 200

    response = client.get(
        "/api/v1/audit/logs",
        params={"action": "notification.channel.update", "keyword": "notification"},
    )
    assert response.status_code == 200
    logs = response.json()["data"]
    assert logs
    assert {log["action"] for log in logs} == {"notification.channel.update"}
