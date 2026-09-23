<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { Post } from '@/api/types'
import { POST_STATUS_LABEL, POST_TYPE_LABEL } from '@/constants/taxonomy'
import { displayTitle, formatDateTime } from '@/utils/format'
import { coverUrl } from '@/utils/images'

const props = defineProps<{
  post: Post
  extra?: string
}>()

const router = useRouter()
const cover = computed(() => coverUrl(props.post.images))
const title = computed(() =>
  displayTitle(props.post.title, props.post.description.slice(0, 24) || '未命名物品'),
)

function openDetail() {
  void router.push({ name: 'detail', params: { id: props.post.id } })
}
</script>

<template>
  <article class="card" @click="openDetail">
    <div class="cover" :style="cover ? { backgroundImage: `url(${cover})` } : undefined">
      <span class="tag">{{ POST_TYPE_LABEL[post.type] || post.type }}</span>
    </div>
    <div class="body">
      <h3>{{ title }}</h3>
      <p class="meta">{{ post.category_l1_label }} · {{ post.category_l2_label }}</p>
      <p class="meta">
        {{ post.found_place?.name || post.found_region?.name || '地点未填' }}
      </p>
      <p class="time">{{ formatDateTime(post.published_at || post.created_at) }}</p>
      <p v-if="extra" class="extra">{{ extra }}</p>
      <p class="status">{{ POST_STATUS_LABEL[post.status] || post.status }}</p>
    </div>
  </article>
</template>

<style scoped>
.card {
  background: #fff;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  cursor: pointer;
}
.cover {
  height: 160px;
  background: #eceff3 center/cover no-repeat;
  position: relative;
}
.tag {
  position: absolute;
  top: 10px;
  left: 10px;
  background: #ff6b35;
  color: #fff;
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
}
.body {
  padding: 12px 14px 16px;
}
h3 {
  margin: 0 0 8px;
  font-size: 16px;
}
.meta,
.time,
.status,
.extra {
  margin: 0 0 4px;
  font-size: 13px;
  color: #888;
}
.extra {
  color: #ff6b35;
}
.status {
  color: #555;
}
</style>
