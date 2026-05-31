from copy import deepcopy
from datetime import date, datetime, time, timedelta
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.data_source import DataSourceConnection
from app.models.identity import Member, User, Workspace
from app.models.organization import Department, ProjectTeam, ReportRule, ReportSpace
from app.models.report import ReportDraft, ReportInstance, ReportSubmission
from app.services.bootstrap import DEMO_MEMBER
from app.services.templates import DEFAULT_WEEKLY_SCHEMA, get_version, list_versions

WORKSPACE_ID = str(DEMO_MEMBER["workspace_id"])
MEMBER_ID = str(DEMO_MEMBER["id"])
USER_ID = str(DEMO_MEMBER["user_id"])
REPORT_ALIAS = "report-weekly-backend-20260525"
REPORT_INSTANCE_ID = UUID("00000000-0000-0000-0000-000000000601")
REPORT_DRAFT_ID = UUID("00000000-0000-0000-0000-000000000701")
DEPARTMENT_ID = UUID("00000000-0000-0000-0000-000000000301")
REPORT_SPACE_ID = UUID("00000000-0000-0000-0000-000000000401")
PROJECT_A_ID = UUID("00000000-0000-0000-0000-000000000801")
PROJECT_REPORT_ID = UUID("00000000-0000-0000-0000-000000000802")
PROJECT_A_REPORT_SPACE_ID = UUID("00000000-0000-0000-0000-000000000811")
PROJECT_REPORT_REPORT_SPACE_ID = UUID("00000000-0000-0000-0000-000000000812")
TEMPLATE_ID = UUID("00000000-0000-0000-0000-000000000501")
TEMPLATE_VERSION_ID = UUID("00000000-0000-0000-0000-000000000502")
DAILY_TEMPLATE_ID = UUID("00000000-0000-0000-0000-000000000503")
DAILY_TEMPLATE_VERSION_ID = UUID("00000000-0000-0000-0000-000000000504")
TEMPLATE_ALIAS_TO_UUID = {
    "template-weekly-default": TEMPLATE_ID,
    "template-weekly-default-v1": TEMPLATE_VERSION_ID,
    "template-daily-default": DAILY_TEMPLATE_ID,
    "template-daily-default-v1": DAILY_TEMPLATE_VERSION_ID,
}
TEMPLATE_UUID_TO_ALIAS = {value: key for key, value in TEMPLATE_ALIAS_TO_UUID.items()}


def default_report_content() -> dict[str, object]:
    completed_columns = DEFAULT_WEEKLY_SCHEMA["groups"][0]["fields"][0]["config"]["columns"]
    risk_columns = DEFAULT_WEEKLY_SCHEMA["groups"][1]["fields"][0]["config"]["columns"]
    plan_columns = DEFAULT_WEEKLY_SCHEMA["groups"][1]["fields"][1]["config"]["columns"]

    return {
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
                        "columns_snapshot": completed_columns,
                        "value": [
                            {
                                "title": "完成登录模块重构",
                                "source": "Git",
                                "status": "已完成",
                                "description": "拆分认证中间件和会话刷新逻辑。",
                            },
                            {
                                "title": "接入 Jira 周报数据源设计",
                                "source": "Jira",
                                "status": "进行中",
                                "description": "完成字段映射和抓取范围定义。",
                            },
                        ],
                    }
                ],
            },
            {
                "group_id": "risk_plan",
                "group_label_snapshot": "风险与计划",
                "fields": [
                    {
                        "field_id": "risks",
                        "field_label_snapshot": "风险与阻塞",
                        "field_type_snapshot": "table",
                        "columns_snapshot": risk_columns,
                        "value": [
                            {
                                "risk": "Jira OAuth 刷新策略待确认",
                                "level": "medium",
                                "need_help": "需要确认企业 Jira 的授权方式。",
                            }
                        ],
                    },
                    {
                        "field_id": "next_plan",
                        "field_label_snapshot": "下周计划",
                        "field_type_snapshot": "table",
                        "columns_snapshot": plan_columns,
                        "value": [
                            {"title": "完成 ReportRule 编辑接口", "priority": "高"},
                            {"title": "实现报告提交版本记录", "priority": "高"},
                        ],
                    },
                ],
            },
        ],
    }


