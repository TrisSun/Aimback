import { http } from './http'
import type {
  AuthUser,
  Claim,
  ClaimQuestion,
  MatchHit,
  PageResult,
  Place,
  Post,
  Region,
  UploadTicket,
} from './types'

export function sendCode(phone: string) {
  return http.post<{ msg: string; dev_code?: string }>('/auth/send-code/', { phone })
}

export function loginCode(phone: string, code: string) {
  return http.post<{ token: string; user: AuthUser }>('/auth/login-code/', {
    phone,
    code,
  })
}

export function fetchMe() {
  return http.get<{ id: number; username: string }>('/auth/me/')
}

export function fetchPosts(params: Record<string, string | number | undefined>) {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== '') query.set(key, String(value))
  }
  const suffix = query.toString()
  return http.get<PageResult<Post>>(`/posts${suffix ? `?${suffix}` : ''}`)
}

export function fetchPost(id: number) {
  return http.get<Post>(`/posts/${id}`)
}

export function createPost(payload: Record<string, unknown>) {
  return http.post<Post>('/posts', payload)
}

export function publishPost(id: number) {
  return http.post<Post>(`/posts/${id}/publish`)
}

export function closePost(id: number) {
  return http.post<Post>(`/posts/${id}/close`)
}

export function deletePost(id: number) {
  return http.delete(`/posts/${id}`)
}

export function fetchMyPosts(page = 1) {
  return http.get<PageResult<Post>>(`/my-posts?page=${page}&page_size=20`)
}

export function fetchRegions() {
  return http.get<Region[]>('/regions')
}

export function fetchPlaces(regionCode?: string) {
  const suffix = regionCode ? `?region_code=${encodeURIComponent(regionCode)}` : ''
  return http.get<Place[]>(`/places${suffix}`)
}

export function presignUpload(count: number, contentType: string) {
  return http.post<{ count: number; tickets: UploadTicket[]; expires_in: number }>(
    '/upload/presign/',
    { count, content_type: contentType },
  )
}

export async function uploadToCos(ticket: UploadTicket, file: File) {
  const response = await fetch(ticket.upload_url, {
    method: ticket.method || 'PUT',
    headers: ticket.headers,
    body: file,
  })
  if (!response.ok) {
    throw new Error('图片上传到对象存储失败')
  }
}

export function fetchClaimQuestions(postId: number) {
  return http.get<ClaimQuestion[]>(`/posts/${postId}/claim-questions`)
}

export function saveClaimQuestions(postId: number, questions: string[]) {
  return http.put<ClaimQuestion[]>(`/posts/${postId}/claim-questions`, {
    questions: questions.map((question) => ({ question })),
  })
}

export function createClaim(postId: number, answers: { question_id: number; answer: string }[]) {
  return http.post<Claim>(`/posts/${postId}/claim`, { answers })
}

export function fetchPostClaims(postId: number) {
  return http.get<Claim[]>(`/posts/${postId}/claims`)
}

export function fetchMyClaims() {
  return http.get<Claim[]>('/my-claims')
}

export function fetchClaim(id: number) {
  return http.get<Claim>(`/claims/${id}`)
}

export function approveClaim(id: number) {
  return http.post<Claim>(`/claims/${id}/approve`)
}

export function rejectClaim(id: number) {
  return http.post<Claim>(`/claims/${id}/reject`)
}

export function cancelClaim(id: number) {
  return http.post<Claim>(`/claims/${id}/cancel`)
}

export function confirmHandover(id: number) {
  return http.post<Claim>(`/claims/${id}/confirm-handover`)
}

export function searchMatches(payload: Record<string, unknown>) {
  return http.post<PageResult<MatchHit>>('/matches/search', payload)
}

export function markMatchFeedback(matchId: number, label: 'not_match' | 'reset') {
  return http.post<{ match_id: number; feedback: string }>(
    `/matches/${matchId}/feedback`,
    { label },
  )
}

export function fetchSavedMatches(postId: number) {
  return http.get<PageResult<MatchHit>>(`/posts/${postId}/matches`)
}
