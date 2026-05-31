from datetime import date, datetime

from pydantic import BaseModel, Field


class ReportInstanceRead(BaseModel):
    id: str
    workspace_id: str
    report_space_id: str
    report_type: str
    assignee_member_id: str
    period_start: date
    period_end: date
    due_at: datetime
    status: str
    template_id: str | None = None
    template_version_id: str | None = None
    submitted_at: datetime | None = None
    submitted_late: bool = False


class ReportDraftRead(BaseModel):
    id: str
    workspace_id: str
    report_instance_id: str
    member_id: str
    content_snapshot: dict[str, object]
    ai_generated: bool


class ReportDraftUpdate(BaseModel):
    content_snapshot: dict[str, object]
    ai_generated: bool = False


class ReportAIDraftRequest(BaseModel):
    data_source_ids: list[str] = Field(default_factory=list)
    fill_empty_only: bool = True


class ReportSubmissionRead(BaseModel):
    id: str
    workspace_id: str
    report_instance_id: str
    member_id: str
    version_no: int
    content_snapshot: dict[str, object]
    change_reason: str | None = None
    submitted_at: datetime


class ReportSubmitRequest(BaseModel):
    content_snapshot: dict[str, object]
    change_reason: str | None = Field(default=None, max_length=500)


class ReportDetailRead(BaseModel):
    instance: ReportInstanceRead
    draft: ReportDraftRead | None = None
    latest_submission: ReportSubmissionRead | None = None


class ReportGenerateRequest(BaseModel):
    anchor_date: date | None = None


class ReportGenerateResult(BaseModel):
    created: list[ReportInstanceRead]
    existing: list[ReportInstanceRead]
