<script setup lang="ts">
import type { ClaimQuestion } from '@/api/types'

const props = defineProps<{
  questions: ClaimQuestion[]
  answers: Record<number, string>
  submitting: boolean
  loggedIn: boolean
}>()

const emit = defineEmits<{
  'update:answers': [value: Record<number, string>]
  submit: []
}>()

function updateAnswer(id: number, value: string) {
  emit('update:answers', { ...props.answers, [id]: value })
}
</script>

<template>
  <article class="block">
    <h2>发起认领</h2>
    <p class="tip">请回答隐藏特征问题。认领通过后才会看到对方手机号。</p>
    <div v-for="question in questions" :key="question.id" class="qa">
      <label>{{ question.question }}</label>
      <input
        :value="answers[question.id] || ''"
        @input="updateAnswer(question.id, ($event.target as HTMLInputElement).value)"
      />
    </div>
    <p v-if="!questions.length">发帖人未设置问题，可以直接提交认领。</p>
    <button type="button" :disabled="submitting" @click="emit('submit')">
      {{ loggedIn ? (submitting ? '提交中…' : '提交认领') : '登录后认领' }}
    </button>
  </article>
</template>

<style scoped>
.block {
  margin-top: 16px;
  background: #fff;
  padding: 20px;
  border-radius: 16px;
}
.qa {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}
input,
button {
  border-radius: 10px;
  padding: 10px 12px;
  border: 1px solid #e5e5e5;
}
button {
  background: #ff6b35;
  color: #fff;
  border: 0;
  cursor: pointer;
}
.tip {
  color: #888;
  font-size: 13px;
}
</style>
