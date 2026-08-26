 <template>
    <div class="home-container">
      <!-- 顶部搜索栏 (模仿闲鱼) -->
      <div class="search-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索失物 / 招领信息"
          size="large"
          class="search-input"
        >
          <template #append>
            <el-button>搜索</el-button>
          </template>
        </el-input>
      </div>

      <div class="main-content">
        <!-- 左侧分类菜单 -->
        <div class="side-menu">
          <div class="side-title">物品分类</div>
          <div
            v-for="item in categories"
            :key="item"
            class="menu-item"
            :class="{ active: currentCategory === item }"
            @click="currentCategory = item"
          >
            {{ item }}
          </div>
        </div>

        <!-- 右侧失物卡片列表 -->
        <div class="card-list">
          <el-card
            v-for="item in items"
            :key="item.id"
            class="item-card"
            shadow="hover"
            @click="goDetail(item)"
          >
            <div class="image-placeholder"></div>
            <div class="item-info">
              <h3>{{ item.name }}</h3>
              <p class="location">📍 {{ item.location }}</p>
              <p class="time">🕒 {{ item.time }}</p>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'

  // 物品数据类型
  interface LostItem {
    id: number
    name: string
    location: string
    time: string
  }

  const router = useRouter()

  // 搜索框的内容
  const searchText = ref('')

  // 左侧分类列表
  const categories = ['全部', '证件', '钱包', '电子产品', '钥匙', '衣物']
  const currentCategory = ref('全部')

  // 假数据（Mock Data）：目前先随便写，等后端写好了再替换
  const items: LostItem[] = [
    { id: 1, name: '黑色钱包', location: '图书馆三楼', time: '2026-08-20' },
    { id: 2, name: '学生证', location: '食堂一楼', time: '2026-08-19' },
    { id: 3, name: '苹果耳机', location: '操场跑道', time: '2026-08-18' },
    { id: 4, name: '蓝色雨伞', location: '教学楼B座', time: '2026-08-17' }
  ]

  // 点击卡片跳转到详情页
  const goDetail = (item: LostItem) => {
    router.push(`/detail/${item.id}`)
  }
  </script>

  <style scoped>
  .home-container {
    background-color: #f5f5f5;
    min-height: 100vh;
    padding: 20px;
  }

  .search-bar {
    max-width: 600px;
    margin: 0 auto 20px;
  }

  .main-content {
    display: flex;
    max-width: 1200px;
    margin: 0 auto;
    gap: 20px;
  }

  .side-menu {
    width: 180px;
    background: white;
    border-radius: 8px;
    padding: 10px;
  }

  .side-title {
    font-weight: bold;
    margin-bottom: 10px;
    color: #333;
  }

  .menu-item {
    padding: 10px;
    cursor: pointer;
    border-radius: 4px;
  }

  .menu-item:hover, .menu-item.active {
    background-color: #ffd04b;
    color: #333;
    font-weight: bold;
  }

  .card-list {
    flex: 1;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
  }

  .item-card {
    text-align: center;
    cursor: pointer;
  }

  .image-placeholder {
    width: 100%;
    height: 150px;
    background-color: #e0e0e0;
    border-radius: 4px;
  }

  .item-info h3 {
    margin: 10px 0 5px;
    font-size: 16px;
  }

  .location, .time {
    color: #888;
    font-size: 12px;
    margin: 0;
  }
  </style>