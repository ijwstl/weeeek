from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import ReportRule, ReportSpace
from app.services.bootstrap import DEMO_WORKSPACE
from app.services.reports import (
    PROJECT_A_ID,
    PROJECT_A_REPORT_SPACE_ID,
    PROJECT_REPORT_ID,
    PROJECT_REPORT_REPORT_SPACE_ID,
    REPORT_SPACE_ID,
    ensure_demo_report_seed,
)

WORKSPACE_ID = str(DEMO_WORKSPACE["id"])
REPORT_SPACE_CONFIG_OVERRIDES: dict[str, dict[str, object]] = {}
REPORT_SPACE_ALIASES = {
    "space-dept-backend": REPORT_SPACE_ID,
    "space-project-a": PROJECT_A_REPORT_SPACE_ID,
    "space-project-report": PROJECT_REPORT_REPORT_SPACE_ID,
}
PROJECT_ALIASES = {
    "project-a": PROJECT_A_ID,
    "project-report": PROJECT_REPORT_ID,
}


def make_report_space(
    space_id: str,
    name: str,
    space_type: str,
    department_id: str | None = None,
    project_team_id: str | None = None,
) -> dict[str, object]:
    default_space = {
        "id": space_id,
        "workspace_id": WORKSPACE_ID,
        "space_type": space_type,
        "department_id": department_id,
        "project_team_id": project_team_id,
        "name": name,
        "status": "active",
        "report_enabled": True,
        "report_mode": "weekly",
        "ai_enabled": True,
        "allowed_data_source_types": ["git", "jira", "project_progress", "history"],
        "template_bindings": {
            "weekly": {
                "template_id": "template-weekly-default",
                "version_policy": "latest_published",
            }
        },
        "member_visibility": "private",
    }
    return {**default_space, **REPORT_SPACE_CONFIG_OVERRIDES.get(space_id, {})}


DEMO_DEPARTMENTS = [
    {
        "id": "dept-rd",
        "workspace_id": WORKSPACE_ID,
        "parent_id": None,
        "name": "研发中心",
        "path": "/研发中心",
        "depth": 1,
        "sort_order": 1,
        "status": "active",
    },
    {
        "id": "dept-backend",
        "workspace_id": WORKSPACE_ID,
        "parent_id": "dept-rd",
        "name": "后端研发组",
        "path": "/研发中心/后端研发组",
        "depth": 2,
        "sort_order": 1,
        "status": "active",
    },
    {
        "id": "dept-frontend",
        "workspace_id": WORKSPACE_ID,
        "parent_id": "dept-rd",
        "name": "前端研发组",
        "path": "/研发中心/前端研发组",
        "depth": 2,
        "sort_order": 2,
        "status": "active",
    },
    {
        "id": "dept-qa",
        "workspace_id": WORKSPACE_ID,
        "parent_id": "dept-rd",
        "name": "测试组",
        "path": "/研发中心/测试组",
        "depth": 2,
        "sort_order": 3,
        "status": "active",
    },
]


def department_with_space(department: dict[str, object]) -> dict[str, object]:
    space_id = f"space-{department['id']}"
    return {
        **department,
        "report_space": make_report_space(
            space_id=space_id,
            name=str(department["name"]),
            space_type="department",
            department_id=str(department["id"]),
        ),
    }


def list_departments() -> list[dict[str, object]]:
    return [department_with_space(department) for department in DEMO_DEPARTMENTS]


def build_department_tree() -> list[dict[str, object]]:
    nodes = [
        {**department_with_space(department), "children": []}
        for department in DEMO_DEPARTMENTS
    ]
    by_id = {node["id"]: node for node in nodes}
    roots = []

    for node in nodes:
        parent_id = node["parent_id"]
        if parent_id and parent_id in by_id:
            by_id[parent_id]["children"].append(node)
        else:
            roots.append(node)

    return roots


def get_department(department_id: str) -> dict[str, object] | None:
    return next(
        (
            department_with_space(department)
            for department in DEMO_DEPARTMENTS
            if department["id"] == department_id
        ),
        None,
    )


def resolve_report_space_id(report_space_id: str) -> UUID:
    return REPORT_SPACE_ALIASES.get(report_space_id) or UUID(report_space_id)


def serialize_report_space(space: ReportSpace, alias: str | None = None) -> dict[str, object]:
    project_team_id = None
    if space.project_team_id == PROJECT_A_ID:
        project_team_id = "project-a"
    elif space.project_team_id == PROJECT_REPORT_ID:
        project_team_id = "project-report"
    elif space.project_team_id:
        project_team_id = str(space.project_team_id)

    return {
        "id": alias or str(space.id),
        "workspace_id": str(space.workspace_id),
        "space_type": space.space_type,
        "department_id": "dept-backend"
        if space.department_id == UUID("00000000-0000-0000-0000-000000000301")
        else str(space.department_id)
        if space.department_id
        else None,
        "project_team_id": project_team_id,
        "name": space.name,
        "status": space.status,
        "report_enabled": space.report_enabled,
        "report_mode": space.report_mode,
        "ai_enabled": space.ai_enabled,
        "allowed_data_source_types": space.allowed_data_source_types,
        "template_bindings": space.template_bindings,
        "member_visibility": space.member_visibility,
    }


