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
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getPosts } from '@/api/posts'
import type { Post } from '@/api/posts'

const router = useRouter()
const searchText = ref('')
const categories = ['全部', '电子设备', '证件', '包袋', '衣物', '其他']
const currentCategory = ref('全部')

// 帖子列表（真实数据，契约 3.3）
const items = ref<Post[]>([])

const fetchPosts = async () => {
  try {
    const res = await getPosts({ page: 1, page_size: 20 })
    items.value = res.results
    // 打印符合契约 3.3 的返回结构
    console.log('帖子列表响应：', res)
  } catch (error) {
    console.error('获取帖子列表失败：', error)
  }
}

onMounted(fetchPosts)

const handleSearch = () => {
  // TODO: 这里接入真实接口，按 keyword 过滤查询
  console.log('搜索关键词：', searchText.value)
}

// 跳转到详情页
function goDetail(item: Post) {
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