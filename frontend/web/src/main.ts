import { createApp } from 'vue'
import App from './App.vue'

// 这两行是关键的引入！必须要写！
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css' // 注意：这行末尾有 ; 或者没 ; 都可以

const app = createApp(App)

app.use(ElementPlus)

app.mount('#app')