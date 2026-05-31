from fastapi import APIRouter

from app.api.v1 import (
    audit,
    auth,
    data_sources,
    departments,
    health,
    members,
    mock,
    notifications,
    project_teams,
    rbac,
    report_spaces,
    reports,
    templates,
    workspace,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(data_sources.router, prefix="/data-sources", tags=["data-sources"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
api_router.include_router(members.router, prefix="/members", tags=["members"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(project_teams.router, prefix="/project-teams", tags=["project-teams"])
api_router.include_router(report_spaces.router, prefix="/report-spaces", tags=["report-spaces"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(templates.router, prefix="/templates", tags=["templates"])
api_router.include_router(rbac.router, tags=["rbac"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(mock.router, prefix="/mock", tags=["mock"])
