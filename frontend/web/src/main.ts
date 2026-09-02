import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入页面：Preview 作为唯一主页面
import Preview from './components/Preview.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Preview', component: Preview },
    // 旧页面（Home / Detail / SearchResult / Login）已停用，旧链接统一回退到首页
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ]
})

const app = createApp(App)

app.use(ElementPlus)
app.use(router)

app.mount('#app')