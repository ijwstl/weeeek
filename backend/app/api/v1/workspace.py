from fastapi import APIRouter

from app.schemas.common import APIResponse
from app.schemas.identity import WorkspaceRead, WorkspaceUpdate
from app.services.bootstrap import DEMO_WORKSPACE

router = APIRouter()


@router.get("", response_model=APIResponse[WorkspaceRead])
def get_workspace() -> APIResponse[WorkspaceRead]:
    return APIResponse(data=WorkspaceRead.model_validate(DEMO_WORKSPACE))


@router.patch("", response_model=APIResponse[WorkspaceRead])
def update_workspace(payload: WorkspaceUpdate) -> APIResponse[WorkspaceRead]:
    updated = {**DEMO_WORKSPACE, **payload.model_dump(exclude_none=True)}
    return APIResponse(data=WorkspaceRead.model_validate(updated))


@router.get("/security-settings", response_model=APIResponse[dict[str, object]])
def get_security_settings() -> APIResponse[dict[str, object]]:
    return APIResponse(
        data={
            "workspace_admin_can_view_all_submitted_reports": False,
            "audit_enabled": True,
            "private_deployment_single_workspace": True,
        }
    )


@router.patch("/security-settings", response_model=APIResponse[dict[str, object]])
def update_security_settings(payload: dict[str, object]) -> APIResponse[dict[str, object]]:
    return APIResponse(data=payload)