def resolve_template_id(template_id: str | None) -> UUID | None:
    if not template_id:
        return None
    return TEMPLATE_ALIAS_TO_UUID.get(template_id) or UUID(template_id)


def serialize_template_id(template_id: UUID | None) -> str | None:
    if template_id is None:
        return None
    return TEMPLATE_UUID_TO_ALIAS.get(template_id, str(template_id))


def latest_published_version(template_id: str) -> dict[str, object] | None:
    published_versions = [
        version for version in list_versions(template_id) if version["status"] == "published"
    ]
    return max(published_versions, key=lambda version: int(version["version_no"]), default=None)


def template_schema_to_content_snapshot(version: dict[str, object]) -> dict[str, object]:
    schema = version["schema_snapshot"]
    schema_data = schema.model_dump() if hasattr(schema, "model_dump") else schema
    groups = []
    for group in schema_data["groups"]:
        fields = []
        for field in group["fields"]:
            field_type = field["type"]
            columns = field.get("config", {}).get("columns", []) if field_type == "table" else None
            fields.append(
                {
                    "field_id": field["field_id"],
                    "field_label_snapshot": field["label"],
                    "field_type_snapshot": field_type,
                    "columns_snapshot": columns,
                    "value": [] if field_type == "table" else "",
                }
            )
        groups.append(
            {
                "group_id": group["group_id"],
                "group_label_snapshot": group["label"],
                "fields": fields,
            }
        )
    return {"template_version_id": version["id"], "groups": groups}


DEMO_REPORT_INSTANCE = {
    "id": REPORT_ALIAS,
    "workspace_id": WORKSPACE_ID,
    "report_space_id": "space-dept-backend",
    "report_type": "weekly",
    "assignee_member_id": MEMBER_ID,
    "period_start": date(2026, 5, 25),
    "period_end": date(2026, 5, 31),
    "due_at": datetime.fromisoformat("2026-05-29T19:00:00+08:00"),
    "status": "draft",
    "template_id": "template-weekly-default",
    "template_version_id": "template-weekly-default-v1",
    "submitted_at": None,
    "submitted_late": False,
}

DEMO_REPORT_DRAFT = {
    "id": "draft-report-weekly-backend-20260525",
    "workspace_id": WORKSPACE_ID,
    "report_instance_id": DEMO_REPORT_INSTANCE["id"],
    "member_id": MEMBER_ID,
    "content_snapshot": default_report_content(),
    "ai_generated": True,
}

_demo_report_instance = deepcopy(DEMO_REPORT_INSTANCE)
_demo_report_draft = deepcopy(DEMO_REPORT_DRAFT)
_demo_submissions: list[dict[str, object]] = []


