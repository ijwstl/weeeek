<template>
  <div class="settings-page">
    <div class="page-heading">
      <div>
        <h1>设置</h1>
        <p>管理工作区、成员、角色权限、认证接入和审计策略。</p>
      </div>
    </div>

    <div class="settings-tabs">
      <button
        class="toolbar-tab"
        :class="{ active: activeSettingsTab === 'basic' }"
        type="button"
        @click="activeSettingsTab = 'basic'"
      >
        基础设置
      </button>
      <button
        class="toolbar-tab"
        :class="{ active: activeSettingsTab === 'audit' }"
        type="button"
        @click="activeSettingsTab = 'audit'"
      >
        审计日志
      </button>
    </div>

    <div v-if="activeSettingsTab === 'basic'" class="settings-grid">
      <section class="panel settings-main-panel">
        <div class="panel-header">
          <h2>工作区信息</h2>
          <n-tag size="small" type="success">{{ workspace?.status ?? '加载中' }}</n-tag>
        </div>

        <n-skeleton v-if="workspaceLoading" text :repeat="4" />
        <div v-else class="definition-list">
          <div>
            <span>名称</span>
            <strong>{{ workspace?.name }}</strong>
          </div>
          <div>
            <span>Slug</span>
            <strong>{{ workspace?.slug }}</strong>
          </div>
          <div>
            <span>部署模式</span>
            <strong>{{ workspace?.deployment_mode }}</strong>
          </div>
          <div>
            <span>时区</span>
            <strong>{{ workspace?.timezone }}</strong>
          </div>
          <div>
            <span>部门最大层级</span>
            <strong>{{ workspace?.department_max_depth }}</strong>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <h2>当前身份</h2>
          <n-tag size="small" type="info">{{ principal?.roles.join(', ') }}</n-tag>
        </div>

        <n-skeleton v-if="principalLoading" text :repeat="3" />
        <div v-else class="principal-card">
          <div class="large-avatar">王</div>
          <div>
            <strong>{{ principal?.member.display_name }}</strong>
            <span>{{ principal?.member.email }}</span>
          </div>
        </div>
      </section>

      <section class="panel settings-main-panel">
        <div class="panel-header">
          <h2>成员</h2>
          <n-button size="small" secondary>
            <template #icon>
              <n-icon><UserPlus /></n-icon>
            </template>
            邀请成员
          </n-button>
        </div>

        <div class="member-table">
          <div class="member-table-head">
            <span>姓名</span>
            <span>邮箱</span>
            <span>工号</span>
            <span>状态</span>
          </div>
          <div v-for="member in members ?? []" :key="member.id" class="member-table-row">
            <strong>{{ member.display_name }}</strong>
            <span>{{ member.email }}</span>
            <span>{{ member.employee_no }}</span>
            <n-tag size="small" type="success">{{ member.status }}</n-tag>
          </div>
        </div>
      </section>

      <section class="panel">
        <div class="panel-header">
          <h2>安全策略</h2>
          <n-tag size="small" type="success">已启用审计</n-tag>
        </div>

        <div class="policy-list">
          <div>
            <span>管理员查看全部报告</span>
            <strong>{{ security?.workspace_admin_can_view_all_submitted_reports ? '允许' : '默认禁止' }}</strong>
          </div>
          <div>
            <span>审计日志</span>
            <strong>{{ security?.audit_enabled ? '开启' : '关闭' }}</strong>
          </div>
          <div>
            <span>私有化单工作区</span>
            <strong>{{ security?.private_deployment_single_workspace ? '开启' : '关闭' }}</strong>
          </div>
        </div>
      </section>

      <section class="panel settings-main-panel">
        <div class="panel-header">
          <h2>角色权限</h2>
          <n-button size="small" secondary @click="$router.push('/settings/roles')">
            <template #icon>
              <n-icon><ShieldCheck /></n-icon>
            </template>
            查看权限矩阵
          </n-button>
        </div>
        <p class="muted-text">
          角色由权限标识符组成，成员授权时绑定工作区、部门、项目团队或个人作用域。
        </p>
      </section>

      <section class="panel settings-main-panel auth-provider-panel">
        <div class="panel-header">
          <div>
            <h2>认证接入</h2>
            <p>私有化部署可通过 LDAP / AD 同步成员身份。</p>
          </div>
          <n-switch
            :value="ldapForm.enabled"
            :loading="ldapUpdateMutation.isPending.value"
            @update:value="ldapForm.enabled = $event"
          />
        </div>

        <div class="ldap-config-grid">
          <label>
            <span>服务地址</span>
            <input v-model="ldapForm.server_url" class="rule-input" placeholder="ldap://host:389" />
          </label>
          <label>
            <span>Base DN</span>
            <input v-model="ldapForm.base_dn" class="rule-input" placeholder="dc=example,dc=local" />
          </label>
          <label>
            <span>绑定 DN</span>
            <input v-model="ldapForm.bind_dn" class="rule-input" placeholder="cn=readonly,dc=example,dc=local" />
          </label>
          <label>
            <span>绑定密码</span>
            <input
              v-model="ldapForm.bind_password"
              class="rule-input"
              type="password"
              :placeholder="ldapConfig?.bind_password_configured ? '已配置，留空不变' : '请输入绑定密码'"
            />
          </label>
          <label>
            <span>用户过滤器</span>
            <input v-model="ldapForm.user_filter" class="rule-input" placeholder="(uid={username})" />
          </label>
          <label>
            <span>连接方式</span>
            <select v-model="ldapForm.use_ssl" class="rule-input">
              <option :value="false">LDAP</option>
              <option :value="true">LDAPS</option>
            </select>
          </label>
        </div>

        <div class="ldap-mapping-grid">
          <label>
            <span>姓名字段</span>
            <input v-model="ldapForm.attribute_mapping.display_name" class="rule-input" />
          </label>
          <label>
            <span>邮箱字段</span>
            <input v-model="ldapForm.attribute_mapping.email" class="rule-input" />
          </label>
          <label>
            <span>工号字段</span>
            <input v-model="ldapForm.attribute_mapping.employee_no" class="rule-input" />
          </label>
          <label>
            <span>部门字段</span>
            <input v-model="ldapForm.attribute_mapping.department" class="rule-input" />
          </label>
        </div>

        <div class="ldap-action-row">
          <label class="template-check">
            <input v-model="ldapForm.department_sync_enabled" type="checkbox" />
            同步 LDAP 部门字段
          </label>
          <div class="heading-actions">
            <n-button
              secondary
              :loading="ldapTestMutation.isPending.value"
              @click="handleTestLdap"
            >
              <template #icon>
                <n-icon><PlugZap /></n-icon>
              </template>
              测试
            </n-button>
            <n-button
              type="primary"
              :loading="ldapUpdateMutation.isPending.value"
              @click="handleSaveLdap"
            >
              保存 LDAP
            </n-button>
          </div>
        </div>
      </section>

      <section class="panel settings-main-panel notification-panel">
        <div class="panel-header">
          <div>
            <h2>通知渠道</h2>
            <p>配置站内、飞书和自定义 Webhook 通知插件。</p>
          </div>
          <n-tag size="small" type="info">{{ notificationChannels?.length ?? 0 }} 个渠道</n-tag>
        </div>

        <div class="notification-channel-list">
          <article
            v-for="channel in notificationChannels ?? []"
            :key="channel.id"
            class="notification-channel-card"
          >
            <div class="notification-channel-head">
              <div class="notification-channel-title">
                <n-icon size="22" :class="channelIconClass(channel.channel_type)">
                  <component :is="channelIcon(channel.channel_type)" />
                </n-icon>
                <div>
                  <strong>{{ channel.name }}</strong>
                  <span>{{ channelTypeText(channel.channel_type) }}</span>
                </div>
              </div>
              <n-switch
                :value="channel.enabled"
                :loading="updatingChannelId === channel.id"
                @update:value="updateChannelEnabled(channel.id, $event)"
              />
            </div>

            <div class="notification-config-grid">
              <label v-if="channel.channel_type === 'in_app'">
                <span>保留天数</span>
                <input
                  class="rule-input"
                  type="number"
                  :value="configText(channel.config.retention_days)"
                  @change="updateChannelConfig(channel, 'retention_days', numberValue($event))"
                />
              </label>

              <label v-if="channel.channel_type === 'feishu'">
                <span>Webhook 地址</span>
                <input
                  class="rule-input"
                  :value="configText(channel.config.webhook_url)"
                  @change="updateChannelConfig(channel, 'webhook_url', inputValue($event))"
                />
              </label>
              <label v-if="channel.channel_type === 'feishu'">
                <span>提醒策略</span>
                <select
                  class="rule-input"
                  :value="configText(channel.config.mention_policy)"
                  @change="updateChannelConfig(channel, 'mention_policy', inputValue($event))"
                >
                  <option value="none">不 @ 人</option>
                  <option value="report_owner">@ 填报人</option>
                  <option value="department_admin">@ 部门管理员</option>
                </select>
              </label>

              <label v-if="channel.channel_type === 'webhook'">
                <span>请求地址</span>
                <input
                  class="rule-input"
                  :value="configText(channel.config.url)"
                  @change="updateChannelConfig(channel, 'url', inputValue($event))"
                />
              </label>
              <label v-if="channel.channel_type === 'webhook'">
                <span>请求方法</span>
                <select
                  class="rule-input"
                  :value="configText(channel.config.method)"
                  @change="updateChannelConfig(channel, 'method', inputValue($event))"
                >
                  <option value="POST">POST</option>
                  <option value="PUT">PUT</option>
                  <option value="PATCH">PATCH</option>
                </select>
              </label>
            </div>

            <div class="notification-channel-foot">
              <span>{{ channel.last_test_status ? `最近测试：${channel.last_test_status}` : '尚未测试' }}</span>
              <n-button
                size="small"
                secondary
                :loading="testingChannelId === channel.id"
                @click="handleTestChannel(channel.id)"
              >
                <template #icon>
                  <n-icon><PlugZap /></n-icon>
                </template>
                测试
              </n-button>
            </div>
          </article>
        </div>
      </section>
    </div>

    <section v-else class="panel audit-search-panel">
      <div class="panel-header">
        <div>
          <h2>审计日志</h2>
          <p>查询关键操作、资源变更和接口调用记录。</p>
        </div>
        <n-tag size="small" type="success">AOP 落库</n-tag>
      </div>

      <div class="audit-filter-bar">
        <label>
          <span>关键字</span>
          <input v-model="auditFilters.keyword" class="rule-input" placeholder="动作、资源或路径" />
        </label>
        <label>
          <span>动作</span>
          <select v-model="auditFilters.action" class="rule-input">
            <option value="">全部动作</option>
            <option v-for="action in auditActionOptions" :key="action" :value="action">
              {{ actionText(action) }}
            </option>
          </select>
        </label>
        <label>
          <span>资源类型</span>
          <select v-model="auditFilters.resource_type" class="rule-input">
            <option value="">全部资源</option>
            <option v-for="type in auditResourceTypes" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </label>
        <label>
          <span>状态</span>
          <select v-model="auditFilters.status" class="rule-input">
            <option value="">全部状态</option>
            <option value="success">success</option>
            <option value="failed">failed</option>
          </select>
        </label>
        <label>
          <span>条数</span>
          <select v-model.number="auditFilters.limit" class="rule-input">
            <option :value="20">20</option>
            <option :value="50">50</option>
            <option :value="100">100</option>
            <option :value="200">200</option>
          </select>
        </label>
        <n-button type="primary" @click="handleAuditSearch">
          <template #icon>
            <n-icon><Search /></n-icon>
          </template>
          查询
        </n-button>
      </div>

      <div class="audit-table">
        <div class="audit-table-head">
          <span>时间</span>
          <span>动作</span>
          <span>资源</span>
          <span>资源 ID</span>
          <span>状态</span>
        </div>
        <div v-for="log in auditLogs ?? []" :key="log.id" class="audit-table-row">
          <time>{{ formatDateTime(log.created_at) }}</time>
          <strong>{{ actionText(log.action) }}</strong>
          <span>{{ log.resource_type }}</span>
          <span>{{ log.resource_id ?? '-' }}</span>
          <n-tag size="small" :type="log.status === 'success' ? 'success' : 'warning'">
            {{ log.status }}
          </n-tag>
          <small>{{ log.request_method ?? '-' }} {{ log.request_path ?? '' }}</small>
        </div>
        <div v-if="!auditLogs?.length" class="audit-empty-state">暂无匹配的审计记录</div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { NButton, NIcon, NSkeleton, NSwitch, NTag, useMessage } from 'naive-ui'
