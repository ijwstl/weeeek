<template>
  <div class="report-fill-page">
    <div class="page-heading report-heading">
      <div>
        <n-button text class="back-button" @click="$router.back()">
          <template #icon>
            <n-icon><ArrowLeft /></n-icon>
          </template>
          返回
        </n-button>
        <h1>填写{{ reportTypeLabel }}</h1>
      </div>
      <div class="heading-actions">
        <n-button secondary :loading="saveDraftMutation.isPending.value" @click="handleSaveDraft">
          <template #icon>
            <n-icon><Save /></n-icon>
          </template>
          保存草稿
        </n-button>
        <n-button secondary @click="showAction('预览功能待接入')">
          <template #icon>
            <n-icon><Eye /></n-icon>
          </template>
          预览
        </n-button>
        <n-button type="primary" :loading="submitMutation.isPending.value" @click="handleSubmitReport">
          <template #icon>
            <n-icon><Send /></n-icon>
          </template>
          提交{{ reportTypeLabel }}
        </n-button>
      </div>
    </div>

    <section class="report-meta-strip">
      <div>
        <n-icon size="22"><Users /></n-icon>
        <strong>后端研发组 · {{ reportTypeLabel }}</strong>
      </div>
      <div>
        <n-icon><CalendarDays /></n-icon>
        <span>周期 {{ detail?.instance.period_start }} 至 {{ detail?.instance.period_end }}</span>
      </div>
      <div>
        <n-icon><Clock3 /></n-icon>
        <span>截止 {{ formatDateTime(detail?.instance.due_at) }}</span>
      </div>
      <div>
        <span>状态</span>
        <n-tag size="small" type="info">{{ detail?.instance.status }}</n-tag>
      </div>
    </section>

    <div class="report-fill-grid">
      <section class="panel report-form-panel">
        <div
          v-for="(group, groupIndex) in detail?.draft?.content_snapshot.groups ?? []"
          :key="group.group_id"
          class="report-snapshot-group"
        >
          <div class="section-title-row">
            <div>
              <span class="section-index">{{ groupIndex + 1 }}</span>
              <h2>{{ group.group_label_snapshot }}</h2>
            </div>
            <div class="section-tools">
              <n-button text size="small">
                <template #icon>
                  <n-icon><Maximize2 /></n-icon>
                </template>
              </n-button>
              <n-button text size="small">
                <template #icon>
                  <n-icon><MoreVertical /></n-icon>
                </template>
              </n-button>
            </div>
          </div>

          <article
            v-for="field in group.fields"
            :key="field.field_id"
            class="report-snapshot-field"
          >
            <div class="field-title">
              <span>{{ field.field_label_snapshot }}</span>
              <n-icon size="14"><Info /></n-icon>
            </div>
            <table v-if="field.field_type_snapshot === 'table'" class="report-table">
              <thead>
                <tr>
                  <th v-for="column in tableColumns(field)" :key="column.column_id">
                    {{ column.label }}
                  </th>
                  <th class="row-action-column"></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, index) in tableRows(field)" :key="index">
                  <td v-for="column in tableColumns(field)" :key="column.column_id">
                    <select
                      v-if="isSelectColumn(column)"
                      class="table-cell-input"
                      :value="String(row[column.column_id] ?? '')"
                      @change="updateTableCell(field.field_id, index, column.column_id, $event)"
                    >
                      <option value="">请选择{{ column.label }}</option>
                      <option v-for="option in columnOptions(column)" :key="option" :value="option">
                        {{ option }}
                      </option>
                    </select>
                    <input
                      v-else
                      class="table-cell-input"
                      :type="inputType(column.type)"
                      :value="String(row[column.column_id] ?? '')"
                      :placeholder="column.label"
                      @input="updateTableCell(field.field_id, index, column.column_id, $event)"
                    />
                  </td>
                  <td class="row-action-column">
                    <n-button text size="tiny" @click="removeTableRow(field.field_id, index)">
                      <template #icon>
                        <n-icon><Trash2 /></n-icon>
                      </template>
                    </n-button>
                  </td>
                </tr>
                <tr v-if="!tableColumns(field).length">
                  <td class="empty-table-hint" colspan="2">
                    模板列快照为空，请重新生成该报告实例或检查模板绑定。
                  </td>
                </tr>
              </tbody>
            </table>
            <button
              v-if="field.field_type_snapshot === 'table'"
              class="add-row-button"
              type="button"
              @click="addTableRow(field)"
            >
              <n-icon><Plus /></n-icon>
              添加{{ tableActionLabel(field.field_label_snapshot) }}
            </button>
            <div v-else class="field-card">
              {{ field.value }}
            </div>
          </article>
        </div>
      </section>

      <aside class="panel ai-panel">
        <div class="panel-header">
          <h2>AI 草稿助手</h2>
          <n-button text size="small">
            <template #icon>
              <n-icon><X /></n-icon>
            </template>
          </n-button>
        </div>
        <div class="ai-time-range">
          <span>选择数据来源（可多选）</span>
          <n-tag size="small" type="info">本周期</n-tag>
        </div>
        <div class="ai-source-list">
          <label v-for="source in aiSources" :key="source.id" class="ai-source-row">
            <input
              v-model="selectedDataSourceIds"
              :disabled="!source.available"
              :value="source.id"
              type="checkbox"
            />
            <n-icon size="22" :class="source.className">
              <component :is="source.icon" />
            </n-icon>
            <div>
              <strong>{{ source.name }}</strong>
              <span>{{ source.description }}</span>
            </div>
            <n-tag size="small" :type="source.selected ? 'success' : source.available ? 'info' : 'default'">
              {{ sourceStatusText(source) }}
            </n-tag>
          </label>
          <div v-if="!aiSources.length" class="empty-table-hint">
            暂无可用数据源，请先到数据源页面完成配置。
          </div>
        </div>
        <n-button
          block
          type="primary"
          class="ai-generate-button"
          :loading="aiDraftMutation.isPending.value"
          @click="generateAIDraft(false)"
        >
          <template #icon>
            <n-icon><Sparkles /></n-icon>
          </template>
          生成草稿
        </n-button>
        <n-button
          block
          secondary
          :loading="aiDraftMutation.isPending.value"
          @click="generateAIDraft(true)"
        >
          仅填充空字段
        </n-button>
        <div class="policy-list">
          <div><span>生成模式</span><strong>仅填充空字段</strong></div>
          <div><span>时间范围</span><strong>本周期</strong></div>
          <div><span>安全边界</span><strong>不读取同事数据</strong></div>
        </div>
      </aside>
    </div>

    <div class="sticky-action-bar">
      <div class="autosave-status">
        <n-icon><CheckCircle2 /></n-icon>
        <span>已自动保存 10:24:30</span>
      </div>
      <div class="heading-actions">
        <n-button secondary :loading="saveDraftMutation.isPending.value" @click="handleSaveDraft">
          <template #icon>
            <n-icon><Save /></n-icon>
          </template>
          保存草稿
        </n-button>
        <n-button secondary @click="showAction('预览功能待接入')">
          <template #icon>
            <n-icon><Eye /></n-icon>
          </template>
          预览
        </n-button>
        <n-button type="primary" :loading="submitMutation.isPending.value" @click="handleSubmitReport">
          <template #icon>
            <n-icon><Send /></n-icon>
          </template>
          提交{{ reportTypeLabel }}
        </n-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { NButton, NIcon, NTag, useMessage } from 'naive-ui'
