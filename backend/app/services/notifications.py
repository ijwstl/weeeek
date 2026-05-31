from copy import deepcopy
from datetime import datetime, timedelta
from uuid import uuid4

from app.services.bootstrap import DEMO_MEMBER

DEMO_NOTIFICATION_CHANNELS: list[dict[str, object]] = [
    {
        "id": "channel-in-app-default",
        "channel_type": "in_app",
        "name": "站内通知",
        "enabled": True,
        "config": {"retention_days": 90, "show_unread_badge": True},
        "last_tested_at": None,
        "last_test_status": None,
    },
    {
        "id": "channel-feishu-default",
        "channel_type": "feishu",
        "name": "飞书群通知",
        "enabled": True,
        "config": {
            "webhook_url": "https://open.feishu.cn/open-apis/bot/v2/hook/demo",
            "secret_configured": False,
            "mention_policy": "none",
        },
        "last_tested_at": None,
        "last_test_status": None,
    },
    {
        "id": "channel-webhook-default",
        "channel_type": "webhook",
        "name": "自定义 Webhook",
        "enabled": False,
        "config": {
            "url": "https://example.com/report-notify",
            "method": "POST",
            "headers": [{"key": "X-Source", "value": "weeeek"}],
        },
        "last_tested_at": None,
        "last_test_status": None,
    },
]

MEMBER_ID = str(DEMO_MEMBER["id"])
_now = datetime.now().astimezone()
DEMO_IN_APP_NOTIFICATIONS: list[dict[str, object]] = [
    {
        "id": "notice-report-weekly-due",
        "receiver_member_id": MEMBER_ID,
        "title": "本周周报待提交",
        "content": "后端研发组周报将在今天 19:00 截止，请确认 AI 草稿后提交。",
        "category": "report_due",
        "resource_type": "report_instance",
        "resource_id": "report-weekly-backend-20260525",
        "read_at": None,
        "created_at": _now - timedelta(minutes=18),
    },
    {
        "id": "notice-ai-draft-ready",
        "receiver_member_id": MEMBER_ID,
        "title": "AI 草稿已生成",
        "content": "已根据 GitLab、GitHub、Jira 数据生成报告草稿，请检查内容准确性。",
        "category": "ai_draft",
        "resource_type": "report_instance",
        "resource_id": "report-weekly-backend-20260525",
        "read_at": None,
        "created_at": _now - timedelta(hours=2),
    },
    {
        "id": "notice-template-published",
        "receiver_member_id": MEMBER_ID,
        "title": "研发周报模板已发布",
        "content": "模板 v2 已发布，之后新生成的报告会使用最新字段快照。",
        "category": "template",
        "resource_type": "template",
        "resource_id": "template-weekly-default",
        "read_at": _now - timedelta(hours=1),
        "created_at": _now - timedelta(days=1),
    },
]


def list_channels() -> list[dict[str, object]]:
    return [deepcopy(channel) for channel in DEMO_NOTIFICATION_CHANNELS]


def get_channel(channel_id: str) -> dict[str, object] | None:
    channel = find_channel(channel_id)
    return deepcopy(channel) if channel else None


def create_channel(payload: dict[str, object]) -> dict[str, object]:
    channel = {
        "id": f"channel-{uuid4()}",
        "channel_type": payload["channel_type"],
        "name": payload["name"],
        "enabled": payload.get("enabled", True),
        "config": deepcopy(payload.get("config") or {}),
        "last_tested_at": None,
        "last_test_status": None,
    }
    DEMO_NOTIFICATION_CHANNELS.append(channel)
    return deepcopy(channel)


def update_channel(channel_id: str, payload: dict[str, object]) -> dict[str, object] | None:
    channel = find_channel(channel_id)
    if channel is None:
        return None

    for key in ["name", "enabled", "config"]:
        if key in payload and payload[key] is not None:
            channel[key] = deepcopy(payload[key])
    return deepcopy(channel)


def test_channel(channel_id: str) -> dict[str, object] | None:
    channel = find_channel(channel_id)
    if channel is None:
        return None

    ok, message = validate_channel_config(channel)
    checked_at = datetime.now().astimezone()
    channel["last_tested_at"] = checked_at
    channel["last_test_status"] = "connected" if ok else "invalid_config"
    return {
        "ok": ok,
        "status": channel["last_test_status"],
        "checked_at": checked_at,
        "message": message,
    }


def validate_channel_config(channel: dict[str, object]) -> tuple[bool, str]:
    if not channel.get("enabled"):
        return False, "渠道已停用"

    channel_type = channel.get("channel_type")
    config = channel.get("config")
    if not isinstance(config, dict):
        return False, "配置格式不正确"

    if channel_type == "in_app":
        return True, "站内通知可用"

    if channel_type == "feishu":
        webhook_url = str(config.get("webhook_url") or "")
        if not webhook_url.startswith("http"):
            return False, "飞书 Webhook 地址不正确"
        return True, "飞书通知配置可用"

    if channel_type == "webhook":
        url = str(config.get("url") or "")
        method = str(config.get("method") or "POST").upper()
        if not url.startswith("http"):
            return False, "Webhook 地址不正确"
        if method not in {"POST", "PUT", "PATCH"}:
            return False, "Webhook 方法只支持 POST、PUT、PATCH"
        return True, "自定义 Webhook 配置可用"

    return False, "不支持的通知渠道"


def find_channel(channel_id: str) -> dict[str, object] | None:
    return next(
        (channel for channel in DEMO_NOTIFICATION_CHANNELS if channel["id"] == channel_id),
        None,
    )


def list_in_app_notifications(only_unread: bool = False) -> list[dict[str, object]]:
    notifications = [
        deepcopy(notification)
        for notification in DEMO_IN_APP_NOTIFICATIONS
        if notification["receiver_member_id"] == MEMBER_ID
    ]
    if only_unread:
        notifications = [
            notification for notification in notifications if notification["read_at"] is None
        ]
    return sorted(notifications, key=lambda item: item["created_at"], reverse=True)


def unread_count() -> int:
    return len(list_in_app_notifications(only_unread=True))


def mark_notification_read(notification_id: str) -> dict[str, object] | None:
    notification = find_notification(notification_id)
    if notification is None:
        return None
    notification["read_at"] = notification["read_at"] or datetime.now().astimezone()
    return deepcopy(notification)


def mark_all_notifications_read() -> dict[str, int]:
    changed = 0
    for notification in DEMO_IN_APP_NOTIFICATIONS:
        if notification["receiver_member_id"] == MEMBER_ID and notification["read_at"] is None:
            notification["read_at"] = datetime.now().astimezone()
            changed += 1
    return {"updated": changed}


def find_notification(notification_id: str) -> dict[str, object] | None:
    return next(
        (
            notification
            for notification in DEMO_IN_APP_NOTIFICATIONS
            if notification["id"] == notification_id
            and notification["receiver_member_id"] == MEMBER_ID
        ),
        None,
    )
