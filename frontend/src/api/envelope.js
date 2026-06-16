import axios from 'axios'

/**
 * 信封收藏模块共享 Axios 实例。
 * 基地址指向 `/api`，默认请求头为 JSON 格式。
 */
const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export default api

/**
 * 获取信封收藏统计数据。
 * @returns {Promise<{total: number, by_condition: Record<string, number>, by_era: Record<string, number>}>}
 *   总收藏数、按品相分组数量、按年代区间分组数量
 */
export async function fetchStats() {
  const { data } = await api.get('/envelopes/stats')
  return data
}
