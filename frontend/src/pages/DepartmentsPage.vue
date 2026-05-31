<template>
  <div class="departments-page">
    <div class="page-heading">
      <div>
        <h1>部门管理</h1>
        <p>管理部门树、成员归属、填报空间和可见性策略。</p>
      </div>
      <n-button type="primary" @click="showAction('新建部门接口待接入')">
        <template #icon>
          <n-icon><Plus /></n-icon>
        </template>
        新建部门
      </n-button>
    </div>

    <div class="department-grid">
      <section class="panel department-tree-panel">
        <div class="panel-header">
          <h2>部门树</h2>
          <n-tag size="small">最大 5 层</n-tag>
        </div>

        <div class="department-tree">
          <DepartmentNode
            v-for="node in departments ?? []"
            :key="node.id"
            :node="node"
            :selected-id="selectedDepartmentId"
            @select="selectedDepartmentId = $event"
          />
        </div>
      </section>

      <section class="panel department-config-panel">
        <div class="panel-header">
          <div>
            <h2>{{ selectedDepartment?.name ?? '部门配置' }}</h2>
            <p>{{ selectedDepartment?.path }}</p>
          </div>
          <n-tag size="small" type="success">{{ selectedDepartment?.status }}</n-tag>
        </div>

        <div class="tab-row">
          <button
            class="tab"
            :class="{ active: activeDepartmentTab === 'rules' }"
            type="button"
            @click="activeDepartmentTab = 'rules'"
          >
            填报规则
          </button>
          <button
            class="tab"
            :class="{ active: activeDepartmentTab === 'templates' }"
            type="button"
            @click="activeDepartmentTab = 'templates'"
          >
            模板
          </button>
          <button
            class="tab"
            :class="{ active: activeDepartmentTab === 'visibility' }"
            type="button"
            @click="activeDepartmentTab = 'visibility'"
          >
            权限与可见性
          </button>
          <button
            class="tab"
            :class="{ active: activeDepartmentTab === 'members' }"
            type="button"
            @click="activeDepartmentTab = 'members'"
          >
            成员
          </button>
        </div>

        <div v-if="activeDepartmentTab === 'rules'" class="config-sections">
          <section class="config-section">
            <h3>报告模式</h3>
            <div class="segmented-row">
              <button
                class="segment"
                :class="{ active: activeReportMode === 'daily' }"
                type="button"
                @click="activeReportMode = 'daily'"
              >
                仅日报
              </button>
              <button
                class="segment"
                :class="{ active: activeReportMode === 'weekly' }"
                type="button"
                @click="activeReportMode = 'weekly'"
              >
                仅周报
              </button>
              <button
                class="segment"
                :class="{ active: activeReportMode === 'daily_weekly' }"
                type="button"
                @click="activeReportMode = 'daily_weekly'"
              >
                日报+周报
              </button>
            </div>
          </section>

          <section v-if="showWeeklyRule" class="config-section rule-preview">
            <h3>周报规则 <n-tag size="small" type="info">启用</n-tag></h3>
            <div class="rule-grid">
              <div>
                <span>周起始日</span>
                <select v-model.number="weeklyRuleForm.week_start_day" class="rule-input">
                  <option v-for="day in weekDayOptions" :key="day.value" :value="day.value">
                    {{ day.label }}
                  </option>
                </select>
              </div>
              <div>
                <span>提醒日</span>
                <select v-model.number="weeklyRuleForm.reminder_day" class="rule-input">
                  <option v-for="day in weekDayOptions" :key="day.value" :value="day.value">
                    {{ day.label }}
                  </option>
                </select>
              </div>
              <div>
                <span><n-icon><Clock3 /></n-icon> 提醒时间</span>
                <input v-model="weeklyRuleForm.reminder_time" class="rule-input" type="time" />
              </div>
              <div>
                <span><n-icon><Clock3 /></n-icon> 截止时间</span>
                <div class="rule-combo">
                  <select v-model.number="weeklyRuleForm.due_day" class="rule-input">
                    <option v-for="day in weekDayOptions" :key="day.value" :value="day.value">
                      {{ day.label }}
                    </option>
                  </select>
                  <input v-model="weeklyRuleForm.due_time" class="rule-input" type="time" />
                </div>
              </div>
            </div>
          </section>

          <section v-if="showDailyRule" class="config-section rule-preview">
            <h3>日报规则 <n-tag size="small" type="info">启用</n-tag></h3>
            <div class="rule-grid">
              <div>
                <span>频率</span>
                <strong>每天</strong>
              </div>
              <div>
                <span>跳过周末</span>
                <n-switch v-model:value="dailyRuleForm.skip_weekends" size="small" />
              </div>
              <div>
                <span><n-icon><Clock3 /></n-icon> 提醒时间</span>
                <input v-model="dailyRuleForm.reminder_time" class="rule-input" type="time" />
              </div>
              <div>
                <span><n-icon><Clock3 /></n-icon> 截止时间</span>
                <input v-model="dailyRuleForm.due_time" class="rule-input" type="time" />
              </div>
            </div>
          </section>
        </div>

        <div v-if="activeDepartmentTab === 'templates'" class="config-sections">
          <section class="config-section">
            <h3>模板绑定</h3>
            <div class="template-binding-list">
              <div v-if="showDailyRule" class="template-binding-row">
                <div>
                  <span>日报模板</span>
                  <strong>{{ templateName(templateBindings.daily.template_id) }}</strong>
                </div>
                <select v-model="templateBindings.daily.template_id" class="rule-input">
                  <option value="">未绑定</option>
                  <option v-for="template in templates ?? []" :key="template.id" :value="template.id">
                    {{ template.name }}
                  </option>
                </select>
              </div>
              <div v-if="showWeeklyRule" class="template-binding-row">
                <div>
                  <span>周报模板</span>
                  <strong>{{ templateName(templateBindings.weekly.template_id) }}</strong>
                </div>
                <select v-model="templateBindings.weekly.template_id" class="rule-input">
                  <option value="">未绑定</option>
                  <option v-for="template in templates ?? []" :key="template.id" :value="template.id">
                    {{ template.name }}
                  </option>
                </select>
              </div>
            </div>
          </section>

          <section class="config-section">
            <h3>版本策略</h3>
            <div class="inline-config-row">
              <div>
                <span>新报告使用版本</span>
                <strong>发布后自动使用最新版本</strong>
              </div>
              <n-tag size="small" type="info">latest_published</n-tag>
            </div>
          </section>

          <section class="config-section">
            <h3>当前周报字段预览</h3>
            <div class="field-grid">
              <div class="field-card"><span>本周完成事项</span><strong>表格字段</strong></div>
              <div class="field-card"><span>下周计划</span><strong>表格字段</strong></div>
              <div class="field-card"><span>风险与阻塞</span><strong>表格字段</strong></div>
              <div class="field-card"><span>补充说明</span><strong>长文本字段</strong></div>
            </div>
          </section>
        </div>

        <div v-if="activeDepartmentTab === 'visibility'" class="config-sections">
          <section class="config-section">
            <h3>报告可见性</h3>
            <div class="inline-config-row">
              <div>
                <span>成员是否可以相互查看报告</span>
                <strong>{{ visibilityLabel }}</strong>
              </div>
              <n-switch v-model:value="memberVisibilityEnabled" />
            </div>
          </section>

          <section class="config-section">
            <h3>AI 与数据源允许</h3>
            <div class="toggle-chip-row">
              <span class="active"><Sparkles :size="16" /> AI 辅助</span>
              <span class="active"><GitBranch :size="16" /> Git</span>
              <span class="active"><FolderKanban :size="16" /> Jira</span>
              <span><FileText :size="16" /> 历史报告</span>
            </div>
          </section>
        </div>

        <div v-if="activeDepartmentTab === 'members'" class="config-sections">
          <section class="config-section">
            <h3>成员概览</h3>
            <div class="rule-grid">
              <div>
                <span>成员数量</span>
                <strong>{{ submissionStatus?.total_members ?? 0 }} 人</strong>
              </div>
              <div>
                <span>部门管理员</span>
                <strong>2 人</strong>
              </div>
              <div>
                <span>本周期已提交</span>
                <strong>{{ submissionStatus?.submitted_members ?? 0 }} 人</strong>
              </div>
              <div>
                <span>待提交</span>
                <strong>{{ submissionStatus?.pending_members ?? 0 }} 人</strong>
              </div>
            </div>
          </section>

          <section class="config-section">
            <h3>成员操作</h3>
            <div class="heading-actions">
              <n-button secondary @click="showAction('添加成员接口待接入')">添加成员</n-button>
              <n-button secondary @click="showAction('批量导入接口待接入')">批量导入</n-button>
              <n-button secondary @click="showAction('成员同步接口待接入')">同步 LDAP</n-button>
            </div>
          </section>
        </div>
      </section>

      <aside class="panel department-summary-panel">
        <div class="panel-header">
          <h2>本部门配置摘要</h2>
          <n-tag size="small" type="info">已发布</n-tag>
        </div>

        <div class="definition-list">
          <div>
            <span>部门名称</span>
            <strong>{{ selectedDepartment?.name ?? '-' }}</strong>
          </div>
          <div>
            <span>负责人</span>
            <strong>王琪</strong>
          </div>
          <div>
            <span>部门管理员</span>
            <strong>2 人</strong>
          </div>
          <div>
            <span>成员数量</span>
            <strong>{{ submissionStatus?.total_members ?? 0 }} 人</strong>
          </div>
          <div>
            <span>报告模式</span>
            <strong>{{ reportModeLabel }}</strong>
          </div>
          <div>
            <span>子部门</span>
            <strong>{{ selectedDepartment?.children.length ?? 0 }} 个</strong>
          </div>
          <div>
            <span>最近修改</span>
            <strong>今天 10:24</strong>
          </div>
        </div>

        <n-button
          block
          type="primary"
          class="summary-primary-button"
          :loading="saveConfigMutation.isPending.value"
          @click="saveDepartmentConfig"
        >
          <template #icon>
            <n-icon><Save /></n-icon>
          </template>
          保存配置
        </n-button>
        <n-button
          block
          secondary
          :loading="generateInstancesMutation.isPending.value"
          @click="generateCurrentReports"
        >
          <template #icon>
            <n-icon><FileText /></n-icon>
          </template>
          生成本周期报告
        </n-button>
        <n-button block secondary @click="resetLocalConfig">
          <template #icon>
            <n-icon><RotateCcw /></n-icon>
          </template>
          重置为默认
        </n-button>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { NButton, NIcon, NSwitch, NTag, useMessage } from 'naive-ui'
