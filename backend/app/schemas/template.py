from pydantic import BaseModel, Field, field_validator, model_validator

FIELD_TYPES = {
    "text",
    "textarea",
    "rich_text",
    "table",
    "single_select",
    "multi_select",
    "number",
    "date",
    "progress",
    "member_select",
    "project_select",
    "risk_level",
    "jira_issue",
    "git_ref",
    "url",
}

TABLE_COLUMN_TYPES = FIELD_TYPES - {"table", "rich_text"}
TEMPLATE_RENDER_MODES = {"structured_form", "markdown_doc"}


class TemplateTableColumn(BaseModel):
    column_id: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=120)
    type: str
    required: bool = False
    config: dict[str, object] = Field(default_factory=dict)

    @field_validator("type")
    @classmethod
    def validate_column_type(cls, value: str) -> str:
        if value not in TABLE_COLUMN_TYPES:
            raise ValueError(f"Unsupported table column type: {value}")
        return value


class TemplateField(BaseModel):
    field_id: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=120)
    type: str
    required: bool = False
    summary_enabled: bool = False
    ai_supported: bool = False
    sort_order: int = 0
    config: dict[str, object] = Field(default_factory=dict)

    @field_validator("type")
    @classmethod
    def validate_field_type(cls, value: str) -> str:
        if value not in FIELD_TYPES:
            raise ValueError(f"Unsupported field type: {value}")
        return value

    @model_validator(mode="after")
    def validate_table_config(self) -> "TemplateField":
        if self.type != "table":
            return self

        columns = self.config.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError("Table field requires non-empty config.columns")
        parsed_columns = [TemplateTableColumn.model_validate(column) for column in columns]
        self.config["columns"] = [column.model_dump() for column in parsed_columns]
        return self


class TemplateGroup(BaseModel):
    group_id: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=120)
    description: str = ""
    sort_order: int = 0
    collapsible: bool = False
    fields: list[TemplateField] = Field(default_factory=list)


class TemplateSchema(BaseModel):
    render_mode: str = "structured_form"
    groups: list[TemplateGroup] = Field(default_factory=list)
    markdown_template: str = ""
    html_template: str = ""
    editor_schema: dict[str, object] = Field(default_factory=dict)
    ai_blocks: list[dict[str, object]] = Field(default_factory=list)

    @field_validator("render_mode")
    @classmethod
    def validate_render_mode(cls, value: str) -> str:
        if value not in TEMPLATE_RENDER_MODES:
            raise ValueError(f"Unsupported template render_mode: {value}")
        return value

    @model_validator(mode="after")
    def validate_unique_ids(self) -> "TemplateSchema":
        if self.render_mode == "markdown_doc":
            if not self.markdown_template.strip() and not self.html_template.strip():
                raise ValueError("Markdown template requires rich text content")
            return self

        group_ids = [group.group_id for group in self.groups]
        if len(group_ids) != len(set(group_ids)):
            raise ValueError("Duplicate group_id in template schema")

        field_ids = [field.field_id for group in self.groups for field in group.fields]
        if len(field_ids) != len(set(field_ids)):
            raise ValueError("Duplicate field_id in template schema")
        return self


class ReportTemplateRead(BaseModel):
    id: str
    workspace_id: str
    name: str
    template_scope: str
    description: str
    status: str
    created_by_member_id: str | None = None


class ReportTemplateCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    template_scope: str
    description: str = ""


class ReportTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = None
    status: str | None = None


class ReportTemplateVersionRead(BaseModel):
    id: str
    workspace_id: str
    template_id: str
    version_no: int
    status: str
    schema_snapshot: TemplateSchema
    published_by_member_id: str | None = None
    published_at: str | None = None


class TemplateDraftUpdate(BaseModel):
    schema_snapshot: TemplateSchema


class TemplateSchemaValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
