import { defineStore } from 'pinia'
import api, { fetchStats, importEnvelopes } from '@/api/envelope'

/**
 * @typedef {Object} Envelope
 * @property {number} id
 * @property {string} origin - 寄出地
 * @property {string} destination - 目的地
 * @property {number} year - 年份
 * @property {string} stamp_description - 邮票描述
 * @property {string} postmark_type - 邮戳类型
 * @property {string} condition - 品相
 * @property {string} remark - 备注
 */

/**
 * @typedef {Object} StatsData
 * @property {number} total - 总收藏数
 * @property {Record<string, number>} by_condition - 按品相分组数量
 * @property {Record<string, number>} by_era - 按年代区间分组数量
 */

export const useEnvelopeStore = defineStore('envelope', {
  state: () => ({
    /** @type {Envelope[]} */
    items: [],
    /** @type {Envelope | null} */
    current: null,
    /** @type {StatsData} */
    stats: { total: 0, by_condition: {}, by_era: {} },
    loading: false,
    statsLoading: false,
    error: null,
    statsError: null,
  }),

  actions: {
    /**
     * 加载统计数据。
     * @returns {Promise<void>}
     */
    async fetchStats() {
      this.statsLoading = true
      this.statsError = null
      try {
        this.stats = await fetchStats()
      } catch (err) {
        this.statsError = err.response?.data?.error || '加载统计数据失败'
        throw err
      } finally {
        this.statsLoading = false
      }
    },

    /**
     * 加载全部信封列表，同时并行加载统计数据。
     * @returns {Promise<void>}
     */
    async fetchAll() {
      this.loading = true
      this.statsLoading = true
      this.error = null
      this.statsError = null
      try {
        const [listRes] = await Promise.all([
          api.get('/envelopes'),
          this.fetchStats().catch(() => {}),
        ])
        this.items = listRes.data
      } catch (err) {
        this.error = err.response?.data?.error || '加载列表失败'
        throw err
      } finally {
        this.loading = false
        this.statsLoading = false
      }
    },

    /**
     * 按 ID 加载单条记录。
     * @param {number} id
     * @returns {Promise<Envelope>}
     */
    async fetchOne(id) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.get(`/envelopes/${id}`)
        this.current = data
        return data
      } catch (err) {
        this.error = err.response?.data?.error || '加载详情失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 新建信封。
     * @param {Omit<Envelope, 'id'> & {tag_ids?: number[]}} payload
     * @returns {Promise<Envelope>}
     */
    async create(payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.post('/envelopes', payload)
        this.items.unshift(data)
        this.fetchStats().catch(() => {})
        return data
      } catch (err) {
        this.error = err.response?.data?.error || '创建失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 更新信封。
     * @param {number} id
     * @param {Omit<Envelope, 'id'> & {tag_ids?: number[]}} payload
     * @returns {Promise<Envelope>}
     */
    async update(id, payload) {
      this.loading = true
      this.error = null
      try {
        const { data } = await api.put(`/envelopes/${id}`, payload)
        const idx = this.items.findIndex((e) => e.id === id)
        if (idx !== -1) this.items[idx] = data
        this.current = data
        this.fetchStats().catch(() => {})
        return data
      } catch (err) {
        this.error = err.response?.data?.error || '更新失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 删除信封。
     * @param {number} id
     * @returns {Promise<void>}
     */
    async remove(id) {
      this.loading = true
      this.error = null
      try {
        await api.delete(`/envelopes/${id}`)
        this.items = this.items.filter((e) => e.id !== id)
        if (this.current?.id === id) this.current = null
        this.fetchStats().catch(() => {})
      } catch (err) {
        this.error = err.response?.data?.error || '删除失败'
        throw err
      } finally {
        this.loading = false
      }
    },

    /**
     * 批量导入信封。
     * @param {File} file
     * @returns {Promise<{success: number, failed_count: number, failed_lines: string[], processed: number}>}
     */
    async batchImport(file) {
      this.loading = true
      this.error = null
      try {
        const result = await importEnvelopes(file)
        await this.fetchAll()
        return result
      } catch (err) {
        this.error = err.response?.data?.error || '导入失败'
        throw err
      } finally {
        this.loading = false
      }
    },
  },
})
