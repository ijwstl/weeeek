from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_list_templates() -> None:
    response = client.get("/api/v1/templates")
    assert response.status_code == 200
    body = response.json()["data"]
    assert body[0]["name"] == "研发周报模板"


def test_get_template_draft_contains_table_field() -> None:
    response = client.get("/api/v1/templates/template-weekly-default/draft")
    assert response.status_code == 200
    schema = response.json()["data"]["schema_snapshot"]
    fields = schema["groups"][0]["fields"]
    assert fields[0]["type"] == "table"
    assert fields[0]["config"]["columns"][0]["column_id"] == "title"


def test_validate_template_schema_rejects_nested_table() -> None:
    response = client.post(
        "/api/v1/templates/validate-schema",
        json={
            "groups": [
                {
                    "group_id": "g1",
                    "label": "分组",
                    "fields": [
                        {
                            "field_id": "f1",
                            "label": "明细",
                            "type": "table",
                            "config": {
                                "columns": [
                                    {"column_id": "c1", "label": "嵌套", "type": "table"}
                                ]
                            },
                        }
                    ],
                }
            ]
        },
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["valid"] is False


def test_update_template_draft_persists_select_options() -> None:
    response = client.get("/api/v1/templates/template-weekly-default/draft")
    assert response.status_code == 200
    draft = response.json()["data"]
    schema = draft["schema_snapshot"]
    first_column = schema["groups"][0]["fields"][0]["config"]["columns"][1]
    first_column["config"]["options"] = ["Git", "Jira", "会议纪要", "手动"]

    update_response = client.put(
        "/api/v1/templates/template-weekly-default/draft",
        json={"schema_snapshot": schema},
    )
    assert update_response.status_code == 200

    detail_response = client.get("/api/v1/templates/template-weekly-default/draft")
    assert detail_response.status_code == 200
    updated_schema = detail_response.json()["data"]["schema_snapshot"]
    options = updated_schema["groups"][0]["fields"][0]["config"]["columns"][1]["config"]["options"]
    assert "会议纪要" in options


def test_update_template_draft_supports_markdown_mode() -> None:
    original_response = client.get("/api/v1/templates/template-weekly-default/draft")
    assert original_response.status_code == 200
    original_schema = original_response.json()["data"]["schema_snapshot"]
    schema = {
        "render_mode": "markdown_doc",
        "groups": [],
        "markdown_template": "# 本周工作报告\n\n{{ai:block:weekly_done}}",
        "editor_schema": {"format": "markdown"},
        "ai_blocks": [{"id": "weekly_done", "label": "本周完成"}],
    }

    update_response = client.put(
        "/api/v1/templates/template-weekly-default/draft",
        json={"schema_snapshot": schema},
    )
    assert update_response.status_code == 200
    updated_schema = update_response.json()["data"]["schema_snapshot"]
    assert updated_schema["render_mode"] == "markdown_doc"
    assert "weekly_done" in updated_schema["markdown_template"]

    restore_response = client.put(
        "/api/v1/templates/template-weekly-default/draft",
        json={"schema_snapshot": original_schema},
    )
    assert restore_response.status_code == 200


def test_validate_markdown_template_requires_content() -> None:
    response = client.post(
        "/api/v1/templates/validate-schema",
        json={"render_mode": "markdown_doc", "groups": [], "markdown_template": ""},
    )
    assert response.status_code == 200
    body = response.json()["data"]
    assert body["valid"] is False
