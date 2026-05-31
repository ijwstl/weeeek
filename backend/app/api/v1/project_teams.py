from fastapi import APIRouter, HTTPException, status

from app.audit.decorator import audit_log
from app.schemas.common import APIResponse
from app.schemas.identity import MemberRead
from app.schemas.organization import (
    ProjectTeamCreate,
    ProjectTeamMemberAdd,
    ProjectTeamMemberRead,
    ProjectTeamMemberUpdate,
    ProjectTeamRead,
    ProjectTeamUpdate,
)
from app.services.bootstrap import DEMO_MEMBER
from app.services.organization import DEMO_PROJECT_TEAMS, project_with_space

router = APIRouter()
DEMO_AVAILABLE_MEMBERS = [
    DEMO_MEMBER,
    {
        **DEMO_MEMBER,
        "id": "00000000-0000-0000-0000-000000000202",
        "user_id": "00000000-0000-0000-0000-000000000102",
        "display_name": "李明",
        "email": "liming@example.com",
        "employee_no": "E0002",
    },
    {
        **DEMO_MEMBER,
        "id": "00000000-0000-0000-0000-000000000203",
        "user_id": "00000000-0000-0000-0000-000000000103",
        "display_name": "陈晨",
        "email": "chenchen@example.com",
        "employee_no": "E0003",
    },
]
DEMO_PROJECT_MEMBERS: dict[str, list[dict[str, str]]] = {
    "project-a": [
        {"member_id": DEMO_MEMBER["id"], "role": "project_admin"},
        {"member_id": "00000000-0000-0000-0000-000000000202", "role": "project_member"},
    ],
    "project-report": [
        {"member_id": DEMO_MEMBER["id"], "role": "project_admin"},
        {"member_id": "00000000-0000-0000-0000-000000000203", "role": "project_member"},
    ],
}


def find_project(project_team_id: str) -> dict[str, object] | None:
    return next(
        (
            project_with_space(project)
            for project in DEMO_PROJECT_TEAMS
            if project["id"] == project_team_id
        ),
        None,
    )


def find_raw_project(project_team_id: str) -> dict[str, object] | None:
    return next(
        (
            project
            for project in DEMO_PROJECT_TEAMS
            if project["id"] == project_team_id
        ),
        None,
    )


def find_available_member(member_id: str) -> dict[str, object] | None:
    return next(
        (member for member in DEMO_AVAILABLE_MEMBERS if member["id"] == member_id),
        None,
    )


def serialize_project_member(project_team_id: str, relation: dict[str, str]) -> dict[str, object]:
    member = find_available_member(relation["member_id"]) or DEMO_MEMBER
    return {
        "project_team_id": project_team_id,
        "member_id": relation["member_id"],
        "role": relation["role"],
        "display_name": member["display_name"],
        "email": member["email"],
        "employee_no": member["employee_no"],
        "status": member["status"],
    }


@router.get("", response_model=APIResponse[list[ProjectTeamRead]])
def list_project_teams() -> APIResponse[list[ProjectTeamRead]]:
    return APIResponse(
        data=[
            ProjectTeamRead.model_validate(project_with_space(project))
            for project in DEMO_PROJECT_TEAMS
        ]
    )


@router.post("", response_model=APIResponse[ProjectTeamRead])
@audit_log("project_team.create", "project_team")
def create_project_team(payload: ProjectTeamCreate) -> APIResponse[ProjectTeamRead]:
    project = {
        "id": f"project-{len(DEMO_PROJECT_TEAMS) + 1}",
        "workspace_id": DEMO_MEMBER["workspace_id"],
        "name": payload.name,
        "description": payload.description,
        "goal": payload.goal,
        "status": "not_started",
        "start_date": payload.start_date,
        "expected_end_date": payload.expected_end_date,
        "actual_end_date": None,
    }
    DEMO_PROJECT_TEAMS.append(project)
    return APIResponse(data=ProjectTeamRead.model_validate(project_with_space(project)))


@router.get("/available-members", response_model=APIResponse[list[MemberRead]])
def list_available_project_members() -> APIResponse[list[MemberRead]]:
    return APIResponse(
        data=[MemberRead.model_validate(member) for member in DEMO_AVAILABLE_MEMBERS]
    )


