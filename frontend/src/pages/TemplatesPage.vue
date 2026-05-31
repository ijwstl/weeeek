<template>
  <div class="templates-page">
    <div class="page-heading">
      <div>
        <h1>模板编辑器</h1>
        <p>配置分组、字段、明细表列和模板版本。</p>
      </div>
      <div class="heading-actions">
        <n-button secondary :loading="validateMutation.isPending.value" @click="handleValidateSchema">
          <template #icon>
            <n-icon><CheckCircle2 /></n-icon>
          </template>
          校验 Schema
        </n-button>
        <n-button secondary :loading="saveDraftMutation.isPending.value" @click="handleSaveDraft">
          <template #icon>
            <n-icon><Save /></n-icon>
          </template>
          保存草稿
        </n-button>
        <n-button type="primary" :loading="publishMutation.isPending.value" @click="handlePublish">
          <template #icon>
            <n-icon><UploadCloud /></n-icon>
          </template>
          发布新版本
        </n-button>
      </div>
    </div>

    <div class="template-grid">
      <section class="panel template-list-panel">
        <div class="panel-header">
          <h2>模板</h2>
          <n-tag size="small">{{ templates?.length ?? 0 }} 个</n-tag>
        </div>
        <button
          v-for="template in templates ?? []"
          :key="template.id"
          class="template-item"
          :class="{ active: selectedTemplateId === template.id }"
          type="button"
          @click="selectedTemplateId = template.id"
        >
          <strong>{{ template.name }}</strong>
          <span>{{ template.description }}</span>
          <n-tag size="small" type="info">{{ template.template_scope }}</n-tag>
        </button>
      </section>

      <section class="panel template-canvas-panel">
        <div class="panel-header">
          <div>
            <h2>{{ selectedTemplate?.name ?? '模板画布' }}</h2>
            <p>草稿版本 v{{ draft?.version_no }} · {{ draft?.status }}</p>
          </div>
        </div>

        <div class="template-groups">
          <section
            v-for="(group, groupIndex) in editableSchema.groups"
            :key="group.group_id"
            class="template-group-card"
          >
            <div class="template-group-head">
              <div class="template-edit-stack">
                <input
                  v-model="group.label"
                  class="template-input strong-input"
                  placeholder="分组名称"
                />
                <input
                  v-model="group.description"
                  class="template-input"
                  placeholder="分组说明"
                />
              </div>
              <div class="template-head-actions">
                <n-tag size="small">{{ group.fields.length }} 字段</n-tag>
                <n-button text size="small" @click="removeGroup(groupIndex)">
                  <template #icon>
                    <n-icon><Trash2 /></n-icon>
                  </template>
                </n-button>
              </div>
            </div>

            <div class="template-fields">
              <article
                v-for="(field, fieldIndex) in group.fields"
                :key="field.field_id"
                class="template-field"
              >
                <div class="template-field-head">
                  <div class="template-field-edit-grid">
                    <label>
                      <span>字段名称</span>
                      <input v-model="field.label" class="template-input" />
                    </label>
                    <label>
                      <span>字段标识</span>
                      <input v-model="field.field_id" class="template-input" />
                    </label>
                    <label>
                      <span>字段类型</span>
                      <select
                        v-model="field.type"
                        class="template-input"
                        @change="normalizeFieldConfig(field)"
                      >
                        <option v-for="type in fieldTypes" :key="type" :value="type">
                          {{ fieldTypeLabel(type) }}
                        </option>
                      </select>
                    </label>
                  </div>
                  <div class="field-badges">
                    <label class="template-check">
                      <input v-model="field.required" type="checkbox" />
                      必填
                    </label>
                    <label class="template-check">
                      <input v-model="field.ai_supported" type="checkbox" />
                      AI
                    </label>
                    <label class="template-check">
                      <input v-model="field.summary_enabled" type="checkbox" />
                      汇总
                    </label>
                    <n-button text size="small" @click="removeField(group, fieldIndex)">
                      <template #icon>
                        <n-icon><Trash2 /></n-icon>
                      </template>
                    </n-button>
                  </div>
                </div>

                <table v-if="field.type === 'table'" class="template-column-table">
                  <thead>
                    <tr>
                      <th>列标识</th>
                      <th>列名</th>
                      <th>类型</th>
                      <th>选项</th>
                      <th>必填</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(column, columnIndex) in field.config.columns ?? []" :key="column.column_id">
                      <td>
                        <input v-model="column.column_id" class="template-input compact-input" />
                      </td>
                      <td>
                        <input v-model="column.label" class="template-input compact-input" />
                      </td>
                      <td>
                        <select
                          v-model="column.type"
                          class="template-input compact-input"
                          @change="normalizeColumnConfig(column)"
                        >
                          <option v-for="type in columnTypes" :key="type" :value="type">
                            {{ fieldTypeLabel(type) }}
                          </option>
                        </select>
                      </td>
                      <td>
                        <input
                          v-if="supportsOptions(column.type)"
                          class="template-input compact-input"
                          :value="columnOptionsText(column)"
                          placeholder="用逗号分隔"
                          @input="updateColumnOptions(column, $event)"
                        />
                        <span v-else class="muted-text">-</span>
                      </td>
                      <td>
                        <input v-model="column.required" type="checkbox" />
                      </td>
                      <td>
                        <n-button text size="small" @click="removeColumn(field, columnIndex)">
                          <template #icon>
                            <n-icon><Trash2 /></n-icon>
                          </template>
                        </n-button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <button
                  v-if="field.type === 'table'"
                  class="template-add-button"
                  type="button"
                  @click="addColumn(field)"
                >
                  <n-icon><Plus /></n-icon>
                  添加列
                </button>
              </article>
              <button class="template-add-button" type="button" @click="addField(group)">
                <n-icon><Plus /></n-icon>
                添加字段
              </button>
            </div>
          </section>
          <button class="template-add-button wide-add-button" type="button" @click="addGroup">
            <n-icon><Plus /></n-icon>
            添加分组
          </button>
        </div>
      </section>

      <aside class="panel template-inspector-panel">
        <div class="panel-header">
          <h2>版本</h2>
        </div>
        <div class="version-list">
          <div v-for="version in versions ?? []" :key="version.id" class="version-row">
            <strong>v{{ version.version_no }}</strong>
            <n-tag size="small" :type="version.status === 'published' ? 'success' : 'warning'">
              {{ version.status }}
            </n-tag>
            <span>{{ version.published_at ?? '未发布' }}</span>
          </div>
        </div>
        <div class="template-hint-box">
          <strong>编辑规则</strong>
          <span>保存草稿不会影响历史报告；发布后新报告会使用新的模板快照。</span>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { NButton, NIcon, NTag, useMessage } from 'naive-ui'
