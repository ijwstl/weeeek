from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import APIResponse
from app.schemas.organization import (
    ReportRuleRead,
    ReportRuleUpsert,
    ReportSpaceConfigUpdate,
    ReportSpaceRead,
)
from app.schemas.report import (
    ReportGenerateRequest,
    ReportGenerateResult,
    ReportInstanceRead,
)
from app.services.organization import (
    default_rules_for_space,
    get_report_rule,
    get_report_space,
    update_report_space_config,
    upsert_report_rule_config,
)
from app.services.reports import generate_report_instances

router = APIRouter()
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/{report_space_id}", response_model=APIResponse[ReportSpaceRead])
def get_report_space_detail(
    report_space_id: str,
    db: DbSession,
) -> APIResponse[ReportSpaceRead]:
    report_space = get_report_space(report_space_id, db)
    if report_space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report space not found")
    return APIResponse(data=ReportSpaceRead.model_validate(report_space))


@router.put("/{report_space_id}/config", response_model=APIResponse[ReportSpaceRead])
def update_report_space_detail(
    report_space_id: str,
    payload: ReportSpaceConfigUpdate,
    db: DbSession,
) -> APIResponse[ReportSpaceRead]:
    report_space = update_report_space_config(
        report_space_id,
        payload.model_dump(exclude_none=True),
        db,
    )
    if report_space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report space not found")
    return APIResponse(data=ReportSpaceRead.model_validate(report_space))


@router.post(
    "/{report_space_id}/generate-instances",
    response_model=APIResponse[ReportGenerateResult],
)
def generate_instances(
    report_space_id: str,
    payload: ReportGenerateRequest,
    db: DbSession,
) -> APIResponse[ReportGenerateResult]:
    try:
        result = generate_report_instances(
            report_space_id,
            payload.anchor_date or date.today(),
            db,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report space not found",
        ) from None
    return APIResponse(
        data=ReportGenerateResult(
            created=[
                ReportInstanceRead.model_validate(instance)
                for instance in result["created"]
            ],
            existing=[
                ReportInstanceRead.model_validate(instance)
                for instance in result["existing"]
            ],
        )
    )


@router.get("/{report_space_id}/rules", response_model=APIResponse[list[ReportRuleRead]])
def list_report_rules(
    report_space_id: str,
    db: DbSession,
) -> APIResponse[list[ReportRuleRead]]:
    if get_report_space(report_space_id, db) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report space not found")
    return APIResponse(
        data=[
            ReportRuleRead.model_validate(rule)
            for rule in default_rules_for_space(report_space_id, db)
        ]
    )


@router.put("/{report_space_id}/rules/{report_type}", response_model=APIResponse[ReportRuleRead])
def upsert_report_rule(
    report_space_id: str,
    report_type: str,
    payload: ReportRuleUpsert,
    db: DbSession,
) -> APIResponse[ReportRuleRead]:
    if get_report_space(report_space_id, db) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report space not found")

    current_rule = get_report_rule(report_space_id, report_type, db)
    if current_rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report rule not found")

    rule = upsert_report_rule_config(
        report_space_id,
        report_type,
        payload.model_dump(),
        db,
    )
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report rule not found")
    return APIResponse(data=ReportRuleRead.model_validate(rule))


@router.get("/{report_space_id}/visibility", response_model=APIResponse[dict[str, str]])
def get_visibility(
    report_space_id: str,
    db: DbSession,
) -> APIResponse[dict[str, str]]:
    report_space = get_report_space(report_space_id, db)
    if report_space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report space not found")
    return APIResponse(data={"member_visibility": str(report_space["member_visibility"])})


@router.put("/{report_space_id}/visibility", response_model=APIResponse[dict[str, str]])
def update_visibility(
    report_space_id: str,
    payload: dict[str, str],
    db: DbSession,
) -> APIResponse[dict[str, str]]:
    report_space = update_report_space_config(
        report_space_id,
        {"member_visibility": payload.get("member_visibility", "private")},
        db,
    )
    if report_space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report space not found")
    return APIResponse(data={"member_visibility": str(report_space["member_visibility"])})
