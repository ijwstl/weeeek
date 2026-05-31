<template>
  <div class="dashboard">
    <div class="page-heading">
      <div>
        <h1>工作台</h1>
        <p>查看待填报、AI 草稿、团队提交状态和项目进展。</p>
      </div>
      <n-button type="primary" :disabled="!firstTask" @click="openFirstTask">
        <template #icon>
          <n-icon><PenLine /></n-icon>
        </template>
        填写报告
      </n-button>
    </div>

    <div class="dashboard-grid">
      <section class="panel tasks-panel">
        <div class="panel-header">
          <h2>我的待填报</h2>
          <n-tag size="small" type="info">{{ tasks.length }} 项</n-tag>
        </div>

        <div class="task-list">
          <article v-for="task in tasks" :key="task.id" class="task-row">
            <div>
              <strong>{{ task.title }}</strong>
              <span>{{ task.type }} · 截止 {{ task.due }}</span>
            </div>
            <n-tag :type="task.tagType" size="small">{{ task.statusText }}</n-tag>
            <n-button size="small" secondary @click="$router.push(`/reports/${task.id}`)">
              <template #icon>
                <n-icon><Pencil /></n-icon>
              </template>
              填写
            </n-button>
          </article>
        </div>
      </section>

      <section class="panel draft-panel">
        <div class="panel-header">
          <h2>周报草稿</h2>
          <n-button size="small" secondary>
            <template #icon>
              <n-icon><Sparkles /></n-icon>
            </template>
            AI 生成草稿
          </n-button>
        </div>

        <div class="source-chips">
          <n-tag v-for="source in sources" :key="source" size="small" round>{{ source }}</n-tag>
        </div>

        <div class="field-group">
          <div class="field-title">本周完成事项</div>
          <table class="report-table">
            <thead>
              <tr>
                <th>事项</th>
                <th>来源</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>登录模块重构</td>
                <td>GitLab</td>
                <td><span class="status done">已完成</span></td>
              </tr>
              <tr>
                <td>Jira 数据同步设计</td>
                <td>Jira</td>
                <td><span class="status active">进行中</span></td>
              </tr>
              <tr>
                <td>周报模板明细表字段</td>
                <td>项目进度</td>
                <td><span class="status done">已完成</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="field-grid">
          <div class="field-card">
            <span>风险与阻塞</span>
            <strong>Jira OAuth 刷新策略待确认</strong>
          </div>
          <div class="field-card">
            <span>下周计划</span>
            <strong>完成 ReportSpace 与模板绑定接口</strong>
          </div>
        </div>
      </section>

      <aside class="panel status-panel">
        <div class="panel-header">
          <h2>提交状态</h2>
          <n-tag size="small" type="success">本周期</n-tag>
        </div>
        <div class="progress-block">
          <div class="progress-number">18 / 24</div>
          <n-progress type="line" :percentage="75" :height="8" :show-indicator="false" />
          <span>后端研发组已提交</span>
        </div>

        <div class="mini-section">
          <h3>未提交成员</h3>
          <div class="member-line">李明 · 王凯 · 陈雪</div>
        </div>

        <div class="mini-section">
          <h3>风险提示</h3>
          <div class="risk-line">3 条高优先级阻塞需要关注</div>
        </div>
      </aside>
    </div>

    <section class="panel project-panel">
      <div class="panel-header">
        <h2>项目团队进展</h2>
        <n-button size="small" text>
          <template #icon>
            <n-icon><ArrowRight /></n-icon>
          </template>
          查看全部
        </n-button>
      </div>
      <div class="project-list">
        <div v-for="project in projects" :key="project.name" class="project-row">
          <div>
            <strong>{{ project.name }}</strong>
            <span>{{ project.desc }}</span>
          </div>
          <n-progress
            type="line"
            :percentage="project.progress"
            :height="8"
            :show-indicator="false"
          />
          <n-tag :type="project.tagType" size="small">{{ project.status }}</n-tag>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { NButton, NProgress, NTag } from 'naive-ui'
import { useQuery } from '@tanstack/vue-query'
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowRight, Pencil, PenLine, Sparkles } from 'lucide-vue-next'
import { NIcon } from 'naive-ui'

import { listMyReportTasks } from '@/api/reports'

const { data: reportTasks } = useQuery({
  queryKey: ['my-report-tasks'],
  queryFn: listMyReportTasks
})
const router = useRouter()

const fallbackTasks = [
  {
    id: 'weekly',
    title: '后端研发组周报',
    type: '部门周报',
    due: '周五 19:00',
    statusText: '草稿',
    tagType: 'info' as const
  },
  {
    id: 'project',
    title: 'A 项目进度',
    type: '项目进度',
    due: '今天 18:00',
    statusText: '待填写',
    tagType: 'warning' as const
  },
  {
    id: 'overdue',
    title: '接口联调日报',
    type: '逾期日报',
    due: '昨天 20:00',
    statusText: '已逾期',
    tagType: 'error' as const
  }
]

const tasks = computed(() =>
  reportTasks.value
    ? reportTasks.value.map((task) => ({
      id: task.id,
      title: task.report_type === 'weekly' ? '后端研发组周报' : '后端研发组日报',
      type: task.report_type === 'weekly' ? '部门周报' : '部门日报',
      due: task.due_at.replace('T', ' ').slice(0, 16),
      statusText: statusText(task.status),
      tagType: statusTagType(task.status)
    }))
    : fallbackTasks
)

const firstTask = computed(() => tasks.value[0])

function openFirstTask() {
  if (firstTask.value) {
    router.push(`/reports/${firstTask.value.id}`)
  }
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

const sources = ['GitLab', 'GitHub', 'Jira', '项目进度']

const projects = [
  { name: 'A 项目攻坚', desc: '支付链路重构', progress: 68, status: '有风险', tagType: 'warning' as const },
  { name: '报表平台 MVP', desc: '模板与 AI 草稿', progress: 42, status: '进行中', tagType: 'info' as const },
  { name: '稳定性治理', desc: '告警降噪与巡检', progress: 81, status: '正常', tagType: 'success' as const }
]
</script>
