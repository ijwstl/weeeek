<template>
  <div class="data-sources-page">
    <div class="page-heading">
      <div>
        <h1>数据源与 AI 设置</h1>
        <p>连接个人数据源，控制 AI 生成周报时可以使用的上下文。</p>
      </div>
      <div class="heading-actions">
        <n-button secondary :loading="syncAllMutation.isPending.value" @click="syncAllMutation.mutate()">
          <template #icon>
            <n-icon><RefreshCw /></n-icon>
          </template>
          同步全部
        </n-button>
        <n-button type="primary" @click="openCreateDrawer('gitlab')">
          <template #icon>
            <n-icon><PlugZap /></n-icon>
          </template>
          连接数据源
        </n-button>
      </div>
    </div>

    <div class="tab-row data-source-tabs">
      <button
        class="tab"
        :class="{ active: activeSourceTab === 'sources' }"
        type="button"
        @click="activeSourceTab = 'sources'"
      >
        个人数据源
      </button>
      <button
        class="tab"
        :class="{ active: activeSourceTab === 'ai' }"
        type="button"
        @click="activeSourceTab = 'ai'"
      >
        AI 偏好
      </button>
      <button
        class="tab"
        :class="{ active: activeSourceTab === 'records' }"
        type="button"
        @click="activeSourceTab = 'records'"
      >
        授权记录
      </button>
    </div>

    <div v-if="activeSourceTab !== 'records'" class="data-source-grid">
      <section class="panel source-main-panel">
        <div class="panel-header">
          <div>
            <h2>已连接数据源</h2>
            <p>AI 只会读取你授权范围内的数据，不会读取同事的私人数据。</p>
          </div>
          <n-tag size="small" type="success">{{ enabledSources.length }} 个已启用</n-tag>
        </div>

        <div class="source-card-list">
          <article v-for="source in sourceCards" :key="source.id" class="source-card">
            <div class="source-card-head">
              <div class="source-brand">
                <span class="source-icon-box">
                  <n-icon size="24" :class="source.className">
                    <component :is="source.icon" />
                  </n-icon>
                </span>
                <div>
                  <strong>{{ source.name }}</strong>
                  <span>{{ source.account_name }}</span>
                </div>
              </div>
              <n-tag :type="source.statusType" size="small">{{ source.statusLabel }}</n-tag>
            </div>

            <div class="source-meta-grid">
              <div>
                <span>授权范围</span>
                <strong>{{ source.scope }}</strong>
              </div>
              <div>
                <span>最近同步</span>
                <strong>{{ source.syncedAt }}</strong>
              </div>
              <div>
                <span>可用数据</span>
                <strong>{{ source.available }}</strong>
              </div>
            </div>

            <div class="scope-chip-row">
              <n-tag v-for="tag in source.tags" :key="tag" size="small">{{ tag }}</n-tag>
            </div>

            <div class="source-actions">
              <n-button size="small" secondary @click="testMutation.mutate(source.id)">
                <template #icon>
                  <n-icon><CheckCircle2 /></n-icon>
                </template>
                测试连接
              </n-button>
              <n-button size="small" secondary @click="openEditDrawer(source)">
                编辑范围
              </n-button>
              <n-button
                size="small"
                quaternary
                :type="source.enabled ? 'error' : 'primary'"
                @click="toggleSource(source)"
              >
                {{ source.enabled ? '停用' : '启用' }}
              </n-button>
            </div>
          </article>
        </div>

        <section class="connect-section">
          <h3>可继续连接</h3>
          <div class="connect-grid">
            <button
              v-for="item in connectableSources"
              :key="item.name"
              class="connect-tile"
              type="button"
              @click="openCreateDrawer(item.type)"
            >
              <n-icon size="22"><component :is="item.icon" /></n-icon>
              <span>{{ item.name }}</span>
              <small>{{ item.description }}</small>
            </button>
          </div>
        </section>

        <section class="source-preview-section">
          <div class="panel-header">
            <h2>本次 AI 可用来源预览</h2>
            <n-tag size="small" type="info">2026-05-25 至 2026-05-31</n-tag>
          </div>
          <div class="preview-list">
            <div>
              <GitBranch :size="18" />
              <span>Git 提交 18 条，合并请求 4 个，代码评审 6 条</span>
            </div>
            <div>
              <FolderKanban :size="18" />
              <span>Jira 任务 7 个，状态变更 12 次，新增评论 9 条</span>
            </div>
            <div>
              <FileText :size="18" />
              <span>历史报告 4 篇，可用于保持表达风格一致</span>
            </div>
          </div>
        </section>
      </section>

      <aside v-if="activeSourceTab === 'sources' || activeSourceTab === 'ai'" class="panel ai-preference-panel">
        <div class="panel-header">
          <h2>AI 生成偏好</h2>
          <n-tag size="small">个人</n-tag>
        </div>

        <div class="preference-list">
          <div class="preference-row">
            <div>
              <strong>生成前确认数据源</strong>
              <span>每次生成草稿前允许临时取消某个来源。</span>
            </div>
            <n-switch v-model:value="aiPreferences.confirmSources" />
          </div>
          <div class="preference-row">
            <div>
              <strong>仅填充空字段</strong>
              <span>保留你已手动填写的内容。</span>
            </div>
            <n-switch v-model:value="aiPreferences.fillEmptyOnly" />
          </div>
          <div class="preference-row">
            <div>
              <strong>包含技术细节</strong>
              <span>提交、任务、风险项会保留关键编号。</span>
            </div>
            <n-switch v-model:value="aiPreferences.includeTechnicalDetails" />
          </div>
        </div>

        <div class="select-like-list">
          <div>
            <span>默认生成语言</span>
            <strong>中文</strong>
          </div>
          <div>
            <span>默认报告风格</span>
            <strong>简洁汇总</strong>
          </div>
          <div>
            <span>数据时间范围</span>
            <strong>当前填报周期</strong>
          </div>
        </div>

        <section class="safety-checklist">
          <h3>安全边界</h3>
          <div><CheckCircle2 :size="16" /> 不读取同事私人仓库</div>
          <div><CheckCircle2 :size="16" /> 不写入 Jira 或 Git 系统</div>
          <div><CheckCircle2 :size="16" /> 生成内容提交前必须人工确认</div>
        </section>
      </aside>
    </div>

    <section v-if="activeSourceTab !== 'ai'" class="panel sync-record-panel">
      <div class="panel-header">
        <h2>最近同步记录</h2>
        <n-button text size="small" @click="activeSourceTab = 'records'">查看全部</n-button>
      </div>
      <table class="record-table">
        <thead>
          <tr>
            <th>数据源</th>
            <th>触发方式</th>
            <th>读取内容</th>
            <th>结果</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in records" :key="record.time">
            <td>{{ record.source }}</td>
            <td>{{ record.trigger }}</td>
            <td>{{ record.content }}</td>
            <td><n-tag size="small" type="success">{{ record.result }}</n-tag></td>
            <td>{{ record.time }}</td>
          </tr>
        </tbody>
      </table>
    </section>

    <div v-if="sourceDrawerOpen" class="preview-overlay">
      <section class="source-config-drawer">
        <div class="preview-head">
          <div>
            <h2>{{ editingSourceId ? '编辑数据源' : '连接数据源' }}</h2>
            <span>配置 AI 可以读取的个人授权范围。</span>
          </div>
          <n-button text @click="closeSourceDrawer">
            <template #icon>
              <n-icon><X /></n-icon>
            </template>
          </n-button>
        </div>

        <div class="source-config-body">
          <section class="source-type-grid">
            <button
              v-for="type in sourceTypes"
              :key="type.value"
              class="source-type-tile"
              :class="{ active: sourceForm.source_type === type.value }"
              type="button"
              :disabled="Boolean(editingSourceId)"
              @click="selectSourceType(type.value)"
            >
              <n-icon size="24" :class="sourceClass(type.value)">
                <component :is="type.icon" />
              </n-icon>
              <span>{{ type.label }}</span>
              <small>{{ type.description }}</small>
            </button>
          </section>

          <div class="source-form-grid">
            <label>
              <span>连接名称</span>
              <input v-model="sourceForm.name" class="rule-input" placeholder="例如 GitLab" />
            </label>
            <label>
              <span>账号标识</span>
              <input v-model="sourceForm.account_name" class="rule-input" placeholder="例如 wangqi@gitlab.local" />
            </label>
            <label>
              <span>{{ sourceScopeLabel }}</span>
              <textarea
                v-model="sourceForm.scopeText"
                class="rule-textarea"
                :placeholder="sourceScopePlaceholder"
              />
            </label>
            <label>
              <span>读取权限</span>
              <textarea
                v-model="sourceForm.permissionsText"
                class="rule-textarea"
                placeholder="commits:read, merge_requests:read, issues:read"
              />
            </label>
          </div>

          <section class="source-config-note">
            <CheckCircle2 :size="16" />
            <span>这里只保存授权范围配置。真实 OAuth、Token 加密与后台同步任务会接在后续集成层。</span>
          </section>
        </div>

        <div class="preview-actions">
          <n-button secondary @click="closeSourceDrawer">取消</n-button>
          <n-button
            type="primary"
            :loading="saveSourceMutation.isPending.value"
            @click="handleSaveSource"
          >
            保存配置
          </n-button>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { NButton, NIcon, NSwitch, NTag, useMessage } from 'naive-ui'