@router.get("/{project_team_id}", response_model=APIResponse[ProjectTeamRead])
def get_project_team(project_team_id: str) -> APIResponse[ProjectTeamRead]:
    project = find_project(project_team_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project team not found")
    return APIResponse(data=ProjectTeamRead.model_validate(project))


@router.patch("/{project_team_id}", response_model=APIResponse[ProjectTeamRead])
@audit_log("project_team.update", "project_team")
def update_project_team(
    project_team_id: str,
    payload: ProjectTeamUpdate,
) -> APIResponse[ProjectTeamRead]:
    project = find_project(project_team_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project team not found")
    raw_project = find_raw_project(project_team_id)
    if raw_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project team not found")
    raw_project.update(payload.model_dump(exclude_none=True))
    return APIResponse(data=ProjectTeamRead.model_validate(project_with_space(raw_project)))


@router.post("/{project_team_id}/archive", response_model=APIResponse[ProjectTeamRead])
@audit_log("project_team.archive", "project_team")
def archive_project_team(project_team_id: str) -> APIResponse[ProjectTeamRead]:
    project = find_project(project_team_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project team not found")
    raw_project = find_raw_project(project_team_id)
    if raw_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project team not found")
    raw_project["status"] = "archived"
    return APIResponse(data=ProjectTeamRead.model_validate(project_with_space(raw_project)))


@router.post("/{project_team_id}/restore", response_model=APIResponse[ProjectTeamRead])
@audit_log("project_team.restore", "project_team")
def restore_project_team(project_team_id: str) -> APIResponse[ProjectTeamRead]:
    project = find_project(project_team_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project team not found")
    raw_project = find_raw_project(project_team_id)
    if raw_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project team not found")
    raw_project["status"] = "in_progress"
    return APIResponse(data=ProjectTeamRead.model_validate(project_with_space(raw_project)))


@router.get("/{project_team_id}/members", response_model=APIResponse[list[ProjectTeamMemberRead]])
def list_project_members(project_team_id: str) -> APIResponse[list[ProjectTeamMemberRead]]:
    if find_project(project_team_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project team not found")
    relations = DEMO_PROJECT_MEMBERS.setdefault(
        project_team_id,
        [{"member_id": DEMO_MEMBER["id"], "role": "project_admin"}],
    )
    return APIResponse(
        data=[
            ProjectTeamMemberRead.model_validate(
                serialize_project_member(project_team_id, relation)
            )
            for relation in relations
        ]
    )


@router.post("/{project_team_id}/members", response_model=APIResponse[ProjectTeamMemberRead])
@audit_log("project_team.member.add", "project_team")
def add_project_member(
    project_team_id: str,
    payload: ProjectTeamMemberAdd,
) -> APIResponse[ProjectTeamMemberRead]:
    if find_project(project_team_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project team not found")
    if find_available_member(payload.member_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

    relations = DEMO_PROJECT_MEMBERS.setdefault(project_team_id, [])
    existing = next(
        (relation for relation in relations if relation["member_id"] == payload.member_id),
        None,
    )
    if existing:
        existing["role"] = payload.role
        relation = existing
    else:
        relation = {"member_id": payload.member_id, "role": payload.role}
        relations.append(relation)
    return APIResponse(
        data=ProjectTeamMemberRead.model_validate(
            serialize_project_member(project_team_id, relation)
        )
    )


@router.patch(
    "/{project_team_id}/members/{member_id}",
    response_model=APIResponse[ProjectTeamMemberRead],
)
@audit_log("project_team.member.update", "project_team")
def update_project_member(
    project_team_id: str,
    member_id: str,
    payload: ProjectTeamMemberUpdate,
) -> APIResponse[ProjectTeamMemberRead]:
    relations = DEMO_PROJECT_MEMBERS.get(project_team_id, [])
    relation = next(
        (item for item in relations if item["member_id"] == member_id),
        None,
    )
    if relation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )
    relation["role"] = payload.role
    return APIResponse(
        data=ProjectTeamMemberRead.model_validate(
            serialize_project_member(project_team_id, relation)
        )
    )


@router.delete(
    "/{project_team_id}/members/{member_id}",
    response_model=APIResponse[dict[str, bool]],
)
@audit_log("project_team.member.remove", "project_team")
def remove_project_member(project_team_id: str, member_id: str) -> APIResponse[dict[str, bool]]:
    relations = DEMO_PROJECT_MEMBERS.get(project_team_id, [])
    DEMO_PROJECT_MEMBERS[project_team_id] = [
        relation for relation in relations if relation["member_id"] != member_id
    ]
    return APIResponse(data={"ok": True})
