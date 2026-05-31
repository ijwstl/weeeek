import { apiGet, apiPost, apiPut } from './client'
import type { ReportInstance } from './reports'

export interface ReportSpace {
  id: string
  workspace_id: string
  space_type: string
  department_id?: string | null
  project_team_id?: string | null
  name: string
  status: string
  report_enabled: boolean
  report_mode: ReportMode
  ai_enabled: boolean
  allowed_data_source_types: string[]
  template_bindings: Record<string, TemplateBinding>
  member_visibility: string
}

export type ReportMode = 'daily' | 'weekly' | 'daily_weekly'

export interface TemplateBinding {
  template_id?: string
  version_policy?: 'latest_published' | 'fixed_version'
  template_version_id?: string
}

export interface DepartmentTreeNode {
  id: string
  workspace_id: string
  parent_id?: string | null
  name: string
  path: string
  depth: number
  sort_order: number
  status: string
  report_space?: ReportSpace | null
  children: DepartmentTreeNode[]
}

export interface SubmissionStatus {
  report_space_id: string
  total_members: number
  submitted_members: number
  pending_members: number
  overdue_members: number
}

export interface ReportRule {
  id: string
  workspace_id: string
  report_space_id: string
  report_type: string
  enabled: boolean
  frequency: string
  interval_value?: number | null
  week_start_day?: number | null
  reminder_day?: number | null
  reminder_time?: string | null
  due_type: string
  due_day?: number | null
  due_time?: string | null
  skip_weekends: boolean
  notification_channels: string[]
  overdue_policy: Record<string, unknown>
  extra_config: Record<string, unknown>
}

export interface ReportRuleUpsert {
  enabled: boolean
  frequency: string
  interval_value?: number | null
  week_start_day?: number | null
  reminder_day?: number | null
  reminder_time?: string | null
  due_type: string
  due_day?: number | null
  due_time?: string | null
  skip_weekends: boolean
  notification_channels: string[]
  overdue_policy: Record<string, unknown>
  extra_config: Record<string, unknown>
}

export function getDepartmentTree() {
  return apiGet<DepartmentTreeNode[]>('/departments/tree')
}

export function getDepartmentSubmissionStatus(departmentId: string) {
  return apiGet<SubmissionStatus>(`/departments/${departmentId}/submission-status`)
}

export function listReportRules(reportSpaceId: string) {
  return apiGet<ReportRule[]>(`/report-spaces/${reportSpaceId}/rules`)
}

export function updateReportRule(
  reportSpaceId: string,
  reportType: 'daily' | 'weekly',
  payload: ReportRuleUpsert
) {
  return apiPut<ReportRule, ReportRuleUpsert>(
    `/report-spaces/${reportSpaceId}/rules/${reportType}`,
    payload
  )
}

export interface ReportSpaceConfigUpdate {
  report_enabled?: boolean
  report_mode?: ReportMode
  ai_enabled?: boolean
  allowed_data_source_types?: string[]
  template_bindings?: Record<string, TemplateBinding>
  member_visibility?: 'private' | 'department'
}

export function updateReportSpaceConfig(reportSpaceId: string, payload: ReportSpaceConfigUpdate) {
  return apiPut<ReportSpace, ReportSpaceConfigUpdate>(
    `/report-spaces/${reportSpaceId}/config`,
    payload
  )
}

export interface GenerateReportInstancesRequest {
  anchor_date?: string | null
}

export interface GenerateReportInstancesResult {
  created: ReportInstance[]
  existing: ReportInstance[]
}

export function generateReportInstances(
  reportSpaceId: string,
  payload: GenerateReportInstancesRequest = {}
) {
  return apiPost<GenerateReportInstancesResult, GenerateReportInstancesRequest>(
    `/report-spaces/${reportSpaceId}/generate-instances`,
    payload
  )
}
