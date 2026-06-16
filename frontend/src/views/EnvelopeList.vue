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
import Dialog from 'primevue/dialog'
import { useEnvelopeStore } from '@/stores/envelope'

const router = useRouter()
const toast = useToast()
const confirm = useConfirm()
const store = useEnvelopeStore()

const dt = ref(null)
const filteredCount = ref(0)

const importDialogVisible = ref(false)
const selectedFile = ref(null)
const previewRows = ref([])
const previewHeaders = ref([])
const fileParseError = ref('')
const isHeaderError = ref(false)
const importing = ref(false)

const CSV_HEADERS = ['寄出地', '目的地', '年份', '邮票描述', '邮戳类型', '品相']

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
      item.remark || '',
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

function parseCSVLine(line) {
  const result = []
  let current = ''
  let inQuotes = false
  for (let i = 0; i < line.length; i++) {
    const char = line[i]
    if (inQuotes) {
      if (char === '"') {
        if (line[i + 1] === '"') {
          current += '"'
          i++
        } else {
          inQuotes = false
        }
      } else {
        current += char
      }
    } else {
      if (char === '"') {
        inQuotes = true
      } else if (char === ',') {
        result.push(current)
        current = ''
      } else {
        current += char
      }
    }
  }
  result.push(current)
  return result.map((s) => s.trim())
}

async function handleFileSelect(event) {
  const file = event.target.files?.[0]
  if (!file) return
  selectedFile.value = file
  fileParseError.value = ''
  isHeaderError.value = false
  previewHeaders.value = []
  previewRows.value = []

  try {
    const text = await file.text()
    const allLines = text.split(/\r?\n/).filter((l) => l.trim() !== '')
    if (allLines.length === 0) {
      fileParseError.value = '文件内容为空'
      return
    }
    const headerLine = parseCSVLine(allLines[0])
    const headerTrimmed = headerLine.map((h) => h.trim())

    if (headerTrimmed.length !== CSV_HEADERS.length || !headerTrimmed.every((h, i) => h === CSV_HEADERS[i])) {
      fileParseError.value = '表头格式不正确，请与下方期望表头对比后修正文件'
      isHeaderError.value = true
      previewHeaders.value = headerTrimmed
      previewRows.value = allLines.slice(1, 6).map(parseCSVLine)
      return
    }
    previewHeaders.value = headerTrimmed
    previewRows.value = allLines.slice(1, 11).map(parseCSVLine)
    if (allLines.length - 1 > 10) {
      previewRows.value.push(Array(CSV_HEADERS.length).fill(`... 共 ${allLines.length - 1} 行数据，仅预览前 10 行`))
    }
  } catch (err) {
    fileParseError.value = `读取文件失败：${err.message || err}`
  }
}

function openImportDialog() {
  importDialogVisible.value = true
  selectedFile.value = null
  previewRows.value = []
  previewHeaders.value = []
  fileParseError.value = ''
  isHeaderError.value = false
  const fileInput = document.getElementById('csv-file-input')
  if (fileInput) fileInput.value = ''
}

async function doImport() {
  if (!selectedFile.value) {
    toast.add({ severity: 'warn', summary: '请先选择 CSV 文件', life: 3000 })
    return
  }
  importing.value = true
  try {
    const result = await store.batchImport(selectedFile.value)
    importDialogVisible.value = false
    filteredCount.value = displayItems.value.length

    if (result.failed_count > 0) {
      const detailLines = result.failed_lines.slice(0, 5)
      if (result.failed_lines.length > 5) {
        detailLines.push(`... 还有 ${result.failed_lines.length - 5} 条错误未显示`)
      }
      toast.add({
        severity: 'warn',
        summary: `导入完成：成功 ${result.success} 条，失败 ${result.failed_count} 条`,
        detail: detailLines.join('\n'),
        life: 8000,
      })
    } else {
      toast.add({
        severity: 'success',
        summary: `导入成功 ${result.success} 条记录`,
        life: 4000,
      })
    }
  } catch (err) {
    const detail = store.error || err.message || '导入失败'
    toast.add({ severity: 'error', summary: '导入失败', detail, life: 6000 })
  } finally {
    importing.value = false
  }
}

