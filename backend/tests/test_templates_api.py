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
