<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <router-view />
    </n-message-provider>
  </n-config-provider>
</template>

<script setup lang="ts">
import type { GlobalThemeOverrides } from 'naive-ui'
import { NConfigProvider, NMessageProvider } from 'naive-ui'

const themeOverrides: GlobalThemeOverrides = {
  common: {
    primaryColor: '#2563EB',
    primaryColorHover: '#1D4ED8',
    primaryColorPressed: '#1E40AF',
    primaryColorSuppl: '#3B82F6',
    borderRadius: '8px'
  },
  Button: {
    borderRadiusMedium: '8px',
    borderRadiusSmall: '8px'
  },
  Tag: {
    borderRadius: '999px'
  }
}
</script>