import { computed, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  Clock3,
  Eye,
  FileText,
  Github,
  Gitlab,
  Info,
  Maximize2,
  MoreVertical,
  Plus,
  Save,
  Send,
  Sparkles,
  Trash2,
  Users,
  X
} from 'lucide-vue-next'

import {
  generateReportAIDraft,
  getReportDetail,
  saveReportDraft,
  submitReport,
  type ReportContentSnapshot,
  type ReportDraft,
  type ReportFieldSnapshot
} from '@/api/reports'
import { listDataSources, type DataSourceConnection } from '@/api/dataSources'

type TableColumnSnapshot = NonNullable<ReportFieldSnapshot['columns_snapshot']>[number]

const route = useRoute()
const message = useMessage()
const queryClient = useQueryClient()
const reportId = computed(() => String(route.params.reportId))
const tableDrafts = reactive<Record<string, Array<Record<string, unknown>>>>({})
const selectedDataSourceIds = ref<string[]>([])

const { data: detail } = useQuery({
  queryKey: ['report-detail', reportId],
  queryFn: () => getReportDetail(reportId.value)
})

const { data: dataSources } = useQuery({
  queryKey: ['data-sources'],
  queryFn: listDataSources
})

const saveDraftMutation = useMutation({
  mutationFn: () =>
    saveReportDraft(reportId.value, {
      content_snapshot: buildContentSnapshot(),
      ai_generated: Boolean(detail.value?.draft?.ai_generated)
    }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['report-detail'] })
    message.success('草稿已保存')
  }
})

