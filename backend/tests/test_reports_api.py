from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_my_report_tasks() -> None:
    response = client.get("/api/v1/reports/my-tasks")
    assert response.status_code == 200
    body = response.json()["data"]
    demo_task = next(item for item in body if item["id"] == "report-weekly-backend-20260525")
    assert demo_task["status"] in {"draft", "submitted"}


def test_get_report_detail_with_draft() -> None:
    response = client.get("/api/v1/reports/report-weekly-backend-20260525")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["instance"]["report_type"] == "weekly"
    assert body["draft"]["content_snapshot"]["groups"][0]["group_id"] == "work_summary"


def test_save_report_draft_persists_in_demo_store() -> None:
    content_snapshot = {
        "template_version_id": "template-weekly-default-v1",
        "groups": [
            {
                "group_id": "work_summary",
                "group_label_snapshot": "工作总结",
                "fields": [
                    {
                        "field_id": "completed_items",
                        "field_label_snapshot": "本周完成事项",
                        "field_type_snapshot": "table",
                        "columns_snapshot": [],
                        "value": [{"title": "新增可编辑草稿保存"}],
                    }
                ],
            }
        ],
    }

    save_response = client.put(
        "/api/v1/reports/report-weekly-backend-20260525/draft",
        json={"content_snapshot": content_snapshot, "ai_generated": False},
    )
    assert save_response.status_code == 200

    detail_response = client.get("/api/v1/reports/report-weekly-backend-20260525")
    assert detail_response.status_code == 200
    body = detail_response.json()["data"]
    value = body["draft"]["content_snapshot"]["groups"][0]["fields"][0]["value"]
    assert value[0]["title"] == "新增可编辑草稿保存"


def test_submit_report() -> None:
    response = client.post(
        "/api/v1/reports/report-weekly-backend-20260525/submit",
        json={"content_snapshot": {"groups": []}, "change_reason": "首次提交"},
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["version_no"] >= 1
    assert body["change_reason"] == "首次提交"


def test_generate_report_instances_from_space_configuration() -> None:
    config_response = client.put(
        "/api/v1/report-spaces/space-dept-backend/config",
        json={
            "report_mode": "daily_weekly",
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
    assert config_response.status_code == 200

    response = client.post(
        "/api/v1/report-spaces/space-dept-backend/generate-instances",
        json={"anchor_date": "2026-06-02"},
    )
    assert response.status_code == 200
    body = response.json()["data"]
    generated = body["created"] + body["existing"]
    assert {item["report_type"] for item in generated} >= {"daily", "weekly"}

    daily = next(item for item in generated if item["report_type"] == "daily")
    detail_response = client.get(f"/api/v1/reports/{daily['id']}")
    assert detail_response.status_code == 200
    draft = detail_response.json()["data"]["draft"]
    field = draft["content_snapshot"]["groups"][0]["fields"][0]
    assert field["field_type_snapshot"] == "table"
    assert field["columns_snapshot"][0]["column_id"] == "title"


def test_generate_ai_draft_from_enabled_data_sources() -> None:
    config_response = client.put(
        "/api/v1/report-spaces/space-dept-backend/config",
        json={
            "report_mode": "daily_weekly",
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
    assert config_response.status_code == 200

    instance_response = client.post(
        "/api/v1/report-spaces/space-dept-backend/generate-instances",
        json={"anchor_date": "2026-06-04"},
    )
    assert instance_response.status_code == 200
    daily = next(
        item
        for item in instance_response.json()["data"]["created"]
        + instance_response.json()["data"]["existing"]
        if item["report_type"] == "daily"
    )

    sources_response = client.get("/api/v1/data-sources")
    assert sources_response.status_code == 200
    enabled_source_ids = [
        source["id"]
        for source in sources_response.json()["data"]
        if source["enabled"] and source["source_type"] in {"gitlab", "github", "jira"}
    ]
    assert enabled_source_ids

    draft_response = client.post(
        f"/api/v1/reports/{daily['id']}/ai-draft",
        json={"data_source_ids": enabled_source_ids[:2], "fill_empty_only": True},
    )
    assert draft_response.status_code == 200
    draft = draft_response.json()["data"]
    assert draft["ai_generated"] is True
    first_field = draft["content_snapshot"]["groups"][0]["fields"][0]
    assert len(first_field["value"]) >= 1
    assert first_field["value"][0]["source"] in {"Git", "Jira"}
