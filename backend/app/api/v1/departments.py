from fastapi import APIRouter, HTTPException, status

from app.schemas.common import APIResponse
from app.schemas.identity import MemberRead
from app.schemas.organization import (
    DepartmentCreate,
    DepartmentMemberAdd,
    DepartmentRead,
    DepartmentTreeNode,
    DepartmentUpdate,
    SubmissionStatusRead,
)
from app.services.bootstrap import DEMO_MEMBER
from app.services.organization import build_department_tree as build_tree
from app.services.organization import department_with_space, get_department

router = APIRouter()


@router.get("/tree", response_model=APIResponse[list[DepartmentTreeNode]])
def get_department_tree() -> APIResponse[list[DepartmentTreeNode]]:
    return APIResponse(data=[DepartmentTreeNode.model_validate(node) for node in build_tree()])


@router.post("", response_model=APIResponse[DepartmentRead])
def create_department(payload: DepartmentCreate) -> APIResponse[DepartmentRead]:
    parent = get_department(payload.parent_id) if payload.parent_id else None
    depth = int(parent["depth"]) + 1 if parent else 1
    path = f"{parent['path']}/{payload.name}" if parent else f"/{payload.name}"
    department = {
        "id": f"dept-{payload.name}",
        "workspace_id": DEMO_MEMBER["workspace_id"],
        "parent_id": payload.parent_id,
        "name": payload.name,
        "path": path,
        "depth": depth,
        "sort_order": payload.sort_order,
        "status": "active",
    }
    return APIResponse(data=DepartmentRead.model_validate(department_with_space(department)))


@router.get("/{department_id}", response_model=APIResponse[DepartmentRead])
def get_department_detail(department_id: str) -> APIResponse[DepartmentRead]:
    department = get_department(department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    return APIResponse(data=DepartmentRead.model_validate(department))


@router.patch("/{department_id}", response_model=APIResponse[DepartmentRead])
def update_department(
    department_id: str,
    payload: DepartmentUpdate,
) -> APIResponse[DepartmentRead]:
    department = get_department(department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Department not found")
    updated = {**department, **payload.model_dump(exclude_none=True)}
    return APIResponse(data=DepartmentRead.model_validate(updated))


@router.delete("/{department_id}", response_model=APIResponse[dict[str, bool]])
def delete_department(department_id: str) -> APIResponse[dict[str, bool]]:
    _ = department_id
    return APIResponse(data={"ok": True})


@router.get("/{department_id}/members", response_model=APIResponse[list[MemberRead]])
def list_department_members(department_id: str) -> APIResponse[list[MemberRead]]:
    member = {**DEMO_MEMBER, "department_id": department_id}
    return APIResponse(data=[MemberRead.model_validate(member)])


@router.post("/{department_id}/members", response_model=APIResponse[MemberRead])
def add_department_member(
    department_id: str,
    payload: DepartmentMemberAdd,
) -> APIResponse[MemberRead]:
    member = {**DEMO_MEMBER, "id": payload.member_id, "department_id": department_id}
    return APIResponse(data=MemberRead.model_validate(member))


@router.delete(
    "/{department_id}/members/{member_id}",
    response_model=APIResponse[dict[str, bool]],
)
def remove_department_member(department_id: str, member_id: str) -> APIResponse[dict[str, bool]]:
    _ = (department_id, member_id)
    return APIResponse(data={"ok": True})


@router.get("/{department_id}/submission-status", response_model=APIResponse[SubmissionStatusRead])
def get_submission_status(department_id: str) -> APIResponse[SubmissionStatusRead]:
    return APIResponse(
        data=SubmissionStatusRead(
            report_space_id=f"space-{department_id}",
            total_members=24,
            submitted_members=18,
            pending_members=4,
            overdue_members=2,
        )
    )


@router.get("/{department_id}/summary", response_model=APIResponse[dict[str, object]])
def get_department_summary(department_id: str) -> APIResponse[dict[str, object]]:
    return APIResponse(
        data={
            "department_id": department_id,
            "period": "2026-05-25 至 2026-05-31",
            "submitted": 18,
            "total": 24,
            "risks": 3,
            "blockers": 2,
        }
    )
