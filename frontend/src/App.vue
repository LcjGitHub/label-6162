<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="min-h-screen">
    <header class="border-b border-slate-200 bg-white shadow-sm">
      <div class="mx-auto flex max-w-6xl items-center gap-3 px-4 py-4">
        <i class="pi pi-envelope text-2xl text-amber-700" />
        <div>
          <h1 class="text-xl font-semibold text-slate-900">手写信封邮票组合收藏</h1>
          <p class="text-sm text-slate-500">记录寄出地、目的地与邮票邮戳信息</p>
        </div>
      </div>
    </header>
    <main class="mx-auto max-w-6xl px-4 py-6">
      <RouterView />
    </main>
  </div>
</template>
