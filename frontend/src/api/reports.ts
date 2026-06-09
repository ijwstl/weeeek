import { apiGet, apiPost, apiPut } from './client'

export interface ReportInstance {
  id: string
  workspace_id: string
  report_space_id: string
  report_type: string
  assignee_member_id: string
  period_start: string
  period_end: string
  due_at: string
  status: string
  template_id?: string | null
  template_version_id?: string | null
  submitted_at?: string | null
  submitted_late: boolean
}

export interface ReportDraft {
  id: string
  workspace_id: string
  report_instance_id: string
  member_id: string
  content_snapshot: ReportContentSnapshot
  ai_generated: boolean
}

export interface ReportContentSnapshot {
  template_version_id?: string
  render_mode?: 'structured_form' | 'markdown_doc'
  content_format?: string
  markdown_template_snapshot?: string
  markdown_value?: string
  html_value?: string
  editor_json?: Record<string, unknown> | null
  editor_schema_snapshot?: Record<string, unknown>
  ai_blocks_snapshot?: Array<Record<string, unknown>>
  groups: ReportGroupSnapshot[]
}

export interface ReportGroupSnapshot {
  group_id: string
  group_label_snapshot: string
  fields: ReportFieldSnapshot[]
}

export interface ReportFieldSnapshot {
  field_id: string
  field_label_snapshot: string
  field_type_snapshot: string
  config_snapshot?: Record<string, unknown>
  columns_snapshot?: Array<{
    column_id: string
    label: string
    type: string
    required?: boolean
    config?: Record<string, unknown>
  }>
  value: unknown
}

export interface ReportDetail {
  instance: ReportInstance
  draft?: ReportDraft | null
}

export interface ReportSubmission {
  id: string
  workspace_id: string
  report_instance_id: string
  member_id: string
  version_no: number
  content_snapshot: ReportContentSnapshot
  change_reason?: string | null
  submitted_at: string
}

export function listMyReportTasks() {
  return apiGet<ReportInstance[]>('/reports/my-tasks')
}

export function listMyReportHistory() {
  return apiGet<ReportSubmission[]>('/reports/my-history')
}

export function listReportSubmissions(reportInstanceId: string) {
  return apiGet<ReportSubmission[]>(`/reports/${reportInstanceId}/submissions`)
}

export function getReportDetail(reportInstanceId: string) {
  return apiGet<ReportDetail>(`/reports/${reportInstanceId}`)
}

export interface ReportDraftUpdate {
  content_snapshot: ReportContentSnapshot
  ai_generated: boolean
}

export interface ReportSubmitRequest {
  content_snapshot: ReportContentSnapshot
  change_reason?: string | null
}

export interface ReportAIDraftRequest {
  data_source_ids: string[]
  fill_empty_only: boolean
}

export function saveReportDraft(reportInstanceId: string, payload: ReportDraftUpdate) {
  return apiPut<ReportDraft, ReportDraftUpdate>(`/reports/${reportInstanceId}/draft`, payload)
}

export function generateReportAIDraft(reportInstanceId: string, payload: ReportAIDraftRequest) {
  return apiPost<ReportDraft, ReportAIDraftRequest>(`/reports/${reportInstanceId}/ai-draft`, payload)
}

export function submitReport(reportInstanceId: string, payload: ReportSubmitRequest) {
  return apiPost<ReportSubmission, ReportSubmitRequest>(
    `/reports/${reportInstanceId}/submit`,
    payload
  )
}