const submitMutation = useMutation({
  mutationFn: () =>
    submitReport(reportId.value, {
      content_snapshot: buildContentSnapshot(),
      change_reason: '用户提交'
    }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['report-detail'] })
    queryClient.invalidateQueries({ queryKey: ['my-report-tasks'] })
    message.success('报告已提交')
  }
})

const aiDraftMutation = useMutation({
  mutationFn: (fillEmptyOnly: boolean) =>
    generateReportAIDraft(reportId.value, {
      data_source_ids: selectedDataSourceIds.value,
      fill_empty_only: fillEmptyOnly
  }),
  onSuccess: (draft) => {
    hydrateTableDrafts(draft, false)
    queryClient.invalidateQueries({ queryKey: ['report-detail'] })
    message.success('AI 草稿已生成，请确认后再提交')
  },
  onError: () => {
    message.error('AI 草稿生成失败，请检查数据源状态')
  }
})

watch(
  detail,
  (value) => {
    if (value?.draft) hydrateTableDrafts(value.draft, false)
  },
  { immediate: true }
)

watch(
  dataSources,
  (value) => {
    const enabledSourceIds = (value ?? [])
      .filter((source) => source.enabled && source.status !== 'disabled')
      .map((source) => source.id)
    selectedDataSourceIds.value = Array.from(
      new Set([...selectedDataSourceIds.value, ...enabledSourceIds])
    )
  },
  { immediate: true }
)

const reportTypeLabel = computed(() => {
  if (detail.value?.instance.report_type === 'daily') return '日报'
  return '周报'
})

const aiSources = computed(() =>
  (dataSources.value ?? []).map((source) => ({
    id: source.id,
    name: source.name,
    description: sourceDescription(source),
    available: source.enabled && source.status !== 'disabled',
    selected: selectedDataSourceIds.value.includes(source.id),
    icon: sourceIcon(source.source_type),
    className: sourceClass(source.source_type)
  }))
)

function hydrateTableDrafts(draft: ReportDraft, keepExisting = true) {
  for (const group of draft.content_snapshot.groups ?? []) {
    for (const field of group.fields) {
      if (field.field_type_snapshot !== 'table') continue
      if (keepExisting && tableDrafts[field.field_id]) continue
      tableDrafts[field.field_id] = Array.isArray(field.value)
        ? (field.value as Array<Record<string, unknown>>).map((row) => ({ ...row }))
        : []
    }
  }
}

function tableRows(field: ReportFieldSnapshot): Array<Record<string, unknown>> {
  return tableDrafts[field.field_id] ?? []
}