def ensure_demo_report_seed(db: Session) -> None:
    workspace_id = UUID(WORKSPACE_ID)
    user_id = UUID(USER_ID)
    member_id = UUID(MEMBER_ID)

    if db.get(Workspace, workspace_id) is None:
        db.add(
            Workspace(
                id=workspace_id,
                name="研发协作空间",
                slug="engineering",
                deployment_mode="private",
                default_locale="zh-CN",
                timezone="Asia/Shanghai",
                department_max_depth=5,
                status="active",
            )
        )

    if db.get(User, user_id) is None:
        db.add(
            User(
                id=user_id,
                display_name=str(DEMO_MEMBER["display_name"]),
                email=str(DEMO_MEMBER["email"]),
                avatar_url=None,
                status="active",
            )
        )

    if db.get(Department, DEPARTMENT_ID) is None:
        db.add(
            Department(
                id=DEPARTMENT_ID,
                workspace_id=workspace_id,
                parent_id=None,
                name="后端研发组",
                path="/研发中心/后端研发组",
                depth=2,
                sort_order=1,
                status="active",
            )
        )

    if db.get(Member, member_id) is None:
        db.add(
            Member(
                id=member_id,
                workspace_id=workspace_id,
                user_id=user_id,
                department_id=DEPARTMENT_ID,
                display_name=str(DEMO_MEMBER["display_name"]),
                email=str(DEMO_MEMBER["email"]),
                employee_no=str(DEMO_MEMBER["employee_no"]),
                avatar_url=None,
                status="active",
            )
        )

    if db.get(ReportSpace, REPORT_SPACE_ID) is None:
        db.add(
            ReportSpace(
                id=REPORT_SPACE_ID,
                workspace_id=workspace_id,
                space_type="department",
                department_id=DEPARTMENT_ID,
                project_team_id=None,
                name="后端研发组",
                status="active",
                report_enabled=True,
                report_mode="weekly",
                ai_enabled=True,
                allowed_data_source_types=["git", "jira", "project_progress", "history"],
                template_bindings={
                    "weekly": {
                        "template_id": "template-weekly-default",
                        "version_policy": "latest_published",
                    }
                },
                member_visibility="private",
            )
        )
    if db.get(ProjectTeam, PROJECT_A_ID) is None:
        db.add(
            ProjectTeam(
                id=PROJECT_A_ID,
                workspace_id=workspace_id,
                name="A 项目攻坚",
                description="支付链路重构与压测",
                goal="提升支付链路稳定性和可观测性",
                status="in_progress",
                start_date=date(2026, 5, 1),
                expected_end_date=date(2026, 6, 15),
                actual_end_date=None,
                created_by_member_id=member_id,
            )
        )
    if db.get(ProjectTeam, PROJECT_REPORT_ID) is None:
        db.add(
            ProjectTeam(
                id=PROJECT_REPORT_ID,
                workspace_id=workspace_id,
                name="报表平台 MVP",
                description="日报周报平台第一版",
                goal="完成填报闭环和 AI 草稿",
                status="at_risk",
                start_date=date(2026, 5, 20),
                expected_end_date=date(2026, 7, 1),
                actual_end_date=None,
                created_by_member_id=member_id,
            )
        )
    db.flush()

    for space_id, project_id, name in [
        (PROJECT_A_REPORT_SPACE_ID, PROJECT_A_ID, "A 项目攻坚"),
        (PROJECT_REPORT_REPORT_SPACE_ID, PROJECT_REPORT_ID, "报表平台 MVP"),
    ]:
        if db.get(ReportSpace, space_id) is None:
            db.add(
                ReportSpace(
                    id=space_id,
                    workspace_id=workspace_id,
                    space_type="project",
                    department_id=None,
                    project_team_id=project_id,
                    name=name,
                    status="active",
                    report_enabled=True,
                    report_mode="weekly",
                    ai_enabled=True,
                    allowed_data_source_types=["git", "jira", "project_progress", "history"],
                    template_bindings={
                        "weekly": {
                            "template_id": "template-weekly-default",
                            "version_policy": "latest_published",
                        }
                    },
                    member_visibility="private",
                )
            )
    db.flush()

    if db.get(ReportInstance, REPORT_INSTANCE_ID) is None:
        db.add(
            ReportInstance(
                id=REPORT_INSTANCE_ID,
                workspace_id=workspace_id,
                report_space_id=REPORT_SPACE_ID,
                report_type="weekly",
                assignee_member_id=member_id,
                period_start=date(2026, 5, 25),
                period_end=date(2026, 5, 31),
                due_at=datetime.fromisoformat("2026-05-29T19:00:00+08:00"),
                status="draft",
                template_id=TEMPLATE_ID,
                template_version_id=TEMPLATE_VERSION_ID,
                submitted_at=None,
                submitted_late=False,
            )
        )
    db.flush()

    if db.get(ReportDraft, REPORT_DRAFT_ID) is None:
        db.add(
            ReportDraft(
                id=REPORT_DRAFT_ID,
                workspace_id=workspace_id,
                report_instance_id=REPORT_INSTANCE_ID,
                member_id=member_id,
                content_snapshot=default_report_content(),
                ai_generated=True,
            )
        )
        instance = db.get(ReportInstance, REPORT_INSTANCE_ID)
        if instance:
            instance.latest_draft_id = REPORT_DRAFT_ID

    db.commit()


