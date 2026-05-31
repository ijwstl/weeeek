<template>
  <div class="reports-page">
    <div class="page-heading">
      <div>
        <h1>报告中心</h1>
        <p>统一查看待填报、草稿、已提交报告和历史版本。</p>
      </div>
      <div class="heading-actions">
        <n-button secondary @click="refreshTasks">
          <template #icon>
            <n-icon><RefreshCw /></n-icon>
          </template>
          刷新
        </n-button>
        <n-button type="primary" :disabled="!firstWritableTask" @click="openTask(firstWritableTask?.id)">
          <template #icon>
            <n-icon><PenLine /></n-icon>
          </template>
          填写报告
        </n-button>
      </div>
    </div>

    <section class="reports-toolbar panel">
      <div class="segmented-row report-filter">
        <button
          v-for="option in filterOptions"
          :key="option.value"
          class="segment"
          :class="{ active: activeFilter === option.value }"
          type="button"
          @click="activeFilter = option.value"
        >
          {{ option.label }}
        </button>
      </div>
      <div class="report-search">
        <n-icon><Search /></n-icon>
        <input v-model="keyword" placeholder="搜索报告类型、周期或状态" />
      </div>
    </section>

    <div class="reports-grid">
      <section class="panel report-list-panel">
        <div class="panel-header">
          <h2>我的报告</h2>
          <n-tag size="small" type="info">{{ filteredTasks.length }} 份</n-tag>
        </div>

        <div class="report-task-list">
          <article v-for="task in filteredTasks" :key="task.id" class="report-task-row">
            <div class="report-type-mark">
              <n-icon><component :is="task.report_type === 'weekly' ? CalendarDays : FileText" /></n-icon>
            </div>
            <div>
              <strong>{{ reportTitle(task) }}</strong>
              <span>{{ periodText(task) }} · 截止 {{ formatDateTime(task.due_at) }}</span>
            </div>
            <n-tag :type="statusTagType(task.status)" size="small">{{ statusText(task.status) }}</n-tag>
            <n-button size="small" secondary @click="openTask(task.id)">
              <template #icon>
                <n-icon><Pencil /></n-icon>
              </template>
              {{ task.status === 'submitted' ? '查看' : '填写' }}
            </n-button>
          </article>

          <div v-if="!filteredTasks.length" class="empty-state">
            <n-icon size="28"><Inbox /></n-icon>
            <span>当前筛选下没有报告</span>
          </div>
        </div>
      </section>

      <aside class="panel report-summary-panel">
        <div class="panel-header">
          <h2>本周期概览</h2>
          <n-tag size="small">个人</n-tag>
        </div>
        <div class="report-stat-grid">
          <div>
            <span>待处理</span>
            <strong>{{ pendingCount }}</strong>
          </div>
          <div>
            <span>草稿</span>
            <strong>{{ draftCount }}</strong>
          </div>
          <div>
            <span>已提交</span>
            <strong>{{ submittedCount }}</strong>
          </div>
          <div>
            <span>历史版本</span>
            <strong>{{ history?.length ?? 0 }}</strong>
          </div>
        </div>

        <section class="mini-section">
          <h3>最近提交</h3>
          <div class="history-list">
            <div v-for="item in history ?? []" :key="item.id" class="history-row">
              <span>v{{ item.version_no }}</span>
              <strong>{{ formatDateTime(item.submitted_at) }}</strong>
            </div>
            <p v-if="!history?.length" class="muted-text">暂无提交记录</p>
          </div>
        </section>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { NButton, NIcon, NTag } from 'naive-ui'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  CalendarDays,
  FileText,
  Inbox,
  Pencil,
  PenLine,
  RefreshCw,
  Search
} from 'lucide-vue-next'

import {
  listMyReportHistory,
  listMyReportTasks,
  type ReportInstance
} from '@/api/reports'

type FilterValue = 'all' | 'todo' | 'submitted'

const router = useRouter()
const activeFilter = ref<FilterValue>('all')
const keyword = ref('')

const {
  data: tasks,
  refetch: refetchTasks
} = useQuery({
  queryKey: ['my-report-tasks'],
  queryFn: listMyReportTasks
})

const { data: history } = useQuery({
  queryKey: ['my-report-history'],
  queryFn: listMyReportHistory
})

const filterOptions: Array<{ label: string; value: FilterValue }> = [
  { label: '全部', value: 'all' },
  { label: '待处理', value: 'todo' },
  { label: '已提交', value: 'submitted' }
]

const filteredTasks = computed(() => {
  const normalizedKeyword = keyword.value.trim().toLowerCase()
  return (tasks.value ?? []).filter((task) => {
    const matchesFilter =
      activeFilter.value === 'all' ||
      (activeFilter.value === 'todo' && task.status !== 'submitted') ||
      (activeFilter.value === 'submitted' && task.status === 'submitted')
    const haystack = `${reportTitle(task)} ${periodText(task)} ${statusText(task.status)}`.toLowerCase()
    return matchesFilter && (!normalizedKeyword || haystack.includes(normalizedKeyword))
  })
})

const firstWritableTask = computed(() =>
  (tasks.value ?? []).find((task) => task.status !== 'submitted')
)
const pendingCount = computed(() => (tasks.value ?? []).filter((task) => task.status === 'pending').length)
const draftCount = computed(() => (tasks.value ?? []).filter((task) => task.status === 'draft').length)
const submittedCount = computed(() =>
  (tasks.value ?? []).filter((task) => task.status === 'submitted').length
)

function openTask(reportId?: string) {
  if (reportId) {
    router.push(`/reports/${reportId}`)
  }
}

function refreshTasks() {
  refetchTasks()
}

function reportTitle(task: ReportInstance) {
  return task.report_type === 'weekly' ? '后端研发组周报' : '后端研发组日报'
}

function periodText(task: ReportInstance) {
  return task.period_start === task.period_end
    ? task.period_start
    : `${task.period_start} 至 ${task.period_end}`
}

function formatDateTime(value: string) {
  return value.replace('T', ' ').slice(0, 16)
}

function statusText(status: string) {
  const labels: Record<string, string> = {
    draft: '草稿',
    pending: '待填写',
    submitted: '已提交',
    overdue: '已逾期'
  }
  return labels[status] ?? status
}

function statusTagType(status: string) {
  if (status === 'overdue') return 'error' as const
  if (status === 'submitted') return 'success' as const
  if (status === 'pending') return 'warning' as const
  return 'info' as const
}
</script>
