from fastapi import APIRouter

from app.schemas.common import APIResponse
from app.schemas.identity import MemberCreate, MemberRead, MemberUpdate
from app.services.bootstrap import DEMO_MEMBER

router = APIRouter()


@router.get("", response_model=APIResponse[list[MemberRead]])
def list_members() -> APIResponse[list[MemberRead]]:
    return APIResponse(data=[MemberRead.model_validate(DEMO_MEMBER)])


@router.post("", response_model=APIResponse[MemberRead])
def create_member(payload: MemberCreate) -> APIResponse[MemberRead]:
    member = {
        **DEMO_MEMBER,
        "id": "00000000-0000-0000-0000-000000000202",
        **payload.model_dump(),
        "user_id": "00000000-0000-0000-0000-000000000102",
        "workspace_id": DEMO_MEMBER["workspace_id"],
        "status": "active",
        "avatar_url": None,
    }
    return APIResponse(data=MemberRead.model_validate(member))


@router.get("/{member_id}", response_model=APIResponse[MemberRead])
def get_member(member_id: str) -> APIResponse[MemberRead]:
    member = {**DEMO_MEMBER, "id": member_id}
    return APIResponse(data=MemberRead.model_validate(member))


@router.patch("/{member_id}", response_model=APIResponse[MemberRead])
def update_member(member_id: str, payload: MemberUpdate) -> APIResponse[MemberRead]:
    member = {**DEMO_MEMBER, "id": member_id, **payload.model_dump(exclude_none=True)}
    return APIResponse(data=MemberRead.model_validate(member))


@router.post("/{member_id}/disable", response_model=APIResponse[MemberRead])
def disable_member(member_id: str) -> APIResponse[MemberRead]:
    member = {**DEMO_MEMBER, "id": member_id, "status": "disabled"}
    return APIResponse(data=MemberRead.model_validate(member))


@router.post("/{member_id}/enable", response_model=APIResponse[MemberRead])
def enable_member(member_id: str) -> APIResponse[MemberRead]:
    member = {**DEMO_MEMBER, "id": member_id, "status": "active"}
    return APIResponse(data=MemberRead.model_validate(member))


@router.post("/{member_id}/move-department", response_model=APIResponse[MemberRead])
def move_department(member_id: str, payload: dict[str, str | None]) -> APIResponse[MemberRead]:
    member = {**DEMO_MEMBER, "id": member_id, "department_id": payload.get("department_id")}
    return APIResponse(data=MemberRead.model_validate(member))

