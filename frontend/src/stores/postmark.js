import { defineStore } from 'pinia'
import api from '@/api/postmark'

export const usePostmarkStore = defineStore('postmark', {
  state: () => ({
    items: [],
    current: null,
    loading: false,
    error: null,
  }),

  actions: {
    async fetchAll() {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.get('/postmarks')
        this.items = data
      } catch (err) {
        this.error = err.response?.data?.error || '加载列表失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchOne(id) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.get(`/postmarks/${id}`)
        this.current = data
        return data
      } catch (err) {
        this.error = err.response?.data?.error || '加载详情失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    async create(payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/postmarks', payload)
        this.items.push(data)
        return data
      } catch (err) {
        this.error = err.response?.data?.error || '创建失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    async update(id, payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.put(`/postmarks/${id}`, payload)
        const idx = this.items.findIndex((e) => e.id === id)
        if (idx !== -1) this.items[idx] = data
        this.current = data
        return data
      } catch (err) {
        this.error = err.response?.data?.error || '更新失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    async remove(id) {
      this.loading = true
      this.error = null
      try {
        await api.delete(`/postmarks/${id}`)
        this.items = this.items.filter((e) => e.id !== id)
        if (this.current?.id === id) this.current = null
      } catch (err) {
        this.error = err.response?.data?.error || '删除失败'
        throw err
      } finally {
        this.loading = false
      }
    },
  },
})
