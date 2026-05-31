from datetime import date

from pydantic import BaseModel, Field


class ReportSpaceRead(BaseModel):
    id: str
    workspace_id: str
    space_type: str
    department_id: str | None = None
    project_team_id: str | None = None
    name: str
    status: str
    report_enabled: bool
    report_mode: str = "weekly"
    ai_enabled: bool
    allowed_data_source_types: list[str]
    template_bindings: dict[str, object] = Field(default_factory=dict)
    member_visibility: str


class ReportSpaceConfigUpdate(BaseModel):
    report_enabled: bool | None = None
    report_mode: str | None = Field(default=None, pattern="^(daily|weekly|daily_weekly)$")
    ai_enabled: bool | None = None
    allowed_data_source_types: list[str] | None = None
    template_bindings: dict[str, object] | None = None
    member_visibility: str | None = Field(default=None, pattern="^(private|department)$")


class DepartmentRead(BaseModel):
    id: str
    workspace_id: str
    parent_id: str | None = None
    name: str
    path: str
    depth: int
    sort_order: int
    status: str
    report_space: ReportSpaceRead | None = None


class DepartmentTreeNode(DepartmentRead):
    children: list["DepartmentTreeNode"] = Field(default_factory=list)


class DepartmentCreate(BaseModel):
    parent_id: str | None = None
    name: str = Field(min_length=1, max_length=120)
    sort_order: int = 0


class DepartmentUpdate(BaseModel):
    parent_id: str | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)
    sort_order: int | None = None
    status: str | None = None


class DepartmentMemberAdd(BaseModel):
    member_id: str


class SubmissionStatusRead(BaseModel):
    report_space_id: str
    total_members: int
    submitted_members: int
    pending_members: int
    overdue_members: int


class ReportRuleRead(BaseModel):
    id: str
    workspace_id: str
    report_space_id: str
    report_type: str
    enabled: bool
    frequency: str
    interval_value: int | None = None
    week_start_day: int | None = None
    reminder_day: int | None = None
    reminder_time: str | None = None
    due_type: str
    due_day: int | None = None
    due_time: str | None = None
    skip_weekends: bool
    notification_channels: list[str]
    overdue_policy: dict[str, object]
    extra_config: dict[str, object]


class ReportRuleUpsert(BaseModel):
    enabled: bool = True
    frequency: str
    interval_value: int | None = Field(default=None, ge=1)
    week_start_day: int | None = Field(default=None, ge=1, le=7)
    reminder_day: int | None = Field(default=None, ge=1, le=7)
    reminder_time: str | None = None
    due_type: str = "same_day"
    due_day: int | None = Field(default=None, ge=1, le=7)
    due_time: str | None = None
    skip_weekends: bool = False
    notification_channels: list[str] = Field(default_factory=lambda: ["in_app", "feishu"])
    overdue_policy: dict[str, object] = Field(default_factory=dict)
    extra_config: dict[str, object] = Field(default_factory=dict)


class ProjectTeamRead(BaseModel):
    id: str
    workspace_id: str
    name: str
    description: str
    goal: str
    status: str
    start_date: date | None = None
    expected_end_date: date | None = None
    actual_end_date: date | None = None
    report_space: ReportSpaceRead | None = None


class ProjectTeamMemberRead(BaseModel):
    project_team_id: str
    member_id: str
    role: str
    display_name: str
    email: str | None = None
    employee_no: str | None = None
    status: str


class ProjectTeamMemberAdd(BaseModel):
    member_id: str
    role: str = Field(default="project_member", pattern="^(project_admin|project_member)$")


class ProjectTeamMemberUpdate(BaseModel):
    role: str = Field(pattern="^(project_admin|project_member)$")


class ProjectTeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = ""
    goal: str = ""
    start_date: date | None = None
    expected_end_date: date | None = None


class ProjectTeamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    goal: str | None = None
    status: str | None = None
    start_date: date | None = None
    expected_end_date: date | None = None
    actual_end_date: date | None = None
