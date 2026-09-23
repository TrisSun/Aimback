<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  approveClaim,
  cancelClaim,
  confirmHandover,
  createClaim,
  fetchClaim,
  fetchClaimQuestions,
  fetchPost,
  fetchPostClaims,
  rejectClaim,
} from '@/api'
import { ApiError } from '@/api/http'
import type { Claim, ClaimQuestion, Post } from '@/api/types'
import AuthorClaimList from '@/components/posts/AuthorClaimList.vue'
import ClaimForm from '@/components/posts/ClaimForm.vue'
import { useAuth } from '@/composables/useAuth'
import { POST_STATUS_LABEL, POST_TYPE_LABEL } from '@/constants/taxonomy'
import { displayTitle, formatDateTime } from '@/utils/format'
import { coverUrl, visibleImages } from '@/utils/images'

const route = useRoute()
const router = useRouter()
const { isLoggedIn, restore } = useAuth()

const post = ref<Post | null>(null)
const questions = ref<ClaimQuestion[]>([])
const answers = ref<Record<number, string>>({})
const claims = ref<Claim[]>([])
const activeImage = ref(0)
const loading = ref(false)
const submitting = ref(false)
const authorMode = ref(false)
const contact = ref<Claim['contact']>(null)

const postId = computed(() => Number(route.params.id))
const images = computed(() => (post.value ? visibleImages(post.value.images) : []))
const currentImage = computed(() => images.value[activeImage.value])

async function load() {
  loading.value = true
  contact.value = null
  authorMode.value = false
  claims.value = []
  try {
    await restore()
    post.value = await fetchPost(postId.value)
    questions.value = await fetchClaimQuestions(postId.value)
    answers.value = Object.fromEntries(questions.value.map((q) => [q.id, '']))
    if (isLoggedIn.value) {
      try {
        claims.value = await fetchPostClaims(postId.value)
        authorMode.value = true
      } catch {
        claims.value = []
      }
    }
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '帖子不存在')
    post.value = null
  } finally {
    loading.value = false
  }
}

async function submitClaim() {
  if (!isLoggedIn.value) {
    void router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  submitting.value = true
  try {
    const payload = questions.value.map((q) => ({
      question_id: q.id,
      answer: answers.value[q.id] || '',
    }))
    await createClaim(postId.value, payload)
    ElMessage.success('已提交认领，等待拾取者确认')
    await load()
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '认领失败')
  } finally {
    submitting.value = false
  }
}

async function runClaimAction(action: 'approve' | 'reject' | 'cancel' | 'confirm', id: number) {
  try {
    const map = {
      approve: approveClaim,
      reject: rejectClaim,
      cancel: cancelClaim,
      confirm: confirmHandover,
    }
    const result = await map[action](id)
    if (result.contact) contact.value = result.contact
    ElMessage.success('操作成功')
    await load()
    if (action === 'approve' || action === 'confirm') {
      const detail = await fetchClaim(id)
      contact.value = detail.contact || contact.value
    }
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '操作失败')
  }
}

watch(postId, load)
onMounted(load)
</script>

<template>
  <section v-if="loading">加载中…</section>
  <section v-else-if="!post">未找到这条信息</section>
  <section v-else class="detail">
    <div class="hero">
      <div class="gallery">
        <img v-if="currentImage?.url" :src="currentImage.url" alt="" />
        <div v-else class="placeholder">
          {{ coverUrl(post.images) ? '图片审核中' : '暂无图片' }}
        </div>
        <div v-if="images.length > 1" class="thumbs">
          <button
            v-for="(img, index) in images"
            :key="img.id"
            type="button"
            :class="{ on: index === activeImage }"
            @click="activeImage = index"
          >
            <img v-if="img.url" :src="img.url" alt="" />
          </button>
        </div>
      </div>
      <div class="info">
        <p class="badge">
          {{ POST_TYPE_LABEL[post.type] }} · {{ POST_STATUS_LABEL[post.status] }}
        </p>
        <h1>{{ displayTitle(post.title, post.description.slice(0, 30)) }}</h1>
        <p>{{ post.category_l1_label }} / {{ post.category_l2_label }}</p>
        <p>地点：{{ post.found_place?.name || post.found_region?.name || '未填写' }}</p>
        <p>时间：{{ formatDateTime(post.event_start_at) }} ~ {{ formatDateTime(post.event_end_at) }}</p>
        <p>发布于 {{ formatDateTime(post.published_at || post.created_at) }}</p>
      </div>
    </div>

    <article class="block">
      <h2>详细描述</h2>
      <p class="desc">{{ post.description }}</p>
      <p v-if="post.attribute?.brand">品牌：{{ post.attribute.brand }}</p>
      <p v-if="post.attribute?.primary_color">颜色：{{ post.attribute.primary_color }}</p>
    </article>

    <article v-if="contact" class="block contact">
      <h2>双方联系方式</h2>
      <p>发帖人：{{ contact.post_author_phone }}</p>
      <p>认领人：{{ contact.claimant_phone }}</p>
    </article>

    <AuthorClaimList
      v-if="authorMode"
      :claims="claims"
      @action="runClaimAction($event.action, $event.id)"
    />

    <ClaimForm
      v-if="post.status === 'published' && !authorMode"
      :questions="questions"
      :answers="answers"
      :submitting="submitting"
      :logged-in="isLoggedIn"
      @update:answers="answers = $event"
      @submit="submitClaim"
    />
  </section>
</template>

<style scoped>
.hero {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  background: #fff;
  padding: 20px;
  border-radius: 16px;
}
.gallery img {
  width: 100%;
  height: 360px;
  object-fit: cover;
  border-radius: 12px;
}
.placeholder {
  height: 360px;
  display: grid;
  place-items: center;
  background: #f3f4f6;
  border-radius: 12px;
  color: #aaa;
}
.thumbs {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}
.thumbs button {
  width: 64px;
  height: 64px;
  padding: 0;
  border: 2px solid transparent;
  overflow: hidden;
  border-radius: 8px;
}
.thumbs .on {
  border-color: #ff6b35;
}
.thumbs img {
  height: 100%;
}
.badge {
  color: #ff6b35;
  font-weight: 600;
}
.block {
  margin-top: 16px;
  background: #fff;
  padding: 20px;
  border-radius: 16px;
}
.desc {
  white-space: pre-wrap;
}
.contact {
  border: 1px solid #ffd7c6;
}
@media (max-width: 800px) {
  .hero {
    grid-template-columns: 1fr;
  }
}
</style>
