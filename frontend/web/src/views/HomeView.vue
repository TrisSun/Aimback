<script setup lang="ts">
import { onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchPosts } from '@/api'
import { ApiError } from '@/api/http'
import type { Post } from '@/api/types'
import PostCard from '@/components/PostCard.vue'
import PostFilterBar from '@/components/posts/PostFilterBar.vue'

const filters = reactive({
  q: '',
  type: '',
  category_l1: '',
  page: 1,
})
const posts = ref<Post[]>([])
const count = ref(0)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const data = await fetchPosts({
      q: filters.q,
      type: filters.type || undefined,
      category_l1: filters.category_l1 || undefined,
      page: filters.page,
      page_size: 12,
    })
    posts.value = data.results
    count.value = data.count
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '加载失败，请确认后端已启动')
  } finally {
    loading.value = false
  }
}

function search() {
  filters.page = 1
  void load()
}

watch(
  () => [filters.type, filters.category_l1],
  () => {
    filters.page = 1
    void load()
  },
)

onMounted(load)
</script>

<template>
  <section>
    <PostFilterBar
      v-model:q="filters.q"
      v-model:type="filters.type"
      v-model:categoryL1="filters.category_l1"
      @search="search"
    />
    <p class="count">共 {{ count }} 条公开信息</p>
    <p v-if="loading" class="empty">加载中…</p>
    <p v-else-if="!posts.length" class="empty">暂时没有帖子。登录后可以发布第一条。</p>
    <div v-else class="grid">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>
    <div v-if="count > 12" class="pager">
      <button type="button" :disabled="filters.page <= 1" @click="filters.page -= 1; load()">
        上一页
      </button>
      <span>第 {{ filters.page }} 页</span>
      <button
        type="button"
        :disabled="filters.page * 12 >= count"
        @click="filters.page += 1; load()"
      >
        下一页
      </button>
    </div>
  </section>
</template>

<style scoped>
.count,
.empty {
  color: #888;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.pager {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 20px;
}
.pager button {
  border: 0;
  background: #ff6b35;
  color: #fff;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
}
</style>
