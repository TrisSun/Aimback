<template>
    <div class="search-result">
      <!-- 顶部搜索框 -->
      <div class="search-bar">
        <el-input
          v-model="keyword"
          placeholder="搜索失物名称、地点…"
          size="large"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #append>
            <el-button :icon="Search" @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>

      <!-- 结果统计 -->
      <div class="result-info">共找到 <span>{{ list.length }}</span> 条相关失物</div>

      <!-- 卡片列表 -->
      <el-row :gutter="20">
        <el-col
          v-for="item in list"
          :key="item.id"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
        >
          <el-card class="item-card" shadow="hover" :body-style="{ padding: '0' }">
            <!-- 图片占位 -->
            <div class="item-img">
              <el-icon :size="48"><Picture /></el-icon>
              <span>暂无图片</span>
            </div>
            <div class="item-body">
              <div class="item-name">{{ item.name }}</div>
              <div class="item-meta">
                <span class="meta-item">
                  <el-icon><Location /></el-icon>{{ item.location }}
                </span>
                <span class="meta-item">
                  <el-icon><Clock /></el-icon>{{ item.time }}
                </span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 空状态 -->
      <el-empty v-if="!list.length" description="暂无搜索结果" />
    </div>
  </template>

  <script setup lang="ts">
  import { ref } from 'vue'
  import { Search, Picture, Location, Clock } from '@element-plus/icons-vue'

  interface LostItem {
    id: number
    name: string
    location: string
    time: string
  }

  const keyword = ref('')

  // 假数据
  const list = ref<LostItem[]>([
    { id: 1, name: '黑色双肩包', location: '图书馆二楼自习区', time: '2026-08-26 14:30' },
    { id: 2, name: 'iPhone 15 手机', location: '三号教学楼 302', time: '2026-08-26 09:15' },
    { id: 3, name: '蓝色保温杯', location: '操场看台', time: '2026-08-25 18:00' },
    { id: 4, name: '校园卡（张三）', location: '一食堂门口', time: '2026-08-25 12:20' },
    { id: 5, name: '白色耳机 AirPods', location: '体育馆篮球场', time: '2026-08-24 20:45' },
    { id: 6, name: '棕色钱包', location: '校门口公交站', time: '2026-08-24 07:50' },
  ])

  const handleSearch = () => {
    // TODO: 这里接入真实接口，按 keyword 过滤查询
    console.log('搜索关键词：', keyword.value)
  }
  </script>

  <style scoped>
  .search-result {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
  }

  .search-bar {
    max-width: 560px;
    margin: 0 auto 24px;
  }

  .result-info {
    color: #909399;
    font-size: 14px;
    margin-bottom: 16px;
  }

  .result-info span {
    color: #409eff;
    font-weight: 600;
  }

  .item-card {
    margin-bottom: 20px;
    border-radius: 8px;
    overflow: hidden;
  }

  .item-img {
    height: 160px;
    background: #f5f7fa;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #c0c4cc;
  }

  .item-body {
    padding: 14px 16px;
  }

  .item-name {
    font-size: 16px;
    font-weight: 600;
    color: #303133;
    margin-bottom: 8px;
  }

  .item-meta {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .meta-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: #909399;
  }
  </style>
