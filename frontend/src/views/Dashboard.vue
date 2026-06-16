<script setup>
import { computed, onMounted, ref } from 'vue'
import Card from 'primevue/card'
import ProgressSpinner from 'primevue/progressspinner'
import { fetchStats } from '@/api/envelope'

const CONDITION_ORDER = ['优秀', '良好', '一般']
const ERA_ORDER = ['清末及以前', '民国时期', '建国初期', '改革开放', '新世纪']

const loading = ref(true)
const error = ref(null)
const stats = ref({ total: 0, by_condition: {}, by_era: {} })

const conditionList = computed(() =>
  CONDITION_ORDER.map((cond) => ({
    label: cond,
    count: stats.value.by_condition?.[cond] ?? 0,
  }))
)

const eraList = computed(() =>
  ERA_ORDER.map((era, idx) => ({
    label: era,
    count: stats.value.by_era?.[era] ?? 0,
    index: idx,
  }))
)

const conditionColors = {
  '优秀': 'bg-emerald-50 text-emerald-700 border-emerald-200',
  '良好': 'bg-blue-50 text-blue-700 border-blue-200',
  '一般': 'bg-amber-50 text-amber-700 border-amber-200',
}

const defaultConditionColor = 'bg-slate-50 text-slate-700 border-slate-200'

const eraColor = (index) => {
  const palette = [
    'bg-violet-50 text-violet-700 border-violet-200',
    'bg-sky-50 text-sky-700 border-sky-200',
    'bg-teal-50 text-teal-700 border-teal-200',
    'bg-orange-50 text-orange-700 border-orange-200',
    'bg-rose-50 text-rose-700 border-rose-200',
  ]
  return palette[index % palette.length]
}

onMounted(async () => {
  try {
    stats.value = await fetchStats()
  } catch (err) {
    error.value = err.response?.data?.error || '加载统计数据失败'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-lg font-semibold text-slate-900">收藏数据统计看板</h2>
      <p class="text-sm text-slate-500">信封收藏汇总概览</p>
    </div>

    <div v-if="loading" class="flex justify-center py-16">
      <ProgressSpinner />
    </div>

    <div v-else-if="error" class="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
      {{ error }}
    </div>

    <template v-else>
      <Card>
        <template #title>总收藏数</template>
        <template #content>
          <div class="text-center">
            <span class="text-5xl font-bold text-amber-700">{{ stats.total }}</span>
            <p class="mt-2 text-sm text-slate-500">条记录</p>
          </div>
        </template>
      </Card>

      <div class="grid gap-6 sm:grid-cols-2">
        <Card>
          <template #title>按品相分组</template>
          <template #content>
            <div v-if="conditionList.length === 0" class="text-center text-sm text-slate-400">暂无数据</div>
            <div v-else class="space-y-3">
              <div
                v-for="item in conditionList"
                :key="item.label"
                class="flex items-center justify-between rounded-lg border px-4 py-3"
                :class="conditionColors[item.label] || defaultConditionColor"
              >
                <span class="text-sm font-medium">{{ item.label }}</span>
                <span class="text-lg font-bold">{{ item.count }}</span>
              </div>
            </div>
          </template>
        </Card>

        <Card>
          <template #title>按年代区间分组</template>
          <template #content>
            <div v-if="eraList.length === 0" class="text-center text-sm text-slate-400">暂无数据</div>
            <div v-else class="space-y-3">
              <div
                v-for="item in eraList"
                :key="item.label"
                class="flex items-center justify-between rounded-lg border px-4 py-3"
                :class="eraColor(item.index)"
              >
                <span class="text-sm font-medium">{{ item.label }}</span>
                <span class="text-lg font-bold">{{ item.count }}</span>
              </div>
            </div>
          </template>
        </Card>
      </div>
    </template>
  </div>
</template>
