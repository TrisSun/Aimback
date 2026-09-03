import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { ElMessage } from 'element-plus'

// 统一封装的 axios 实例，所有接口共用
const request = axios.create({
  baseURL: 'http://118.25.145.183/api/v1/',
  timeout: 10000,
})

// 请求拦截器：从 localStorage 读取 token，并自动携带 Authorization: Bearer <token>
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// 响应拦截器：统一处理 401 / 400 / 403 / 409 等错误
request.interceptors.response.use(
  (response) => response.data,
  (error: AxiosError) => {
    const status = error.response?.status

    if (status === 401) {
      // 登录态失效：清除 token 并强制跳转登录页
      localStorage.removeItem('token')
      ElMessage.error('登录已过期，请重新登录')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else if (status === 400 || status === 403 || status === 404 || status === 409 || status === 429 || status === 502) {
      ElMessage.error(extractErrorMessage(error))
    }

    return Promise.reject(error)
  },
)

// 从后端错误响应中提取可读信息（契约第 4 节）
function extractErrorMessage(error: AxiosError): string {
  const data = error.response?.data
  if (!data) {
    return error.message || '请求失败'
  }
  if (typeof data === 'string') {
    return data
  }
  if (typeof data === 'object') {
    const obj = data as Record<string, unknown>
    // 统一错误返回：{ "detail": "可读错误信息" }
    if (typeof obj.detail === 'string') {
      return obj.detail
    }
    // 字段校验错误返回：{ "field_name": ["错误信息"] }
    const messages: string[] = []
    for (const value of Object.values(obj)) {
      if (typeof value === 'string') {
        messages.push(value)
      } else if (Array.isArray(value)) {
        for (const v of value) {
          if (typeof v === 'string') messages.push(v)
        }
      }
    }
    if (messages.length) {
      return messages.join('；')
    }
  }
  return error.message || '请求失败'
}

export default request
