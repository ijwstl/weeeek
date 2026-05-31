from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class NotificationMessage:
    receiver_member_id: str
    title: str
    content: str
    resource_type: str | None = None
    resource_id: str | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class NotificationResult:
    success: bool
    error_message: str | None = None
    provider_message_id: str | None = None


class NotificationChannel(Protocol):
    channel_type: str

    async def send(self, message: NotificationMessage) -> NotificationResult:
        ...

    async def test_connection(self, config: dict[str, object]) -> NotificationResult:
        ...