def serialize_report_instance(instance: ReportInstance) -> dict[str, object]:
    report_id = REPORT_ALIAS if instance.id == REPORT_INSTANCE_ID else str(instance.id)
    return {
        "id": report_id,
        "workspace_id": str(instance.workspace_id),
        "report_space_id": str(instance.report_space_id),
        "report_type": instance.report_type,
        "assignee_member_id": str(instance.assignee_member_id),
        "period_start": instance.period_start,
        "period_end": instance.period_end,
        "due_at": instance.due_at,
        "status": instance.status,
        "template_id": serialize_template_id(instance.template_id),
        "template_version_id": serialize_template_id(instance.template_version_id),
        "submitted_at": instance.submitted_at,
        "submitted_late": instance.submitted_late,
    }


def serialize_report_draft(draft: ReportDraft) -> dict[str, object]:
    return {
        "id": str(draft.id),
        "workspace_id": str(draft.workspace_id),
        "report_instance_id": REPORT_ALIAS
        if draft.report_instance_id == REPORT_INSTANCE_ID
        else str(draft.report_instance_id),
        "member_id": str(draft.member_id),
        "content_snapshot": draft.content_snapshot,
        "ai_generated": draft.ai_generated,
    }


def serialize_report_submission(submission: ReportSubmission) -> dict[str, object]:
    return {
        "id": str(submission.id),
        "workspace_id": str(submission.workspace_id),
        "report_instance_id": REPORT_ALIAS
        if submission.report_instance_id == REPORT_INSTANCE_ID
        else str(submission.report_instance_id),
        "member_id": str(submission.member_id),
        "version_no": submission.version_no,
        "content_snapshot": submission.content_snapshot,
        "change_reason": submission.change_reason,
        "submitted_at": submission.submitted_at,
    }


def resolve_report_instance_id(report_instance_id: str) -> UUID:
    if report_instance_id == REPORT_ALIAS:
        return REPORT_INSTANCE_ID
    return UUID(report_instance_id)


def list_my_tasks(db: Session | None = None) -> list[dict[str, object]]:
    if db is not None:
        ensure_demo_report_seed(db)
        instances = db.scalars(
            select(ReportInstance)
            .where(ReportInstance.assignee_member_id == UUID(MEMBER_ID))
            .order_by(ReportInstance.period_start.desc())
        ).all()
        return [serialize_report_instance(instance) for instance in instances]

    return [
        _demo_report_instance,
        {
            **DEMO_REPORT_INSTANCE,
            "id": "report-project-a-20260530",
            "report_space_id": "space-project-a",
            "report_type": "daily",
            "period_start": date(2026, 5, 30),
            "period_end": date(2026, 5, 30),
            "status": "pending",
        },
    ]


def get_report_instance(
    report_instance_id: str,
    db: Session | None = None,
) -> dict[str, object] | None:
    if db is not None:
        ensure_demo_report_seed(db)
        try:
            instance_id = resolve_report_instance_id(report_instance_id)
        except ValueError:
            return None
        instance = db.get(ReportInstance, instance_id)
        return serialize_report_instance(instance) if instance else None

    return next(
        (task for task in list_my_tasks() if task["id"] == report_instance_id),
        None,
    )


