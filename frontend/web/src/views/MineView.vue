<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  cancelClaim,
  closePost,
  confirmHandover,
  deletePost,
  fetchClaim,
  fetchMyClaims,
  fetchMyPosts,
  publishPost,
} from '@/api'
import { ApiError } from '@/api/http'
import type { Claim, Post } from '@/api/types'
import PostCard from '@/components/PostCard.vue'
import { CLAIM_STATUS_LABEL } from '@/constants/taxonomy'

const router = useRouter()
const tab = ref<'posts' | 'claims'>('posts')
const posts = ref<Post[]>([])
const claims = ref<Claim[]>([])
const contact = ref<Claim['contact']>(null)

async function load() {
  try {
    posts.value = (await fetchMyPosts()).results
    const mine = await fetchMyClaims()
    claims.value = Array.isArray(mine) ? mine : []
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '加载失败')
  }
}

async function publish(post: Post) {
  try {
    await publishPost(post.id)
    ElMessage.success('已发布')
    await load()
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '发布失败')
  }
}

async function close(post: Post) {
  try {
    await closePost(post.id)
    ElMessage.success('已关闭')
    await load()
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '关闭失败')
  }
}

async function remove(post: Post) {
  try {
    await ElMessageBox.confirm('删除后不可恢复，确定删除？', '删除帖子')
    await deletePost(post.id)
    ElMessage.success('已删除')
    await load()
  } catch (error) {
    if (error === 'cancel' || error === 'close') return
    ElMessage.error(error instanceof ApiError ? error.message : '删除失败')
  }
}

async function handleClaim(action: 'cancel' | 'confirm', claim: Claim) {
  try {
    const result =
      action === 'cancel' ? await cancelClaim(claim.id) : await confirmHandover(claim.id)
    if (action === 'confirm') {
      const detail = await fetchClaim(claim.id)
      contact.value = detail.contact || result.contact
    }
    ElMessage.success('已更新')
    await load()
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '操作失败')
  }
}

onMounted(load)
</script>

<template>
  <section>
    <div class="tabs">
      <button type="button" :class="{ on: tab === 'posts' }" @click="tab = 'posts'">我的帖子</button>
      <button type="button" :class="{ on: tab === 'claims' }" @click="tab = 'claims'">我的认领</button>
    </div>

    <div v-if="tab === 'posts'" class="list">
      <p v-if="!posts.length">还没有帖子。</p>
      <article v-for="post in posts" :key="post.id" class="item">
        <PostCard :post="post" />
        <div class="actions">
          <button v-if="post.status === 'draft'" type="button" @click="publish(post)">发布</button>
          <button
            v-if="post.status === 'published' || post.status === 'claiming' || post.status === 'draft'"
            type="button"
            class="ghost"
            @click="close(post)"
          >
            关闭
          </button>
          <button
            v-if="post.status === 'draft' || post.status === 'closed'"
            type="button"
            class="ghost"
            @click="remove(post)"
          >
            删除
          </button>
          <button
            v-if="post.type === 'lost' && (post.status === 'published' || post.status === 'claiming')"
            type="button"
            class="ghost"
            @click="router.push({ name: 'search' })"
          >
            去搜寻
          </button>
        </div>
      </article>
    </div>

    <div v-else class="list">
      <article v-if="contact" class="contact">
        <h3>联系方式</h3>
        <p>发帖人 {{ contact.post_author_phone }}</p>
        <p>认领人 {{ contact.claimant_phone }}</p>
      </article>
      <p v-if="!claims.length">还没有认领记录。</p>
      <article v-for="claim in claims" :key="claim.id" class="claim">
        <p>认领 #{{ claim.id }} · 帖子 {{ claim.post }} · {{ CLAIM_STATUS_LABEL[claim.status] || claim.status }}</p>
        <div class="actions">
          <button type="button" class="ghost" @click="router.push({ name: 'detail', params: { id: claim.post } })">
            查看帖子
          </button>
          <button v-if="claim.status === 'pending'" type="button" class="ghost" @click="handleClaim('cancel', claim)">
            撤回
          </button>
          <button v-if="claim.status === 'approved'" type="button" @click="handleClaim('confirm', claim)">
            确认交接
          </button>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.tabs,
.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.item,
.claim,
.contact {
  background: #fff;
  padding: 12px;
  border-radius: 14px;
  margin-bottom: 12px;
}
button {
  border: 0;
  background: #ff6b35;
  color: #fff;
  border-radius: 8px;
  padding: 8px 12px;
  cursor: pointer;
}
.tabs button,
.ghost {
  background: #f3f4f6;
  color: #333;
}
.tabs .on {
  background: #ff6b35;
  color: #fff;
}
</style>
