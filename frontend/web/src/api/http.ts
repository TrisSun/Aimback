const TOKEN_KEY = 'aimback_token'

let onUnauthorized: (() => void) | null = null

export function setUnauthorizedHandler(handler: (() => void) | null): void {
  onUnauthorized = handler
}

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) || ''
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export class ApiError extends Error {
  status: number
  body: unknown

  constructor(status: number, body: unknown) {
    super(extractDetail(body) || `请求失败（${status}）`)
    this.status = status
    this.body = body
  }
}

function extractDetail(body: unknown): string {
  if (!body || typeof body !== 'object') return ''
  const data = body as Record<string, unknown>
  if (typeof data.detail === 'string') return data.detail
  const first = Object.values(data)[0]
  if (Array.isArray(first) && typeof first[0] === 'string') return first[0]
  if (typeof first === 'string') return first
  return ''
}

const API_BASE = (import.meta.env.VITE_API_BASE || '/api/v1').replace(/\/$/, '')

async function parseBody(response: Response): Promise<unknown> {
  const text = await response.text()
  if (!text) return null
  try {
    return JSON.parse(text)
  } catch {
    return text
  }
}

export async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers)
  if (!headers.has('Content-Type') && init.body) {
    headers.set('Content-Type', 'application/json')
  }
  const token = getToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)

  const response = await fetch(`${API_BASE}${path}`, { ...init, headers })
  const body = await parseBody(response)
  if (response.status === 401) {
    clearToken()
    onUnauthorized?.()
  }
  if (!response.ok) {
    throw new ApiError(response.status, body)
  }
  return body as T
}

export const http = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'POST',
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'PUT',
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: 'PATCH',
      body: body === undefined ? undefined : JSON.stringify(body),
    }),
  delete: (path: string) => request<unknown>(path, { method: 'DELETE' }),
}