import { computed, reactive, ref, watch, watchEffect } from 'vue'
import { CheckCircle2, Plus, Save, Trash2, UploadCloud } from 'lucide-vue-next'

import {
  getTemplateDraft,
  listTemplateVersions,
  listTemplates,
  publishTemplate,
  updateTemplateDraft,
  validateTemplateSchema
} from '@/api/templates'
import type { TemplateColumn, TemplateField, TemplateGroup, TemplateSchema } from '@/api/templates'

const message = useMessage()
const queryClient = useQueryClient()
const editableSchema = reactive<TemplateSchema>({ groups: [] })

const fieldTypes = [
  'text',
  'textarea',
  'table',
  'single_select',
  'multi_select',
  'number',
  'date',
  'progress',
  'member_select',
  'project_select',
  'risk_level',
  'jira_issue',
  'git_ref',
  'url'
]
const columnTypes = fieldTypes.filter((type) => type !== 'table')

const { data: templates } = useQuery({
  queryKey: ['templates'],
  queryFn: listTemplates
})

const selectedTemplateId = ref<string>()

watchEffect(() => {
  if (!selectedTemplateId.value && templates.value?.length) {
    selectedTemplateId.value = templates.value[0].id
  }
})

const selectedTemplate = computed(() =>
  templates.value?.find((template) => template.id === selectedTemplateId.value)
)

const { data: draft } = useQuery({
  queryKey: ['template-draft', selectedTemplateId],
  queryFn: () => getTemplateDraft(selectedTemplateId.value as string),
  enabled: computed(() => Boolean(selectedTemplateId.value))
})

watch(
  draft,
  (value) => {
    editableSchema.groups.splice(
      0,
      editableSchema.groups.length,
      ...cloneSchema(value?.schema_snapshot ?? { groups: [] }).groups
    )
  },
  { immediate: true }
)

const { data: versions } = useQuery({
  queryKey: ['template-versions', selectedTemplateId],
  queryFn: () => listTemplateVersions(selectedTemplateId.value as string),
  enabled: computed(() => Boolean(selectedTemplateId.value))
})

