<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  createPost,
  fetchPlaces,
  fetchRegions,
  presignUpload,
  publishPost,
  saveClaimQuestions,
  uploadToCos,
} from '@/api'
import { ApiError } from '@/api/http'
import type { Place, Region, UploadTicket } from '@/api/types'
import { CATEGORY_L1, CATEGORY_L2_BY_L1, PRIMARY_COLORS } from '@/constants/taxonomy'
import { toIsoFromLocal } from '@/utils/format'

const router = useRouter()
const submitting = ref(false)
const regions = ref<Region[]>([])
const places = ref<Place[]>([])
const files = ref<File[]>([])
const questions = ref<string[]>([''])

const form = reactive({
  type: 'found' as 'lost' | 'found',
  category_l1: 'electronics',
  category_l2: 'phone',
  title: '',
  description: '',
  found_region_code: '',
  found_place_id: '' as number | '',
  custody_type: 'personal',
  custody_place_id: '' as number | '',
  event_start_at: '',
  event_end_at: '',
  brand: '',
  primary_color: '',
})

const l2Options = computed(() => CATEGORY_L2_BY_L1[form.category_l1] || [])

watch(
  () => form.category_l1,
  () => {
    const options = l2Options.value
    form.category_l2 = options[0]?.value || 'other'
  },
)

watch(
  () => form.found_region_code,
  async (code) => {
    form.found_place_id = ''
    form.custody_place_id = ''
    if (!code) {
      places.value = []
      return
    }
    places.value = await fetchPlaces(code)
  },
)

onMounted(async () => {
  regions.value = await fetchRegions()
  if (regions.value[0]) form.found_region_code = regions.value[0].code
})

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  files.value = Array.from(input.files || []).slice(0, 4)
}

function buildDescription(): string {
  const extra = [
    form.brand ? `品牌：${form.brand}` : '',
    form.primary_color ? `颜色：${form.primary_color}` : '',
  ]
    .filter(Boolean)
    .join('\n')
  return extra ? `${form.description.trim()}\n${extra}` : form.description.trim()
}

async function uploadImages(): Promise<{ cos_key: string; sort_order: number }[]> {
  if (!files.value.length) return []
  const grouped = new Map<string, File[]>()
  for (const file of files.value) {
    const type = file.type || 'image/jpeg'
    grouped.set(type, [...(grouped.get(type) || []), file])
  }
  const images: { cos_key: string; sort_order: number }[] = []
  let order = 0
  for (const [contentType, group] of grouped) {
    const { tickets } = await presignUpload(group.length, contentType)
    await Promise.all(
      group.map(async (file, index) => {
        const ticket = tickets[index]
        if (!ticket) throw new Error('上传凭证数量不足')
        await uploadToCos(ticket as UploadTicket, file)
        images.push({ cos_key: ticket.cos_key, sort_order: order + index })
      }),
    )
    order += group.length
  }
  return images.sort((a, b) => a.sort_order - b.sort_order)
}

