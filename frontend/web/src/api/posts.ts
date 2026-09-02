import request from '@/utils/request'

// 帖子图片（契约 3.1）
export interface PostImage {
  id: number
  sort_order: number
  review_status: string
  url: string
}

// AI 结构化属性（契约 3.2）
export interface PostAttribute {
  brand: string | null
  primary_color: string | null
  text_mark: string | null
  distinctive_features: string | null
  normalized_description: string | null
}

// 帖子公开字段（契约 3.1）
export interface Post {
  id: number
  type: string
  status: string
  category_l1: string
  category_l2: string
  category_l1_label: string
  category_l2_label: string
  title: string | null
  description: string
  found_region: { code: string; name: string } | null
  found_place: { id: number; name: string; place_type: string } | null
  custody_type: string
  event_start_at: string | null
  event_end_at: string | null
  published_at: string | null
  created_at: string
  updated_at: string
  images: PostImage[]
  attribute: PostAttribute | null
}

// 列表查询参数（契约 3.3）
export interface GetPostsParams {
  type?: string
  category_l1?: string
  category_l2?: string
  region_code?: string
  place_id?: number
  event_start?: string
  event_end?: string
  q?: string
  page?: number
  page_size?: number
}

// 列表查询响应（契约 3.3）
export interface PaginatedPosts {
  count: number
  page: number
  page_size: number
  results: Post[]
}

// 创建帖子请求体（契约 3.5）
export interface CreatePostData {
  type: string
  category_l1: string
  category_l2: string
  title?: string | null
  description: string
  found_region_code: string
  found_place_id?: number | null
  found_location_lat?: number | null
  found_location_lng?: number | null
  custody_type: string
  custody_place_id?: number | null
  custody_address?: string
  event_start_at: string
  event_end_at: string
  images?: { cos_key: string; sort_order: number }[]
}

// 3.3 列表查询：GET /posts
export function getPosts(params: GetPostsParams = {}) {
  return request.get<PaginatedPosts, PaginatedPosts>('/posts', { params })
}

// 3.4 详情查询：GET /posts/{id}
export function getPostDetail(id: number | string) {
  return request.get<Post, Post>(`/posts/${id}`)
}

// 3.5 创建帖子：POST /posts
export function createPost(data: CreatePostData) {
  return request.post<Post, Post>('/posts', data)
}