import { computed, reactive, ref } from 'vue'
import {
  CheckCircle2,
  Database,
  FileText,
  FolderKanban,
  Github,
  GitBranch,
  Gitlab,
  PlugZap,
  RefreshCw,
  X
} from 'lucide-vue-next'

import {
  createDataSource,
  listDataSources,
  testDataSource,
  updateDataSource,
  type DataSourceConnection,
  type DataSourceConnectionCreate,
  type DataSourceType
} from '@/api/dataSources'

const message = useMessage()
const queryClient = useQueryClient()
const activeSourceTab = ref<'sources' | 'ai' | 'records'>('sources')
const sourceDrawerOpen = ref(false)
const editingSourceId = ref<string | null>(null)
const aiPreferences = reactive({
  confirmSources: true,
  fillEmptyOnly: true,
  includeTechnicalDetails: true
})
const sourceForm = reactive({
  source_type: 'gitlab' as DataSourceType,
  name: 'GitLab',
  account_name: '',
  scopeText: '',
  permissionsText: 'commits:read, merge_requests:read'
})

const { data: connectedSources } = useQuery({
  queryKey: ['data-sources'],
  queryFn: listDataSources
})

const testMutation = useMutation({
  mutationFn: testDataSource,
  onSuccess: (result) => {
    message.success(result.ok ? '连接正常' : '当前数据源已停用')
  }
})

