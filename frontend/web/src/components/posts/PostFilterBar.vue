<script setup lang="ts">
import { CATEGORY_L1 } from '@/constants/taxonomy'

defineProps<{
  q: string
  type: string
  categoryL1: string
}>()

const emit = defineEmits<{
  'update:q': [value: string]
  'update:type': [value: string]
  'update:categoryL1': [value: string]
  search: []
}>()
</script>

<template>
  <div class="toolbar">
    <input
      :value="q"
      placeholder="搜索失物 / 招领信息"
      @input="emit('update:q', ($event.target as HTMLInputElement).value)"
      @keyup.enter="emit('search')"
    />
    <select
      :value="type"
      @change="emit('update:type', ($event.target as HTMLSelectElement).value)"
    >
      <option value="">全部类型</option>
      <option value="lost">丢失</option>
      <option value="found">捡到</option>
    </select>
    <select
      :value="categoryL1"
      @change="emit('update:categoryL1', ($event.target as HTMLSelectElement).value)"
    >
      <option value="">全部分类</option>
      <option v-for="item in CATEGORY_L1" :key="item.value" :value="item.value">
        {{ item.label }}
      </option>
    </select>
    <button type="button" @click="emit('search')">搜索</button>
  </div>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
input,
select,
button {
  border: 1px solid #e5e5e5;
  border-radius: 10px;
  padding: 10px 12px;
  background: #fff;
}
button {
  background: #ff6b35;
  color: #fff;
  border: 0;
  cursor: pointer;
}
</style>
