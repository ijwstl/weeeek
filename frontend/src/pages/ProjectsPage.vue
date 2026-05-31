<template>
  <div class="projects-page">
    <div class="page-heading">
      <div>
        <h1>项目团队</h1>
        <p>管理跨部门项目攻坚团队、目标周期和项目进度填报空间。</p>
      </div>
      <div class="heading-actions">
        <n-button type="primary" @click="startCreate">
          <template #icon>
            <n-icon><Plus /></n-icon>
          </template>
          新建项目团队
        </n-button>
      </div>
    </div>

    <div class="projects-grid">
      <section class="panel project-list-panel">
        <div class="panel-header">
          <h2>项目列表</h2>
          <n-tag size="small">{{ projectTeams?.length ?? 0 }} 个</n-tag>
        </div>
        <button
          v-for="project in projectTeams ?? []"
          :key="project.id"
          class="project-list-item"
          :class="{ active: selectedProjectId === project.id }"
          type="button"
          @click="selectProject(project.id)"
        >
          <strong>{{ project.name }}</strong>
          <span>{{ project.description || project.goal }}</span>
          <n-tag size="small" :type="statusTagType(project.status)">
            {{ statusText(project.status) }}
          </n-tag>
        </button>
      </section>

      <section class="panel project-detail-panel">
        <div class="panel-header">
          <div>
            <h2>{{ selectedProject?.name ?? '项目详情' }}</h2>
            <p>{{ selectedProject?.goal ?? '选择一个项目团队查看详情。' }}</p>
          </div>
          <div v-if="selectedProject" class="heading-actions">
            <n-button secondary size="small" @click="startEdit(selectedProject)">
              <template #icon>
                <n-icon><Pencil /></n-icon>
              </template>
              编辑
            </n-button>
            <n-button
              secondary
              size="small"
              :loading="statusMutation.isPending.value"
              @click="toggleArchive(selectedProject)"
            >
              <template #icon>
                <n-icon><Archive /></n-icon>
              </template>
              {{ selectedProject.status === 'archived' ? '恢复' : '归档' }}
            </n-button>
          </div>
        </div>

        <div v-if="selectedProject" class="project-summary-grid">
          <div>
            <span>状态</span>
            <strong>{{ statusText(selectedProject.status) }}</strong>
          </div>
          <div>
            <span>开始日期</span>
            <strong>{{ selectedProject.start_date ?? '-' }}</strong>
          </div>
          <div>
            <span>预计结束</span>
            <strong>{{ selectedProject.expected_end_date ?? '-' }}</strong>
          </div>
          <div>
            <span>报告模式</span>
            <strong>{{ reportModeText(selectedProject.report_space?.report_mode) }}</strong>
          </div>
        </div>

        <div v-if="selectedProject" class="project-section">
          <h3>目标</h3>
          <p>{{ selectedProject.goal || '未配置目标' }}</p>
        </div>

        <div v-if="selectedProject?.report_space" class="project-section">
          <h3>填报空间</h3>
          <div class="report-space-preview">
            <div>
              <span>空间名称</span>
              <strong>{{ selectedProject.report_space.name }}</strong>
            </div>
            <div>
              <span>成员可见性</span>
              <strong>{{ selectedProject.report_space.member_visibility }}</strong>
            </div>
            <div>
              <span>AI 草稿</span>
              <strong>{{ selectedProject.report_space.ai_enabled ? '开启' : '关闭' }}</strong>
            </div>
          </div>
          <div class="project-report-config">
            <label>
              <span>填报模式</span>
              <select v-model="projectReportForm.report_mode" class="rule-input">
                <option value="daily">日报</option>
                <option value="weekly">周报</option>
                <option value="daily_weekly">日报+周报</option>
              </select>
            </label>
            <label>
              <span>成员可见性</span>
              <select v-model="projectReportForm.member_visibility" class="rule-input">
                <option value="private">仅管理员/本人</option>
                <option value="department">团队成员互相可见</option>
              </select>
            </label>
            <label class="project-report-switch">
              <input v-model="projectReportForm.ai_enabled" type="checkbox" />
              AI 草稿
            </label>
            <div class="heading-actions">
              <n-button
                secondary
                :loading="saveReportSpaceMutation.isPending.value"
                @click="handleSaveReportSpace"
              >
                保存配置
              </n-button>
              <n-button
                type="primary"
                :loading="generateInstancesMutation.isPending.value"
                @click="handleGenerateReports"
              >
                生成本期报告
              </n-button>
            </div>
          </div>
        </div>

        <div v-if="selectedProject" class="project-section">
          <h3>成员角色</h3>
          <div class="project-member-add-row">
            <select v-model="memberForm.member_id" class="rule-input">
              <option value="">选择成员</option>
              <option v-for="member in addableMembers" :key="member.id" :value="member.id">
                {{ member.display_name }} · {{ member.employee_no }}
              </option>
            </select>
            <select v-model="memberForm.role" class="rule-input">
              <option value="project_member">普通项目成员</option>
              <option value="project_admin">项目管理员</option>
            </select>
            <n-button
              secondary
              :loading="addMemberMutation.isPending.value"
              @click="handleAddMember"
            >
              添加
            </n-button>
          </div>
          <div class="project-member-list">
            <div v-for="member in projectMembers ?? []" :key="member.member_id" class="project-member-row">
              <div class="avatar">{{ member.display_name.slice(0, 1) }}</div>
              <div>
                <strong>{{ member.display_name }}</strong>
                <span>{{ member.email }} · {{ member.employee_no }}</span>
              </div>
              <div class="member-role-actions">
                <select
                  class="role-select"
                  :value="member.role"
                  @change="handleRoleChange(member.member_id, $event)"
                >
                  <option value="project_admin">项目管理员</option>
                  <option value="project_member">普通成员</option>
                </select>
                <n-button text size="small" @click="handleRemoveMember(member.member_id)">
                  移除
                </n-button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <aside class="panel project-editor-panel">
        <div class="panel-header">
          <h2>{{ editingProjectId ? '编辑项目' : '新建项目' }}</h2>
          <n-tag size="small" type="info">跨部门</n-tag>
        </div>

        <div class="project-form">
          <label>
            <span>项目名称</span>
            <input v-model="projectForm.name" class="rule-input" />
          </label>
          <label>
            <span>描述</span>
            <input v-model="projectForm.description" class="rule-input" />
          </label>
          <label>
            <span>目标</span>
            <textarea v-model="projectForm.goal" class="project-textarea" />
          </label>
          <div class="project-date-grid">
            <label>
              <span>开始日期</span>
              <input v-model="projectForm.start_date" class="rule-input" type="date" />
            </label>
            <label>
              <span>预计结束</span>
              <input v-model="projectForm.expected_end_date" class="rule-input" type="date" />
            </label>
          </div>
          <label v-if="editingProjectId">
            <span>状态</span>
            <select v-model="projectForm.status" class="rule-input">
              <option value="not_started">未开始</option>
              <option value="in_progress">进行中</option>
              <option value="at_risk">有风险</option>
              <option value="completed">已完成</option>
              <option value="archived">已归档</option>
            </select>
          </label>
        </div>

        <div class="project-editor-actions">
          <n-button secondary @click="resetForm">重置</n-button>
          <n-button
            type="primary"
            :loading="saveProjectMutation.isPending.value"
            @click="handleSaveProject"
          >
            保存
          </n-button>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { NButton, NIcon, NTag, useMessage } from 'naive-ui'