def serialize_report_rule(
    rule: ReportRule,
    report_space_alias: str | None = None,
) -> dict[str, object]:
    return {
        "id": str(rule.id),
        "workspace_id": str(rule.workspace_id),
        "report_space_id": report_space_alias or str(rule.report_space_id),
        "report_type": rule.report_type,
        "enabled": rule.enabled,
        "frequency": rule.frequency,
        "interval_value": rule.interval_value,
        "week_start_day": rule.week_start_day,
        "reminder_day": rule.reminder_day,
        "reminder_time": rule.reminder_time,
        "due_type": rule.due_type,
        "due_day": rule.due_day,
        "due_time": rule.due_time,
        "skip_weekends": rule.skip_weekends,
        "notification_channels": rule.notification_channels,
        "overdue_policy": rule.overdue_policy,
        "extra_config": rule.extra_config,
    }


def get_report_space(
    report_space_id: str,
    db: Session | None = None,
) -> dict[str, object] | None:
    if db is not None:
        ensure_demo_report_seed(db)
        try:
            resolved_id = resolve_report_space_id(report_space_id)
        except ValueError:
            return None
        space = db.get(ReportSpace, resolved_id)
        return serialize_report_space(space, report_space_id) if space else None

    for department in DEMO_DEPARTMENTS:
        space = department_with_space(department)["report_space"]
        if space["id"] == report_space_id:
            return space
    for project in DEMO_PROJECT_TEAMS:
        space = project_with_space(project)["report_space"]
        if space["id"] == report_space_id:
            return space
    return None


def default_rules_for_space(
    report_space_id: str,
    db: Session | None = None,
) -> list[dict[str, object]]:
    report_space = get_report_space(report_space_id, db)
    report_mode = str(report_space.get("report_mode", "weekly")) if report_space else "weekly"
    default_rules = [
        {
            "id": f"rule-{report_space_id}-daily",
            "workspace_id": WORKSPACE_ID,
            "report_space_id": report_space_id,
            "report_type": "daily",
            "enabled": report_mode in {"daily", "daily_weekly"},
            "frequency": "daily",
            "interval_value": None,
            "week_start_day": None,
            "reminder_day": None,
            "reminder_time": "18:00",
            "due_type": "same_day",
            "due_day": None,
            "due_time": "20:00",
            "skip_weekends": True,
            "notification_channels": ["in_app", "feishu"],
            "overdue_policy": {"notify_once_after_due": True},
            "extra_config": {},
        },
        {
            "id": f"rule-{report_space_id}-weekly",
            "workspace_id": WORKSPACE_ID,
            "report_space_id": report_space_id,
            "report_type": "weekly",
            "enabled": report_mode in {"weekly", "daily_weekly"},
            "frequency": "weekly",
            "interval_value": None,
            "week_start_day": 1,
            "reminder_day": 5,
            "reminder_time": "17:00",
            "due_type": "weekday",
            "due_day": 5,
            "due_time": "19:00",
            "skip_weekends": False,
            "notification_channels": ["in_app", "feishu"],
            "overdue_policy": {"notify_once_after_due": True, "notify_lead": True},
            "extra_config": {},
        },
    ]

    if db is not None and report_space is not None:
        resolved_id = resolve_report_space_id(report_space_id)
        existing_rules = {
            rule.report_type: rule
            for rule in db.scalars(
                select(ReportRule).where(ReportRule.report_space_id == resolved_id)
            ).all()
        }
        created = False
        workspace_id = UUID(str(report_space["workspace_id"]))
        for default_rule in default_rules:
            report_type = str(default_rule["report_type"])
            if report_type not in existing_rules:
                db.add(
                    ReportRule(
                        workspace_id=workspace_id,
                        report_space_id=resolved_id,
                        report_type=report_type,
                        enabled=bool(default_rule["enabled"]),
                        frequency=str(default_rule["frequency"]),
                        interval_value=default_rule["interval_value"],
                        week_start_day=default_rule["week_start_day"],
                        reminder_day=default_rule["reminder_day"],
                        reminder_time=default_rule["reminder_time"],
                        due_type=str(default_rule["due_type"]),
                        due_day=default_rule["due_day"],
                        due_time=default_rule["due_time"],
                        skip_weekends=bool(default_rule["skip_weekends"]),
                        notification_channels=list(default_rule["notification_channels"]),
                        overdue_policy=dict(default_rule["overdue_policy"]),
                        extra_config=dict(default_rule["extra_config"]),
                    )
                )
                created = True
        if created:
            db.commit()

        rules = db.scalars(
            select(ReportRule)
            .where(ReportRule.report_space_id == resolved_id)
            .order_by(ReportRule.report_type.asc())
        ).all()
        mode_enabled = {
            "daily": report_mode in {"daily", "daily_weekly"},
            "weekly": report_mode in {"weekly", "daily_weekly"},
        }
        return [
            {
                **serialize_report_rule(rule, report_space_id),
                "enabled": mode_enabled.get(rule.report_type, rule.enabled),
            }
            for rule in rules
        ]

    return default_rules


