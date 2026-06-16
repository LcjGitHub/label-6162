import { defineStore } from 'pinia'
import { fetchTags, fetchTag, createTag, updateTag, deleteTag, updateEnvelopeTags } from '@/api/tag'

/**
 * @typedef {Object} Tag
 * @property {number} id
 * @property {string} name - 标签名称
 * @property {string} color - 标签颜色
 */

export const useTagStore = defineStore('tag', {
  state: () => ({
    /** @type {Tag[]} */
    items: [],
    /** @type {Tag | null} */
    current: null,
    loading: false,
    error: null,
  }),

  actions: {
    /**
     * 加载全部标签。
     * @returns {Promise<void>}
     */
    async fetchAll() {
      this.loading = true
      this.error = null
      try {
        const data = await fetchTags()
        this.items = data
      } catch (err) {
        this.error = err.response?.data?.error || '加载标签列表失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 按 ID 加载单条标签。
     * @param {number} id
     * @returns {Promise<Tag>}
     */
    async fetchOne(id) {
      this.loading = true
      this.error = null
      try {
        const data = await fetchTag(id)
        this.current = data
        return data
      } catch (err) {
        this.error = err.response?.data?.error || '加载标签详情失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 新建标签。
     * @param {{name: string, color?: string}} payload
     * @returns {Promise<Tag>}
     */
    async create(payload) {
      this.loading = true
      this.error = null
      try {
        const data = await createTag(payload)
        this.items.push(data)
        return data
      } catch (err) {
        this.error = err.response?.data?.error || '创建标签失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 更新标签。
     * @param {number} id
     * @param {{name: string, color?: string}} payload
     * @returns {Promise<Tag>}
     */
    async update(id, payload) {
      this.loading = true
      this.error = null
      try {
        const data = await updateTag(id, payload)
        const idx = this.items.findIndex((t) => t.id === id)
        if (idx !== -1) this.items[idx] = data
        if (this.current?.id === id) this.current = data
        return data
      } catch (err) {
        this.error = err.response?.data?.error || '更新标签失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 删除标签。
     * @param {number} id
     * @returns {Promise<void>}
     */
    async remove(id) {
      this.loading = true
      this.error = null
      try {
        await deleteTag(id)
        this.items = this.items.filter((t) => t.id !== id)
        if (this.current?.id === id) this.current = null
      } catch (err) {
        this.error = err.response?.data?.error || '删除标签失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 更新信封的标签。
     * @param {number} envelopeId
     * @param {number[]} tagIds
     * @returns {Promise<Tag[]>}
     */
    async updateEnvelopeTags(envelopeId, tagIds) {
      this.loading = true
      this.error = null
      try {
        const data = await updateEnvelopeTags(envelopeId, tagIds)
        return data
      } catch (err) {
        this.error = err.response?.data?.error || '更新信封标签失败'
        throw err
      } finally {
        this.loading = false
      }
    },
  },
})