import { computed, ref, watchEffect } from 'vue'
import {
  Clock3,
  FileText,
  FolderKanban,
  GitBranch,
  Plus,
  RotateCcw,
  Save,
  Sparkles
} from 'lucide-vue-next'

import {
  generateReportInstances,
  getDepartmentSubmissionStatus,
  getDepartmentTree,
  listReportRules,
  updateReportRule,
  updateReportSpaceConfig,
  type ReportMode,
  type ReportRule,
  type ReportRuleUpsert,
  type TemplateBinding,
  type DepartmentTreeNode
} from '@/api/organization'
import DepartmentNode from '@/components/DepartmentNode.vue'
import { listTemplates } from '@/api/templates'

const { data: departments } = useQuery({
  queryKey: ['departments-tree'],
  queryFn: getDepartmentTree
})

const { data: templates } = useQuery({
  queryKey: ['templates'],
  queryFn: listTemplates
})

const message = useMessage()
const queryClient = useQueryClient()
const selectedDepartmentId = ref<string>()
const activeDepartmentTab = ref<'rules' | 'templates' | 'visibility' | 'members'>('rules')
const activeReportMode = ref<ReportMode>('weekly')
const memberVisibilityEnabled = ref(true)
const weekDayOptions = [
  { value: 1, label: '周一' },
  { value: 2, label: '周二' },
  { value: 3, label: '周三' },
  { value: 4, label: '周四' },
  { value: 5, label: '周五' },
  { value: 6, label: '周六' },
  { value: 7, label: '周日' }
]
const weeklyRuleForm = ref({
  week_start_day: 1,
  reminder_day: 5,
  reminder_time: '17:00',
  due_day: 5,
  due_time: '19:00'
})
const dailyRuleForm = ref({
  reminder_time: '18:00',
  due_time: '20:00',
  skip_weekends: true
})
const templateBindings = ref({
  daily: { template_id: '', version_policy: 'latest_published' } as TemplateBinding,
  weekly: { template_id: '', version_policy: 'latest_published' } as TemplateBinding
})

