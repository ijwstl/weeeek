from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_department_tree() -> None:
    response = client.get("/api/v1/departments/tree")
    assert response.status_code == 200
    tree = response.json()["data"]
    assert tree[0]["name"] == "研发中心"
    assert tree[0]["children"][0]["report_space"]["space_type"] == "department"


def test_get_department_submission_status() -> None:
    response = client.get("/api/v1/departments/dept-backend/submission-status")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["total_members"] == 24
    assert body["submitted_members"] == 18


def test_list_project_teams() -> None:
    response = client.get("/api/v1/project-teams")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body[0]["report_space"]["space_type"] == "project"


def test_create_and_archive_project_team() -> None:
    create_response = client.post(
        "/api/v1/project-teams",
        json={
            "name": "搜索质量攻坚",
            "description": "优化搜索结果召回和排序",
            "goal": "核心查询成功率提升到 99%",
            "start_date": "2026-06-01",
            "expected_end_date": "2026-07-15",
        },
    )
    assert create_response.status_code == 200
    project = create_response.json()["data"]
    assert project["name"] == "搜索质量攻坚"
    assert project["report_space"]["space_type"] == "project"

    archive_response = client.post(f"/api/v1/project-teams/{project['id']}/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["data"]["status"] == "archived"


def test_project_team_members_support_roles() -> None:
    members_response = client.get("/api/v1/project-teams/available-members")
    assert members_response.status_code == 200
    member_id = members_response.json()["data"][1]["id"]

    add_response = client.post(
        "/api/v1/project-teams/project-a/members",
        json={"member_id": member_id, "role": "project_admin"},
    )
    assert add_response.status_code == 200
    assert add_response.json()["data"]["role"] == "project_admin"

    update_response = client.patch(
        f"/api/v1/project-teams/project-a/members/{member_id}",
        json={"role": "project_member"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["role"] == "project_member"


def test_project_report_space_config_and_generation() -> None:
    config_response = client.put(
        "/api/v1/report-spaces/space-project-a/config",
        json={
            "report_mode": "daily_weekly",
            "member_visibility": "department",
            "ai_enabled": True,
        },
    )
    assert config_response.status_code == 200
    space = config_response.json()["data"]
    assert space["space_type"] == "project"
    assert space["report_mode"] == "daily_weekly"

    generate_response = client.post(
        "/api/v1/report-spaces/space-project-a/generate-instances",
        json={"anchor_date": "2026-06-05"},
    )
    assert generate_response.status_code == 200
    generated_data = generate_response.json()["data"]
    generated = generated_data["created"] + generated_data["existing"]
    assert {item["report_type"] for item in generated} >= {"daily", "weekly"}


def test_list_report_space_rules() -> None:
    response = client.get("/api/v1/report-spaces/space-dept-backend/rules")
    assert response.status_code == 200
    body = response.json()["data"]
    rules = {item["report_type"]: item for item in body}
    assert isinstance(rules["weekly"]["reminder_day"], int)
    assert rules["daily"]["skip_weekends"] is True


def test_report_space_config_supports_daily_and_weekly_mode() -> None:
    response = client.put(
        "/api/v1/report-spaces/space-dept-backend/config",
        json={
            "report_mode": "daily_weekly",
            "member_visibility": "department",
            "template_bindings": {
                "daily": {
                    "template_id": "template-daily-default",
                    "version_policy": "latest_published",
                },
                "weekly": {
                    "template_id": "template-weekly-default",
                    "version_policy": "latest_published",
                },
            },
        },
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["report_mode"] == "daily_weekly"
    assert body["member_visibility"] == "department"
    assert body["template_bindings"]["daily"]["template_id"] == "template-daily-default"
    assert body["template_bindings"]["weekly"]["template_id"] == "template-weekly-default"

    rules_response = client.get("/api/v1/report-spaces/space-dept-backend/rules")
    assert rules_response.status_code == 200
    rules = rules_response.json()["data"]
    assert all(rule["enabled"] for rule in rules)


def test_upsert_report_rule() -> None:
    response = client.put(
        "/api/v1/report-spaces/space-dept-backend/rules/weekly",
        json={
            "enabled": True,
            "frequency": "weekly",
            "week_start_day": 1,
            "reminder_day": 4,
            "reminder_time": "18:00",
            "due_type": "weekday",
            "due_day": 5,
            "due_time": "20:00",
            "skip_weekends": False,
            "notification_channels": ["in_app"],
        },
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["reminder_day"] == 4
    assert body["notification_channels"] == ["in_app"]

    rules_response = client.get("/api/v1/report-spaces/space-dept-backend/rules")
    assert rules_response.status_code == 200
    rules = {rule["report_type"]: rule for rule in rules_response.json()["data"]}
    assert rules["weekly"]["reminder_day"] == 4
    assert rules["weekly"]["due_time"] == "20:00"