async function submit() {
  if (!form.found_region_code) {
    ElMessage.warning('请选择行政区。若列表为空，请先在 Django Admin 添加 Region / Place。')
    return
  }
  if (form.custody_type === 'official' && !form.custody_place_id) {
    ElMessage.warning('官方保管必须选择保管场所')
    return
  }
  submitting.value = true
  try {
    const images = await uploadImages()
    const post = await createPost({
      type: form.type,
      category_l1: form.category_l1,
      category_l2: form.category_l2,
      title: form.title || null,
      description: buildDescription(),
      found_region_code: form.found_region_code,
      found_place_id: form.found_place_id || null,
      custody_type: form.custody_type,
      custody_place_id: form.custody_place_id || null,
      event_start_at: toIsoFromLocal(form.event_start_at),
      event_end_at: toIsoFromLocal(form.event_end_at),
      images,
    })
    const cleaned = questions.value.map((q) => q.trim()).filter(Boolean)
    if (cleaned.length) {
      await saveClaimQuestions(post.id, cleaned)
    }
    await publishPost(post.id)
    ElMessage.success('已发布')
    await router.push({ name: 'detail', params: { id: post.id } })
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '发布失败')
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form class="form" @submit.prevent="submit">
    <h1>发布信息</h1>
    <p class="tip">结束时间不能晚于现在。隐藏问题建议只问拾取者才知道的细节。</p>

    <label>
      类型
      <select v-model="form.type">
        <option value="found">我捡到了</option>
        <option value="lost">我丢失了</option>
      </select>
    </label>
    <div class="row">
      <label>
        一级分类
        <select v-model="form.category_l1">
          <option v-for="item in CATEGORY_L1" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
      </label>
      <label>
        二级分类
        <select v-model="form.category_l2">
          <option v-for="item in l2Options" :key="item.value" :value="item.value">
            {{ item.label }}
          </option>
        </select>
      </label>
    </div>
    <label>
      标题（可选）
      <input v-model="form.title" />
    </label>
    <label>
      描述
      <textarea v-model="form.description" rows="5" required />
    </label>
    <div class="row">
      <label>
        行政区
        <select v-model="form.found_region_code">
          <option disabled value="">请选择</option>
          <option v-for="region in regions" :key="region.code" :value="region.code">
            {{ region.name }}（{{ region.code }}）
          </option>
        </select>
      </label>
      <label>
        场所（可选）
        <select v-model="form.found_place_id">
          <option value="">不指定</option>
          <option v-for="place in places" :key="place.id" :value="place.id">
            {{ place.name }}
          </option>
        </select>
      </label>
    </div>
    <label>
      保管方式
      <select v-model="form.custody_type">
        <option value="personal">个人保管</option>
        <option value="official">官方保管</option>
      </select>
    </label>
    <label v-if="form.custody_type === 'official'">
      保管场所
      <select v-model="form.custody_place_id" required>
        <option disabled value="">请选择</option>
        <option v-for="place in places" :key="place.id" :value="place.id">
          {{ place.name }}
        </option>
      </select>
    </label>
    <div class="row">
      <label>
        事件开始
        <input v-model="form.event_start_at" type="datetime-local" required />
      </label>
      <label>
        事件结束
        <input v-model="form.event_end_at" type="datetime-local" required />
      </label>
    </div>
    <div class="row">
      <label>
        品牌（可选）
        <input v-model="form.brand" />
      </label>
      <label>
        主色（可选）
        <select v-model="form.primary_color">
          <option value="">不填</option>
          <option v-for="color in PRIMARY_COLORS" :key="color.value" :value="color.value">
            {{ color.label }}
          </option>
        </select>
      </label>
    </div>
    <label>
      图片（最多 4 张）
      <input type="file" accept="image/*" multiple @change="onFileChange" />
    </label>
    <p class="tip">已选 {{ files.length }} 张。无 COS 配置时上传会失败，可先不选图。</p>
    <div>
      <p>隐藏特征问题（可选，最多 5 个）</p>
      <input
        v-for="(_, index) in questions"
        :key="index"
        v-model="questions[index]"
        :placeholder="`问题 ${index + 1}`"
      />
      <button v-if="questions.length < 5" type="button" class="ghost" @click="questions.push('')">
        加一题
      </button>
    </div>
    <button :disabled="submitting">{{ submitting ? '发布中…' : '发布' }}</button>
  </form>
</template>

<style scoped>
.form {
  background: #fff;
  padding: 24px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
label,
input,
select,
textarea,
button {
  display: block;
  width: 100%;
}
input,
select,
textarea,
button {
  margin-top: 6px;
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
.ghost {
  background: #f3f4f6;
  color: #333;
  margin-top: 8px;
}
.tip {
  color: #888;
  font-size: 13px;
}
@media (max-width: 700px) {
  .row {
    grid-template-columns: 1fr;
  }
}
</style>