const saveDraftMutation = useMutation({
  mutationFn: () => updateTemplateDraft(selectedTemplateId.value as string, cloneSchema(editableSchema)),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['template-draft'] })
    message.success('模板草稿已保存')
  },
  onError: () => {
    message.error('模板草稿保存失败，请检查字段配置')
  }
})

const validateMutation = useMutation({
  mutationFn: () => validateTemplateSchema(cloneSchema(editableSchema)),
  onSuccess: (result) => {
    if (result.valid) {
      message.success('Schema 校验通过')
      return
    }
    message.error(result.errors[0] ?? 'Schema 校验未通过')
  }
})

const publishMutation = useMutation({
  mutationFn: () => publishTemplate(selectedTemplateId.value as string),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['template-draft'] })
    queryClient.invalidateQueries({ queryKey: ['template-versions'] })
    message.success('模板新版本已发布')
  },
  onError: () => {
    message.error('模板发布失败，请先保存并校验草稿')
  }
})

function columnOptions(column: TemplateColumn) {
  const configuredOptions = column.config?.options
  return Array.isArray(configuredOptions) ? configuredOptions.map(String) : []
}

function columnOptionsText(column: TemplateColumn) {
  return columnOptions(column).join('，')
}

function updateColumnOptions(column: TemplateColumn, event: Event) {
  const value = (event.target as HTMLInputElement).value
  column.config = {
    ...(column.config ?? {}),
    options: value
      .split(/[,，]/)
      .map((option) => option.trim())
      .filter(Boolean)
  }
}

function supportsOptions(type: string) {
  return ['single_select', 'multi_select', 'risk_level'].includes(type)
}

function normalizeColumnConfig(column: TemplateColumn) {
  if (supportsOptions(column.type)) {
    column.config = { ...(column.config ?? {}), options: columnOptions(column) }
    if (!columnOptions(column).length && column.type === 'risk_level') {
      column.config.options = ['low', 'medium', 'high']
    }
    return
  }
  column.config = {}
}

function normalizeFieldConfig(field: TemplateField) {
  if (field.type === 'table') {
    field.config = {
      columns: field.config.columns?.length
        ? field.config.columns
        : [newColumn('title', '事项', 'text')]
    }
    return
  }
  field.config = {}
}

function addGroup() {
  const index = editableSchema.groups.length + 1
  editableSchema.groups.push({
    group_id: `group_${index}`,
    label: `新分组 ${index}`,
    description: '',
    sort_order: index,
    collapsible: false,
    fields: []
  })
}

function removeGroup(index: number) {
  editableSchema.groups.splice(index, 1)
}

function addField(group: TemplateGroup) {
  const index = group.fields.length + 1
  group.fields.push({
    field_id: `${group.group_id}_field_${index}`,
    label: `新字段 ${index}`,
    type: 'text',
    required: false,
    summary_enabled: false,
    ai_supported: false,
    sort_order: index,
    config: {}
  })
}

function removeField(group: TemplateGroup, index: number) {
  group.fields.splice(index, 1)
}

function addColumn(field: TemplateField) {
  const columns = field.config.columns ?? []
  const index = columns.length + 1
  field.config.columns = [...columns, newColumn(`column_${index}`, `列 ${index}`, 'text')]
}

function removeColumn(field: TemplateField, index: number) {
  field.config.columns = (field.config.columns ?? []).filter((_, columnIndex) => columnIndex !== index)
}

function newColumn(columnId: string, label: string, type: string): TemplateColumn {
  return {
    column_id: columnId,
    label,
    type,
    required: false,
    config: {}
  }
}

function handleSaveDraft() {
  if (!selectedTemplateId.value) return
  saveDraftMutation.mutate()
}

function handleValidateSchema() {
  validateMutation.mutate()
}

function handlePublish() {
  if (!selectedTemplateId.value) return
  publishMutation.mutate()
}

function fieldTypeLabel(type: string) {
  const labels: Record<string, string> = {
    text: '单行文本',
    textarea: '多行文本',
    table: '表格',
    single_select: '单选',
    multi_select: '多选',
    number: '数字',
    date: '日期',
    progress: '进度',
    member_select: '成员',
    project_select: '项目',
    risk_level: '风险等级',
    jira_issue: 'Jira 事项',
    git_ref: 'Git 引用',
    url: '链接'
  }
  return labels[type] ?? type
}

function cloneSchema(schema: TemplateSchema): TemplateSchema {
  return JSON.parse(JSON.stringify(schema)) as TemplateSchema
}
</script>
