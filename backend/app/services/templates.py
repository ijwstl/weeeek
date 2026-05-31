from app.schemas.template import TemplateSchema
from app.services.bootstrap import DEMO_MEMBER

WORKSPACE_ID = str(DEMO_MEMBER["workspace_id"])
MEMBER_ID = str(DEMO_MEMBER["id"])


DEFAULT_WEEKLY_SCHEMA = {
    "groups": [
        {
            "group_id": "work_summary",
            "label": "工作总结",
            "description": "本周期主要产出",
            "sort_order": 1,
            "fields": [
                {
                    "field_id": "completed_items",
                    "label": "本周完成事项",
                    "type": "table",
                    "required": True,
                    "summary_enabled": True,
                    "ai_supported": True,
                    "sort_order": 1,
                    "config": {
                        "min_rows": 1,
                        "columns": [
                            {
                                "column_id": "title",
                                "label": "事项",
                                "type": "text",
                                "required": True,
                            },
                            {
                                "column_id": "source",
                                "label": "来源",
                                "type": "single_select",
                                "required": False,
                                "config": {"options": ["Git", "Jira", "项目进度", "手动"]},
                            },
                            {
                                "column_id": "status",
                                "label": "状态",
                                "type": "single_select",
                                "required": True,
                                "config": {"options": ["已完成", "进行中", "延期"]},
                            },
                            {
                                "column_id": "description",
                                "label": "说明",
                                "type": "textarea",
                                "required": False,
                            },
                        ],
                    },
                }
            ],
        },
        {
            "group_id": "risk_plan",
            "label": "风险与计划",
            "description": "",
            "sort_order": 2,
            "fields": [
                {
                    "field_id": "risks",
                    "label": "风险与阻塞",
                    "type": "table",
                    "required": False,
                    "summary_enabled": True,
                    "ai_supported": True,
                    "sort_order": 1,
                    "config": {
                        "columns": [
                            {
                                "column_id": "risk",
                                "label": "风险",
                                "type": "text",
                                "required": True,
                            },
                            {
                                "column_id": "level",
                                "label": "等级",
                                "type": "risk_level",
                                "required": True,
                            },
                            {
                                "column_id": "need_help",
                                "label": "需要协助",
                                "type": "textarea",
                                "required": False,
                            },
                        ]
                    },
                },
                {
                    "field_id": "next_plan",
                    "label": "下周计划",
                    "type": "table",
                    "required": True,
                    "summary_enabled": True,
                    "ai_supported": True,
                    "sort_order": 2,
                    "config": {
                        "columns": [
                            {
                                "column_id": "title",
                                "label": "计划事项",
                                "type": "text",
                                "required": True,
                            },
                            {
                                "column_id": "priority",
                                "label": "优先级",
                                "type": "single_select",
                                "required": False,
                                "config": {"options": ["高", "中", "低"]},
                            },
                        ]
                    },
                },
            ],
        },
    ]
}

DEMO_TEMPLATES = [
    {
        "id": "template-weekly-default",
        "workspace_id": WORKSPACE_ID,
        "name": "研发周报模板",
        "template_scope": "department",
        "description": "默认研发团队周报模板",
        "status": "active",
        "created_by_member_id": MEMBER_ID,
    },
    {
        "id": "template-daily-default",
        "workspace_id": WORKSPACE_ID,
        "name": "研发日报模板",
        "template_scope": "department",
        "description": "默认研发团队日报模板",
        "status": "active",
        "created_by_member_id": MEMBER_ID,
    }
]

DEMO_TEMPLATE_VERSIONS = [
    {
        "id": "template-weekly-default-v1",
        "workspace_id": WORKSPACE_ID,
        "template_id": "template-weekly-default",
        "version_no": 1,
        "status": "published",
        "schema_snapshot": TemplateSchema.model_validate(DEFAULT_WEEKLY_SCHEMA),
        "published_by_member_id": MEMBER_ID,
        "published_at": "2026-05-30T00:00:00+08:00",
    },
    {
        "id": "template-weekly-default-draft",
        "workspace_id": WORKSPACE_ID,
        "template_id": "template-weekly-default",
        "version_no": 2,
        "status": "draft",
        "schema_snapshot": TemplateSchema.model_validate(DEFAULT_WEEKLY_SCHEMA),
        "published_by_member_id": None,
        "published_at": None,
    },
    {
        "id": "template-daily-default-v1",
        "workspace_id": WORKSPACE_ID,
        "template_id": "template-daily-default",
        "version_no": 1,
        "status": "published",
        "schema_snapshot": TemplateSchema.model_validate(DEFAULT_WEEKLY_SCHEMA),
        "published_by_member_id": MEMBER_ID,
        "published_at": "2026-05-30T00:00:00+08:00",
    },
    {
        "id": "template-daily-default-draft",
        "workspace_id": WORKSPACE_ID,
        "template_id": "template-daily-default",
        "version_no": 2,
        "status": "draft",
        "schema_snapshot": TemplateSchema.model_validate(DEFAULT_WEEKLY_SCHEMA),
        "published_by_member_id": None,
        "published_at": None,
    },
]


def list_templates() -> list[dict[str, object]]:
    return DEMO_TEMPLATES


def get_template(template_id: str) -> dict[str, object] | None:
    return next((template for template in DEMO_TEMPLATES if template["id"] == template_id), None)


def list_versions(template_id: str) -> list[dict[str, object]]:
    return [
        version for version in DEMO_TEMPLATE_VERSIONS if version["template_id"] == template_id
    ]


def get_version(version_id: str) -> dict[str, object] | None:
    return next(
        (version for version in DEMO_TEMPLATE_VERSIONS if version["id"] == version_id),
        None,
    )


def get_draft(template_id: str) -> dict[str, object] | None:
    return next(
        (
            version
            for version in DEMO_TEMPLATE_VERSIONS
            if version["template_id"] == template_id and version["status"] == "draft"
        ),
        None,
    )


def update_draft(template_id: str, schema_snapshot: TemplateSchema) -> dict[str, object] | None:
    draft = get_draft(template_id)
    if draft is None:
        return None
    draft["schema_snapshot"] = schema_snapshot
    return draft


def publish_draft(template_id: str) -> dict[str, object] | None:
    draft = get_draft(template_id)
    if draft is None:
        return None

    published = {
        **draft,
        "id": f"{template_id}-v{draft['version_no']}",
        "status": "published",
        "published_by_member_id": MEMBER_ID,
        "published_at": "2026-05-30T00:00:00+08:00",
    }
    DEMO_TEMPLATE_VERSIONS.append(published)
    draft["version_no"] = int(draft["version_no"]) + 1
    draft["id"] = f"{template_id}-draft"
    return published
