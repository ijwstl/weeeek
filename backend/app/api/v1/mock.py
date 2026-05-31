from fastapi import APIRouter

router = APIRouter()


@router.get("/dashboard")
def mock_dashboard() -> dict[str, object]:
    return {
        "workspace": {"name": "研发协作空间"},
        "user": {"display_name": "王启"},
        "tasks": [
            {
                "id": "task-weekly",
                "title": "后端研发组周报",
                "type": "部门周报",
                "due": "周五 19:00",
                "status": "draft",
            },
            {
                "id": "task-project",
                "title": "A 项目进度",
                "type": "项目进度",
                "due": "今天 18:00",
                "status": "pending",
            },
            {
                "id": "task-overdue",
                "title": "接口联调日报",
                "type": "逾期日报",
                "due": "昨天 20:00",
                "status": "overdue",
            },
        ],
        "sources": ["GitLab", "GitHub", "Jira", "项目进度"],
        "submission": {"submitted": 18, "total": 24, "risks": 3},
    }

