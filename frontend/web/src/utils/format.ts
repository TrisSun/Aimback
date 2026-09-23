export function formatDateTime(value?: string | null): string {
  if (!value) return '—'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

export function toIsoFromLocal(value: string): string {
  if (!value) return ''
  return new Date(value).toISOString()
}

export function displayTitle(title: string | null | undefined, fallback: string): string {
  const text = (title || '').trim()
  return text || fallback
}