const syncAllMutation = useMutation({
  mutationFn: async () => {
    const enabledIds = (connectedSources.value ?? [])
      .filter((source) => source.enabled)
      .map((source) => source.id)
    await Promise.all(enabledIds.map((id) => testDataSource(id)))
    return enabledIds.length
  },
  onSuccess: (count) => {
    queryClient.invalidateQueries({ queryKey: ['data-sources'] })
    message.success(count ? `已同步 ${count} 个数据源` : '暂无可同步的数据源')
  },
  onError: () => {
    message.error('同步失败，请检查数据源配置')
  }
})

const updateMutation = useMutation({
  mutationFn: (source: DataSourceConnection) =>
    updateDataSource(source.id, { enabled: !source.enabled }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['data-sources'] })
    message.success('数据源状态已更新')
  }
})

const saveSourceMutation = useMutation({
  mutationFn: () => {
    const payload = buildSourcePayload()
    if (editingSourceId.value) {
      return updateDataSource(editingSourceId.value, payload)
    }
    return createDataSource(payload)
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['data-sources'] })
    closeSourceDrawer()
    message.success('数据源配置已保存')
  },
  onError: () => {
    message.error('数据源配置保存失败')
  }
})

const enabledSources = computed(() => (connectedSources.value ?? []).filter((source) => source.enabled))
const sourceCards = computed(() => (connectedSources.value ?? []).map(toSourceCard))
const sourceScopeLabel = computed(() =>
  sourceForm.source_type === 'jira'
    ? 'Jira 项目范围'
    : sourceForm.source_type === 'custom'
      ? 'Webhook 标识'
      : '仓库范围'
)
const sourceScopePlaceholder = computed(() =>
  sourceForm.source_type === 'jira'
    ? 'WEEK, INFRA'
    : sourceForm.source_type === 'custom'
      ? 'release-webhook, incident-webhook'
      : 'weeeek/backend, AIProject/weeeek'
)

function toSourceCard(source: DataSourceConnection) {
  const permissions = Array.isArray(source.scope_config.permissions)
    ? source.scope_config.permissions.map(String)
    : []
  const scopeItems = [
    ...(Array.isArray(source.scope_config.repositories) ? source.scope_config.repositories : []),
    ...(Array.isArray(source.scope_config.projects) ? source.scope_config.projects : [])
  ].map(String)
  return {
    ...source,
    icon: sourceIcon(source.source_type),
    className: sourceClass(source.source_type),
    scope: scopeItems.join(', ') || '-',
    tags: permissions,
    available: availableText(source.source_type),
    syncedAt: source.last_sync_at ? source.last_sync_at.replace('T', ' ').slice(0, 16) : '-',
    statusLabel: source.enabled ? statusLabel(source.status) : '已停用',
    statusType: source.enabled && source.status === 'connected' ? ('success' as const) : ('warning' as const)
  }
}

function sourceIcon(type: string) {
  if (type === 'gitlab') return Gitlab
  if (type === 'github') return Github
  if (type === 'jira') return FileText
  return Database
}

function sourceClass(type: string) {
  if (type === 'gitlab') return 'source-gitlab'
  if (type === 'github') return 'source-github'
  if (type === 'jira') return 'source-jira'
  return 'source-history'
}

