from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.audit import AuditLog
from app.services.bootstrap import DEMO_MEMBER

WORKSPACE_ID = UUID(str(DEMO_MEMBER["workspace_id"]))
MEMBER_ID = UUID(str(DEMO_MEMBER["id"]))

_memory_audit_logs: list[dict[str, object]] = []


def record_audit_log(
    *,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    db: Session | None = None,
    request_method: str | None = None,
    request_path: str | None = None,
    status: str = "success",
    metadata_json: dict[str, object] | None = None,
) -> dict[str, object]:
    payload = {
        "id": str(uuid4()),
        "workspace_id": str(WORKSPACE_ID),
        "actor_member_id": str(MEMBER_ID),
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "request_method": request_method,
        "request_path": request_path,
        "status": status,
        "ip_address": None,
        "user_agent": None,
        "metadata_json": metadata_json or {},
        "created_at": datetime.now().astimezone(),
    }

    if db is None:
        _memory_audit_logs.append(payload)
        return payload

    try:
        audit_log = AuditLog(
            workspace_id=WORKSPACE_ID,
            actor_member_id=MEMBER_ID,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request_method=request_method,
            request_path=request_path,
            status=status,
            ip_address=None,
            user_agent=None,
            metadata_json=metadata_json or {},
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return serialize_audit_log(audit_log)
    except SQLAlchemyError:
        db.rollback()
        _memory_audit_logs.append(payload)
        return payload


def list_audit_logs(
    db: Session | None = None,
    limit: int = 50,
    action: str | None = None,
    resource_type: str | None = None,
    status: str | None = None,
    keyword: str | None = None,
) -> list[dict[str, object]]:
    if db is None:
        logs = sorted(
            _memory_audit_logs,
            key=lambda item: item["created_at"],
            reverse=True,
        )
        return filter_serialized_logs(logs, action, resource_type, status, keyword)[:limit]

    try:
        statement = select(AuditLog)
        if action:
            statement = statement.where(AuditLog.action == action)
        if resource_type:
            statement = statement.where(AuditLog.resource_type == resource_type)
        if status:
            statement = statement.where(AuditLog.status == status)
        if keyword:
            pattern = f"%{keyword}%"
            statement = statement.where(
                or_(
                    AuditLog.action.ilike(pattern),
                    AuditLog.resource_type.ilike(pattern),
                    AuditLog.resource_id.ilike(pattern),
                    AuditLog.request_path.ilike(pattern),
                )
            )
        rows = db.scalars(statement.order_by(AuditLog.created_at.desc()).limit(limit)).all()
        logs = [serialize_audit_log(row) for row in rows]
        logs.extend(
            filter_serialized_logs(_memory_audit_logs, action, resource_type, status, keyword)
        )
        return sorted(logs, key=lambda item: item["created_at"], reverse=True)[:limit]
    except SQLAlchemyError:
        db.rollback()
        return list_audit_logs(None, limit, action, resource_type, status, keyword)


def serialize_audit_log(audit_log: AuditLog) -> dict[str, object]:
    return {
        "id": str(audit_log.id),
        "workspace_id": str(audit_log.workspace_id),
        "actor_member_id": str(audit_log.actor_member_id)
        if audit_log.actor_member_id
        else None,
        "action": audit_log.action,
        "resource_type": audit_log.resource_type,
        "resource_id": audit_log.resource_id,
        "request_method": audit_log.request_method,
        "request_path": audit_log.request_path,
        "status": audit_log.status,
        "ip_address": audit_log.ip_address,
        "user_agent": audit_log.user_agent,
        "metadata_json": audit_log.metadata_json,
        "created_at": audit_log.created_at,
    }


def filter_serialized_logs(
    logs: list[dict[str, object]],
    action: str | None,
    resource_type: str | None,
    status: str | None,
    keyword: str | None,
) -> list[dict[str, object]]:
    filtered = logs
    if action:
        filtered = [log for log in filtered if log["action"] == action]
    if resource_type:
        filtered = [log for log in filtered if log["resource_type"] == resource_type]
    if status:
        filtered = [log for log in filtered if log["status"] == status]
    if keyword:
        lowered_keyword = keyword.lower()
        filtered = [
            log
            for log in filtered
            if any(
                lowered_keyword in str(log.get(key) or "").lower()
                for key in ["action", "resource_type", "resource_id", "request_path"]
            )
        ]
    return filtered
