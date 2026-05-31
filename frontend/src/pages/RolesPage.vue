<template>
  <div class="roles-page">
    <div class="page-heading">
      <div>
        <h1>角色权限</h1>
        <p>角色是权限集合，成员授权时会绑定作用域。</p>
      </div>
      <n-button type="primary">
        <template #icon>
          <n-icon><Plus /></n-icon>
        </template>
        新建角色
      </n-button>
    </div>

    <div class="roles-grid">
      <section class="panel roles-list-panel">
        <div class="panel-header">
          <h2>角色</h2>
          <n-tag size="small" type="info">{{ roles?.length ?? 0 }} 个</n-tag>
        </div>

        <div class="role-list">
          <button
            v-for="role in roles ?? []"
            :key="role.id"
            class="role-item"
            :class="{ active: role.id === selectedRoleId }"
            type="button"
            @click="selectedRoleId = role.id"
          >
            <strong>{{ role.name }}</strong>
            <span>{{ role.description }}</span>
            <n-tag size="small" :type="role.is_editable ? 'default' : 'warning'">
              {{ role.is_editable ? '可配置' : '锁定' }}
            </n-tag>
          </button>
        </div>
      </section>

      <section class="panel permission-panel">
        <div class="panel-header">
          <div>
            <h2>{{ selectedRole?.name ?? '权限矩阵' }}</h2>
            <p>{{ selectedRole?.description }}</p>
          </div>
          <n-button size="small" secondary :disabled="!selectedRole?.is_editable">
            <template #icon>
              <n-icon><Save /></n-icon>
            </template>
            保存权限
          </n-button>
        </div>

        <div class="permission-groups">
          <section
            v-for="group in permissionGroups"
            :key="group.category"
            class="permission-group"
          >
            <div class="permission-group-title">
              <strong>{{ categoryLabels[group.category] ?? group.category }}</strong>
              <span>{{ group.items.length }} 项权限</span>
            </div>
            <div class="permission-list">
              <label v-for="permission in group.items" :key="permission.code" class="permission-row">
                <input
                  type="checkbox"
                  :checked="selectedRole?.permissions.includes(permission.code)"
                  :disabled="!selectedRole?.is_editable"
                />
                <div>
                  <strong>{{ permission.name }}</strong>
                  <span>{{ permission.code }} · {{ permission.description }}</span>
                </div>
              </label>
            </div>
          </section>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'
import { NButton, NIcon, NTag } from 'naive-ui'
import { computed, ref, watchEffect } from 'vue'
import { Plus, Save } from 'lucide-vue-next'

import { listPermissions, listRoles } from '@/api/rbac'

const { data: permissions } = useQuery({
  queryKey: ['permissions'],
  queryFn: listPermissions
})

const { data: roles } = useQuery({
  queryKey: ['roles'],
  queryFn: listRoles
})

const selectedRoleId = ref<string>()

watchEffect(() => {
  if (!selectedRoleId.value && roles.value?.length) {
    selectedRoleId.value = roles.value[0].id
  }
})

const selectedRole = computed(() => roles.value?.find((role) => role.id === selectedRoleId.value))

const permissionGroups = computed(() => {
  const groups = new Map<string, NonNullable<typeof permissions.value>>()
  for (const permission of permissions.value ?? []) {
    const items = groups.get(permission.category) ?? []
    items.push(permission)
    groups.set(permission.category, items)
  }
  return Array.from(groups.entries()).map(([category, items]) => ({ category, items }))
})

const categoryLabels: Record<string, string> = {
  workspace: '工作区',
  department: '部门',
  project: '项目团队',
  report: '报告',
  template: '模板',
  datasource: '数据源',
  ai: 'AI',
  notification: '通知'
}
</script>