function tableColumns(field: ReportFieldSnapshot) {
  return field.columns_snapshot ?? []
}

function isSelectColumn(column: TableColumnSnapshot) {
  return ['single_select', 'risk_level', 'member_select', 'project_select'].includes(column.type)
}

function columnOptions(column: TableColumnSnapshot) {
  const configuredOptions = column.config?.options
  if (Array.isArray(configuredOptions)) {
    return configuredOptions.map(String)
  }
  if (column.type === 'risk_level') return ['low', 'medium', 'high']
  return []
}

function inputType(type: string) {
  if (type === 'number' || type === 'progress') return 'number'
  if (type === 'date') return 'date'
  if (type === 'url') return 'url'
  return 'text'
}

function addTableRow(field: ReportFieldSnapshot) {
  const rows = tableDrafts[field.field_id] ?? []
  const emptyRow = Object.fromEntries(
    (field.columns_snapshot ?? []).map((column) => [column.column_id, ''])
  )
  tableDrafts[field.field_id] = [...rows, emptyRow]
}

function removeTableRow(fieldId: string, index: number) {
  tableDrafts[fieldId] = (tableDrafts[fieldId] ?? []).filter((_, rowIndex) => rowIndex !== index)
}

function updateTableCell(fieldId: string, rowIndex: number, columnId: string, event: Event) {
  const target = event.target as HTMLInputElement
  const rows = tableDrafts[fieldId] ?? []
  tableDrafts[fieldId] = rows.map((row, index) =>
    index === rowIndex ? { ...row, [columnId]: target.value } : row
  )
}

function buildContentSnapshot(): ReportContentSnapshot {
  const snapshot = detail.value?.draft?.content_snapshot
  if (!snapshot) return { groups: [] }

  return {
    template_version_id: snapshot.template_version_id,
    groups: snapshot.groups.map((group) => ({
      ...group,
      fields: group.fields.map((field) => ({
        ...field,
        value:
          field.field_type_snapshot === 'table'
            ? (tableDrafts[field.field_id] ?? [])
            : field.value
      }))
    }))
  }
}

function handleSaveDraft() {
  if (!detail.value?.draft) {
    message.warning('当前报告没有可保存的草稿')
    return
  }
  saveDraftMutation.mutate()
}

function handleSubmitReport() {
  if (!detail.value?.draft) {
    message.warning('当前报告没有可提交的草稿')
    return
  }
  submitMutation.mutate()
}

function generateAIDraft(fillEmptyOnly: boolean) {
  if (!selectedDataSourceIds.value.length) {
    message.warning('请先选择至少一个可用数据源')
    return
  }
  aiDraftMutation.mutate(fillEmptyOnly)
}

function showAction(text: string) {
  message.info(text)
}

function formatDateTime(value?: string) {
  if (!value) return '-'
  return value.replace('T', ' ').slice(0, 16)
}

function tableActionLabel(label: string) {
  if (label.includes('风险')) return '风险'
  if (label.includes('计划')) return '计划事项'
  return '事项'
}

function sourceDescription(source: DataSourceConnection) {
  if (source.source_type === 'gitlab') return `${source.account_name} · 提交、MR、流水线`
  if (source.source_type === 'github') return `${source.account_name} · 提交、PR、Issue`
  if (source.source_type === 'jira') return `${source.account_name} · 任务、状态、评论`
  return `${source.account_name} · 自定义数据源`
}

function sourceIcon(type: string) {
  if (type === 'gitlab') return Gitlab
  if (type === 'github') return Github
  return FileText
}

function sourceClass(type: string) {
  if (type === 'gitlab') return 'source-gitlab'
  if (type === 'github') return 'source-github'
  if (type === 'jira') return 'source-jira'
  return 'source-history'
}

function sourceStatusText(source: { selected: boolean; available: boolean }) {
  if (!source.available) return '不可用'
  return source.selected ? '已选' : '未选'
}
</script>
