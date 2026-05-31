from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.audit.decorator import audit_log
from app.db.session import get_db
from app.schemas.common import APIResponse
from app.schemas.report import (
    ReportAIDraftRequest,
    ReportDetailRead,
    ReportDraftRead,
    ReportDraftUpdate,
    ReportInstanceRead,
    ReportSubmissionRead,
    ReportSubmitRequest,
)
from app.services.reports import (
    build_submission,
    generate_ai_report_draft,
    get_report_draft,
    get_report_instance,
    list_my_tasks,
    list_report_submissions,
    save_report_draft,
)

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/my-tasks", response_model=APIResponse[list[ReportInstanceRead]])
def get_my_tasks(db: DbSession) -> APIResponse[list[ReportInstanceRead]]:
    return APIResponse(data=[ReportInstanceRead.model_validate(task) for task in list_my_tasks(db)])


@router.get("/my-history", response_model=APIResponse[list[ReportSubmissionRead]])
def get_my_history() -> APIResponse[list[ReportSubmissionRead]]:
    submission = build_submission(
        "report-weekly-backend-20260518",
        {"groups": []},
        "历史提交示例",
        persist=False,
    )
    return APIResponse(data=[ReportSubmissionRead.model_validate(submission)])


@router.get("/{report_instance_id}", response_model=APIResponse[ReportDetailRead])
def get_report_detail(
    report_instance_id: str,
    db: DbSession,
) -> APIResponse[ReportDetailRead]:
    instance = get_report_instance(report_instance_id, db)
    if instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    draft = get_report_draft(report_instance_id, db)
    return APIResponse(
        data=ReportDetailRead(
            instance=ReportInstanceRead.model_validate(instance),
            draft=ReportDraftRead.model_validate(draft) if draft else None,
            latest_submission=None,
        )
    )


@router.get("/{report_instance_id}/draft", response_model=APIResponse[ReportDraftRead])
def get_draft(
    report_instance_id: str,
    db: DbSession,
) -> APIResponse[ReportDraftRead]:
    draft = get_report_draft(report_instance_id, db)
    if draft is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found")
    return APIResponse(data=ReportDraftRead.model_validate(draft))


@router.put("/{report_instance_id}/draft", response_model=APIResponse[ReportDraftRead])
@audit_log("report.draft.save", "report_instance")
def save_draft(
    report_instance_id: str,
    payload: ReportDraftUpdate,
    db: DbSession,
) -> APIResponse[ReportDraftRead]:
    if get_report_instance(report_instance_id, db) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    draft = save_report_draft(
        report_instance_id,
        payload.content_snapshot,
        payload.ai_generated,
        db,
    )
    return APIResponse(data=ReportDraftRead.model_validate(draft))


@router.post("/{report_instance_id}/ai-draft", response_model=APIResponse[ReportDraftRead])
@audit_log("report.ai_draft.generate", "report_instance")
def generate_ai_draft(
    report_instance_id: str,
    payload: ReportAIDraftRequest,
    db: DbSession,
) -> APIResponse[ReportDraftRead]:
    if get_report_instance(report_instance_id, db) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    try:
        draft = generate_ai_report_draft(
            report_instance_id,
            payload.data_source_ids,
            payload.fill_empty_only,
            db,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return APIResponse(data=ReportDraftRead.model_validate(draft))


@router.post("/{report_instance_id}/submit", response_model=APIResponse[ReportSubmissionRead])
@audit_log("report.submit", "report_instance")
def submit_report(
    report_instance_id: str,
    payload: ReportSubmitRequest,
    db: DbSession,
) -> APIResponse[ReportSubmissionRead]:
    if get_report_instance(report_instance_id, db) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    submission = build_submission(
        report_instance_id,
        payload.content_snapshot,
        payload.change_reason,
        db=db,
    )
    return APIResponse(data=ReportSubmissionRead.model_validate(submission))


@router.post("/{report_instance_id}/reopen", response_model=APIResponse[dict[str, bool]])
def reopen_report(
    report_instance_id: str,
    db: DbSession,
) -> APIResponse[dict[str, bool]]:
    if get_report_instance(report_instance_id, db) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return APIResponse(data={"ok": True})


@router.get(
    "/{report_instance_id}/submissions",
    response_model=APIResponse[list[ReportSubmissionRead]],
)
def list_submissions(
    report_instance_id: str,
    db: DbSession,
) -> APIResponse[list[ReportSubmissionRead]]:
    submissions = list_report_submissions(report_instance_id, db)
    if submissions:
        return APIResponse(
            data=[ReportSubmissionRead.model_validate(submission) for submission in submissions]
        )

    draft = get_report_draft(report_instance_id, db)
    content = draft["content_snapshot"] if draft else {"groups": []}
    return APIResponse(
        data=[
            ReportSubmissionRead.model_validate(
                build_submission(report_instance_id, content, "首次提交", persist=False, db=db)
            )
        ]
    )
