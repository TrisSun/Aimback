export interface Region {
  code: string
  name: string
}

export interface Place {
  id: number
  name: string
  place_type: string
}

export interface PostImage {
  id: number
  sort_order: number
  review_status: string
  url: string | null
}

export interface PostAttribute {
  brand: string
  primary_color: string
  text_mark: string
  distinctive_features: string
  normalized_description: string
}

export interface Post {
  id: number
  type: 'lost' | 'found'
  status: string
  category_l1: string
  category_l2: string
  category_l1_label: string
  category_l2_label: string
  title: string | null
  description: string
  found_region: Region | null
  found_place: Place | null
  custody_type: string
  event_start_at: string
  event_end_at: string
  published_at: string | null
  created_at: string
  updated_at: string
  images: PostImage[]
  attribute: PostAttribute | null
}

export interface PageResult<T> {
  count: number
  page: number
  page_size: number
  results: T[]
}

export interface AuthUser {
  id: number
  phone?: string
  username?: string
  is_new?: boolean
}

export interface ClaimAnswer {
  question_id: number
  question: string
  answer: string
}

export interface Claim {
  id: number
  post: number
  claimant: number
  status: string
  answers: ClaimAnswer[]
  author_confirmed: boolean
  claimant_confirmed: boolean
  created_at: string
  approved_at: string | null
  completed_at: string | null
  contact?: {
    post_author_phone: string
    claimant_phone: string
    custody_place: Place | null
    custody_address: string | null
  } | null
}

export interface ClaimQuestion {
  id: number
  question: string
  sort_order: number
}

export interface MatchHit {
  match_id: number | null
  score: number
  vector_score: number
  reason: string
  feedback: string
  post: Post
}

export interface UploadTicket {
  cos_key: string
  upload_url: string
  method: string
  headers: Record<string, string>
}
