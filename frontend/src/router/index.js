import { createRouter, createWebHistory } from 'vue-router'
import EnvelopeList from '@/views/EnvelopeList.vue'
import EnvelopeDetail from '@/views/EnvelopeDetail.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'list', component: EnvelopeList },
    { path: '/envelopes/new', name: 'create', component: EnvelopeDetail, props: { mode: 'create' } },
    { path: '/envelopes/:id', name: 'detail', component: EnvelopeDetail, props: (route) => ({ id: Number(route.params.id), mode: 'view' }) },
    { path: '/envelopes/:id/edit', name: 'edit', component: EnvelopeDetail, props: (route) => ({ id: Number(route.params.id), mode: 'edit' }) },
  ],
})

export default router