function availableText(type: string) {
  if (type === 'jira') return '任务、状态、评论'
  if (type === 'github') return '提交、PR、Issue'
  if (type === 'gitlab') return '提交、MR、流水线'
  return '外部事件'
}

function statusLabel(status: string) {
  if (status === 'needs_refresh') return '需要刷新'
  if (status === 'connected') return '连接正常'
  return status
}

function toggleSource(source: DataSourceConnection) {
  updateMutation.mutate(source)
}

function selectSourceType(type: DataSourceType) {
  sourceForm.source_type = type
  sourceForm.name = defaultSourceName(type)
  sourceForm.permissionsText = defaultPermissions(type)
}

function openCreateDrawer(type: DataSourceType) {
  editingSourceId.value = null
  sourceDrawerOpen.value = true
  sourceForm.source_type = type
  sourceForm.name = defaultSourceName(type)
  sourceForm.account_name = ''
  sourceForm.scopeText = ''
  sourceForm.permissionsText = defaultPermissions(type)
}

function openEditDrawer(source: DataSourceConnection) {
  editingSourceId.value = source.id
  sourceDrawerOpen.value = true
  sourceForm.source_type = source.source_type
  sourceForm.name = source.name
  sourceForm.account_name = source.account_name
  sourceForm.scopeText = scopeTextFromConfig(source)
  const permissions = Array.isArray(source.scope_config.permissions)
    ? source.scope_config.permissions.map(String)
    : []
  sourceForm.permissionsText = permissions.join(', ')
}

function closeSourceDrawer() {
  sourceDrawerOpen.value = false
  editingSourceId.value = null
}

function handleSaveSource() {
  if (!sourceForm.name.trim() || !sourceForm.account_name.trim()) {
    message.warning('请填写连接名称和账号标识')
    return
  }
  saveSourceMutation.mutate()
}

function buildSourcePayload(): DataSourceConnectionCreate {
  return {
    source_type: sourceForm.source_type,
    name: sourceForm.name.trim(),
    account_name: sourceForm.account_name.trim(),
    scope_config: buildScopeConfig()
  }
}

function buildScopeConfig() {
  const scopeItems = splitInput(sourceForm.scopeText)
  const config: Record<string, unknown> = {
    permissions: splitInput(sourceForm.permissionsText)
  }
  if (sourceForm.source_type === 'jira') {
    config.projects = scopeItems
  } else if (sourceForm.source_type === 'custom') {
    config.events = scopeItems
  } else {
    config.repositories = scopeItems
  }
  return config
}

function scopeTextFromConfig(source: DataSourceConnection) {
  const keys = source.source_type === 'jira'
    ? ['projects']
    : source.source_type === 'custom'
      ? ['events']
      : ['repositories']
  const items = keys.flatMap((key) =>
    Array.isArray(source.scope_config[key]) ? source.scope_config[key].map(String) : []
  )
  return items.join(', ')
}

function splitInput(value: string) {
  return value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean)
}

function defaultSourceName(type: DataSourceType) {
  if (type === 'gitlab') return 'GitLab'
  if (type === 'github') return 'GitHub'
  if (type === 'jira') return 'Jira'
  return '自定义 Webhook'
}

function defaultPermissions(type: DataSourceType) {
  if (type === 'jira') return 'issues:read, comments:read, projects:read'
  if (type === 'github') return 'repo:read, pull_requests:read, issues:read'
  if (type === 'custom') return 'events:read'
  return 'commits:read, merge_requests:read, pipelines:read'
}

const sourceTypes = [
  { value: 'gitlab' as const, label: 'GitLab', description: '提交、MR、流水线', icon: Gitlab },
  { value: 'github' as const, label: 'GitHub', description: '提交、PR、Issue', icon: Github },
  { value: 'jira' as const, label: 'Jira', description: '任务、状态、评论', icon: FileText },
  { value: 'custom' as const, label: 'Webhook', description: '外部系统事件', icon: PlugZap }
]

const connectableSources = [
  { name: 'GitLab', description: '提交、MR、流水线', icon: Gitlab, type: 'gitlab' as const },
  { name: 'Jira', description: '任务、状态、评论', icon: FileText, type: 'jira' as const },
  { name: '自定义 Webhook', description: '接收外部系统事件', icon: PlugZap, type: 'custom' as const }
]

const records = [
  {
    source: 'GitLab',
    trigger: 'AI 生成草稿',
    content: '18 条提交，4 个 MR',
    result: '成功',
    time: '今天 10:24'
  },
  {
    source: 'Jira',
    trigger: '定时同步',
    content: '7 个任务，12 次状态变更',
    result: '成功',
    time: '今天 09:40'
  },
  {
    source: 'GitHub',
    trigger: '手动测试连接',
    content: '仓库权限校验',
    result: '成功',
    time: '昨天 18:12'
  }
]
</script>