def get_report_draft(
    report_instance_id: str,
    db: Session | None = None,
) -> dict[str, object] | None:
    if db is not None:
        ensure_demo_report_seed(db)
        try:
            instance_id = resolve_report_instance_id(report_instance_id)
        except ValueError:
            return None
        draft = db.scalar(
            select(ReportDraft)
            .where(ReportDraft.report_instance_id == instance_id)
            .order_by(ReportDraft.updated_at.desc())
            .limit(1)
        )
        return serialize_report_draft(draft) if draft else None

    if report_instance_id != DEMO_REPORT_INSTANCE["id"]:
        return None
    return _demo_report_draft


def save_report_draft(
    report_instance_id: str,
    content_snapshot: dict[str, object],
    ai_generated: bool,
    db: Session | None = None,
) -> dict[str, object]:
    if db is not None:
        ensure_demo_report_seed(db)
        instance_id = resolve_report_instance_id(report_instance_id)
        instance = db.get(ReportInstance, instance_id)
        if instance is None:
            raise ValueError("Report not found")

        draft = db.scalar(
            select(ReportDraft)
            .where(ReportDraft.report_instance_id == instance_id)
            .order_by(ReportDraft.updated_at.desc())
            .limit(1)
        )
        if draft is None:
            draft = ReportDraft(
                workspace_id=instance.workspace_id,
                report_instance_id=instance.id,
                member_id=instance.assignee_member_id,
                content_snapshot=deepcopy(content_snapshot),
                ai_generated=ai_generated,
            )
            db.add(draft)
            db.flush()
        else:
            draft.content_snapshot = deepcopy(content_snapshot)
            draft.ai_generated = ai_generated

        instance.status = "draft"
        instance.latest_draft_id = draft.id
        db.commit()
        db.refresh(draft)
        return serialize_report_draft(draft)

    _demo_report_draft.update(
        {
            "id": f"draft-{report_instance_id}",
            "workspace_id": WORKSPACE_ID,
            "report_instance_id": report_instance_id,
            "member_id": MEMBER_ID,
            "content_snapshot": deepcopy(content_snapshot),
            "ai_generated": ai_generated,
        }
    )
    if report_instance_id == _demo_report_instance["id"]:
        _demo_report_instance["status"] = "draft"
    return _demo_report_draft


def generate_ai_report_draft(
    report_instance_id: str,
    data_source_ids: list[str],
    fill_empty_only: bool,
    db: Session,
) -> dict[str, object]:
    ensure_demo_report_seed(db)
    instance_id = resolve_report_instance_id(report_instance_id)
    instance = db.get(ReportInstance, instance_id)
    if instance is None:
        raise ValueError("Report not found")

    requested_source_ids = []
    for source_id in data_source_ids:
        try:
            requested_source_ids.append(UUID(source_id))
        except ValueError:
            continue

    if not requested_source_ids:
        raise ValueError("No data source selected")

    sources = db.scalars(
        select(DataSourceConnection)
        .where(
            DataSourceConnection.member_id == instance.assignee_member_id,
            DataSourceConnection.enabled.is_(True),
            DataSourceConnection.id.in_(requested_source_ids),
        )
        .order_by(DataSourceConnection.created_at.asc())
    ).all()
    if not sources:
        raise ValueError("No enabled data source selected")

    draft = db.scalar(
        select(ReportDraft)
        .where(ReportDraft.report_instance_id == instance_id)
        .order_by(ReportDraft.updated_at.desc())
        .limit(1)
    )
    if draft is None:
        content_snapshot = {"groups": []}
    else:
        content_snapshot = deepcopy(draft.content_snapshot)

    enriched = enrich_content_with_ai_sources(content_snapshot, sources, instance, fill_empty_only)
    return save_report_draft(report_instance_id, enriched, True, db)