import { Archive, Pencil, Plus } from 'lucide-vue-next'
import { computed, reactive, ref, watchEffect } from 'vue'

import {
  generateReportInstances,
  updateReportSpaceConfig,
  type ReportMode
} from '@/api/organization'
import {
  addProjectTeamMember,
  archiveProjectTeam,
  createProjectTeam,
  listAvailableProjectMembers,
  listProjectTeamMembers,
  listProjectTeams,
  removeProjectTeamMember,
  restoreProjectTeam,
  updateProjectTeamMember,
  updateProjectTeam,
  type ProjectTeam,
  type ProjectTeamMember
} from '@/api/projectTeams'

const message = useMessage()
const queryClient = useQueryClient()
const selectedProjectId = ref<string>()
const editingProjectId = ref<string>()
const projectForm = reactive({
  name: '',
  description: '',
  goal: '',
  start_date: '',
  expected_end_date: '',
  status: 'in_progress'
})
const memberForm = reactive<{ member_id: string; role: ProjectTeamMember['role'] }>({
  member_id: '',
  role: 'project_member'
})
const projectReportForm = reactive<{
  report_mode: ReportMode
  member_visibility: 'private' | 'department'
  ai_enabled: boolean
}>({
  report_mode: 'weekly',
  member_visibility: 'private',
  ai_enabled: true
})

