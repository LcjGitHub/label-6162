import axios from 'axios'

/**
 * 共享 axios 实例，开发环境经 Vite 代理访问后端。
 */
const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

export default api
