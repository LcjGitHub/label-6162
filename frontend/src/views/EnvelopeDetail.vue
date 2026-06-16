<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import InputNumber from 'primevue/inputnumber'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import Tag from 'primevue/tag'
import MultiSelect from 'primevue/multiselect'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'
import { useEnvelopeStore } from '@/stores/envelope'
import { useTagStore } from '@/stores/tag'

const props = defineProps({
  id: { type: Number, default: null },
  mode: { type: String, default: 'view' },
})

const router = useRouter()
const toast = useToast()
const store = useEnvelopeStore()
const tagStore = useTagStore()

/** 是否处于可编辑状态 */
const editing = computed(() => props.mode === 'create' || props.mode === 'edit')
const submitted = ref(false)

const postmarkOptions = ['圆形日戳', '方形纪念戳', '风景日戳', '机盖戳', '其他']
const conditionOptions = ['优秀', '良好', '一般']

const form = reactive({
  origin: '',
  destination: '',
  year: new Date().getFullYear(),
  stamp_description: '',
  postmark_type: '圆形日戳',
  condition: '良好',
  remark: '',
  tagIds: [],
})

const tagOptions = computed(() => {
  return tagStore.items.map((t) => ({
    label: t.name,
    value: t.id,
    color: t.color,
  }))
})

const pageTitle = computed(() => {
  if (props.mode === 'create') return '新增收藏'
  if (props.mode === 'edit') return '编辑收藏'
  return '收藏详情'
})

/** 品相对应 Tag 样式 */
const conditionSeverity = {
  优秀: 'success',
  良好: 'info',
  一般: 'warn',
}

onMounted(async () => {
  try {
    await tagStore.fetchAll()
  } catch {
    toast.add({ severity: 'warn', summary: '标签加载失败', detail: tagStore.error, life: 4000 })
  }

  if (props.mode === 'create') return
  try {
    const data = await store.fetchOne(props.id)
    Object.assign(form, {
      origin: data.origin,
      destination: data.destination,
      year: data.year,
      stamp_description: data.stamp_description,
      postmark_type: data.postmark_type,
      condition: data.condition,
      remark: data.remark || '',
      tagIds: (data.tags || []).map((t) => t.id),
    })
  } catch {
    toast.add({ severity: 'error', summary: '加载失败', detail: store.error, life: 4000 })
    router.push({ name: 'list' })
  }
})

/**
 * 校验表单必填项。
 * @returns {boolean}
 */
function validate() {
  submitted.value = true
  return (
    form.origin.trim() &&
    form.destination.trim() &&
    form.year &&
    form.stamp_description.trim() &&
    form.postmark_type &&
    form.condition
  )
}

/**
 * 保存（新建或更新）。
 * @returns {Promise<void>}
 */
async function save() {
  if (!validate()) {
    toast.add({ severity: 'warn', summary: '请填写完整信息', life: 3000 })
    return
  }
  const payload = { ...form, year: Number(form.year), tag_ids: form.tagIds }
  try {
    if (props.mode === 'create') {
      const created = await store.create(payload)
      toast.add({ severity: 'success', summary: '创建成功', life: 3000 })
      router.push({ name: 'detail', params: { id: created.id } })
    } else {
      await store.update(props.id, payload)
      toast.add({ severity: 'success', summary: '保存成功', life: 3000 })
      router.push({ name: 'detail', params: { id: props.id } })
    }
  } catch {
    toast.add({ severity: 'error', summary: '保存失败', detail: store.error, life: 4000 })
  }
}

/**
 * 进入编辑模式。
 */
function startEdit() {
  router.push({ name: 'edit', params: { id: props.id } })
}

/**
 * 返回列表。
 */
function goBack() {
  router.push({ name: 'list' })
}

/**
 * 根据标签ID获取标签信息。
 * @param {number} tagId
 * @returns {{id: number, name: string, color: string} | undefined}
 */
function getTagById(tagId) {
  return tagStore.items.find((t) => t.id === tagId)
}

/**
 * 根据标签ID获取标签颜色。
 * @param {number} tagId
 * @returns {string | undefined}
 */
function getTagColor(tagId) {
  const tag = getTagById(tagId)
  return tag?.color
}

/**
 * 移除已选标签芯片。
 * @param {number} tagId
 */
function removeChip(tagId) {
  form.tagIds = form.tagIds.filter((id) => id !== tagId)
}
</script>

