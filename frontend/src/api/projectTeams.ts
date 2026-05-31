import { apiDelete, apiGet, apiPatch, apiPost } from './client'
import type { Member } from './identity'
import type { ReportSpace } from './organization'

export interface ProjectTeam {
  id: string
  workspace_id: string
  name: string
  description: string
  goal: string
  status: string
  start_date?: string | null
  expected_end_date?: string | null
  actual_end_date?: string | null
  report_space?: ReportSpace | null
}

export interface ProjectTeamCreate {
  name: string
  description: string
  goal: string
  start_date?: string | null
  expected_end_date?: string | null
}

export interface ProjectTeamUpdate {
  name?: string
  description?: string
  goal?: string
  status?: string
  start_date?: string | null
  expected_end_date?: string | null
  actual_end_date?: string | null
}

export interface ProjectTeamMember {
  project_team_id: string
  member_id: string
  role: 'project_admin' | 'project_member'
  display_name: string
  email?: string | null
  employee_no?: string | null
  status: string
}

export function listProjectTeams() {
  return apiGet<ProjectTeam[]>('/project-teams')
}

export function listAvailableProjectMembers() {
  return apiGet<Member[]>('/project-teams/available-members')
}

export function listProjectTeamMembers(projectTeamId: string) {
  return apiGet<ProjectTeamMember[]>(`/project-teams/${projectTeamId}/members`)
}

export function addProjectTeamMember(
  projectTeamId: string,
  payload: { member_id: string; role: ProjectTeamMember['role'] }
) {
  return apiPost<ProjectTeamMember, typeof payload>(
    `/project-teams/${projectTeamId}/members`,
    payload
  )
}

export function updateProjectTeamMember(
  projectTeamId: string,
  memberId: string,
  payload: { role: ProjectTeamMember['role'] }
) {
  return apiPatch<ProjectTeamMember, typeof payload>(
    `/project-teams/${projectTeamId}/members/${memberId}`,
    payload
  )
}

export function removeProjectTeamMember(projectTeamId: string, memberId: string) {
  return apiDelete<{ ok: boolean }>(`/project-teams/${projectTeamId}/members/${memberId}`)
}

export function createProjectTeam(payload: ProjectTeamCreate) {
  return apiPost<ProjectTeam, ProjectTeamCreate>('/project-teams', payload)
}

export function updateProjectTeam(id: string, payload: ProjectTeamUpdate) {
  return apiPatch<ProjectTeam, ProjectTeamUpdate>(`/project-teams/${id}`, payload)
}

export function archiveProjectTeam(id: string) {
  return apiPost<ProjectTeam, Record<string, never>>(`/project-teams/${id}/archive`, {})
}

export function restoreProjectTeam(id: string) {
  return apiPost<ProjectTeam, Record<string, never>>(`/project-teams/${id}/restore`, {})
}
