import request from '@/utils/request'

// ===== 账号 / 鉴权接口（Base URL: /api/v1，见后端 apps/accounts/views.py） =====

// 发送验证码响应
export interface SendCodeResult {
  msg: string
  dev_code?: string // 开发模式（console 通道）下返回，便于联调
}

// 验证码登录响应
export interface LoginResult {
  token: string
  user: {
    id: number
    phone: string
    is_new: boolean
  }
}

// 当前用户信息
export interface UserProfile {
  id: number
  username: string // 手机号
  nickname?: string
  avatar?: string
  contact?: string
}

// 更新个人信息的请求体
export interface UpdateProfileData {
  nickname?: string
  avatar?: string
  contact?: string
}

// POST /auth/send-code/ 发送短信验证码
export function sendCode(phone: string) {
  return request.post<SendCodeResult, SendCodeResult>('/auth/send-code/', { phone })
}

// POST /auth/login-code/ 验证码登录（新手机号自动注册），成功后把 token 存入 localStorage
export async function loginByCode(phone: string, code: string) {
  const res = await request.post<LoginResult, LoginResult>('/auth/login-code/', { phone, code })
  localStorage.setItem('token', res.token)
  return res
}

// GET /auth/me/ 获取当前登录用户信息
export function getProfile() {
  return request.get<UserProfile, UserProfile>('/auth/me/')
}

// PATCH /users/me/ 更新个人信息
// 注意：后端目前只有 GET /auth/me/，PATCH 更新接口尚未实现，
// 这里按契约约定封装为 PATCH /users/me/，联调前需与后端确认路径与字段。
export function updateProfile(data: UpdateProfileData) {
  return request.patch<UserProfile, UserProfile>('/users/me/', data)
}
