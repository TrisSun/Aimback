<template>
    <div class="detail-page">
      <div class="detail-card">
        <!-- 左侧：大图占位区 -->
        <div class="gallery">
          <div class="main-image">
            <el-image
              v-if="item.images.length"
              :src="item.images[activeIndex]"
              fit="cover"
              class="main-image__img"
            >
              <template #error>
                <div class="image-placeholder">
                  <el-icon :size="56"><Picture /></el-icon>
                  <span>图片加载失败</span>
                </div>
              </template>
            </el-image>
            <!-- 无图时的占位 -->
            <div v-else class="image-placeholder">
              <el-icon :size="56"><Picture /></el-icon>
              <span>暂无图片</span>
            </div>
            <span class="main-image__tag">{{ item.category_l1_label }}</span>
          </div>

          <!-- 缩略图列表（仅一张图时自动隐藏） -->
          <div v-if="item.images.length > 1" class="thumbs">
            <div
              v-for="(img, i) in item.images"
              :key="i"
              class="thumb"
              :class="{ 'is-active': i === activeIndex }"
              @click="activeIndex = i"
            >
              <el-image :src="img" fit="cover" class="thumb__img" />
            </div>
          </div>
        </div>

        <!-- 右侧：核心信息 -->
        <div class="info">
          <h1 class="info__title">{{ item.title }}</h1>

          <div class="info__meta">
            <div class="meta-row">
              <el-icon class="meta-row__icon"><Location /></el-icon>
              <span class="meta-row__label">丢失地点</span>
              <span class="meta-row__value">{{ item.found_place?.name }}</span>
            </div>
            <div class="meta-row">
              <el-icon class="meta-row__icon"><Clock /></el-icon>
              <span class="meta-row__label">丢失时间</span>
              <span class="meta-row__value">{{ item.event_start_at }}</span>
            </div>
            <div class="meta-row">
              <el-icon class="meta-row__icon"><Box /></el-icon>
              <span class="meta-row__label">物品类别</span>
              <span class="meta-row__value">{{ item.category_l1_label }} / {{ item.category_l2_label }}</span>
            </div>
          </div>

          <div class="info__owner">
            <el-avatar :size="36" class="owner-avatar">{{ item.ownerName?.slice(0, 1) }}</el-avatar>
            <span class="owner-name">{{ item.ownerName }}</span>
            <span class="owner-time">发布于 {{ item.published_at }}</span>
          </div>

          <div class="info__actions">
            <el-button
              type="primary"
              size="large"
              class="contact-btn"
              @click="contactOwner"
            >
              <el-icon class="btn-icon"><ChatDotRound /></el-icon>
              联系失主
            </el-button>
            <el-button size="large" plain @click="handleFavorite">
              <el-icon class="btn-icon"><Star /></el-icon>
              {{ isFavorite ? '已收藏' : '收藏' }}
            </el-button>
          </div>

          <p class="info__tips">
            <el-icon><Warning /></el-icon>
            请勿提前支付任何费用，谨防诈骗
          </p>
        </div>
      </div>

      <!-- 详细描述 -->
      <div class="desc-card">
        <h2 class="desc-card__title">详细描述</h2>
        <p class="desc-card__content">{{ item.description }}</p>
      </div>

      <!-- 联系失主弹窗 -->
      <el-dialog v-model="dialogVisible" title="联系失主" width="360px" center>
        <div class="contact-dialog">
          <p class="contact-dialog__tip">请通过以下方式与失主取得联系，说明物品特征以便确认。</p>
          <div class="contact-dialog__row">
            <span class="label">微信</span>
            <span class="value">{{ item.contact?.wechat }}</span>
            <el-button size="small" type="primary" plain @click="copyText(item.contact?.wechat)">
              复制
            </el-button>
          </div>
          <div class="contact-dialog__row">
            <span class="label">手机</span>
            <span class="value">{{ item.contact?.phone }}</span>
            <el-button size="small" type="primary" plain @click="copyText(item.contact?.phone)">
              复制
            </el-button>
          </div>
        </div>
      </el-dialog>
    </div>
  </template>

  <script setup lang="ts">
  import { ref, reactive, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import { ElMessage } from 'element-plus'
  import {
    Picture,
    Location,
    Clock,
    Box,
    ChatDotRound,
    Star,
    Warning
  } from '@element-plus/icons-vue'

  /** 物品详情数据结构（根据后端接口契约更新） */
  /** 物品详情数据结构（根据后端接口契约更新） */
  interface ItemDetail {
    id: number
    title: string | null
    category_l1: string
    category_l1_label: string
    category_l2: string
    category_l2_label: string
    found_region: { code: string, name: string } | null
    found_place: { id: number, name: string, place_type: string } | null
    event_start_at: string | null
    event_end_at: string | null
    published_at: string | null
    description: string
    images: { id: number, sort_order: number, url: string, review_status: string }[]
    ownerName?: string
    contact?: { wechat: string, phone: string } | null
  }

  const route = useRoute()

  const item = reactive<ItemDetail>({
    id: 0,
    title: '',
    category_l1: '',
    category_l1_label: '',
    category_l2: '',
    category_l2_label: '',
    found_region: null,
    found_place: null,
    event_start_at: null,
    event_end_at: null,
    published_at: null,
    description: '',
    images: [],
    ownerName: '',
    contact: { wechat: '', phone: '' }
  })

  const activeIndex = ref(0)
  const isFavorite = ref(false)
  const dialogVisible = ref(false)

  /** 拉取详情数据（这里用 mock 演示，替换为真实接口即可） */
  async function fetchDetail() {
    // const id = route.params.id as string
    // const res = await request.get(`/api/items/${id}`)
    // Object.assign(item, res.data)

    Object.assign(item, {
      id: Number(route.params.id) || 1,
      title: '黑色双肩背包（内含笔记本电脑）',
      category_l1: 'bags',
      category_l1_label: '包袋',
      category_l2: 'backpack',
      category_l2_label: '双肩包',
      found_region: { code: '440305', name: '南山区' },
      found_place: { id: 12, name: '图书馆', place_type: 'school' },
      event_start_at: '2026-08-20T14:30:00Z',
      event_end_at: '2026-08-20T15:00:00Z',
      published_at: '2026-08-21',
      description: '8月20日下午在图书馆三楼自习区丢失一个黑色双肩背包，内有一台银色笔记本电脑（带蓝色贴纸）、若干书本和一副耳机。\n包外侧有一处轻微磨损，拉链头是金属圆环。如有拾到，请及时联系我，万分感谢！',
      images: [
        { id: 1, sort_order: 0, url: 'https://picsum.photos/seed/bag1/600/600', review_status: 'approved' },
        { id: 2, sort_order: 1, url: 'https://picsum.photos/seed/bag2/600/600', review_status: 'approved' },
        { id: 3, sort_order: 2, url: 'https://picsum.photos/seed/bag3/600/600', review_status: 'approved' }
      ],
      ownerName: '林同学',
      contact: {
        wechat: 'lin_xiaolin',
        phone: '138****1234'
      }
    })
  }

  function contactOwner() {
    dialogVisible.value = true
  }

  function handleFavorite() {
    isFavorite.value = !isFavorite.value
    ElMessage.success(isFavorite.value ? '收藏成功' : '已取消收藏')
  }

    async function copyText(text: string | undefined) {
    if (!text) {
      ElMessage.warning('暂无联系方式')
      return
    }
    try {
      await navigator.clipboard.writeText(text)
      ElMessage.success('已复制到剪贴板')
    } catch {
      ElMessage.warning('复制失败，请手动复制')
    }
  }

  onMounted(fetchDetail)
  </script>

  <style scoped>
  /* 主色：改成你想用的品牌色即可 */
  .detail-page {
    --brand: #ff6b35;
    --brand-light: #fff3ec;
    max-width: 1080px;
    margin: 24px auto;
    padding: 0 16px;
    color: #333;
  }

  /* ---------- 主卡片 ---------- */
  .detail-card {
    display: flex;
    gap: 32px;
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  }

  /* ---------- 左侧图片 ---------- */
  .gallery {
    flex: 0 0 460px;
  }

  .main-image {
    position: relative;
    width: 100%;
    height: 460px;
    border-radius: 12px;
    overflow: hidden;
    background: #f5f6f7;
  }

  .main-image__img {
    width: 100%;
    height: 100%;
  }

  .image-placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: #c0c4cc;
    background: linear-gradient(135deg, #f7f9fb 0%, #eef2f5 100%);
  }

  .main-image__tag {
    position: absolute;
    top: 12px;
    left: 12px;
    padding: 4px 10px;
    font-size: 12px;
    color: #fff;
    background: rgba(0, 0, 0, 0.45);
    border-radius: 6px;
    backdrop-filter: blur(4px);
  }

  .thumbs {
    display: flex;
    gap: 10px;
    margin-top: 12px;
  }

  .thumb {
    width: 68px;
    height: 68px;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    border: 2px solid transparent;
    transition: border-color 0.2s;
  }

  .thumb.is-active {
    border-color: var(--brand);
  }

  .thumb__img {
    width: 100%;
    height: 100%;
  }

  /* ---------- 右侧信息 ---------- */
  .info {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
  }

  .info__title {
    font-size: 24px;
    font-weight: 600;
    line-height: 1.4;
    color: #222;
    margin: 0 0 12px;
  }

  .info__meta {
    background: #fafbfc;
    border-radius: 10px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 14px;
  }

  .meta-row {
    display: flex;
    align-items: center;
    font-size: 14px;
  }

  .meta-row__icon {
    color: var(--brand);
    margin-right: 8px;
  }

  .meta-row__label {
    color: #999;
    margin-right: 12px;
    flex: 0 0 auto;
  }

  .meta-row__value {
    color: #333;
    font-weight: 500;
  }

  .info__owner {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 20px 0;
  }

  .owner-avatar {
    background: var(--brand-light);
    color: var(--brand);
    font-weight: 600;
  }

  .owner-name {
    font-size: 14px;
    font-weight: 500;
  }

  .owner-time {
    font-size: 12px;
    color: #bbb;
  }

  .info__actions {
    display: flex;
    gap: 12px;
  }

  .contact-btn {
    flex: 1;
    background: var(--brand);
    border-color: var(--brand);
    font-weight: 500;
  }

  .contact-btn:hover {
    background: #ff8050;
    border-color: #ff8050;
  }

  .btn-icon {
    margin-right: 6px;
  }

  .info__tips {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-top: 16px;
    font-size: 12px;
    color: #b0b3b8;
  }

  /* ---------- 描述卡片 ---------- */
  .desc-card {
    margin-top: 16px;
    background: #fff;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  }

  .desc-card__title {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 14px;
    padding-left: 10px;
    border-left: 4px solid var(--brand);
  }

  .desc-card__content {
    font-size: 14px;
    line-height: 1.8;
    color: #555;
    white-space: pre-line;
    margin: 0;
  }

  /* ---------- 联系弹窗 ---------- */
  .contact-dialog__tip {
    font-size: 13px;
    color: #999;
    margin: 0 0 16px;
  }

  .contact-dialog__row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid #f0f0f0;
    font-size: 14px;
  }

  .contact-dialog__row .label {
    color: #999;
    flex: 0 0 40px;
  }

  .contact-dialog__row .value {
    flex: 1;
    font-weight: 500;
    color: #333;
  }

  /* ---------- 响应式 ---------- */
  @media (max-width: 860px) {
    .detail-card {
      flex-direction: column;
    }

    .gallery {
      flex: none;
      width: 100%;
    }

    .main-image {
      height: 0;
      padding-bottom: 100%; /* 保持 1:1 正方形 */
    }

    .main-image__img {
      position: absolute;
      inset: 0;
    }
  }
  </style>