import { Bell, Bot, PlugZap, Search, Send, ShieldCheck, UserPlus } from 'lucide-vue-next'
import { reactive, ref, watch } from 'vue'

import { listAuditLogs } from '@/api/audit'
import {
  getCurrentPrincipal,
  getLdapProviderConfig,
  getSecuritySettings,
  getWorkspace,
  listMembers,
  testLdapProviderConfig,
  updateLdapProviderConfig
} from '@/api/identity'
import {
  listNotificationChannels,
  testNotificationChannel,
  updateNotificationChannel,
  type NotificationChannel,
  type NotificationChannelType
} from '@/api/notifications'

const message = useMessage()
const queryClient = useQueryClient()
const updatingChannelId = ref('')
const testingChannelId = ref('')
const activeSettingsTab = ref<'basic' | 'audit'>('basic')
const auditFilters = reactive({
  keyword: '',
  action: '',
  resource_type: '',
  status: '',
  limit: 50
})

const auditActionOptions = [
  'report.draft.save',
  'report.ai_draft.generate',
  'report.submit',
  'template.draft.update',
  'template.publish',
  'notification.channel.create',
  'notification.channel.update',
  'notification.channel.test',
  'data_source.create',
  'data_source.update',
  'data_source.test'
]
const auditResourceTypes = [
  'report_instance',
  'template',
  'notification_channel',
  'data_source_connection',
  'auth_provider'
]

