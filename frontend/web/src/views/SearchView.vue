<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { fetchMyPosts, markMatchFeedback, searchMatches } from '@/api'
import { ApiError } from '@/api/http'
import type { MatchHit, Post } from '@/api/types'
import MatchHitCard from '@/components/posts/MatchHitCard.vue'
import { CATEGORY_L1 } from '@/constants/taxonomy'

const mode = ref<'adhoc' | 'post'>('adhoc')
const loading = ref(false)
const results = ref<MatchHit[]>([])
const myLost = ref<Post[]>([])
const form = reactive({
  target_type: 'found',
  text: '',
  q: '',
  category_l1: '',
  source_post_id: '' as number | '',
})

const canSearchFromPost = computed(() => Boolean(form.source_post_id))

onMounted(async () => {
  try {
    const data = await fetchMyPosts()
    myLost.value = data.results.filter(
      (post) => post.type === 'lost' && (post.status === 'published' || post.status === 'claiming'),
    )
  } catch {
    myLost.value = []
  }
})

async function search() {
  if (mode.value === 'post' && !form.source_post_id) {
    ElMessage.warning('请先选择一条丢失帖')
    return
  }
  loading.value = true
  try {
    const payload =
      mode.value === 'post' && form.source_post_id
        ? { source_post_id: Number(form.source_post_id), q: form.q || undefined }
        : {
            target_type: form.target_type,
            text: form.text,
            q: form.q || undefined,
            category_l1: form.category_l1 || undefined,
          }
    const data = await searchMatches(payload)
    results.value = data.results
    if (!data.count) ElMessage.info('没有候选。先发帖并运行向量化，或放宽条件。')
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '搜寻失败，确认已登录且后端含匹配接口')
  } finally {
    loading.value = false
  }
}

async function markNot(hit: MatchHit) {
  if (!hit.match_id) return
  try {
    const next = hit.feedback === 'not_match' ? 'reset' : 'not_match'
    const result = await markMatchFeedback(hit.match_id, next)
    hit.feedback = result.feedback
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '标记失败')
  }
}
</script>

<template>
  <section>
    <h1>AI 搜寻</h1>
    <p class="tip">登录后才能搜寻。有丢失帖时优先用源帖，系统会自动只匹配相反类型。</p>
    <div class="modes">
      <button type="button" :class="{ on: mode === 'adhoc' }" @click="mode = 'adhoc'">临时描述</button>
      <button type="button" :class="{ on: mode === 'post' }" @click="mode = 'post'">从我的丢失帖</button>
    </div>

    <form class="panel" @submit.prevent="search">
      <template v-if="mode === 'adhoc'">
        <label>
          想找的类型
          <select v-model="form.target_type">
            <option value="found">捡到信息（我丢了东西）</option>
            <option value="lost">丢失信息（我捡到了东西）</option>
          </select>
        </label>
        <label>
          文字描述
          <textarea v-model="form.text" rows="4" placeholder="例如：图书馆黑色手机" />
        </label>
        <label>
          分类（可选）
          <select v-model="form.category_l1">
            <option value="">不限</option>
            <option v-for="item in CATEGORY_L1" :key="item.value" :value="item.value">
              {{ item.label }}
            </option>
          </select>
        </label>
      </template>
      <template v-else>
        <label>
          选择丢失帖
          <select v-model="form.source_post_id">
            <option value="">请选择</option>
            <option v-for="post in myLost" :key="post.id" :value="post.id">
              #{{ post.id }} {{ post.title || post.description.slice(0, 20) }}
            </option>
          </select>
        </label>
        <p v-if="!myLost.length" class="tip">还没有已发布的丢失帖，请先去发布。</p>
      </template>
      <label>
        关键词（可选）
        <input v-model="form.q" />
      </label>
      <button :disabled="loading || (mode === 'post' && !canSearchFromPost)">
        {{ loading ? '搜寻中…' : '开始搜寻' }}
      </button>
    </form>

    <div class="results">
      <MatchHitCard v-for="hit in results" :key="hit.match_id || hit.post.id" :hit="hit" @mark-not="markNot(hit)" />
    </div>
  </section>
</template>

<style scoped>
.tip {
  color: #888;
}
.modes {
  display: flex;
  gap: 8px;
  margin: 12px 0;
}
.panel {
  background: #fff;
  padding: 16px;
  border-radius: 14px;
  margin-bottom: 12px;
}
label,
input,
select,
textarea,
button {
  display: block;
  width: 100%;
  margin-top: 8px;
}
input,
select,
textarea,
button {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid #e5e5e5;
}
button {
  background: #ff6b35;
  color: #fff;
  border: 0;
  cursor: pointer;
}
.modes button {
  width: auto;
  background: #f3f4f6;
  color: #333;
}
.modes .on {
  background: #ff6b35;
  color: #fff;
}
.results {
  margin-top: 16px;
}
</style>