function flatten(nodes: DepartmentTreeNode[]): DepartmentTreeNode[] {
  return nodes.flatMap((node) => [node, ...flatten(node.children)])
}

const allDepartments = computed(() => flatten(departments.value ?? []))

watchEffect(() => {
  if (!selectedDepartmentId.value && allDepartments.value.length) {
    selectedDepartmentId.value = allDepartments.value[0].id
  }
})

const selectedDepartment = computed(() =>
  allDepartments.value.find((department) => department.id === selectedDepartmentId.value)
)

const selectedReportSpaceId = computed(() => selectedDepartment.value?.report_space?.id)

const { data: submissionStatus } = useQuery({
  queryKey: ['department-submission-status', selectedDepartmentId],
  queryFn: () => getDepartmentSubmissionStatus(selectedDepartmentId.value as string),
  enabled: computed(() => Boolean(selectedDepartmentId.value))
})

const { data: reportRules } = useQuery({
  queryKey: ['report-rules', selectedReportSpaceId],
  queryFn: () => listReportRules(selectedReportSpaceId.value as string),
  enabled: computed(() => Boolean(selectedReportSpaceId.value))
})

const weeklyRule = computed(() => reportRules.value?.find((rule) => rule.report_type === 'weekly'))
const dailyRule = computed(() => reportRules.value?.find((rule) => rule.report_type === 'daily'))
const showDailyRule = computed(() => ['daily', 'daily_weekly'].includes(activeReportMode.value))
const showWeeklyRule = computed(() => ['weekly', 'daily_weekly'].includes(activeReportMode.value))

