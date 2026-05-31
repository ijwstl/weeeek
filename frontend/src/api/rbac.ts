import { apiGet } from './client'

export interface Permission {
  code: string
  name: string
  description: string
  category: string
  resource_type: string
  action: string
  is_system: boolean
}

export interface Role {
  id: string
  code: string
  name: string
  description: string
  is_builtin: boolean
  is_editable: boolean
  permissions: string[]
}

export function listPermissions() {
  return apiGet<Permission[]>('/permissions')
}

export function listRoles() {
  return apiGet<Role[]>('/roles')
}

