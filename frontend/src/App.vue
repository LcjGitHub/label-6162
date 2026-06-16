<script setup>
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'

const route = useRoute()

const activeTab = computed(() => {
  if (route.name === 'dashboard') return 'dashboard'
  if (route.name?.startsWith('postmark')) return 'postmark'
  return 'envelope'
})
</script>

<template>
  <div class="min-h-screen">
    <header class="border-b border-slate-200 bg-white shadow-sm">
      <div class="mx-auto max-w-6xl px-4 py-4">
        <div class="flex flex-wrap items-center gap-3">
          <i class="pi pi-envelope text-2xl text-amber-700" />
          <div>
            <h1 class="text-xl font-semibold text-slate-900">手写信封邮票组合收藏</h1>
            <p class="text-sm text-slate-500">信封收藏与邮戳图鉴管理</p>
          </div>
        </div>
        <nav class="mt-4 flex gap-1 border-b border-slate-200">
          <router-link
            :to="{ name: 'dashboard' }"
            class="px-4 py-2 text-sm font-medium transition-colors"
            :class="activeTab === 'dashboard' ? 'border-b-2 border-amber-600 text-amber-700 -mb-px' : 'text-slate-500 hover:text-slate-700'"
          >
            <i class="pi pi-chart-bar mr-2" />
            数据看板
          </router-link>
          <router-link
            :to="{ name: 'list' }"
            class="px-4 py-2 text-sm font-medium transition-colors"
            :class="activeTab === 'envelope' ? 'border-b-2 border-amber-600 text-amber-700 -mb-px' : 'text-slate-500 hover:text-slate-700'"
          >
            <i class="pi pi-envelope mr-2" />
            信封收藏
          </router-link>
          <router-link
            :to="{ name: 'postmark-list' }"
            class="px-4 py-2 text-sm font-medium transition-colors"
            :class="activeTab === 'postmark' ? 'border-b-2 border-amber-600 text-amber-700 -mb-px' : 'text-slate-500 hover:text-slate-700'"
          >
            <i class="pi pi-bookmark mr-2" />
            邮戳图鉴
          </router-link>
        </nav>
      </div>
    </header>
    <main class="mx-auto max-w-6xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