const visibilityLabel = computed(() =>
  memberVisibilityEnabled.value ? '允许部门成员互看' : '仅管理员可见'
)
const reportModeLabel = computed(() => {
  const labels: Record<ReportMode, string> = {
    daily: '仅日报',
    weekly: '仅周报',
    daily_weekly: '日报+周报'
  }
  return labels[activeReportMode.value]
})

const saveConfigMutation = useMutation({
  mutationFn: async () => {
    if (!selectedReportSpaceId.value) {
      throw new Error('Report space missing')
    }
    const reportSpace = await updateReportSpaceConfig(selectedReportSpaceId.value, {
      report_mode: activeReportMode.value,
      member_visibility: memberVisibilityEnabled.value ? 'department' : 'private',
      ai_enabled: true,
      allowed_data_source_types: ['git', 'jira', 'project_progress', 'history'],
      template_bindings: buildTemplateBindings()
    })

    const updates: Array<Promise<ReportRule>> = []
    if (showWeeklyRule.value) {
      updates.push(updateReportRule(selectedReportSpaceId.value, 'weekly', weeklyRulePayload()))
    }
    if (showDailyRule.value) {
      updates.push(updateReportRule(selectedReportSpaceId.value, 'daily', dailyRulePayload()))
    }
    await Promise.all(updates)
    return reportSpace
  },
  onSuccess: (reportSpace) => {
    activeReportMode.value = reportSpace.report_mode
    memberVisibilityEnabled.value = reportSpace.member_visibility === 'department'
    queryClient.invalidateQueries({ queryKey: ['report-rules'] })
    message.success('部门配置已保存')
  },
  onError: () => {
    message.error('保存部门配置失败')
  }
})

const generateInstancesMutation = useMutation({
  mutationFn: () => {
    if (!selectedReportSpaceId.value) {
      throw new Error('Report space missing')
    }
    return generateReportInstances(selectedReportSpaceId.value)
  },
  onSuccess: (result) => {
    queryClient.invalidateQueries({ queryKey: ['my-report-tasks'] })
    const createdCount = result.created.length
    const existingCount = result.existing.length
    message.success(`已生成 ${createdCount} 份报告，已有 ${existingCount} 份`)
  },
  onError: () => {
    message.error('生成本周期报告失败')
  }
})

