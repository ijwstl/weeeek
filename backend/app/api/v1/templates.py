from fastapi import APIRouter, HTTPException, status
from pydantic import ValidationError

from app.audit.decorator import audit_log
from app.schemas.common import APIResponse
from app.schemas.template import (
    ReportTemplateCreate,
    ReportTemplateRead,
    ReportTemplateUpdate,
    ReportTemplateVersionRead,
    TemplateDraftUpdate,
    TemplateSchema,
    TemplateSchemaValidationResult,
)
from app.services.templates import (
    get_draft,
    get_template,
    get_version,
    list_templates,
    list_versions,
    publish_draft,
    update_draft,
)

router = APIRouter()


@router.get("", response_model=APIResponse[list[ReportTemplateRead]])
def get_templates() -> APIResponse[list[ReportTemplateRead]]:
    return APIResponse(
        data=[ReportTemplateRead.model_validate(template) for template in list_templates()]
    )


@router.post("", response_model=APIResponse[ReportTemplateRead])
def create_template(payload: ReportTemplateCreate) -> APIResponse[ReportTemplateRead]:
    from app.services.bootstrap import DEMO_MEMBER

    template = {
        "id": f"template-{payload.name}",
        "workspace_id": DEMO_MEMBER["workspace_id"],
        "name": payload.name,
        "template_scope": payload.template_scope,
        "description": payload.description,
        "status": "active",
        "created_by_member_id": DEMO_MEMBER["id"],
    }
    return APIResponse(data=ReportTemplateRead.model_validate(template))


@router.get("/{template_id}", response_model=APIResponse[ReportTemplateRead])
def get_template_detail(template_id: str) -> APIResponse[ReportTemplateRead]:
    template = get_template(template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    return APIResponse(data=ReportTemplateRead.model_validate(template))


@router.patch("/{template_id}", response_model=APIResponse[ReportTemplateRead])
def update_template(
    template_id: str,
    payload: ReportTemplateUpdate,
) -> APIResponse[ReportTemplateRead]:
    template = get_template(template_id)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
    updated = {**template, **payload.model_dump(exclude_none=True)}
    return APIResponse(data=ReportTemplateRead.model_validate(updated))


@router.delete("/{template_id}", response_model=APIResponse[dict[str, bool]])
def delete_template(template_id: str) -> APIResponse[dict[str, bool]]:
    _ = template_id
    return APIResponse(data={"ok": True})


@router.get("/{template_id}/draft", response_model=APIResponse[ReportTemplateVersionRead])
def get_template_draft(template_id: str) -> APIResponse[ReportTemplateVersionRead]:
    draft = get_draft(template_id)
    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template draft not found",
        )
    return APIResponse(data=ReportTemplateVersionRead.model_validate(draft))


@router.put("/{template_id}/draft", response_model=APIResponse[ReportTemplateVersionRead])
@audit_log("template.draft.update", "template")
def update_template_draft(
    template_id: str,
    payload: TemplateDraftUpdate,
) -> APIResponse[ReportTemplateVersionRead]:
    draft = get_draft(template_id)
    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template draft not found",
        )
    updated = update_draft(template_id, payload.schema_snapshot)
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template draft not found",
        )
    return APIResponse(data=ReportTemplateVersionRead.model_validate(updated))


@router.post("/{template_id}/publish", response_model=APIResponse[ReportTemplateVersionRead])
@audit_log("template.publish", "template")
def publish_template(template_id: str) -> APIResponse[ReportTemplateVersionRead]:
    draft = get_draft(template_id)
    if draft is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template draft not found",
        )
    published = publish_draft(template_id)
    if published is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template draft not found",
        )
    return APIResponse(data=ReportTemplateVersionRead.model_validate(published))


@router.get("/{template_id}/versions", response_model=APIResponse[list[ReportTemplateVersionRead]])
def get_template_versions(template_id: str) -> APIResponse[list[ReportTemplateVersionRead]]:
    return APIResponse(
        data=[
            ReportTemplateVersionRead.model_validate(version)
            for version in list_versions(template_id)
        ]
    )


@router.get("/versions/{version_id}", response_model=APIResponse[ReportTemplateVersionRead])
def get_template_version(version_id: str) -> APIResponse[ReportTemplateVersionRead]:
    version = get_version(version_id)
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template version not found",
        )
    return APIResponse(data=ReportTemplateVersionRead.model_validate(version))


@router.post("/validate-schema", response_model=APIResponse[TemplateSchemaValidationResult])
def validate_template_schema(
    payload: dict[str, object],
) -> APIResponse[TemplateSchemaValidationResult]:
    try:
        TemplateSchema.model_validate(payload)
    except ValidationError as exc:
        return APIResponse(
            data=TemplateSchemaValidationResult(
                valid=False,
                errors=[error["msg"] for error in exc.errors()],
            )
        )
    return APIResponse(data=TemplateSchemaValidationResult(valid=True))
