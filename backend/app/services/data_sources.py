from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.data_source import DataSourceConnection
from app.services.bootstrap import DEMO_MEMBER
from app.services.reports import ensure_demo_report_seed

WORKSPACE_ID = UUID(str(DEMO_MEMBER["workspace_id"]))
MEMBER_ID = UUID(str(DEMO_MEMBER["id"]))


def ensure_demo_data_sources(db: Session) -> None:
    ensure_demo_report_seed(db)
    existing = db.scalar(
        select(DataSourceConnection).where(DataSourceConnection.member_id == MEMBER_ID).limit(1)
    )
    if existing is not None:
        return

    db.add_all(
        [
            DataSourceConnection(
                workspace_id=WORKSPACE_ID,
                member_id=MEMBER_ID,
                source_type="gitlab",
                name="GitLab",
                account_name="wangqi@gitlab.local",
                status="connected",
                enabled=True,
                scope_config={
                    "repositories": ["weeeek/backend", "ai-report/service"],
                    "permissions": ["commits:read", "merge_requests:read", "pipelines:read"],
                },
                last_sync_at=datetime.now().astimezone(),
            ),
            DataSourceConnection(
                workspace_id=WORKSPACE_ID,
                member_id=MEMBER_ID,
                source_type="github",
                name="GitHub",
                account_name="wangqi",
                status="connected",
                enabled=True,
                scope_config={
                    "repositories": ["AIProject/weeeek"],
                    "permissions": ["repo:read", "pull_requests:read", "issues:read"],
                },
                last_sync_at=datetime.now().astimezone(),
            ),
            DataSourceConnection(
                workspace_id=WORKSPACE_ID,
                member_id=MEMBER_ID,
                source_type="jira",
                name="Jira",
                account_name="wangqi@jira.local",
                status="needs_refresh",
                enabled=True,
                scope_config={
                    "projects": ["WEEK", "INFRA"],
                    "permissions": ["issues:read", "comments:read", "projects:read"],
                },
                last_sync_at=datetime.now().astimezone(),
            ),
        ]
    )
    db.commit()


def serialize_connection(connection: DataSourceConnection) -> dict[str, object]:
    return {
        "id": str(connection.id),
        "workspace_id": str(connection.workspace_id),
        "member_id": str(connection.member_id),
        "source_type": connection.source_type,
        "name": connection.name,
        "account_name": connection.account_name,
        "status": connection.status,
        "enabled": connection.enabled,
        "scope_config": connection.scope_config,
        "last_sync_at": connection.last_sync_at,
    }


def list_connections(db: Session) -> list[dict[str, object]]:
    ensure_demo_data_sources(db)
    connections = db.scalars(
        select(DataSourceConnection)
        .where(DataSourceConnection.member_id == MEMBER_ID)
        .order_by(DataSourceConnection.created_at.asc())
    ).all()
    return [serialize_connection(connection) for connection in connections]


def create_connection(payload: dict[str, object], db: Session) -> dict[str, object]:
    ensure_demo_data_sources(db)
    connection = DataSourceConnection(
        workspace_id=WORKSPACE_ID,
        member_id=MEMBER_ID,
        source_type=str(payload["source_type"]),
        name=str(payload["name"]),
        account_name=str(payload["account_name"]),
        status="connected",
        enabled=True,
        scope_config=dict(payload.get("scope_config") or {}),
        auth_config_encrypted={},
        last_sync_at=datetime.now().astimezone(),
    )
    db.add(connection)
    db.commit()
    db.refresh(connection)
    return serialize_connection(connection)


def update_connection(
    connection_id: str,
    payload: dict[str, object],
    db: Session,
) -> dict[str, object] | None:
    ensure_demo_data_sources(db)
    connection = db.get(DataSourceConnection, UUID(connection_id))
    if connection is None or connection.member_id != MEMBER_ID:
        return None

    for key in ["name", "account_name", "enabled", "status", "scope_config"]:
        if key in payload and payload[key] is not None:
            setattr(connection, key, payload[key])
    db.commit()
    db.refresh(connection)
    return serialize_connection(connection)


def test_connection(connection_id: str, db: Session) -> dict[str, object] | None:
    connection = db.get(DataSourceConnection, UUID(connection_id))
    if connection is None or connection.member_id != MEMBER_ID:
        return None
    return {
        "ok": connection.enabled,
        "status": "connected" if connection.enabled else "disabled",
        "checked_at": datetime.now().astimezone(),
    }
