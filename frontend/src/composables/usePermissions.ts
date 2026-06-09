import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'

import { getCurrentPrincipal } from '@/api/identity'

export const Permission = {
  DepartmentRead: 'department.read',
  DepartmentCreate: 'department.create',
  DepartmentUpdate: 'department.update',
  DepartmentDelete: 'department.delete',
  DepartmentMemberManage: 'department.member.manage',
  DepartmentRuleManage: 'department.rule.manage',
  DepartmentTemplateManage: 'department.template.manage',
  DepartmentReportView: 'department.report.view',
  DepartmentReportSummary: 'department.report.summary',
  ProjectRead: 'project.read',
  ProjectCreate: 'project.create',
  ProjectUpdate: 'project.update',
  ProjectArchive: 'project.archive',
  ProjectMemberManage: 'project.member.manage',
  ProjectRuleManage: 'project.rule.manage',
  ProjectTemplateManage: 'project.template.manage',
  ProjectProgressView: 'project.progress.view',
  ProjectSummaryView: 'project.summary.view',
  ReportReadOwn: 'report.read.own',
  ReportSubmitOwn: 'report.submit.own',
  ReportUpdateOwn: 'report.update.own',
  ReportReadSpace: 'report.read.space',
  ReportExport: 'report.export',
  TemplateCreate: 'template.create',
  TemplateUpdate: 'template.update',
  TemplatePublish: 'template.publish',
  DatasourceManageOwn: 'datasource.manage.own',
  DatasourceProviderManage: 'datasource.provider.manage',
  WorkspaceMemberManage: 'workspace.member.manage',
  WorkspaceRoleManage: 'workspace.role.manage',
  WorkspaceSettingManage: 'workspace.setting.manage',
  WorkspaceAuditView: 'workspace.audit.view',
  AiGenerateOwn: 'ai.generate.own',
  AiSummarySpace: 'ai.summary.space',
  NotificationChannelManage: 'notification.channel.manage',
  NotificationRuleManage: 'notification.rule.manage'
} as const

export type PermissionCode = (typeof Permission)[keyof typeof Permission]

export function usePermissions() {
  const { data: principal } = useQuery({
    queryKey: ['current-principal'],
    queryFn: getCurrentPrincipal
  })

  const permissionSet = computed(() => new Set(principal.value?.permissions ?? []))

  function hasPermission(permission: PermissionCode | string) {
    return permissionSet.value.has(permission)
  }

  function hasAnyPermission(permissions: Array<PermissionCode | string>) {
    return permissions.some((permission) => hasPermission(permission))
  }

  function hasEveryPermission(permissions: Array<PermissionCode | string>) {
    return permissions.every((permission) => hasPermission(permission))
  }

  return {
    principal,
    permissions: permissionSet,
    hasPermission,
    hasAnyPermission,
    hasEveryPermission
  }
}
