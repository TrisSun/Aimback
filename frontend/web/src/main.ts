import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入你的页面
import Home from './components/Home.vue'
import Detail from './components/Detail.vue'

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Home', component: Home },
    { path: '/detail/:id', name: 'Detail', component: Detail } // 详情页路径，:id 是动态参数
  ]
})

const app = createApp(App)

app.use(ElementPlus)
app.use(router) // 使用路由

app.mount('#app')