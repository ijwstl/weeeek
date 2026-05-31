import { apiGet } from './client'

export interface AuditLog {
  id: string
  workspace_id: string
  actor_member_id?: string | null
  action: string
  resource_type: string
  resource_id?: string | null
  request_method?: string | null
  request_path?: string | null
  status: string
  ip_address?: string | null
  user_agent?: string | null
  metadata_json: Record<string, unknown>
  created_at: string
}

export interface AuditLogQuery {
  limit?: number
  action?: string
  resource_type?: string
  status?: string
  keyword?: string
}

export function listAuditLogs(query: AuditLogQuery = {}) {
  const params = new URLSearchParams()
  params.set('limit', String(query.limit ?? 50))
  if (query.action) params.set('action', query.action)
  if (query.resource_type) params.set('resource_type', query.resource_type)
  if (query.status) params.set('status', query.status)
  if (query.keyword) params.set('keyword', query.keyword)
  return apiGet<AuditLog[]>(`/audit/logs?${params.toString()}`)
}
