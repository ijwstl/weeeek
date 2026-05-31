from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.audit import AuditLogRead
from app.schemas.common import APIResponse
from app.services.audit import list_audit_logs

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/logs", response_model=APIResponse[list[AuditLogRead]])
def get_audit_logs(
    db: DbSession,
    limit: int = Query(default=50, ge=1, le=200),
    action: str | None = None,
    resource_type: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
) -> APIResponse[list[AuditLogRead]]:
    return APIResponse(
        data=[
            AuditLogRead.model_validate(log)
            for log in list_audit_logs(
                db,
                limit,
                action=action,
                resource_type=resource_type,
                status=status,
                keyword=keyword,
            )
        ]
    )
