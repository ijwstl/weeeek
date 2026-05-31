from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    data: T
    request_id: str | None = None


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
