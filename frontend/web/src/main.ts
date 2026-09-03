import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入页面
import Preview from './components/Preview.vue'
import Login from './components/Login.vue'
import Profile from './components/Profile.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Preview', component: Preview },
    { path: '/login', name: 'Login', component: Login },
    { path: '/profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } },
    // 其它旧链接统一回退到首页
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ]
})

// 路由守卫：需要登录的页面（如个人中心），未登录时跳转到 /login
router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  if ((to.meta.requiresAuth as boolean) && !token) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }
  return true
})

const app = createApp(App)

app.use(ElementPlus)
app.use(router)

app.mount('#app')