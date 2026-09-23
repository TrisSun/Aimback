import type { PostImage } from '@/api/types'

export function visibleImages(images: PostImage[]): PostImage[] {
  return images.filter((image) => image.review_status !== 'rejected')
}

export function coverUrl(images: PostImage[]): string {
  const approved = images.find((image) => image.review_status === 'approved' && image.url)
  if (approved?.url) return approved.url
  const pending = images.find((image) => image.review_status === 'pending' && image.url)
  return pending?.url || ''
}