watchEffect(() => {
  memberVisibilityEnabled.value =
    selectedDepartment.value?.report_space?.member_visibility === 'department'
  activeReportMode.value = selectedDepartment.value?.report_space?.report_mode ?? 'weekly'
  const bindings = selectedDepartment.value?.report_space?.template_bindings ?? {}
  templateBindings.value = {
    daily: {
      template_id: bindings.daily?.template_id ?? '',
      version_policy: bindings.daily?.version_policy ?? 'latest_published'
    },
    weekly: {
      template_id: bindings.weekly?.template_id ?? '',
      version_policy: bindings.weekly?.version_policy ?? 'latest_published'
    }
  }
})

watchEffect(() => {
  if (weeklyRule.value) {
    weeklyRuleForm.value = {
      week_start_day: weeklyRule.value.week_start_day ?? 1,
      reminder_day: weeklyRule.value.reminder_day ?? 5,
      reminder_time: weeklyRule.value.reminder_time ?? '17:00',
      due_day: weeklyRule.value.due_day ?? 5,
      due_time: weeklyRule.value.due_time ?? '19:00'
    }
  }
  if (dailyRule.value) {
    dailyRuleForm.value = {
      reminder_time: dailyRule.value.reminder_time ?? '18:00',
      due_time: dailyRule.value.due_time ?? '20:00',
      skip_weekends: dailyRule.value.skip_weekends
    }
  }
})

function resetLocalConfig() {
  activeReportMode.value = selectedDepartment.value?.report_space?.report_mode ?? 'weekly'
  memberVisibilityEnabled.value =
    selectedDepartment.value?.report_space?.member_visibility === 'department'
  message.info('已重置为当前部门默认配置')
}

function saveDepartmentConfig() {
  if (!selectedReportSpaceId.value) {
    message.warning('当前部门没有填报空间')
    return
  }
  saveConfigMutation.mutate()
}

function generateCurrentReports() {
  if (!selectedReportSpaceId.value) {
    message.warning('当前部门没有填报空间')
    return
  }
  generateInstancesMutation.mutate()
}

function showAction(text: string) {
  message.info(text)
}

function buildTemplateBindings() {
  const bindings: Record<string, { template_id: string; version_policy: 'latest_published' }> = {}
  if (showDailyRule.value && templateBindings.value.daily.template_id) {
    bindings.daily = {
      template_id: templateBindings.value.daily.template_id,
      version_policy: 'latest_published'
    }
  }
  if (showWeeklyRule.value && templateBindings.value.weekly.template_id) {
    bindings.weekly = {
      template_id: templateBindings.value.weekly.template_id,
      version_policy: 'latest_published'
    }
  }
  return bindings
}

function templateName(templateId?: string) {
  return templates.value?.find((template) => template.id === templateId)?.name ?? '未绑定'
}

function weeklyRulePayload(): ReportRuleUpsert {
  return {
    enabled: showWeeklyRule.value,
    frequency: 'weekly',
    interval_value: null,
    week_start_day: weeklyRuleForm.value.week_start_day,
    reminder_day: weeklyRuleForm.value.reminder_day,
    reminder_time: weeklyRuleForm.value.reminder_time,
    due_type: 'weekday',
    due_day: weeklyRuleForm.value.due_day,
    due_time: weeklyRuleForm.value.due_time,
    skip_weekends: false,
    notification_channels: weeklyRule.value?.notification_channels ?? ['in_app', 'feishu'],
    overdue_policy: weeklyRule.value?.overdue_policy ?? {},
    extra_config: weeklyRule.value?.extra_config ?? {}
  }
}

function dailyRulePayload(): ReportRuleUpsert {
  return {
    enabled: showDailyRule.value,
    frequency: 'daily',
    interval_value: null,
    week_start_day: null,
    reminder_day: null,
    reminder_time: dailyRuleForm.value.reminder_time,
    due_type: 'same_day',
    due_day: null,
    due_time: dailyRuleForm.value.due_time,
    skip_weekends: dailyRuleForm.value.skip_weekends,
    notification_channels: dailyRule.value?.notification_channels ?? ['in_app', 'feishu'],
    overdue_policy: dailyRule.value?.overdue_policy ?? {},
    extra_config: dailyRule.value?.extra_config ?? {}
  }
}

function dayLabel(day?: number | null) {
  const labels = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
  return day ? labels[day] : '-'
}
</script>