<template>
  <Toast />

  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <Button icon="pi pi-arrow-left" severity="secondary" text rounded @click="goBack" />
        <h2 class="text-lg font-semibold text-slate-900">{{ pageTitle }}</h2>
      </div>
      <div v-if="mode === 'view'" class="flex gap-2">
        <Button label="编辑" icon="pi pi-pencil" @click="startEdit" />
      </div>
      <div v-else class="flex gap-2">
        <Button label="取消" severity="secondary" outlined @click="goBack" />
        <Button label="保存" icon="pi pi-check" :loading="store.loading" @click="save" />
      </div>
    </div>

    <div v-if="store.loading && mode !== 'create'" class="flex justify-center py-16">
      <ProgressSpinner />
    </div>

    <div v-else class="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
      <div class="grid gap-6 md:grid-cols-2">
        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700">寄出地 <span v-if="editing" class="text-red-500">*</span></label>
          <InputText
            v-if="editing"
            v-model="form.origin"
            :invalid="submitted && !form.origin.trim()"
            placeholder="例如：上海"
          />
          <p v-else class="text-slate-900">{{ form.origin }}</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700">目的地 <span v-if="editing" class="text-red-500">*</span></label>
          <InputText
            v-if="editing"
            v-model="form.destination"
            :invalid="submitted && !form.destination.trim()"
            placeholder="例如：北京"
          />
          <p v-else class="text-slate-900">{{ form.destination }}</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700">年份 <span v-if="editing" class="text-red-500">*</span></label>
          <InputNumber
            v-if="editing"
            v-model="form.year"
            :invalid="submitted && !form.year"
            :use-grouping="false"
            :min="1800"
            :max="2100"
          />
          <p v-else class="text-slate-900">{{ form.year }}</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700">邮戳类型 <span v-if="editing" class="text-red-500">*</span></label>
          <Select
            v-if="editing"
            v-model="form.postmark_type"
            :options="postmarkOptions"
            placeholder="选择邮戳类型"
          />
          <p v-else class="text-slate-900">{{ form.postmark_type }}</p>
        </div>

        <div class="flex flex-col gap-2 md:col-span-2">
          <label class="text-sm font-medium text-slate-700">邮票描述 <span v-if="editing" class="text-red-500">*</span></label>
          <Textarea
            v-if="editing"
            v-model="form.stamp_description"
            :invalid="submitted && !form.stamp_description.trim()"
            rows="3"
            placeholder="邮票名称、编号或系列描述"
          />
          <p v-else class="text-slate-900">{{ form.stamp_description }}</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700">品相 <span v-if="editing" class="text-red-500">*</span></label>
          <Select
            v-if="editing"
            v-model="form.condition"
            :options="conditionOptions"
            placeholder="选择品相"
          />
          <Tag v-else :value="form.condition" :severity="conditionSeverity[form.condition] || 'secondary'" />
        </div>

        <div class="flex flex-col gap-2 md:col-span-2">
          <label class="text-sm font-medium text-slate-700">备注</label>
          <Textarea
            v-if="editing"
            v-model="form.remark"
            rows="3"
            placeholder="填写备注信息（可选，最多 1000 字符）"
            :maxlength="1000"
          />
          <p v-else class="text-slate-900 whitespace-pre-wrap">{{ form.remark || '-' }}</p>
        </div>

        <div class="flex flex-col gap-2 md:col-span-2">
          <label class="text-sm font-medium text-slate-700">标签</label>
          <MultiSelect
            v-if="editing"
            v-model="form.tagIds"
            :options="tagOptions"
            optionLabel="label"
            optionValue="value"
            placeholder="选择标签（可多选）"
            display="chip"
            :maxSelectedLabels="5"
            :selectedItemsLabel="selectedCount => `已选 ${selectedCount} 个`"
          >
            <template #chip="{ value, label }">
              <span
                class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium text-white"
                :style="{ backgroundColor: getTagColor(value) || '#6b7280' }"
              >
                {{ label }}
                <i class="pi pi-times cursor-pointer text-white/80 hover:text-white" @click.stop="removeChip(value)" />
              </span>
            </template>
          </MultiSelect>
          <div v-else class="flex flex-wrap gap-2">
            <template v-if="form.tagIds && form.tagIds.length > 0">
              <span
                v-for="tagId in form.tagIds"
                :key="tagId"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white"
                :style="{ backgroundColor: getTagById(tagId)?.color || '#6b7280' }"
              >
                {{ getTagById(tagId)?.name || '未知标签' }}
              </span>
            </template>
            <span v-else class="text-slate-400 text-sm">暂无标签</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
