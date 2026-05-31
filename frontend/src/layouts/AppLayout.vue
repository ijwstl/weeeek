<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <img class="brand-mark" src="/weeeek_icon.svg" alt="Weeeek" />
        <div>
          <strong>Weeeek</strong>
          <span>报告协作平台</span>
        </div>
      </div>

      <nav class="nav-list">
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-item">
          <n-icon size="18">
            <component :is="item.icon" />
          </n-icon>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <main class="main-area">
      <header class="topbar">
        <div>
          <div class="workspace-label">当前工作区</div>
          <div class="workspace-name">研发协作空间</div>
        </div>
        <div class="topbar-actions">
          <div class="notification-anchor">
            <n-button quaternary circle @click="notificationOpen = !notificationOpen">
              <template #icon>
                <n-icon><Bell /></n-icon>
              </template>
            </n-button>
            <span v-if="unreadCount" class="notification-badge">{{ unreadCount }}</span>
            <section v-if="notificationOpen" class="notification-popover">
              <div class="notification-popover-head">
                <div>
                  <strong>站内通知</strong>
                  <span>{{ unreadCount }} 条未读</span>
                </div>
                <n-button text size="small" @click="handleReadAll">全部已读</n-button>
              </div>
              <div class="notification-popover-list">
                <button
                  v-for="notice in notifications ?? []"
                  :key="notice.id"
                  class="notification-item"
                  :class="{ unread: !notice.read_at }"
                  type="button"
                  @click="handleReadNotice(notice.id)"
                >
                  <span class="notification-dot"></span>
                  <div>
                    <strong>{{ notice.title }}</strong>
                    <span>{{ notice.content }}</span>
                    <time>{{ formatNoticeTime(notice.created_at) }}</time>
                  </div>
                </button>
                <div v-if="!notifications?.length" class="notification-empty">暂无通知</div>
              </div>
            </section>
          </div>
          <div class="user-chip">
            <div class="avatar">王</div>
            <span>王启</span>
          </div>
        </div>
      </header>
      <section class="page-container">
        <RouterView />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import {
  Bell,
  Database,
  FileText,
  FolderTree,
  LayoutDashboard,
  PanelsTopLeft,
  Settings,
  Users
} from 'lucide-vue-next'
import { NButton, NIcon } from 'naive-ui'
import { computed, ref } from 'vue'

import {
  getInAppUnreadCount,
  listInAppNotifications,
  markAllInAppNotificationsRead,
  markInAppNotificationRead
} from '@/api/notifications'

const queryClient = useQueryClient()
const notificationOpen = ref(false)

const { data: notifications } = useQuery({
  queryKey: ['in-app-notifications'],
  queryFn: () => listInAppNotifications(false)
})

const { data: unreadSummary } = useQuery({
  queryKey: ['in-app-unread-count'],
  queryFn: getInAppUnreadCount
})

const unreadCount = computed(() => unreadSummary.value?.unread_count ?? 0)

const readNoticeMutation = useMutation({
  mutationFn: markInAppNotificationRead,
  onSuccess: () => {
    invalidateNotifications()
  }
})

const readAllMutation = useMutation({
  mutationFn: markAllInAppNotificationsRead,
  onSuccess: () => {
    invalidateNotifications()
  }
})

const navItems = [
  { label: '工作台', to: '/', icon: LayoutDashboard },
  { label: '部门', to: '/departments', icon: FolderTree },
  { label: '项目团队', to: '/projects', icon: Users },
  { label: '报告中心', to: '/reports', icon: FileText },
  { label: '模板', to: '/templates', icon: PanelsTopLeft },
  { label: '数据源', to: '/data-sources', icon: Database },
  { label: '设置', to: '/settings', icon: Settings }
]

function handleReadNotice(id: string) {
  readNoticeMutation.mutate(id)
}

function handleReadAll() {
  readAllMutation.mutate()
}

function invalidateNotifications() {
  queryClient.invalidateQueries({ queryKey: ['in-app-notifications'] })
  queryClient.invalidateQueries({ queryKey: ['in-app-unread-count'] })
}

function formatNoticeTime(value: string) {
  return value.replace('T', ' ').slice(5, 16)
}
</script>