const ldapForm = reactive({
  enabled: false,
  server_url: '',
  use_ssl: false,
  base_dn: '',
  bind_dn: '',
  bind_password: '',
  user_filter: '',
  department_sync_enabled: true,
  attribute_mapping: {
    display_name: 'cn',
    email: 'mail',
    employee_no: 'employeeNumber',
    department: 'department'
  }
})

const { data: workspace, isLoading: workspaceLoading } = useQuery({
  queryKey: ['workspace'],
  queryFn: getWorkspace
})

const { data: principal, isLoading: principalLoading } = useQuery({
  queryKey: ['principal'],
  queryFn: getCurrentPrincipal
})

const { data: members } = useQuery({
  queryKey: ['members'],
  queryFn: listMembers
})

const { data: security } = useQuery({
  queryKey: ['security-settings'],
  queryFn: getSecuritySettings
})

const { data: ldapConfig } = useQuery({
  queryKey: ['ldap-provider'],
  queryFn: getLdapProviderConfig
})

const { data: auditLogs, refetch: refetchAuditLogs } = useQuery({
  queryKey: ['audit-logs', auditFilters],
  queryFn: () =>
    listAuditLogs({
      limit: auditFilters.limit,
      action: auditFilters.action || undefined,
      resource_type: auditFilters.resource_type || undefined,
      status: auditFilters.status || undefined,
      keyword: auditFilters.keyword || undefined
    })
})

