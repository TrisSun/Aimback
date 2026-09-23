<script setup lang="ts">
import type { Claim } from '@/api/types'
import { CLAIM_STATUS_LABEL } from '@/constants/taxonomy'

defineProps<{
  claims: Claim[]
}>()

const emit = defineEmits<{
  action: [payload: { action: 'approve' | 'reject' | 'confirm'; id: number }]
}>()
</script>

<template>
  <article v-if="claims.length" class="block">
    <h2>认领记录（仅作者可见）</h2>
    <div v-for="claim in claims" :key="claim.id" class="claim">
      <p>认领 #{{ claim.id }} · {{ CLAIM_STATUS_LABEL[claim.status] || claim.status }}</p>
      <p v-for="answer in claim.answers" :key="answer.question_id">
        {{ answer.question }}：{{ answer.answer }}
      </p>
      <div class="actions">
        <button
          v-if="claim.status === 'pending'"
          type="button"
          @click="emit('action', { action: 'approve', id: claim.id })"
        >
          通过
        </button>
        <button
          v-if="claim.status === 'pending'"
          type="button"
          class="ghost"
          @click="emit('action', { action: 'reject', id: claim.id })"
        >
          拒绝
        </button>
        <button
          v-if="claim.status === 'approved'"
          type="button"
          @click="emit('action', { action: 'confirm', id: claim.id })"
        >
          确认交接
        </button>
      </div>
    </div>
  </article>
</template>

<style scoped>
.block {
  margin-top: 16px;
  background: #fff;
  padding: 20px;
  border-radius: 16px;
}
.claim + .claim {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}
.actions {
  display: flex;
  gap: 8px;
  margin-top: 8px;
}
button {
  background: #ff6b35;
  color: #fff;
  border: 0;
  border-radius: 10px;
  padding: 10px 12px;
  cursor: pointer;
}
.ghost {
  background: #eee;
  color: #333;
}
</style>
