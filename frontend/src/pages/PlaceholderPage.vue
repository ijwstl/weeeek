<template>
  <div class="placeholder-page">
    <h1>{{ title }}</h1>
    <p>该模块将在后续里程碑中实现。</p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => String(route.meta.title ?? '页面'))
</script>