def enrich_content_with_ai_sources(
    content_snapshot: dict[str, object],
    sources: list[DataSourceConnection],
    instance: ReportInstance,
    fill_empty_only: bool,
) -> dict[str, object]:
    groups = content_snapshot.get("groups")
    if not isinstance(groups, list):
        return content_snapshot

    for group in groups:
        if not isinstance(group, dict):
            continue
        fields = group.get("fields")
        if not isinstance(fields, list):
            continue
        for field in fields:
            if not isinstance(field, dict) or field.get("field_type_snapshot") != "table":
                continue
            current_value = field.get("value")
            current_rows = current_value if isinstance(current_value, list) else []
            if fill_empty_only and current_rows:
                continue

            columns = field.get("columns_snapshot")
            if not isinstance(columns, list) or not columns:
                continue

            generated_rows = [
                build_ai_table_row(columns, source, field, instance) for source in sources
            ]
            if fill_empty_only:
                field["value"] = generated_rows
            else:
                field["value"] = [*current_rows, *generated_rows]

    return content_snapshot


def build_ai_table_row(
    columns: list[object],
    source: DataSourceConnection,
    field: dict[str, object],
    instance: ReportInstance,
) -> dict[str, object]:
    source_name = source.name or source.source_type.upper()
    field_label = str(field.get("field_label_snapshot") or "")
    row: dict[str, object] = {}

    for column in columns:
        if not isinstance(column, dict):
            continue
        column_id = str(column.get("column_id") or "")
        label = str(column.get("label") or "")
        row[column_id] = ai_cell_value(
            column,
            source_name,
            source.source_type,
            field_label,
            label,
            instance,
        )

    return row


def ai_cell_value(
    column: dict[str, object],
    source_name: str,
    source_type: str,
    field_label: str,
    column_label: str,
    instance: ReportInstance,
) -> str:
    column_id = str(column.get("column_id") or "").lower()
    column_type = str(column.get("type") or "")
    options = column_options(column)
    lowered_label = column_label.lower()
    period_text = f"{instance.period_start.isoformat()} 至 {instance.period_end.isoformat()}"

    if any(keyword in column_id for keyword in ["source", "from", "origin"]):
        if options:
            if source_type in {"gitlab", "github"}:
                return first_matching_option(options, ["Git"]) or options[0]
            if source_type == "jira":
                return first_matching_option(options, ["Jira"]) or options[0]
        return source_name

    select_types = {"single_select", "risk_level", "member_select", "project_select"}
    if options and column_type in select_types:
        if any(keyword in column_id for keyword in ["status", "state"]):
            matched_option = first_matching_option(options, ["已完成", "完成", "done", "closed"])
            return matched_option or options[0]
        if "risk" in column_id or "level" in column_id:
            return first_matching_option(options, ["medium", "中", "一般"]) or options[0]
        if "priority" in column_id:
            return first_matching_option(options, ["中", "medium", "P1"]) or options[0]
        return options[0]

    if any(keyword in column_id for keyword in ["title", "summary", "name", "task"]):
        if source_type in {"gitlab", "github"}:
            return f"{source_name} 代码变更汇总"
        if source_type == "jira":
            return f"{source_name} 项目进度更新"
        return f"{source_name} 工作记录"

    if any(keyword in column_id for keyword in ["status", "state"]):
        return "已完成"

    if any(keyword in column_id for keyword in ["description", "detail", "content", "desc"]):
        if source_type in {"gitlab", "github"}:
            return f"AI 根据 {period_text} 的提交、合并请求和关联任务生成，待本人确认后提交。"
        if source_type == "jira":
            return f"AI 根据 {period_text} 的任务状态、评论和项目字段生成，待本人确认后提交。"
        return f"AI 根据 {period_text} 的数据源记录生成，待本人确认后提交。"

    if "risk" in field_label or "风险" in field_label:
        if "level" in column_id or "等级" in column_label:
            return "medium"
        return "暂无新增阻塞，需持续关注自动生成内容准确性。"

    if "plan" in column_id or "计划" in field_label:
        return f"跟进 {source_name} 中未完成事项并同步进度。"

    if "date" in column_type:
        return instance.period_end.isoformat()

    if "number" in column_type or "progress" in column_type:
        return "80"

    if "url" in column_type:
        return ""

    if lowered_label:
        return f"{source_name} {column_label}"
    return source_name


