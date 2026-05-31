from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.audit.decorator import audit_log
from app.db.session import get_db
from app.schemas.common import APIResponse
from app.schemas.data_source import (
    DataSourceConnectionCreate,
    DataSourceConnectionRead,
    DataSourceConnectionUpdate,
)
from app.services.data_sources import (
    create_connection,
    list_connections,
    test_connection,
    update_connection,
)

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("", response_model=APIResponse[list[DataSourceConnectionRead]])
def get_data_sources(db: DbSession) -> APIResponse[list[DataSourceConnectionRead]]:
    return APIResponse(
        data=[
            DataSourceConnectionRead.model_validate(connection)
            for connection in list_connections(db)
        ]
    )


@router.post("", response_model=APIResponse[DataSourceConnectionRead])
@audit_log("data_source.create", "data_source_connection")
def create_data_source(
    payload: DataSourceConnectionCreate,
    db: DbSession,
) -> APIResponse[DataSourceConnectionRead]:
    connection = create_connection(payload.model_dump(), db)
    return APIResponse(data=DataSourceConnectionRead.model_validate(connection))


@router.patch("/{connection_id}", response_model=APIResponse[DataSourceConnectionRead])
@audit_log("data_source.update", "data_source_connection")
def update_data_source(
    connection_id: str,
    payload: DataSourceConnectionUpdate,
    db: DbSession,
) -> APIResponse[DataSourceConnectionRead]:
    connection = update_connection(connection_id, payload.model_dump(exclude_none=True), db)
    if connection is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found")
    return APIResponse(data=DataSourceConnectionRead.model_validate(connection))


@router.post("/{connection_id}/test", response_model=APIResponse[dict[str, object]])
@audit_log("data_source.test", "data_source_connection")
def test_data_source(
    connection_id: str,
    db: DbSession,
) -> APIResponse[dict[str, object]]:
    result = test_connection(connection_id, db)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found")
    return APIResponse(data=result)
