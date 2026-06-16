<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Dialog from 'primevue/dialog'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { useTagStore } from '@/stores/tag'

const toast = useToast()
const confirm = useConfirm()
const store = useTagStore()

const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const submitted = ref(false)
const editingTag = ref(null)

const colorOptions = [
  '#ef4444',
  '#f59e0b',
  '#eab308',
  '#10b981',
  '#14b8a6',
  '#3b82f6',
  '#6366f1',
  '#8b5cf6',
  '#ec4899',
  '#6b7280',
]

const createForm = reactive({
  name: '',
  color: '#6366f1',
})

const editForm = reactive({
  id: null,
  name: '',
  color: '#6366f1',
})

onMounted(async () => {
  try {
    await store.fetchAll()
  } catch {
    toast.add({ severity: 'error', summary: '加载失败', detail: store.error, life: 4000 })
  }
})

function openCreateDialog() {
  createForm.name = ''
  createForm.color = '#6366f1'
  submitted.value = false
  createDialogVisible.value = true
}

async function doCreate() {
  submitted.value = true
  if (!createForm.name.trim()) {
    toast.add({ severity: 'warn', summary: '请输入标签名称', life: 3000 })
    return
  }
  try {
    await store.create({
      name: createForm.name.trim(),
      color: createForm.color,
    })
    createDialogVisible.value = false
    toast.add({ severity: 'success', summary: '创建成功', life: 3000 })
  } catch {
    toast.add({ severity: 'error', summary: '创建失败', detail: store.error, life: 4000 })
  }
}

function openEditDialog(tag) {
  editingTag.value = tag
  editForm.id = tag.id
  editForm.name = tag.name
  editForm.color = tag.color
  submitted.value = false
  editDialogVisible.value = true
}

async function doEdit() {
  submitted.value = true
  if (!editForm.name.trim()) {
    toast.add({ severity: 'warn', summary: '请输入标签名称', life: 3000 })
    return
  }
  try {
    await store.update(editForm.id, {
      name: editForm.name.trim(),
      color: editForm.color,
    })
    editDialogVisible.value = false
    toast.add({ severity: 'success', summary: '保存成功', life: 3000 })
  } catch {
    toast.add({ severity: 'error', summary: '保存失败', detail: store.error, life: 4000 })
  }
}

function confirmDelete(tag) {
  confirm.require({
    message: `确定删除标签「${tag.name}」吗？删除后所有信封上的该标签都将被移除。`,
    header: '删除确认',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: '取消',
    acceptLabel: '删除',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await store.remove(tag.id)
        toast.add({ severity: 'success', summary: '已删除', life: 3000 })
      } catch {
        toast.add({ severity: 'error', summary: '删除失败', detail: store.error, life: 4000 })
      }
    },
  })
}
</script>

<template>
  <Toast />
  <ConfirmDialog />

  <div class="space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div>
        <h2 class="text-lg font-semibold text-slate-900">标签管理</h2>
        <p class="text-sm text-slate-500">共 {{ store.items.length }} 个标签</p>
      </div>
      <Button label="新建标签" icon="pi pi-plus" @click="openCreateDialog" />
    </div>

    <div v-if="store.loading && !store.items.length" class="flex justify-center py-16">
      <ProgressSpinner />
    </div>

    <div v-else-if="!store.items.length" class="rounded-lg border border-slate-200 bg-white p-12 text-center">
      <i class="pi pi-tags text-5xl text-slate-300 mb-4" />
      <p class="text-slate-500 mb-4">暂无标签，点击「新建标签」添加第一个。</p>
      <Button label="新建标签" icon="pi pi-plus" @click="openCreateDialog" />
    </div>

    <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <div
        v-for="tag in store.items"
        :key="tag.id"
        class="rounded-lg border border-slate-200 bg-white p-4 shadow-sm flex items-center justify-between gap-3"
      >
        <div class="flex items-center gap-3 min-w-0 flex-1">
          <span
            class="h-4 w-4 rounded-full flex-shrink-0"
            :style="{ backgroundColor: tag.color }"
          />
          <span class="font-medium text-slate-900 truncate">{{ tag.name }}</span>
        </div>
        <div class="flex gap-1 flex-shrink-0">
          <Button
            icon="pi pi-pencil"
            severity="secondary"
            text
            rounded
            @click="openEditDialog(tag)"
          />
          <Button
            icon="pi pi-trash"
            severity="danger"
            text
            rounded
            @click="confirmDelete(tag)"
          />
        </div>
      </div>
    </div>

    <Dialog
      v-model:visible="createDialogVisible"
      header="新建标签"
      :modal="true"
      :closable="true"
      :close-on-escape="true"
      :dismissable-mask="true"
      style="width: 420px; max-width: 95vw"
    >
      <div class="space-y-4">
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700">
            标签名称 <span class="text-red-500">*</span>
          </label>
          <InputText
            v-model="createForm.name"
            :invalid="submitted && !createForm.name.trim()"
            placeholder="请输入标签名称"
            maxlength="50"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700">标签颜色</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="color in colorOptions"
              :key="color"
              type="button"
              class="h-8 w-8 rounded-full border-2 transition-all hover:scale-110"
              :class="createForm.color === color ? 'border-slate-800 scale-110' : 'border-transparent'"
              :style="{ backgroundColor: color }"
              @click="createForm.color = color"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          label="取消"
          icon="pi pi-times"
          severity="secondary"
          text
          @click="createDialogVisible = false"
        />
        <Button
          label="创建"
          icon="pi pi-check"
          :loading="store.loading"
          @click="doCreate"
        />
      </template>
    </Dialog>

    <Dialog
      v-model:visible="editDialogVisible"
      header="编辑标签"
      :modal="true"
      :closable="true"
      :close-on-escape="true"
      :dismissable-mask="true"
      style="width: 420px; max-width: 95vw"
    >
      <div class="space-y-4">
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700">
            标签名称 <span class="text-red-500">*</span>
          </label>
          <InputText
            v-model="editForm.name"
            :invalid="submitted && !editForm.name.trim()"
            placeholder="请输入标签名称"
            maxlength="50"
          />
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700">标签颜色</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="color in colorOptions"
              :key="color"
              type="button"
              class="h-8 w-8 rounded-full border-2 transition-all hover:scale-110"
              :class="editForm.color === color ? 'border-slate-800 scale-110' : 'border-transparent'"
              :style="{ backgroundColor: color }"
              @click="editForm.color = color"
            />
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          label="取消"
          icon="pi pi-times"
          severity="secondary"
          text
          @click="editDialogVisible = false"
        />
        <Button
          label="保存"
          icon="pi pi-check"
          :loading="store.loading"
          @click="doEdit"
        />
      </template>
    </Dialog>
  </div>
</template>