def column_options(column: dict[str, object]) -> list[str]:
    config = column.get("config")
    if not isinstance(config, dict):
        return []
    options = config.get("options")
    if not isinstance(options, list):
        return []
    return [str(option) for option in options]


def first_matching_option(options: list[str], candidates: list[str]) -> str | None:
    normalized = {option.lower(): option for option in options}
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    return None


def build_submission(
    report_instance_id: str,
    content_snapshot: dict[str, object],
    change_reason: str | None = None,
    *,
    persist: bool = True,
    db: Session | None = None,
) -> dict[str, object]:
    if db is not None:
        ensure_demo_report_seed(db)
        instance_id = resolve_report_instance_id(report_instance_id)
        instance = db.get(ReportInstance, instance_id)
        if instance is None:
            raise ValueError("Report not found")

        version_no = (
            db.scalar(
                select(func.max(ReportSubmission.version_no)).where(
                    ReportSubmission.report_instance_id == instance_id
                )
            )
            or 0
        ) + 1
        submission = ReportSubmission(
            workspace_id=instance.workspace_id,
            report_instance_id=instance.id,
            member_id=instance.assignee_member_id,
            version_no=version_no,
            content_snapshot=deepcopy(content_snapshot),
            change_reason=change_reason,
            submitted_at=datetime.now().astimezone(),
        )
        if not persist:
            return {
                "id": "preview-submission",
                "workspace_id": str(instance.workspace_id),
                "report_instance_id": report_instance_id,
                "member_id": str(instance.assignee_member_id),
                "version_no": version_no,
                "content_snapshot": deepcopy(content_snapshot),
                "change_reason": change_reason,
                "submitted_at": submission.submitted_at,
            }

        db.add(submission)
        db.flush()
        instance.status = "submitted"
        instance.submitted_at = submission.submitted_at
        instance.latest_submission_id = submission.id
        db.commit()
        db.refresh(submission)
        return serialize_report_submission(submission)

    version_no = (
        len(
            [
                submission
                for submission in _demo_submissions
                if submission["report_instance_id"] == report_instance_id
            ]
        )
        + 1
    )
    submission = {
        "id": f"submission-{report_instance_id}-v{version_no}",
        "workspace_id": WORKSPACE_ID,
        "report_instance_id": report_instance_id,
        "member_id": MEMBER_ID,
        "version_no": version_no,
        "content_snapshot": deepcopy(content_snapshot),
        "change_reason": change_reason,
        "submitted_at": datetime.now().astimezone(),
    }
    if not persist:
        return submission

    _demo_submissions.append(submission)
    if report_instance_id == _demo_report_instance["id"]:
        _demo_report_instance.update(
            {
                "status": "submitted",
                "submitted_at": submission["submitted_at"],
                "latest_submission_id": submission["id"],
            }
        )
    return submission


def list_report_submissions(
    report_instance_id: str,
    db: Session | None = None,
) -> list[dict[str, object]]:
    if db is not None:
        ensure_demo_report_seed(db)
        try:
            instance_id = resolve_report_instance_id(report_instance_id)
        except ValueError:
            return []
        submissions = db.scalars(
            select(ReportSubmission)
            .where(ReportSubmission.report_instance_id == instance_id)
            .order_by(ReportSubmission.version_no.desc())
        ).all()
        return [serialize_report_submission(submission) for submission in submissions]

    return [
        submission
        for submission in _demo_submissions
        if submission["report_instance_id"] == report_instance_id
    ]


def enabled_report_types(report_space: ReportSpace) -> list[str]:
    if not report_space.report_enabled:
        return []
    if report_space.report_mode == "daily":
        return ["daily"]
    if report_space.report_mode == "daily_weekly":
        return ["daily", "weekly"]
    return ["weekly"]


