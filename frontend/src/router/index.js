import { createRouter, createWebHistory } from 'vue-router'
import EnvelopeList from '@/views/EnvelopeList.vue'
import EnvelopeDetail from '@/views/EnvelopeDetail.vue'
import PostmarkList from '@/views/PostmarkList.vue'
import PostmarkDetail from '@/views/PostmarkDetail.vue'
import Dashboard from '@/views/Dashboard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'list', component: EnvelopeList },
    { path: '/dashboard', name: 'dashboard', component: Dashboard },
    { path: '/envelopes/new', name: 'create', component: EnvelopeDetail, props: { mode: 'create' } },
    { path: '/envelopes/:id', name: 'detail', component: EnvelopeDetail, props: (route) => ({ id: Number(route.params.id), mode: 'view' }) },
    { path: '/envelopes/:id/edit', name: 'edit', component: EnvelopeDetail, props: (route) => ({ id: Number(route.params.id), mode: 'edit' }) },
    { path: '/postmarks', name: 'postmark-list', component: PostmarkList },
    { path: '/postmarks/new', name: 'postmark-create', component: PostmarkDetail, props: { mode: 'create' } },
    { path: '/postmarks/:id', name: 'postmark-detail', component: PostmarkDetail, props: (route) => ({ id: Number(route.params.id), mode: 'view' }) },
    { path: '/postmarks/:id/edit', name: 'postmark-edit', component: PostmarkDetail, props: (route) => ({ id: Number(route.params.id), mode: 'edit' }) },
  ],
})

export default router
