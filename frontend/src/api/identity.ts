import { apiGet, apiPatch, apiPost } from './client'

export interface Workspace {
  id: string
  name: string
  slug: string
  deployment_mode: string
  default_locale: string
  timezone: string
  department_max_depth: number
  status: string
}

export interface User {
  id: string
  display_name: string
  email?: string | null
  avatar_url?: string | null
  status: string
}

export interface Member {
  id: string
  workspace_id: string
  user_id: string
  department_id?: string | null
  display_name: string
  email?: string | null
  employee_no?: string | null
  avatar_url?: string | null
  status: string
}

export interface CurrentPrincipal {
  user: User
  member: Member
  workspace: Workspace
  permissions: string[]
  roles: string[]
}

export interface SecuritySettings {
  workspace_admin_can_view_all_submitted_reports: boolean
  audit_enabled: boolean
  private_deployment_single_workspace: boolean
}

export interface AuthProviderConfig {
  id: string
  workspace_id: string
  provider_type: string
  name: string
  enabled: boolean
  config_public: Record<string, unknown>
  bind_password_configured: boolean
}

export interface AuthProviderConfigUpdate {
  name?: string
  enabled?: boolean
  config_public?: Record<string, unknown>
  bind_password?: string
}

export interface AuthProviderTestResult {
  ok: boolean
  status: string
  message: string
}

export function getCurrentPrincipal() {
  return apiGet<CurrentPrincipal>('/auth/me')
}

export function getWorkspace() {
  return apiGet<Workspace>('/workspace')
}

export function listMembers() {
  return apiGet<Member[]>('/members')
}

export function getSecuritySettings() {
  return apiGet<SecuritySettings>('/workspace/security-settings')
}

export function getLdapProviderConfig() {
  return apiGet<AuthProviderConfig>('/auth/providers/ldap')
}

export function updateLdapProviderConfig(payload: AuthProviderConfigUpdate) {
  return apiPatch<AuthProviderConfig, AuthProviderConfigUpdate>('/auth/providers/ldap', payload)
}

export function testLdapProviderConfig() {
  return apiPost<AuthProviderTestResult, Record<string, never>>('/auth/providers/ldap/test', {})
}
