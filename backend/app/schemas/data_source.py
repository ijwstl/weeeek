from datetime import datetime

from pydantic import BaseModel, Field


class DataSourceConnectionRead(BaseModel):
    id: str
    workspace_id: str
    member_id: str
    source_type: str
    name: str
    account_name: str
    status: str
    enabled: bool
    scope_config: dict[str, object]
    last_sync_at: datetime | None = None


class DataSourceConnectionCreate(BaseModel):
    source_type: str = Field(pattern="^(gitlab|github|jira|custom)$")
    name: str = Field(min_length=1, max_length=120)
    account_name: str = Field(min_length=1, max_length=255)
    scope_config: dict[str, object] = Field(default_factory=dict)


class DataSourceConnectionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    account_name: str | None = Field(default=None, min_length=1, max_length=255)
    enabled: bool | None = None
    status: str | None = None
    scope_config: dict[str, object] | None = None
