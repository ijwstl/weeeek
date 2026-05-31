import { apiGet, apiPatch, apiPost } from './client'

export type NotificationChannelType = 'in_app' | 'feishu' | 'webhook'

export interface NotificationChannel {
  id: string
  channel_type: NotificationChannelType
  name: string
  enabled: boolean
  config: Record<string, unknown>
  last_tested_at?: string | null
  last_test_status?: string | null
}

export interface NotificationChannelUpdate {
  name?: string
  enabled?: boolean
  config?: Record<string, unknown>
}

export interface NotificationChannelTestResult {
  ok: boolean
  status: string
  checked_at: string
  message: string
}

export interface InAppNotification {
  id: string
  receiver_member_id: string
  title: string
  content: string
  category: string
  resource_type?: string | null
  resource_id?: string | null
  read_at?: string | null
  created_at: string
}

export interface NotificationUnreadSummary {
  unread_count: number
}

export function listInAppNotifications(onlyUnread = false) {
  return apiGet<InAppNotification[]>(`/notifications/in-app?only_unread=${onlyUnread}`)
}

export function getInAppUnreadCount() {
  return apiGet<NotificationUnreadSummary>('/notifications/in-app/unread-count')
}

export function markInAppNotificationRead(id: string) {
  return apiPost<InAppNotification, Record<string, never>>(
    `/notifications/in-app/${id}/read`,
    {}
  )
}

export function markAllInAppNotificationsRead() {
  return apiPost<{ updated: number }, Record<string, never>>('/notifications/in-app/read-all', {})
}

export function listNotificationChannels() {
  return apiGet<NotificationChannel[]>('/notifications/channels')
}

export function updateNotificationChannel(id: string, payload: NotificationChannelUpdate) {
  return apiPatch<NotificationChannel, NotificationChannelUpdate>(
    `/notifications/channels/${id}`,
    payload
  )
}

export function testNotificationChannel(id: string) {
  return apiPost<NotificationChannelTestResult, Record<string, never>>(
    `/notifications/channels/${id}/test`,
    {}
  )
}
