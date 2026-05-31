from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_notification_channels() -> None:
    response = client.get("/api/v1/notifications/channels")
    assert response.status_code == 200
    body = response.json()["data"]
    assert {channel["channel_type"] for channel in body} >= {"in_app", "feishu", "webhook"}


def test_update_and_test_notification_channel() -> None:
    list_response = client.get("/api/v1/notifications/channels")
    assert list_response.status_code == 200
    feishu = next(
        channel
        for channel in list_response.json()["data"]
        if channel["channel_type"] == "feishu"
    )

    update_response = client.patch(
        f"/api/v1/notifications/channels/{feishu['id']}",
        json={
            "enabled": True,
            "config": {
                "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/test",
                "secret_configured": True,
                "mention_policy": "report_owner",
            },
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["config"]["mention_policy"] == "report_owner"

    test_response = client.post(f"/api/v1/notifications/channels/{feishu['id']}/test")
    assert test_response.status_code == 200
    assert test_response.json()["data"]["ok"] is True


def test_in_app_notifications_can_be_marked_read() -> None:
    response = client.get("/api/v1/notifications/in-app")
    assert response.status_code == 200
    notifications = response.json()["data"]
    assert notifications

    unread_response = client.get("/api/v1/notifications/in-app/unread-count")
    assert unread_response.status_code == 200
    assert unread_response.json()["data"]["unread_count"] >= 1

    first_unread = next(item for item in notifications if item["read_at"] is None)
    read_response = client.post(f"/api/v1/notifications/in-app/{first_unread['id']}/read")
    assert read_response.status_code == 200
    assert read_response.json()["data"]["read_at"] is not None
