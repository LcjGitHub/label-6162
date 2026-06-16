<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import Select from 'primevue/select'
import Textarea from 'primevue/textarea'
import Tag from 'primevue/tag'
import ProgressSpinner from 'primevue/progressspinner'
import Toast from 'primevue/toast'
import { usePostmarkStore } from '@/stores/postmark'

const props = defineProps({
  id: { type: Number, default: null },
  mode: { type: String, default: 'view' },
})

const router = useRouter()
const toast = useToast()
const store = usePostmarkStore()

const editing = computed(() => props.mode === 'create' || props.mode === 'edit')
const submitted = ref(false)

const shapeOptions = ['圆形', '方形', '椭圆形', '其他']

const form = reactive({
  name: '',
  shape: '圆形',
  common_use: '',
  description: '',
})

const pageTitle = computed(() => {
  if (props.mode === 'create') return '新增邮戳'
  if (props.mode === 'edit') return '编辑邮戳'
  return '邮戳详情'
})

const shapeSeverity = {
  圆形: 'info',
  方形: 'success',
  椭圆形: 'warn',
  其他: 'secondary',
}

onMounted(async () => {
  if (props.mode === 'create') return
  try {
    const data = await store.fetchOne(props.id)
    Object.assign(form, {
      name: data.name,
      shape: data.shape,
      common_use: data.common_use,
      description: data.description,
    })
  } catch {
    toast.add({ severity: 'error', summary: '加载失败', detail: store.error, life: 4000 })
    router.push({ name: 'postmark-list' })
  }
})

function validate() {
  submitted.value = true
  return (
    form.name.trim() &&
    form.shape &&
    form.common_use.trim() &&
    form.description.trim()
  )
}

async function save() {
  if (!validate()) {
    toast.add({ severity: 'warn', summary: '请填写完整信息', life: 3000 })
    return
  }
  const payload = { ...form }
  try {
    if (props.mode === 'create') {
      const created = await store.create(payload)
      toast.add({ severity: 'success', summary: '创建成功', life: 3000 })
      router.push({ name: 'postmark-detail', params: { id: created.id } })
    } else {
      await store.update(props.id, payload)
      toast.add({ severity: 'success', summary: '保存成功', life: 3000 })
      router.push({ name: 'postmark-detail', params: { id: props.id } })
    }
  } catch {
    toast.add({ severity: 'error', summary: '保存失败', detail: store.error, life: 4000 })
  }
}

function startEdit() {
  router.push({ name: 'postmark-edit', params: { id: props.id } })
}

function goBack() {
  router.push({ name: 'postmark-list' })
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
          <label class="text-sm font-medium text-slate-700">名称 <span v-if="editing" class="text-red-500">*</span></label>
          <InputText
            v-if="editing"
            v-model="form.name"
            :invalid="submitted && !form.name.trim()"
            placeholder="例如：圆形日戳"
          />
          <p v-else class="text-slate-900">{{ form.name }}</p>
        </div>

        <div class="flex flex-col gap-2">
          <label class="text-sm font-medium text-slate-700">形状 <span v-if="editing" class="text-red-500">*</span></label>
          <Select
            v-if="editing"
            v-model="form.shape"
            :options="shapeOptions"
            placeholder="选择形状"
          />
          <Tag v-else :value="form.shape" :severity="shapeSeverity[form.shape] || 'secondary'" />
        </div>

        <div class="flex flex-col gap-2 md:col-span-2">
          <label class="text-sm font-medium text-slate-700">常见用途 <span v-if="editing" class="text-red-500">*</span></label>
          <InputText
            v-if="editing"
            v-model="form.common_use"
            :invalid="submitted && !form.common_use.trim()"
            placeholder="例如：日常信件盖销"
          />
          <p v-else class="text-slate-900">{{ form.common_use }}</p>
        </div>

        <div class="flex flex-col gap-2 md:col-span-2">
          <label class="text-sm font-medium text-slate-700">简介 <span v-if="editing" class="text-red-500">*</span></label>
          <Textarea
            v-if="editing"
            v-model="form.description"
            :invalid="submitted && !form.description.trim()"
            rows="5"
            placeholder="邮戳的详细介绍说明"
          />
          <p v-else class="text-slate-900 whitespace-pre-wrap">{{ form.description }}</p>
        </div>
      </div>
    </div>
  </div>
</template>