const { data: notificationChannels } = useQuery({
  queryKey: ['notification-channels'],
  queryFn: listNotificationChannels
})

const updateChannelMutation = useMutation({
  mutationFn: ({ id, payload }: { id: string; payload: Record<string, unknown> }) =>
    updateNotificationChannel(id, payload),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['notification-channels'] })
    queryClient.invalidateQueries({ queryKey: ['audit-logs'] })
    message.success('通知渠道已更新')
  },
  onError: () => {
    message.error('通知渠道更新失败')
  },
  onSettled: () => {
    updatingChannelId.value = ''
  }
})

const testChannelMutation = useMutation({
  mutationFn: testNotificationChannel,
  onSuccess: (result) => {
    queryClient.invalidateQueries({ queryKey: ['notification-channels'] })
    queryClient.invalidateQueries({ queryKey: ['audit-logs'] })
    if (result.ok) {
      message.success(result.message)
      return
    }
    message.warning(result.message)
  },
  onError: () => {
    message.error('通知渠道测试失败')
  },
  onSettled: () => {
    testingChannelId.value = ''
  }
})

const ldapUpdateMutation = useMutation({
  mutationFn: () =>
    updateLdapProviderConfig({
      enabled: ldapForm.enabled,
      config_public: {
        server_url: ldapForm.server_url,
        use_ssl: ldapForm.use_ssl,
        base_dn: ldapForm.base_dn,
        bind_dn: ldapForm.bind_dn,
        user_filter: ldapForm.user_filter,
        department_sync_enabled: ldapForm.department_sync_enabled,
        attribute_mapping: { ...ldapForm.attribute_mapping }
      },
      bind_password: ldapForm.bind_password || undefined
    }),
  onSuccess: () => {
    ldapForm.bind_password = ''
    queryClient.invalidateQueries({ queryKey: ['ldap-provider'] })
    queryClient.invalidateQueries({ queryKey: ['audit-logs'] })
    message.success('LDAP 配置已保存')
  },
  onError: () => {
    message.error('LDAP 配置保存失败')
  }
})

