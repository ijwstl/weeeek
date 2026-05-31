from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class NotificationChannelRead(BaseModel):
    id: str
    channel_type: str
    name: str
    enabled: bool
    config: dict[str, object]
    last_tested_at: datetime | None = None
    last_test_status: str | None = None


class NotificationChannelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    enabled: bool | None = None
    config: dict[str, object] | None = None


class NotificationChannelTestResult(BaseModel):
    ok: bool
    status: str
    checked_at: datetime
    message: str


class NotificationChannelCreate(BaseModel):
    channel_type: str
    name: str = Field(min_length=1, max_length=120)
    enabled: bool = True
    config: dict[str, object] = Field(default_factory=dict)

    @field_validator("channel_type")
    @classmethod
    def validate_channel_type(cls, value: str) -> str:
        if value not in {"in_app", "feishu", "webhook"}:
            raise ValueError(f"Unsupported notification channel type: {value}")
        return value


class InAppNotificationRead(BaseModel):
    id: str
    receiver_member_id: str
    title: str
    content: str
    category: str
    resource_type: str | None = None
    resource_id: str | None = None
    read_at: datetime | None = None
    created_at: datetime


class NotificationUnreadSummary(BaseModel):
    unread_count: int