def get_report_rule(
    report_space_id: str,
    report_type: str,
    db: Session | None = None,
) -> dict[str, object] | None:
    return next(
        (
            rule
            for rule in default_rules_for_space(report_space_id, db)
            if rule["report_type"] == report_type
        ),
        None,
    )


def update_report_space_config(
    report_space_id: str,
    payload: dict[str, object],
    db: Session | None = None,
) -> dict[str, object] | None:
    current = get_report_space(report_space_id, db)
    if current is None:
        return None

    allowed_keys = {
        "report_enabled",
        "report_mode",
        "ai_enabled",
        "allowed_data_source_types",
        "template_bindings",
        "member_visibility",
    }
    updates = {
        key: value
        for key, value in payload.items()
        if key in allowed_keys and value is not None
    }
    REPORT_SPACE_CONFIG_OVERRIDES[report_space_id] = {
        **REPORT_SPACE_CONFIG_OVERRIDES.get(report_space_id, {}),
        **updates,
    }
    if db is not None:
        resolved_id = resolve_report_space_id(report_space_id)
        space = db.get(ReportSpace, resolved_id)
        if space is None:
            return None
        for key, value in updates.items():
            setattr(space, key, value)
        db.commit()
        db.refresh(space)
        return serialize_report_space(space, report_space_id)

    return get_report_space(report_space_id)


def upsert_report_rule_config(
    report_space_id: str,
    report_type: str,
    payload: dict[str, object],
    db: Session,
) -> dict[str, object] | None:
    report_space = get_report_space(report_space_id, db)
    if report_space is None:
        return None

    resolved_id = resolve_report_space_id(report_space_id)
    rule = db.scalar(
        select(ReportRule).where(
            ReportRule.report_space_id == resolved_id,
            ReportRule.report_type == report_type,
        )
    )
    if rule is None:
        defaults = get_report_rule(report_space_id, report_type, db)
        if defaults is None:
            return None
        rule = ReportRule(
            workspace_id=UUID(str(report_space["workspace_id"])),
            report_space_id=resolved_id,
            report_type=report_type,
            enabled=bool(defaults["enabled"]),
            frequency=str(defaults["frequency"]),
            interval_value=defaults["interval_value"],
            week_start_day=defaults["week_start_day"],
            reminder_day=defaults["reminder_day"],
            reminder_time=defaults["reminder_time"],
            due_type=str(defaults["due_type"]),
            due_day=defaults["due_day"],
            due_time=defaults["due_time"],
            skip_weekends=bool(defaults["skip_weekends"]),
            notification_channels=list(defaults["notification_channels"]),
            overdue_policy=dict(defaults["overdue_policy"]),
            extra_config=dict(defaults["extra_config"]),
        )
        db.add(rule)

    allowed_keys = {
        "enabled",
        "frequency",
        "interval_value",
        "week_start_day",
        "reminder_day",
        "reminder_time",
        "due_type",
        "due_day",
        "due_time",
        "skip_weekends",
        "notification_channels",
        "overdue_policy",
        "extra_config",
    }
    for key, value in payload.items():
        if key in allowed_keys:
            setattr(rule, key, value)

    db.commit()
    db.refresh(rule)
    return serialize_report_rule(rule, report_space_id)


DEMO_PROJECT_TEAMS = [
    {
        "id": "project-a",
        "workspace_id": WORKSPACE_ID,
        "name": "A 项目攻坚",
        "description": "支付链路重构与压测",
        "goal": "提升支付链路稳定性和可观测性",
        "status": "in_progress",
        "start_date": "2026-05-01",
        "expected_end_date": "2026-06-15",
        "actual_end_date": None,
    },
    {
        "id": "project-report",
        "workspace_id": WORKSPACE_ID,
        "name": "报表平台 MVP",
        "description": "日报周报平台第一版",
        "goal": "完成填报闭环和 AI 草稿",
        "status": "at_risk",
        "start_date": "2026-05-20",
        "expected_end_date": "2026-07-01",
        "actual_end_date": None,
    },
]


def project_with_space(project: dict[str, object]) -> dict[str, object]:
    return {
        **project,
        "report_space": make_report_space(
            space_id=f"space-{project['id']}",
            name=str(project["name"]),
            space_type="project",
            project_team_id=str(project["id"]),
        ),
    }
