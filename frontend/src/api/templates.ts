import { apiGet, apiPost, apiPut } from './client'

export interface TemplateColumn {
  column_id: string
  label: string
  type: string
  required: boolean
  config?: Record<string, unknown>
}

export interface TemplateField {
  field_id: string
  label: string
  type: string
  required: boolean
  summary_enabled: boolean
  ai_supported: boolean
  sort_order: number
  config: {
    columns?: TemplateColumn[]
    [key: string]: unknown
  }
}

export interface TemplateGroup {
  group_id: string
  label: string
  description: string
  sort_order: number
  collapsible: boolean
  fields: TemplateField[]
}

export interface TemplateSchema {
  render_mode?: 'structured_form' | 'markdown_doc'
  groups: TemplateGroup[]
  markdown_template?: string
  html_template?: string
  editor_schema?: Record<string, unknown>
  ai_blocks?: Array<Record<string, unknown>>
}

export interface ReportTemplate {
  id: string
  workspace_id: string
  name: string
  template_scope: string
  description: string
  status: string
  created_by_member_id?: string | null
}

export interface ReportTemplateVersion {
  id: string
  workspace_id: string
  template_id: string
  version_no: number
  status: string
  schema_snapshot: TemplateSchema
  published_by_member_id?: string | null
  published_at?: string | null
}

export function listTemplates() {
  return apiGet<ReportTemplate[]>('/templates')
}

export function getTemplateDraft(templateId: string) {
  return apiGet<ReportTemplateVersion>(`/templates/${templateId}/draft`)
}

export function listTemplateVersions(templateId: string) {
  return apiGet<ReportTemplateVersion[]>(`/templates/${templateId}/versions`)
}

export function updateTemplateDraft(templateId: string, schemaSnapshot: TemplateSchema) {
  return apiPut<ReportTemplateVersion, { schema_snapshot: TemplateSchema }>(
    `/templates/${templateId}/draft`,
    { schema_snapshot: schemaSnapshot }
  )
}

export function publishTemplate(templateId: string) {
  return apiPost<ReportTemplateVersion, Record<string, never>>(
    `/templates/${templateId}/publish`,
    {}
  )
}

export function validateTemplateSchema(schemaSnapshot: TemplateSchema) {
  return apiPost<{ valid: boolean; errors: string[] }, TemplateSchema>(
    '/templates/validate-schema',
    schemaSnapshot
  )
}
