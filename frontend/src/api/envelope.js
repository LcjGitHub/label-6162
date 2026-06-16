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

/**
 * 批量导入信封收藏（CSV 文件上传）。
 * @param {File} file - CSV 文件对象
 * @returns {Promise<{success: number, failed_count: number, failed_lines: string[], processed: number}>}
 */
export async function importEnvelopes(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await api.post('/envelopes/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
