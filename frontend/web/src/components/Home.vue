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
              <!-- 改成新字段 -->
              <h3>{{ item.title }}</h3>
              <p class="location">📍 {{ item.found_place?.name }}</p>
              <p class="time">🕒 {{ item.event_start_at }}</p>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </template>

 <script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// 1. 定义符合后端契约的类型 (把原来的 LostItem 换成这个)
interface LostItem {
  id: number
  title: string
  description: string
  category_l1: string
  category_l1_label: string
  category_l2: string
  category_l2_label: string
  found_region: { code: string, name: string } | null
  found_place: { id: number, name: string, place_type: string } | null
  event_start_at: string
  event_end_at: string
  published_at: string
  images: { id: number, sort_order: number, url: string, review_status: string }[]
}

const router = useRouter()
const searchText = ref('')
const categories = ['全部', '电子设备', '证件', '包袋', '衣物', '其他']
const currentCategory = ref('全部')

// 2. 把原来的 const items 替换成这一段新的假数据
const items = ref<LostItem[]>([
  {
    id: 1,
    title: '黑色双肩包',
    description: '图书馆三楼自习区捡到，内有笔记本电脑。',
    category_l1: 'bags',
    category_l1_label: '包袋',
    category_l2: 'backpack',
    category_l2_label: '双肩包',
    found_region: { code: '440305', name: '南山区' },
    found_place: { id: 12, name: '图书馆', place_type: 'school' },
    event_start_at: '2026-08-26T14:30:00Z',
    event_end_at: '2026-08-26T15:00:00Z',
    published_at: '2026-08-26T15:10:00Z',
    images: [{ id: 1, sort_order: 0, url: '', review_status: 'pending' }]
  },
  {
    id: 2,
    title: 'iPhone 15 手机',
    description: '三号教学楼302捡到，黑色手机。',
    category_l1: 'electronics',
    category_l1_label: '电子设备',
    category_l2: 'phone',
    category_l2_label: '手机',
    found_region: { code: '440305', name: '南山区' },
    found_place: { id: 13, name: '三号教学楼', place_type: 'school' },
    event_start_at: '2026-08-26T09:15:00Z',
    event_end_at: '2026-08-26T10:00:00Z',
    published_at: '2026-08-26T10:05:00Z',
    images: [{ id: 2, sort_order: 0, url: '', review_status: 'pending' }]
  },
  {
    id: 3,
    title: '蓝色保温杯',
    description: '操场看台捡到蓝色保温杯。',
    category_l1: 'other',
    category_l1_label: '其他',
    category_l2: 'other',
    category_l2_label: '其他',
    found_region: { code: '440305', name: '南山区' },
    found_place: { id: 14, name: '操场', place_type: 'school' },
    event_start_at: '2026-08-25T18:00:00Z',
    event_end_at: '2026-08-25T19:00:00Z',
    published_at: '2026-08-25T19:20:00Z',
    images: [{ id: 3, sort_order: 0, url: '', review_status: 'pending' }]
  }
])

const handleSearch = () => {
  // TODO: 这里接入真实接口，按 keyword 过滤查询
  console.log('搜索关键词：', searchText.value)
}

// 跳转到详情页
function goDetail(item: LostItem) {
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