import { createApp } from 'vue'
import App from './App.vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

// 引入页面
import Home from './components/Home.vue'
import Detail from './components/Detail.vue'
import SearchResult from './components/SearchResult.vue'
import Login from './components/Login.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'Home', component: Home },
    { path: '/detail/:id', name: 'Detail', component: Detail },
    { path: '/search', name: 'SearchResult', component: SearchResult },
    { path: '/login', name: 'Login', component: Login }
  ]
})

const app = createApp(App)

app.use(ElementPlus)
app.use(router)

app.mount('#app')