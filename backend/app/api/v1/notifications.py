from fastapi import APIRouter, HTTPException, status

from app.audit.decorator import audit_log
from app.schemas.common import APIResponse
from app.schemas.notification import (
    InAppNotificationRead,
    NotificationChannelCreate,
    NotificationChannelRead,
    NotificationChannelTestResult,
    NotificationChannelUpdate,
    NotificationUnreadSummary,
)
from app.services.notifications import (
    create_channel,
    get_channel,
    list_channels,
    list_in_app_notifications,
    mark_all_notifications_read,
    mark_notification_read,
    test_channel,
    unread_count,
    update_channel,
)

router = APIRouter()


@router.get("/in-app", response_model=APIResponse[list[InAppNotificationRead]])
def get_in_app_notifications(
    only_unread: bool = False,
) -> APIResponse[list[InAppNotificationRead]]:
    return APIResponse(
        data=[
            InAppNotificationRead.model_validate(notification)
            for notification in list_in_app_notifications(only_unread)
        ]
    )


@router.get("/in-app/unread-count", response_model=APIResponse[NotificationUnreadSummary])
def get_in_app_unread_count() -> APIResponse[NotificationUnreadSummary]:
    return APIResponse(data=NotificationUnreadSummary(unread_count=unread_count()))


@router.post("/in-app/{notification_id}/read", response_model=APIResponse[InAppNotificationRead])
def read_in_app_notification(notification_id: str) -> APIResponse[InAppNotificationRead]:
    notification = mark_notification_read(notification_id)
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
    return APIResponse(data=InAppNotificationRead.model_validate(notification))


@router.post("/in-app/read-all", response_model=APIResponse[dict[str, int]])
def read_all_in_app_notifications() -> APIResponse[dict[str, int]]:
    return APIResponse(data=mark_all_notifications_read())


@router.get("/channels", response_model=APIResponse[list[NotificationChannelRead]])
def get_notification_channels() -> APIResponse[list[NotificationChannelRead]]:
    return APIResponse(
        data=[NotificationChannelRead.model_validate(channel) for channel in list_channels()]
    )


@router.post("/channels", response_model=APIResponse[NotificationChannelRead])
@audit_log("notification.channel.create", "notification_channel")
def create_notification_channel(
    payload: NotificationChannelCreate,
) -> APIResponse[NotificationChannelRead]:
    channel = create_channel(payload.model_dump())
    return APIResponse(data=NotificationChannelRead.model_validate(channel))


@router.get("/channels/{channel_id}", response_model=APIResponse[NotificationChannelRead])
def get_notification_channel(channel_id: str) -> APIResponse[NotificationChannelRead]:
    channel = get_channel(channel_id)
    if channel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return APIResponse(data=NotificationChannelRead.model_validate(channel))


@router.patch("/channels/{channel_id}", response_model=APIResponse[NotificationChannelRead])
@audit_log("notification.channel.update", "notification_channel")
def update_notification_channel(
    channel_id: str,
    payload: NotificationChannelUpdate,
) -> APIResponse[NotificationChannelRead]:
    channel = update_channel(channel_id, payload.model_dump(exclude_none=True))
    if channel is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return APIResponse(data=NotificationChannelRead.model_validate(channel))


@router.post(
    "/channels/{channel_id}/test",
    response_model=APIResponse[NotificationChannelTestResult],
)
@audit_log("notification.channel.test", "notification_channel")
def test_notification_channel(channel_id: str) -> APIResponse[NotificationChannelTestResult]:
    result = test_channel(channel_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
    return APIResponse(data=NotificationChannelTestResult.model_validate(result))