const { data: projectTeams } = useQuery({
  queryKey: ['project-teams'],
  queryFn: listProjectTeams
})

const { data: availableMembers } = useQuery({
  queryKey: ['project-available-members'],
  queryFn: listAvailableProjectMembers
})

watchEffect(() => {
  if (!selectedProjectId.value && projectTeams.value?.length) {
    selectedProjectId.value = projectTeams.value[0].id
  }
})

const selectedProject = computed(() =>
  projectTeams.value?.find((project) => project.id === selectedProjectId.value)
)

watchEffect(() => {
  const space = selectedProject.value?.report_space
  if (!space) return
  projectReportForm.report_mode = space.report_mode
  projectReportForm.member_visibility =
    space.member_visibility === 'department' ? 'department' : 'private'
  projectReportForm.ai_enabled = space.ai_enabled
})

const { data: projectMembers } = useQuery({
  queryKey: ['project-members', selectedProjectId],
  queryFn: () => listProjectTeamMembers(selectedProjectId.value as string),
  enabled: computed(() => Boolean(selectedProjectId.value))
})

const addableMembers = computed(() => {
  const currentIds = new Set((projectMembers.value ?? []).map((member) => member.member_id))
  return (availableMembers.value ?? []).filter((member) => !currentIds.has(member.id))
})

const saveProjectMutation = useMutation({
  mutationFn: () => {
    if (editingProjectId.value) {
      return updateProjectTeam(editingProjectId.value, { ...projectForm })
    }
    return createProjectTeam({
      name: projectForm.name,
      description: projectForm.description,
      goal: projectForm.goal,
      start_date: projectForm.start_date || null,
      expected_end_date: projectForm.expected_end_date || null
    })
  },
  onSuccess: (project) => {
    selectedProjectId.value = project.id
    editingProjectId.value = project.id
    queryClient.invalidateQueries({ queryKey: ['project-teams'] })
    message.success('项目团队已保存')
  },
  onError: () => {
    message.error('项目团队保存失败')
  }
})

const statusMutation = useMutation({
  mutationFn: (project: ProjectTeam) =>
    project.status === 'archived'
      ? restoreProjectTeam(project.id)
      : archiveProjectTeam(project.id),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['project-teams'] })
    message.success('项目状态已更新')
  }
})

const addMemberMutation = useMutation({
  mutationFn: () =>
    addProjectTeamMember(selectedProjectId.value as string, {
      member_id: memberForm.member_id,
      role: memberForm.role
    }),
  onSuccess: () => {
    memberForm.member_id = ''
    invalidateProjectMembers()
    message.success('项目成员已添加')
  }
})

