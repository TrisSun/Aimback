<script setup lang="ts">
import type { MatchHit } from '@/api/types'
import PostCard from '@/components/PostCard.vue'

defineProps<{
  hit: MatchHit
}>()

const emit = defineEmits<{
  'mark-not': []
}>()
</script>

<template>
  <article class="hit">
    <PostCard :post="hit.post" :extra="hit.reason" />
    <div class="score">
      <span>综合分 {{ hit.score.toFixed(2) }} · 向量 {{ hit.vector_score.toFixed(2) }}</span>
      <button
        v-if="hit.match_id"
        type="button"
        class="ghost"
        @click="emit('mark-not')"
      >
        {{ hit.feedback === 'not_match' ? '取消「不是这个」' : '不是这个' }}
      </button>
    </div>
  </article>
</template>

<style scoped>
.hit {
  background: #fff;
  padding: 16px;
  border-radius: 14px;
  margin-bottom: 12px;
}
.score {
  display: flex;
  gap: 8px;
  align-items: center;
  justify-content: space-between;
  margin-top: 8px;
}
button {
  border: 0;
  border-radius: 10px;
  padding: 8px 12px;
  cursor: pointer;
}
.ghost {
  background: #f3f4f6;
  color: #333;
}
</style>
