import { computed, ref } from 'vue'
import { clearToken, getToken, setToken, setUnauthorizedHandler } from '@/api/http'
import { fetchMe, loginCode, sendCode } from '@/api'
import type { AuthUser } from '@/api/types'

const token = ref(getToken())
const user = ref<AuthUser | null>(null)

setUnauthorizedHandler(() => {
  token.value = ''
  user.value = null
})

export function useAuth() {
  const isLoggedIn = computed(() => Boolean(token.value))

  async function restore() {
    if (!token.value) {
      user.value = null
      return
    }
    try {
      const me = await fetchMe()
      user.value = { id: me.id, username: me.username, phone: me.username }
    } catch {
      token.value = ''
      user.value = null
      clearToken()
    }
  }

  async function requestCode(phone: string) {
    return sendCode(phone)
  }

  async function login(phone: string, code: string) {
    const result = await loginCode(phone, code)
    setToken(result.token)
    token.value = result.token
    user.value = result.user
    return result
  }

  function logout() {
    clearToken()
    token.value = ''
    user.value = null
  }

  return { token, user, isLoggedIn, restore, requestCode, login, logout }
}
