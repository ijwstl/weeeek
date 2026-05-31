import { apiGet, apiPatch, apiPost } from './client'

export type DataSourceType = 'gitlab' | 'github' | 'jira' | 'custom'

export interface DataSourceConnection {
  id: string
  workspace_id: string
  member_id: string
  source_type: DataSourceType
  name: string
  account_name: string
  status: string
  enabled: boolean
  scope_config: Record<string, unknown>
  last_sync_at?: string | null
}

export interface DataSourceConnectionUpdate {
  name?: string
  account_name?: string
  enabled?: boolean
  status?: string
  scope_config?: Record<string, unknown>
}

export function listDataSources() {
  return apiGet<DataSourceConnection[]>('/data-sources')
}

export function updateDataSource(id: string, payload: DataSourceConnectionUpdate) {
  return apiPatch<DataSourceConnection, DataSourceConnectionUpdate>(`/data-sources/${id}`, payload)
}

export function testDataSource(id: string) {
  return apiPost<Record<string, unknown>, Record<string, never>>(`/data-sources/${id}/test`, {})
}