def period_for_report(
    report_type: str,
    anchor_date: date,
    rule: ReportRule | None,
) -> tuple[date, date]:
    if report_type == "daily":
        return anchor_date, anchor_date

    week_start_day = rule.week_start_day if rule and rule.week_start_day else 1
    days_since_start = (anchor_date.isoweekday() - week_start_day) % 7
    period_start = anchor_date - timedelta(days=days_since_start)
    return period_start, period_start + timedelta(days=6)


def due_at_for_report(period_start: date, period_end: date, rule: ReportRule | None) -> datetime:
    due_time_text = rule.due_time if rule and rule.due_time else "19:00"
    hour, minute = [int(part) for part in due_time_text.split(":", maxsplit=1)]
    if rule and rule.due_type == "weekday" and rule.due_day:
        due_date = period_start + timedelta(days=rule.due_day - 1)
    else:
        due_date = period_end
    return datetime.combine(due_date, time(hour, minute)).astimezone()


def template_version_for_report(
    report_space: ReportSpace,
    report_type: str,
) -> tuple[str | None, dict[str, object] | None]:
    binding = (report_space.template_bindings or {}).get(report_type)
    if not isinstance(binding, dict):
        return None, None

    template_id = binding.get("template_id")
    if not isinstance(template_id, str) or not template_id:
        return None, None

    if binding.get("version_policy") == "fixed_version":
        version_id = binding.get("template_version_id")
        if isinstance(version_id, str):
            return template_id, get_version(version_id)
        return template_id, None

    return template_id, latest_published_version(template_id)


def generate_report_instances(
    report_space_id: str,
    anchor_date: date,
    db: Session,
) -> dict[str, list[dict[str, object]]]:
    ensure_demo_report_seed(db)
    from app.services.organization import resolve_report_space_id

    resolved_space_id = resolve_report_space_id(report_space_id)
    report_space = db.get(ReportSpace, resolved_space_id)
    if report_space is None:
        raise ValueError("Report space not found")

    member_id = UUID(MEMBER_ID)
    created: list[ReportInstance] = []
    existing: list[ReportInstance] = []

    for report_type in enabled_report_types(report_space):
        rule = db.scalar(
            select(ReportRule).where(
                ReportRule.report_space_id == report_space.id,
                ReportRule.report_type == report_type,
            )
        )
        period_start, period_end = period_for_report(report_type, anchor_date, rule)
        instance = db.scalar(
            select(ReportInstance).where(
                ReportInstance.workspace_id == report_space.workspace_id,
                ReportInstance.report_space_id == report_space.id,
                ReportInstance.report_type == report_type,
                ReportInstance.assignee_member_id == member_id,
                ReportInstance.period_start == period_start,
                ReportInstance.period_end == period_end,
            )
        )
        if instance is not None:
            existing.append(instance)
            continue

        template_id, version = template_version_for_report(report_space, report_type)
        if version is None:
            version = latest_published_version("template-weekly-default")
            template_id = "template-weekly-default"

        instance = ReportInstance(
            id=uuid4(),
            workspace_id=report_space.workspace_id,
            report_space_id=report_space.id,
            report_type=report_type,
            assignee_member_id=member_id,
            period_start=period_start,
            period_end=period_end,
            due_at=due_at_for_report(period_start, period_end, rule),
            status="draft",
            template_id=resolve_template_id(template_id),
            template_version_id=resolve_template_id(str(version["id"])) if version else None,
            submitted_at=None,
            submitted_late=False,
        )
        db.add(instance)
        db.flush()

        content_snapshot = (
            template_schema_to_content_snapshot(version) if version else {"groups": []}
        )
        draft = ReportDraft(
            workspace_id=report_space.workspace_id,
            report_instance_id=instance.id,
            member_id=member_id,
            content_snapshot=content_snapshot,
            ai_generated=False,
        )
        db.add(draft)
        db.flush()
        instance.latest_draft_id = draft.id
        created.append(instance)

    db.commit()
    return {
        "created": [serialize_report_instance(instance) for instance in created],
        "existing": [serialize_report_instance(instance) for instance in existing],
    }