const updateMemberMutation = useMutation({
  mutationFn: ({
    memberId,
    role
  }: {
    memberId: string
    role: ProjectTeamMember['role']
  }) => updateProjectTeamMember(selectedProjectId.value as string, memberId, { role }),
  onSuccess: () => {
    invalidateProjectMembers()
    message.success('成员角色已更新')
  }
})

const removeMemberMutation = useMutation({
  mutationFn: (memberId: string) =>
    removeProjectTeamMember(selectedProjectId.value as string, memberId),
  onSuccess: () => {
    invalidateProjectMembers()
    message.success('项目成员已移除')
  }
})

const saveReportSpaceMutation = useMutation({
  mutationFn: () =>
    updateReportSpaceConfig(selectedProject.value?.report_space?.id as string, {
      report_mode: projectReportForm.report_mode,
      member_visibility: projectReportForm.member_visibility,
      ai_enabled: projectReportForm.ai_enabled
    }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['project-teams'] })
    message.success('项目填报配置已保存')
  },
  onError: () => {
    message.error('项目填报配置保存失败')
  }
})

const generateInstancesMutation = useMutation({
  mutationFn: () =>
    generateReportInstances(selectedProject.value?.report_space?.id as string, {}),
  onSuccess: (result) => {
    const total = result.created.length + result.existing.length
    queryClient.invalidateQueries({ queryKey: ['my-report-tasks'] })
    message.success(`已生成/确认 ${total} 个项目报告`)
  },
  onError: () => {
    message.error('项目报告生成失败')
  }
})

function selectProject(id: string) {
  selectedProjectId.value = id
}

function startCreate() {
  editingProjectId.value = undefined
  resetForm()
}

function startEdit(project: ProjectTeam) {
  editingProjectId.value = project.id
  projectForm.name = project.name
  projectForm.description = project.description
  projectForm.goal = project.goal
  projectForm.start_date = project.start_date ?? ''
  projectForm.expected_end_date = project.expected_end_date ?? ''
  projectForm.status = project.status
}

function resetForm() {
  projectForm.name = ''
  projectForm.description = ''
  projectForm.goal = ''
  projectForm.start_date = ''
  projectForm.expected_end_date = ''
  projectForm.status = 'in_progress'
}

function toggleArchive(project: ProjectTeam) {
  statusMutation.mutate(project)
}

function handleSaveProject() {
  if (!projectForm.name.trim()) {
    message.warning('请先填写项目名称')
    return
  }
  saveProjectMutation.mutate()
}

function handleSaveReportSpace() {
  if (!selectedProject.value?.report_space?.id) return
  saveReportSpaceMutation.mutate()
}

function handleGenerateReports() {
  if (!selectedProject.value?.report_space?.id) return
  generateInstancesMutation.mutate()
}

function handleAddMember() {
  if (!selectedProjectId.value || !memberForm.member_id) {
    message.warning('请先选择要添加的成员')
    return
  }
  addMemberMutation.mutate()
}

function handleRoleChange(memberId: string, event: Event) {
  updateMemberMutation.mutate({
    memberId,
    role: (event.target as HTMLSelectElement).value as ProjectTeamMember['role']
  })
}

function handleRemoveMember(memberId: string) {
  removeMemberMutation.mutate(memberId)
}

function invalidateProjectMembers() {
  queryClient.invalidateQueries({ queryKey: ['project-members'] })
  queryClient.invalidateQueries({ queryKey: ['project-available-members'] })
}

function statusText(status: string) {
  const labels: Record<string, string> = {
    not_started: '未开始',
    in_progress: '进行中',
    at_risk: '有风险',
    completed: '已完成',
    archived: '已归档'
  }
  return labels[status] ?? status
}

function statusTagType(status: string) {
  if (status === 'at_risk') return 'warning'
  if (status === 'archived') return 'default'
  if (status === 'completed') return 'success'
  return 'info'
}

function reportModeText(mode?: string) {
  if (mode === 'daily') return '日报'
  if (mode === 'daily_weekly') return '日报+周报'
  return '周报'
}
</script>