const ldapTestMutation = useMutation({
  mutationFn: testLdapProviderConfig,
  onSuccess: (result) => {
    queryClient.invalidateQueries({ queryKey: ['audit-logs'] })
    if (result.ok) {
      message.success(result.message)
      return
    }
    message.warning(result.message)
  },
  onError: () => {
    message.error('LDAP 测试失败')
  }
})

watch(
  ldapConfig,
  (value) => {
    if (!value) return
    const config = value.config_public
    const mapping = config.attribute_mapping as Record<string, string> | undefined
    ldapForm.enabled = value.enabled
    ldapForm.server_url = configText(config.server_url)
    ldapForm.use_ssl = Boolean(config.use_ssl)
    ldapForm.base_dn = configText(config.base_dn)
    ldapForm.bind_dn = configText(config.bind_dn)
    ldapForm.user_filter = configText(config.user_filter)
    ldapForm.department_sync_enabled = Boolean(config.department_sync_enabled)
    ldapForm.attribute_mapping = {
      display_name: mapping?.display_name ?? 'cn',
      email: mapping?.email ?? 'mail',
      employee_no: mapping?.employee_no ?? 'employeeNumber',
      department: mapping?.department ?? 'department'
    }
  },
  { immediate: true }
)

function updateChannelEnabled(id: string, enabled: boolean) {
  updatingChannelId.value = id
  updateChannelMutation.mutate({ id, payload: { enabled } })
}

function updateChannelConfig(channel: NotificationChannel, key: string, value: unknown) {
  updatingChannelId.value = channel.id
  updateChannelMutation.mutate({
    id: channel.id,
    payload: {
      config: {
        ...channel.config,
        [key]: value
      }
    }
  })
}

function handleTestChannel(id: string) {
  testingChannelId.value = id
  testChannelMutation.mutate(id)
}

function handleAuditSearch() {
  refetchAuditLogs()
}

function handleSaveLdap() {
  ldapUpdateMutation.mutate()
}

function handleTestLdap() {
  ldapTestMutation.mutate()
}

function inputValue(event: Event) {
  return (event.target as HTMLInputElement).value
}

function numberValue(event: Event) {
  const value = Number((event.target as HTMLInputElement).value)
  return Number.isFinite(value) ? value : 0
}

function configText(value: unknown) {
  return value == null ? '' : String(value)
}

function channelTypeText(type: NotificationChannelType) {
  if (type === 'in_app') return '站内通知'
  if (type === 'feishu') return '飞书机器人'
  return '自定义 Webhook'
}

function channelIcon(type: NotificationChannelType) {
  if (type === 'in_app') return Bell
  if (type === 'feishu') return Send
  return Bot
}

function channelIconClass(type: NotificationChannelType) {
  if (type === 'in_app') return 'source-history'
  if (type === 'feishu') return 'source-jira'
  return 'source-gitlab'
}

function actionText(action: string) {
  const labels: Record<string, string> = {
    'report.draft.save': '保存报告草稿',
    'report.ai_draft.generate': '生成 AI 草稿',
    'report.submit': '提交报告',
    'template.draft.update': '更新模板草稿',
    'template.publish': '发布模板',
    'notification.channel.create': '创建通知渠道',
    'notification.channel.update': '更新通知渠道',
    'notification.channel.test': '测试通知渠道',
    'data_source.create': '创建数据源',
    'data_source.update': '更新数据源',
    'data_source.test': '测试数据源',
    'auth_provider.ldap.update': '更新 LDAP 配置',
    'auth_provider.ldap.test': '测试 LDAP 配置'
  }
  return labels[action] ?? action
}

function formatDateTime(value: string) {
  return value.replace('T', ' ').slice(0, 16)
}

</script>
