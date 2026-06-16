import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export default api

/**
 * 获取全部标签。
 * @returns {Promise<Array<{id: number, name: string, color: string}>>}
 */
export async function fetchTags() {
  const { data } = await api.get('/tags')
  return data
}

/**
 * 获取单条标签详情。
 * @param {number} id
 * @returns {Promise<{id: number, name: string, color: string}>}
 */
export async function fetchTag(id) {
  const { data } = await api.get(`/tags/${id}`)
  return data
}

/**
 * 新建标签。
 * @param {{name: string, color?: string}} payload
 * @returns {Promise<{id: number, name: string, color: string}>}
 */
export async function createTag(payload) {
  const { data } = await api.post('/tags', payload)
  return data
}

/**
 * 更新标签。
 * @param {number} id
 * @param {{name: string, color?: string}} payload
 * @returns {Promise<{id: number, name: string, color: string}>}
 */
export async function updateTag(id, payload) {
  const { data } = await api.put(`/tags/${id}`, payload)
  return data
}

/**
 * 删除标签。
 * @param {number} id
 * @returns {Promise<{message: string}>}
 */
export async function deleteTag(id) {
  const { data } = await api.delete(`/tags/${id}`)
  return data
}

/**
 * 获取指定信封的所有标签。
 * @param {number} envelopeId
 * @returns {Promise<Array<{id: number, name: string, color: string}>>}
 */
export async function fetchEnvelopeTags(envelopeId) {
  const { data } = await api.get(`/envelopes/${envelopeId}/tags`)
  return data
}

/**
 * 更新信封的标签（全量替换）。
 * @param {number} envelopeId
 * @param {number[]} tagIds
 * @returns {Promise<Array<{id: number, name: string, color: string}>>}
 */
export async function updateEnvelopeTags(envelopeId, tagIds) {
  const { data } = await api.put(`/envelopes/${envelopeId}/tags`, { tag_ids: tagIds })
  return data
}
