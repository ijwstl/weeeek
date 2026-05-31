<template>
  <div class="department-node-wrap">
    <button
      class="department-node"
      :class="{ active: node.id === selectedId }"
      type="button"
      @click="$emit('select', node.id)"
    >
      <span>{{ node.name }}</span>
      <small>Level {{ node.depth }}</small>
    </button>

    <div v-if="node.children.length" class="department-node-children">
      <DepartmentNode
        v-for="child in node.children"
        :key="child.id"
        :node="child"
        :selected-id="selectedId"
        @select="$emit('select', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DepartmentTreeNode } from '@/api/organization'

defineProps<{
  node: DepartmentTreeNode
  selectedId?: string
}>()

defineEmits<{
  select: [id: string]
}>()
</script>