function downloadTemplate() {
  const content = CSV_HEADERS.join(',') + '\n' + '上海,北京,2020,生肖邮票,圆形邮戳,优秀\n'
  const blob = new Blob(['\uFEFF' + content], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '信封收藏导入模板.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
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
      <div class="flex flex-wrap gap-2">
        <Button label="批量导入" icon="pi pi-upload" severity="info" @click="openImportDialog" />
        <Button label="新增收藏" icon="pi pi-plus" @click="goCreate" />
      </div>
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
      <Column field="remark" header="备注" sortable style="min-width: 180px">
        <template #body="{ data }">
          <span
            class="block max-w-[200px] truncate"
            :title="data.remark || ''"
          >
            {{ data.remark || '-' }}
          </span>
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

    <Dialog
      v-model:visible="importDialogVisible"
      header="批量导入收藏记录"
      :modal="true"
      :closable="true"
      :close-on-escape="true"
      :dismissable-mask="true"
      style="width: 800px; max-width: 95vw"
    >
      <div class="space-y-4">
        <div class="rounded-md bg-blue-50 border border-blue-200 p-3 text-sm text-blue-800">
          <p class="font-medium mb-1">CSV 文件格式要求：</p>
          <ul class="list-disc pl-5 space-y-0.5">
            <li>编码：UTF-8（推荐带 BOM）或 GBK</li>
            <li>分隔符：英文逗号</li>
            <li>表头必须为：寄出地、目的地、年份、邮票描述、邮戳类型、品相（顺序不能变）</li>
            <li>年份范围：1800–2100 的整数</li>
            <li>品相：优秀 / 良好 / 一般</li>
          </ul>
          <button
            type="button"
            class="mt-2 inline-flex items-center gap-1 text-blue-700 hover:text-blue-900 underline text-sm"
            @click="downloadTemplate"
          >
            <i class="pi pi-download" />
            下载 CSV 模板（含示例）
          </button>
        </div>

        <div>
          <label class="block text-sm font-medium text-slate-700 mb-2">选择 CSV 文件</label>
          <input
            id="csv-file-input"
            type="file"
            accept=".csv,text/csv"
            @change="handleFileSelect"
            class="block w-full text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer"
          />
          <p v-if="selectedFile" class="mt-2 text-sm text-slate-600">
            已选择文件：<span class="font-medium">{{ selectedFile.name }}</span>（{{ (selectedFile.size / 1024).toFixed(1) }} KB）
          </p>
        </div>

        <div v-if="fileParseError" class="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          <p class="font-medium">⚠️ {{ fileParseError }}</p>
        </div>

        <div v-if="isHeaderError" class="space-y-2">
          <p class="text-sm font-medium text-slate-700">表头对比：</p>
          <div class="overflow-x-auto rounded-md border border-red-200">
            <table class="min-w-full text-sm">
              <thead class="bg-red-50">
                <tr>
                  <th class="px-3 py-2 text-left font-medium text-red-700 border-b border-red-200 w-24">类型</th>
                  <th
                    v-for="(h, i) in CSV_HEADERS"
                    :key="'exp-' + i"
                    class="px-3 py-2 text-left font-medium text-red-700 border-b border-red-200"
                  >
                    第 {{ i + 1 }} 列
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr class="bg-green-50">
                  <td class="px-3 py-2 font-medium text-green-700 border-b border-slate-100">期望表头</td>
                  <td
                    v-for="(h, i) in CSV_HEADERS"
                    :key="'exph-' + i"
                    class="px-3 py-2 text-green-700 border-b border-slate-100"
                  >
                    <span class="font-medium">{{ h }}</span>
                  </td>
                </tr>
                <tr class="bg-red-50">
                  <td class="px-3 py-2 font-medium text-red-700 border-b border-slate-100">实际表头</td>
                  <template v-if="previewHeaders.length > 0">
                    <td
                      v-for="(h, i) in previewHeaders"
                      :key="'acth-' + i"
                      class="px-3 py-2 text-red-700 border-b border-slate-100"
                    >
                      <span v-if="h === CSV_HEADERS[i]" class="text-green-600">{{ h }}</span>
                      <span v-else class="font-medium">{{ h || '(空)' }}</span>
                    </td>
                    <td
                      v-for="i in (CSV_HEADERS.length - previewHeaders.length)"
                      :key="'miss-' + i"
                      class="px-3 py-2 text-red-400 border-b border-slate-100 italic"
                    >
                      （缺失）
                    </td>
                  </template>
                  <td v-else class="px-3 py-2 text-slate-500 border-b border-slate-100 italic" :colspan="CSV_HEADERS.length">
                    无法解析表头
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div v-if="previewHeaders.length > 0 && !isHeaderError" class="space-y-2">
          <p class="text-sm font-medium text-slate-700">文件预览（最多显示前 10 行）：</p>
          <div class="overflow-x-auto rounded-md border border-slate-200 max-h-64 overflow-y-auto">
            <table class="min-w-full text-sm">
              <thead class="bg-slate-50 sticky top-0">
                <tr>
                  <th class="px-2 py-2 text-left text-slate-500 font-medium border-b border-slate-200 w-12">#</th>
                  <th
                    v-for="(h, i) in previewHeaders"
                    :key="i"
                    class="px-3 py-2 text-left font-medium border-b border-slate-200"
                    :class="h !== CSV_HEADERS[i] ? 'bg-red-50 text-red-700' : 'text-slate-700'"
                  >
                    {{ h }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, ri) in previewRows" :key="ri" class="hover:bg-slate-50">
                  <td class="px-2 py-1.5 border-b border-slate-100 text-slate-500">{{ ri + 1 }}</td>
                  <td
                    v-for="(cell, ci) in row"
                    :key="ci"
                    class="px-3 py-1.5 border-b border-slate-100 text-slate-700 max-w-xs truncate"
                    :title="cell"
                  >
                    {{ cell }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <template #footer>
        <Button
          label="取消"
          icon="pi pi-times"
          severity="secondary"
          text
          @click="importDialogVisible = false"
          :disabled="importing"
        />
        <Button
          label="确认导入"
          icon="pi pi-check"
          :loading="importing"
          @click="doImport"
          :disabled="!selectedFile || !!fileParseError || importing"
        />
      </template>
    </Dialog>
  </div>
</template>
