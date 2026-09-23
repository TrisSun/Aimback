<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { isLoggedIn, user, restore, logout } = useAuth()

onMounted(() => {
  void restore()
})

function goLogin() {
  void router.push({ name: 'login', query: { redirect: route.fullPath } })
}

function handleLogout() {
  logout()
  void router.push({ name: 'home' })
}
</script>

<template>
  <div class="shell">
    <header class="nav">
      <RouterLink class="brand" to="/">Aimback</RouterLink>
      <nav class="links">
        <RouterLink to="/">信息流</RouterLink>
        <RouterLink to="/search">AI 搜寻</RouterLink>
        <RouterLink to="/publish">发布</RouterLink>
        <RouterLink to="/mine">我的</RouterLink>
      </nav>
      <div class="account">
        <template v-if="isLoggedIn">
          <span class="phone">{{ user?.phone || user?.username }}</span>
          <button type="button" class="text-btn" @click="handleLogout">退出</button>
        </template>
        <button v-else type="button" class="primary-btn" @click="goLogin">登录</button>
      </div>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.shell {
  min-height: 100vh;
  background: #f4f5f7;
}
.nav {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  gap: 24px;
  height: 64px;
  padding: 0 24px;
  background: #fff;
  border-bottom: 1px solid #eee;
}
.brand {
  font-size: 20px;
  font-weight: 700;
  color: #ff6b35;
  text-decoration: none;
}
.links {
  display: flex;
  gap: 18px;
  flex: 1;
}
.links a {
  color: #555;
  text-decoration: none;
  font-size: 14px;
}
.links a.router-link-exact-active {
  color: #ff6b35;
  font-weight: 600;
}
.account {
  display: flex;
  align-items: center;
  gap: 12px;
}
.phone {
  font-size: 13px;
  color: #666;
}
.text-btn,
.primary-btn {
  border: 0;
  cursor: pointer;
  border-radius: 8px;
}
.text-btn {
  background: transparent;
  color: #888;
}
.primary-btn {
  background: #ff6b35;
  color: #fff;
  padding: 8px 14px;
}
.main {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 16px 48px;
}
</style>
