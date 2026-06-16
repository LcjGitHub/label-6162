import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export default api

export async function fetchStats() {
  const { data } = await api.get('/envelopes/stats')
  return data
}
