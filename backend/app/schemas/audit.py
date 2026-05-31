from datetime import datetime

from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: str
    workspace_id: str
    actor_member_id: str | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    request_method: str | None = None
    request_path: str | None = None
    status: str
    ip_address: str | None = None
    user_agent: str | None = None
    metadata_json: dict[str, object]
    created_at: datetime
