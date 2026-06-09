<template>
<div class="tiptap-report-editor">
    <div v-if="editor" class="tiptap-toolbar">
        <button v-for="action in toolbarActions" :key="action.key" class="tiptap-tool-button"
            :class="{ active: action.active() }" type="button" :title="action.label" @click="action.run()">
            <n-icon size="16">
                <component :is="action.icon" />
            </n-icon>
        </button>
    </div>
    <editor-content class="tiptap-editor-surface" :editor="editor" />
</div>
</template>

<script setup lang="ts">
import { EditorContent, useEditor } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'
import { TableKit } from '@tiptap/extension-table'
import { NIcon } from 'naive-ui'
import {
    Bold,
    Columns3,
    Heading1,
    Heading2,
    Italic,
    List,
    ListOrdered,
    Quote,
    Redo2,
    Rows4,
    Rows3,
    Table,
    TableCellsSplit,
    Trash2,
    Undo2
} from 'lucide-vue-next'
import { computed, watch } from 'vue'

const props = defineProps<{
    modelValue: Record<string, unknown> | null
    fallbackMarkdown?: string
}>()

const emit = defineEmits<{
    'update:modelValue': [value: Record<string, unknown>]
    updateHtml: [value: string]
    updateText: [value: string]
}>()

const editor = useEditor({
    content: initialContent(),
    extensions: [
        StarterKit,
        TableKit.configure({
            table: {
                resizable: true,
                HTMLAttributes: {
                    class: 'tiptap-table'
                }
            }
        })
    ],
    editorProps: {
        attributes: {
            class: 'tiptap-prose'
        }
    },
    onCreate: ({ editor }) => {
        emitEditorContent(editor)
    },
    onUpdate: ({ editor }) => {
        emitEditorContent(editor)
    }
})

const toolbarActions = computed(() => [
    {
        key: 'bold',
        label: '加粗',
        icon: Bold,
        active: () => Boolean(editor.value?.isActive('bold')),
        run: () => editor.value?.chain().focus().toggleBold().run()
    },
    {
        key: 'italic',
        label: '斜体',
        icon: Italic,
        active: () => Boolean(editor.value?.isActive('italic')),
        run: () => editor.value?.chain().focus().toggleItalic().run()
    },
    {
        key: 'heading1',
        label: '一级标题',
        icon: Heading1,
        active: () => Boolean(editor.value?.isActive('heading', { level: 1 })),
        run: () => editor.value?.chain().focus().toggleHeading({ level: 1 }).run()
    },
    {
        key: 'heading2',
        label: '二级标题',
        icon: Heading2,
        active: () => Boolean(editor.value?.isActive('heading', { level: 2 })),
        run: () => editor.value?.chain().focus().toggleHeading({ level: 2 }).run()
    },
    {
        key: 'bulletList',
        label: '无序列表',
        icon: List,
        active: () => Boolean(editor.value?.isActive('bulletList')),
        run: () => editor.value?.chain().focus().toggleBulletList().run()
    },
    {
        key: 'orderedList',
        label: '有序列表',
        icon: ListOrdered,
        active: () => Boolean(editor.value?.isActive('orderedList')),
        run: () => editor.value?.chain().focus().toggleOrderedList().run()
    },
    {
        key: 'blockquote',
        label: '引用',
        icon: Quote,
        active: () => Boolean(editor.value?.isActive('blockquote')),
        run: () => editor.value?.chain().focus().toggleBlockquote().run()
    },
    {
        key: 'insertTable',
        label: '插入表格',
        icon: Table,
        active: () => Boolean(editor.value?.isActive('table')),
        run: () => editor.value?.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run()
    },
    {
        key: 'addColumnAfter',
        label: '右侧加列',
        icon: Columns3,
        active: () => false,
        run: () => editor.value?.chain().focus().addColumnAfter().run()
    },
    {
        key: 'deleteColumn',
        label: '删除列',
        icon: TableCellsSplit,
        active: () => false,
        run: () => editor.value?.chain().focus().deleteColumn().run()
    },
    {
        key: 'addRowAfter',
        label: '下方加行',
        icon: Rows4,
        active: () => false,
        run: () => editor.value?.chain().focus().addRowAfter().run()
    },
    {
        key: 'deleteRow',
        label: '删除行',
        icon: Rows3,
        active: () => false,
        run: () => editor.value?.chain().focus().deleteRow().run()
    },
    {
        key: 'deleteTable',
        label: '删除表格',
        icon: Trash2,
        active: () => false,
        run: () => editor.value?.chain().focus().deleteTable().run()
    },
    {
        key: 'undo',
        label: '撤销',
        icon: Undo2,
        active: () => false,
        run: () => editor.value?.chain().focus().undo().run()
    },
    {
        key: 'redo',
        label: '重做',
        icon: Redo2,
        active: () => false,
        run: () => editor.value?.chain().focus().redo().run()
    }
])

watch(
    () => props.modelValue,
    (value) => {
        if (!editor.value || !value) return
        if (JSON.stringify(editor.value.getJSON()) === JSON.stringify(value)) return
        editor.value.commands.setContent(value)
    }
)

function initialContent() {
    if (props.modelValue) return props.modelValue
    return markdownToHtml(props.fallbackMarkdown ?? '')
}

function emitEditorContent(editor: { getJSON: () => unknown; getHTML: () => string; getText: (options?: { blockSeparator?: string }) => string }) {
    emit('update:modelValue', editor.getJSON() as Record<string, unknown>)
    emit('updateHtml', editor.getHTML())
    emit('updateText', editor.getText({ blockSeparator: '\n' }))
}

function markdownToHtml(markdown: string) {
    const lines = markdown.split('\n')
    return lines
        .map((line) => {
            if (line.startsWith('## ')) return `<h2>${escapeHtml(line.slice(3))}</h2>`
            if (line.startsWith('# ')) return `<h1>${escapeHtml(line.slice(2))}</h1>`
            if (!line.trim()) return '<p></p>'
            return `<p>${escapeHtml(line)}</p>`
        })
        .join('')
}

function escapeHtml(value: string) {
    return value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;')
}
</script>
