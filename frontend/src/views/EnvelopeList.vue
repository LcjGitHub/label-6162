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
import { useEnvelopeStore } from '@/stores/envelope'

const router = useRouter()
const toast = useToast()
const confirm = useConfirm()
const store = useEnvelopeStore()

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
      item.origin,
      item.destination,
      String(item.year),
      item.stamp_description,
      item.postmark_type,
      item.condition,
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

/** 品相对应 Tag 样式 */
const conditionSeverity = {
  优秀: 'success',
  良好: 'info',
  一般: 'warn',
}

onMounted(async () => {
  try {
    await store.fetchAll()
    filteredCount.value = store.items.length
  } catch {
    toast.add({ severity: 'error', summary: '加载失败', detail: store.error, life: 4000 })
  }
})

/**
 * 跳转详情页。
 * @param {number} id
 */
function goDetail(id) {
  router.push({ name: 'detail', params: { id } })
}

/**
 * 跳转新建页。
 */
function goCreate() {
  router.push({ name: 'create' })
}

/**
 * 确认后删除记录。
 * @param {{ id: number, origin: string, destination: string, year: number }} row
 */
function confirmDelete(row) {
  confirm.require({
    message: `确定删除「${row.origin} → ${row.destination}（${row.year}）」？`,
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
        <h2 class="text-lg font-semibold text-slate-900">收藏列表</h2>
        <p class="text-sm text-slate-500">{{ displayCount }}</p>
      </div>
      <Button label="新增收藏" icon="pi pi-plus" @click="goCreate" />
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
      :paginator-template="{ layout: 'RowsPerPageDropdown FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport', 'CurrentPageReport': '第 {first}-{last} 条 / 共 {totalRecords} 条' }"
      :rows-per-page-label="'每页条数'"
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

      <Column field="origin" header="寄出地" sortable />
      <Column field="destination" header="目的地" sortable />
      <Column field="year" header="年份" sortable style="width: 100px" />
      <Column field="stamp_description" header="邮票描述" sortable />
      <Column field="postmark_type" header="邮戳类型" sortable />
      <Column field="condition" header="品相" sortable style="width: 100px">
        <template #body="{ data }">
          <Tag :value="data.condition" :severity="conditionSeverity[data.condition] || 'secondary'" />
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
              @click="router.push({ name: 'edit', params: { id: data.id } })"
            />
            <Button icon="pi pi-trash" severity="danger" text rounded @click="confirmDelete(data)" />
          </div>
        </template>
      </Column>

      <template #empty>
        <div class="py-8 text-center text-slate-500">暂无收藏，点击「新增收藏」添加第一条。</div>
      </template>
    </DataTable>
  </div>
</template>
