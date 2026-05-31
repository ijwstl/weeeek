import { createRouter, createWebHistory } from 'vue-router'

import AppLayout from '@/layouts/AppLayout.vue'
import DataSourcesPage from '@/pages/DataSourcesPage.vue'
import DashboardPage from '@/pages/DashboardPage.vue'
import DepartmentsPage from '@/pages/DepartmentsPage.vue'
import PlaceholderPage from '@/pages/PlaceholderPage.vue'
import ProjectsPage from '@/pages/ProjectsPage.vue'
import ReportFillPage from '@/pages/ReportFillPage.vue'
import ReportsPage from '@/pages/ReportsPage.vue'
import RolesPage from '@/pages/RolesPage.vue'
import SettingsPage from '@/pages/SettingsPage.vue'
import TemplatesPage from '@/pages/TemplatesPage.vue'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppLayout,
      children: [
        { path: '', name: 'dashboard', component: DashboardPage },
        {
          path: 'departments',
          name: 'departments',
          component: DepartmentsPage,
          meta: { title: '部门' }
        },
        {
          path: 'projects',
          name: 'projects',
          component: ProjectsPage,
          meta: { title: '项目团队' }
        },
        {
          path: 'reports',
          name: 'reports',
          component: ReportsPage,
          meta: { title: '报告中心' }
        },
        {
          path: 'reports/:reportId',
          name: 'report-fill',
          component: ReportFillPage,
          meta: { title: '填写报告' }
        },
        {
          path: 'templates',
          name: 'templates',
          component: TemplatesPage,
          meta: { title: '模板编辑器' }
        },
        {
          path: 'data-sources',
          name: 'data-sources',
          component: DataSourcesPage,
          meta: { title: '数据源与 AI 设置' }
        },
        {
          path: 'settings',
          name: 'settings',
          component: SettingsPage,
          meta: { title: '设置' }
        },
        {
          path: 'settings/roles',
          name: 'roles',
          component: RolesPage,
          meta: { title: '角色权限' }
        }
      ]
    }
  ]
})
