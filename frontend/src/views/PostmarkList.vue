<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { FilterMatchMode } from '@primevue/core/api'
import { useToast } from 'primevue/usetoast'
import { useConfirm } from 'primevue/useconfirm'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import { usePostmarkStore } from '@/stores/postmark'

const router = useRouter()
const toast = useToast()
const confirm = useConfirm()
const store = usePostmarkStore()

const dt = ref(null)
const filteredCount = ref(0)

const filters = ref({
  global: { value: null, matchMode: FilterMatchMode.CONTAINS },
})

const displayItems = computed(() => {
  const keyword = filters.value.global?.value?.trim().toLowerCase()
  if (!keyword) {
    filteredCount.value = store.items.length
    return store.items
  }
  const result = store.items.filter((item) =>
    [
      item.name,
      item.shape,
      item.common_use,
      item.description,
    ].some((v) => v.toLowerCase().includes(keyword))
  )
  filteredCount.value = result.length
  return result
})

const displayCount = computed(() => {
  const keyword = filters.value.global?.value?.trim()
  if (keyword) {
    return `搜索结果 ${filteredCount.value} 条 / 共 ${store.items.length} 条`
  }
  return `共 ${store.items.length} 条记录`
})

const shapeSeverity = {
  圆形: 'info',
  方形: 'success',
  椭圆形: 'warn',
  其他: 'secondary',
}

onMounted(async () => {
  try {
    await store.fetchAll()
    filteredCount.value = store.items.length
  } catch {
    toast.add({ severity: 'error', summary: '加载失败', detail: store.error, life: 4000 })
  }
})

function goDetail(id) {
  router.push({ name: 'postmark-detail', params: { id } })
}

function goCreate() {
  router.push({ name: 'postmark-create' })
}

function confirmDelete(row) {
  confirm.require({
    message: `确定删除「${row.name}」？`,
    header: '删除确认',
    icon: 'pi pi-exclamation-triangle',
    rejectLabel: '取消',
    acceptLabel: '删除',
    acceptClass: 'p-button-danger',
    accept: async () => {
      try {
        await store.remove(row.id)
        filteredCount.value = displayItems.value.length
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
        <h2 class="text-lg font-semibold text-slate-900">邮戳图鉴</h2>
        <p class="text-sm text-slate-500">{{ displayCount }}</p>
      </div>
      <Button label="新增邮戳" icon="pi pi-plus" @click="goCreate" />
    </div>

    <div v-if="store.loading && !store.items.length" class="flex justify-center py-16">
      <ProgressSpinner />
    </div>

    <DataTable
      v-else
      ref="dt"
      v-model:filters="filters"
      :value="displayItems"
      :loading="store.loading"
      paginator
      :rows="10"
      :rows-per-page-options="[5, 10, 20]"
      striped-rows
      removable-sort
      class="rounded-lg border border-slate-200 bg-white shadow-sm"
      data-key="id"
      :paginator-template="{
        layout: 'RowsPerPageDropdown FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport',
        FirstPageLink: { label: '首页' },
        PrevPageLink: { label: '上一页' },
        NextPageLink: { label: '下一页' },
        LastPageLink: { label: '末页' },
        RowsPerPageDropdown: { label: '每页条数' },
        CurrentPageReport: '第 {first}-{last} 条 / 共 {totalRecords} 条',
      }"
    >
      <template #header>
        <div class="flex justify-end">
          <span class="relative">
            <i class="pi pi-search absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              v-model="filters.global.value"
              type="text"
              placeholder="搜索..."
              class="rounded border border-slate-300 py-2 pl-9 pr-3 text-sm"
            />
          </span>
        </div>
      </template>

      <Column field="name" header="名称" sortable />
      <Column field="shape" header="形状" sortable style="width: 100px">
        <template #body="{ data }">
          <Tag :value="data.shape" :severity="shapeSeverity[data.shape] || 'secondary'" />
        </template>
      </Column>
      <Column field="common_use" header="常见用途" sortable />
      <Column field="description" header="简介" sortable :style="{ minWidth: '200px' }">
        <template #body="{ data }">
          <span class="line-clamp-2">{{ data.description }}</span>
        </template>
      </Column>
      <Column header="操作" style="width: 180px">
        <template #body="{ data }">
          <div class="flex gap-2">
            <Button icon="pi pi-eye" severity="secondary" text rounded @click="goDetail(data.id)" />
            <Button
              icon="pi pi-pencil"
              severity="secondary"
              text
              rounded
              @click="router.push({ name: 'postmark-edit', params: { id: data.id } })"
            />
            <Button icon="pi pi-trash" severity="danger" text rounded @click="confirmDelete(data)" />
          </div>
        </template>
      </Column>

      <template #empty>
        <div v-if="filters.global?.value?.trim()" class="py-8 text-center text-slate-500">未找到匹配的邮戳</div>
        <div v-else class="py-8 text-center text-slate-500">暂无邮戳，点击「新增邮戳」添加第一条。</div>
      </template>
    </DataTable>
  </div>
</template>
