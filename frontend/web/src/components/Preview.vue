<template>
  <div class="preview" :data-theme="theme">
    <!-- 顶部工具条 -->
    <div class="toolbar">
      <div class="group">
        <span class="lbl">配色</span>
        <button class="tbtn" :class="{ on: theme === 'green' }" @click="theme = 'green'">A 青绿 <span class="rec">（推荐）</span></button>
        <button class="tbtn" :class="{ on: theme === 'blue' }" @click="theme = 'blue'">B 信任蓝</button>
        <button class="tbtn" :class="{ on: theme === 'orange' }" @click="theme = 'orange'">C 暖橙</button>
      </div>
      <div class="group" style="margin-left:auto">
        <span class="lbl">页面</span>
        <button class="tbtn" :class="{ on: page === 'home' }" @click="switchPage('home')">首页</button>
        <button class="tbtn" :class="{ on: page === 'detail' }" @click="switchPage('detail')">详情页</button>
        <button class="tbtn" :class="{ on: page === 'msg' }" @click="switchPage('msg')">消息</button>
        <button class="tbtn" :class="{ on: page === 'publish' }" @click="switchPage('publish')">发布页</button>
      </div>
    </div>

    <!-- 站点头部 -->
    <div class="site-head">
      <div class="inner">
        <div class="logo"><span class="mark">A</span>Aimback</div>
        <div class="search">
          <input v-model="searchText" placeholder="搜索失物 / 招领信息">
          <button @click="toast('搜索：' + (searchText || '全部'))">搜索</button>
        </div>
        <button class="btn-msg" title="消息" @click="switchPage('msg')">🔔<span class="badge" v-show="unreadCount > 0">{{ unreadCount }}</span></button>
        <button class="btn-pub" @click="switchPage('publish')">＋ 发布信息</button>
      </div>
    </div>
    <!-- ========== 首页 ========== -->
    <div v-show="page === 'home'">
      <div class="main">
        <aside class="side">
          <div class="t"><span class="step">2</span>物品分类</div>
          <div
            v-for="c in categories"
            :key="c.key"
            class="it"
            :class="{ on: curCat === c.key }"
            @click="curCat = c.key"
          >
            {{ c.label }}
          </div>
        </aside>

        <div class="content">
          <div class="campus-bar">
            <div class="cap"><span class="step">1</span>选择校区</div>
            <div class="campus-row">
              <div
                v-for="c in campuses"
                :key="c.key"
                class="campus"
                :class="{ on: curCampus === c.key }"
                @click="curCampus = c.key"
              >
                <div class="cn">{{ c.name }}</div>
                <div class="cs">{{ c.sub }}</div>
              </div>
            </div>
          </div>

          <div class="filter-bar">
            <span class="chip" :class="{ on: chip === 0 }" @click="chip = 0">全部</span>
            <span class="chip" :class="{ on: chip === 1 }" @click="chip = 1">我丢的</span>
            <span class="chip" :class="{ on: chip === 2 }" @click="chip = 2">我捡的</span>
            <span class="count">共 {{ filteredItems.length }} 条</span>
          </div>

          <div class="grid">
            <div
              v-for="it in filteredItems"
              :key="it.name"
              class="card"
              @click="openDetail(it)"
            >
              <div class="img">{{ it.icon }}</div>
              <div class="body">
                <div class="name">{{ it.name }}</div>
                <div class="meta">📍 {{ it.campusName }} · {{ it.loc }}</div>
                <div class="meta">🕒 {{ it.time }}</div>
                <div class="foot">
                  <span class="tag" :class="tagMap[it.status].cls"><i class="dot"></i>{{ tagMap[it.status].txt }}</span>
                  <span class="cat">{{ it.cat }}{{ it.reward ? ' · 🏆¥' + netOf(it.reward) : '' }}</span>
                </div>
              </div>
            </div>
            <div v-if="!filteredItems.length" style="padding:40px;text-align:center;color:#86909C;font-size:14px;grid-column:1/-1">该校区暂无相关失物信息</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 详情页 ========== -->
    <div v-show="page === 'detail'">
      <div class="main" style="flex-direction:column">
        <div class="back" @click="switchPage('home')">← 返回列表</div>

        <div v-if="currentDetail">
          <div class="detail">
            <div class="gallery">
              <div class="big-img">
                <img v-if="currentDetail.images && currentDetail.images.length" :src="currentDetail.images[activeThumb]" alt="">
                <template v-else>{{ bigIcon }}</template>
                <span class="tag" :class="tagMap[currentDetail.status].cls"><i class="dot"></i>{{ tagMap[currentDetail.status].txt }}</span>
              </div>
              <div v-if="currentDetail.images && currentDetail.images.length" class="thumbs">
                <div
                  v-for="(img, i) in currentDetail.images"
                  :key="i"
                  class="thumb"
                  :class="{ on: activeThumb === i }"
                  @click="activeThumb = i"
                >
                  <img :src="img" alt="">
                </div>
              </div>
              <div v-else class="thumbs">
                <div
                  v-for="(ic, i) in thumbIcons"
                  :key="i"
                  class="thumb"
                  :class="{ on: activeThumb === i }"
                  @click="pickThumb(i, ic)"
                >
                  {{ ic }}
                </div>
              </div>
            </div>

            <div class="info">
              <h1>{{ currentDetail.name }}</h1>
              <div class="metas">
                <div class="mrow"><span class="k">所属校区</span><span class="v">{{ currentDetail.campusName }}</span></div>
                <div class="mrow"><span class="k">丢失地点</span><span class="v">{{ currentDetail.loc }}</span></div>
                <div class="mrow"><span class="k">丢失时间</span><span class="v">{{ currentDetail.time }}</span></div>
                <div class="mrow"><span class="k">物品类别</span><span class="v">{{ currentDetail.cat }}</span></div>
                <div class="mrow"><span class="k">物品颜色</span><span class="v">黑色</span></div>
              </div>

              <div class="owner">
                <div class="avatar">{{ currentDetail.owner }}</div>
                <span class="oname">{{ currentDetail.ownerName }}</span>
                <span class="otime">发布于 {{ currentDetail.pub }}</span>
              </div>

              <div class="acts">
                <button
                  class="btn btn-main"
                  :disabled="currentDetail.status === 'done'"
                  :style="{ opacity: currentDetail.status === 'done' ? '.6' : '1' }"
                  @click="openClaimModal"
                >
                  {{ claimBtnText }}
                </button>
                <button class="btn btn-sec" :class="{ fav: isFav }" @click="toggleFav">{{ isFav ? '★ 已收藏' : '☆ 收藏' }}</button>
              </div>

              <div class="safety">🛡 认领需通过验证问答，通过后才会交换联系方式</div>

              <div v-if="currentDetail.reward" class="reward-banner">
                <div class="rm">¥{{ netOf(currentDetail.reward) }}</div>
                <div>
                  <div class="rt">拾获者可得赏金（已扣手续费）</div>
                  <div class="rd">失主悬赏 ¥{{ currentDetail.reward }}，已自动扣除 ¥{{ feeOf(currentDetail.reward) }} 平台手续费（10%）</div>
                </div>
              </div>
            </div>
          </div>

          <div class="desc">
            <h2>详细描述</h2>
            <p>{{ currentDetail.desc }}</p>
          </div>
        </div>
      </div>
    </div>
    <!-- ========== 消息页 ========== -->
    <div v-show="page === 'msg'">
      <div class="main" style="display:block">
        <div class="msg-wrap">
          <div class="msg-head">
            <h2>消息</h2>
            <span class="n">{{ unreadCount }} 条未读</span>
          </div>
          <div class="msg-tabs">
            <span class="mt on">全部</span>
            <span class="mt">认领消息</span>
            <span class="mt">系统通知</span>
          </div>

          <!-- AI 智能匹配 · 置顶 -->
          <div class="pinned" @click="toast('AI 正在持续匹配，匹配到会立即推送')">
            <span class="pin-tag">置顶</span>
            <div class="pin-ico">🤖</div>
            <div>
              <div class="pin-title">AI 智能匹配已开启</div>
              <div class="pin-sub">系统正在已上传的失物中自动匹配与你丢失物品相关的信息，匹配到后会第一时间推送给你，请耐心等候。</div>
            </div>
          </div>

          <div
            v-for="(m, i) in msgs"
            :key="i"
            class="msg-item"
            :class="{ unread: m.unread }"
            @click="openReview(i)"
          >
            <div class="msg-ico" :class="m.cls">{{ m.ico }}</div>
            <div class="msg-body">
              <div class="msg-top">
                <span class="msg-title">{{ m.title }}</span>
                <span class="msg-time">{{ m.time }}</span>
              </div>
              <div class="msg-sub">{{ m.sub }}</div>
            </div>
            <span v-if="m.unread" class="red"></span>
          </div>
        </div>
      </div>
    </div>

    <!-- ========== 发布页（赏金设置） ========== -->
    <div v-show="page === 'publish'">
      <div class="main" style="flex-direction:column">
        <div class="back" @click="switchPage('home')">← 返回首页</div>
        <div class="pub-card">
          <h2>发布失物信息</h2>
          <div class="sub">填写物品信息并设置悬赏，拾获者归还后你可发放赏金</div>

          <div class="field">
            <label>信息类型</label>
            <div class="radio-row">
              <div class="r" :class="{ on: publishType === 'lost' }" @click="setPublishType('lost')">我丢失了物品</div>
              <div class="r" :class="{ on: publishType === 'found' }" @click="setPublishType('found')">我捡到了物品</div>
            </div>
          </div>

          <div class="field">
            <label>物品名称<span class="req">*</span></label>
            <input type="text" placeholder="如：黑色双肩背包">
          </div>

          <div class="field">
            <label>所在校区</label>
            <select>
              <option>将军路校区</option>
              <option>天目湖校区</option>
              <option>明故宫校区</option>
            </select>
          </div>

          <div class="field">
            <label>丢失 / 拾获地点<span class="req">*</span></label>
            <input type="text" placeholder="如：图书馆三楼自习区">
          </div>

          <div class="field">
            <label>详细描述<span class="req">*</span></label>
            <textarea v-model="descInput" placeholder="描述物品特征（颜色、磨损、内含物…），AI 会据此生成验证问题"></textarea>
          </div>

          <!-- AI 自动生成验证问题 -->
          <div class="ai-sec">
            <div class="ah">
              <span style="font-size:17px">🤖</span>
              <span class="at">验证问题（防冒领）</span>
              <button class="ab" @click="aiGenQuestions">用 AI 生成</button>
            </div>
            <div class="ad">根据上方详细描述，AI 自动提炼关键特征生成验证问题，用于认领时核对身份。</div>
            <div class="q-list">
              <div v-if="aiLoading" class="ai-loading">🤖 AI 正在分析描述特征…</div>
              <template v-else-if="aiQuestions.length">
                <div v-for="(q, i) in aiQuestions" :key="i" class="q-item">
                  <span class="qn">Q{{ i + 1 }}</span>
                  <span>{{ q }}</span>
                  <span class="qx" @click="delQuestion(i)">×</span>
                </div>
                <button class="vbtn" style="margin-top:6px;background:#fff;color:var(--brand);border:1px solid var(--brand)" @click="aiGenQuestions">重新生成</button>
              </template>
              <div v-else class="q-empty">填写详细描述后，点击「用 AI 生成」自动生成问题</div>
            </div>
          </div>

          <div v-show="publishType === 'lost'" class="field">
            <label>设置悬赏（系统自动扣除手续费后对外展示）</label>
            <input v-model="rewardInput" type="text" inputmode="numeric" placeholder="0 表示不设赏金">
            <div v-if="rewardValue > 0" class="fee-box">
              <div class="fee-row"><span>你设置的悬赏总额</span><span>¥{{ rewardValue }}</span></div>
              <div class="fee-row"><span>平台手续费（{{ FEE_RATE * 100 }}%，自动扣除）</span><span class="hl">- ¥{{ feeOf(rewardValue) }}</span></div>
              <div class="fee-row total"><span>对外展示的赏金</span><span class="hl2">¥{{ netOf(rewardValue) }}</span></div>
              <div class="fee-note">系统自动扣除手续费后，对外展示的赏金为 <b>¥{{ netOf(rewardValue) }}</b>，拾获者归还并通过验证后即可领取。</div>
            </div>
            <div v-else class="fee-box"><div class="fee-note">未设置赏金，拾获者归还后无需发放赏金。</div></div>
          </div>

          <button class="btn btn-main" style="width:100%;margin-top:8px" @click="toast('（预览）已发布，AI 开始自动匹配')">发布信息</button>
        </div>
      </div>
    </div>
    <!-- 认领申请弹窗（访客视角） -->
    <div class="mask" :class="{ show: maskShow }" @click.self="closeModal">
      <div class="modal">
        <div class="head">🔒 认领验证</div>
        <div class="body">
          <p class="tip">为防止冒领，请回答发布者设置的验证问题。提交后由发布者确认，通过后你才能看到对方的联系方式。</p>
          <div class="qa">
            <div class="q"><span class="n">Q1</span> 这个背包外侧有什么特征？</div>
            <input v-model="answer1" placeholder="请输入你的答案">
          </div>
          <div class="qa">
            <div class="q"><span class="n">Q2</span> 包里的电脑是什么颜色？</div>
            <input v-model="answer2" placeholder="请输入你的答案">
          </div>
        </div>
        <div class="foot">
          <button class="btn btn-sec" @click="closeModal">取消</button>
          <button class="btn btn-main" @click="submitClaim">提交认领</button>
        </div>
      </div>
    </div>

    <!-- 认领审核弹窗（发布者视角） -->
    <div class="mask" :class="{ show: reviewShow }" @click.self="closeModal">
      <div class="modal">
        <div class="head">📨 收到一条认领申请</div>
        <div class="body">
          <p class="tip">对方已回答你设置的验证问题。核对无误后通过，通过后双方互相可见联系方式。</p>
          <div class="review-item">
            <div class="rq">物品</div>
            <div class="ra">黑色双肩背包（内含银色笔记本电脑）</div>
          </div>
          <div class="review-item">
            <div class="rq">申请人</div>
            <div class="ra">王同学 · 将军路校区</div>
          </div>
          <div class="review-item">
            <div class="rq">Q1 这个背包外侧有什么特征？</div>
            <div class="ra">有一处轻微磨损，拉链头是金属圆环</div>
          </div>
          <div class="review-item">
            <div class="rq">Q2 包里的电脑是什么颜色？</div>
            <div class="ra">银色，上面贴了蓝色贴纸</div>
          </div>
          <div v-show="reviewApproved">
            <div class="contact-box">
              <div class="ct">✅ 已通过，双方联系方式已互相可见</div>
              <div class="crow"><span class="cl">微信</span><span class="cv">wang_2023</span></div>
              <div class="crow"><span class="cl">手机</span><span class="cv">139****5678</span></div>
            </div>
            <button class="btn btn-main" style="width:100%;margin-top:12px" @click="openChat('wang')">💬 进入对话，约定取物地点</button>
          </div>
        </div>
        <div v-show="!reviewApproved" class="foot">
          <button class="btn btn-danger" @click="rejectClaim">拒绝</button>
          <button class="btn btn-main" @click="approveClaim">核对无误，通过</button>
        </div>
      </div>
    </div>

    <!-- 聊天抽屉 -->
    <div class="chat-mask" :class="{ show: chatShow }" @click.self="closeChat">
      <div v-if="curChat" class="chat">
        <div class="chat-head">
          <div class="av">{{ curChat.av }}</div>
          <div>
            <div class="nm">{{ curChat.name }}</div>
            <div class="st">{{ curChat.verified ? '已通过验证，可对话' : '等待完成验证' }}</div>
          </div>
          <div class="x" @click="closeChat">×</div>
        </div>
        <div class="verify-block">
          <div class="vh">🔒 第一步 · 认领验证问答（必填）</div>
          <template v-if="curChat.verified">
            <div v-for="(q, i) in curChat.qs" :key="i" class="vq">
              <div class="q">{{ q.q }}</div>
              <div class="a">{{ q.a || '—' }}</div>
            </div>
            <div class="vt">✓ 已通过验证，对话已开启</div>
          </template>
          <template v-else>
            <div v-for="(q, i) in curChat.qs" :key="i" class="vq">
              <div class="q">{{ q.q }}</div>
              <input v-model="q.a" placeholder="请输入你的答案">
            </div>
            <button class="vbtn" @click="submitVerify">提交验证，开启对话</button>
          </template>
        </div>
        <div ref="chatMsgsRef" class="chat-msgs">
          <div v-for="(m, i) in curChat.msgs" :key="i" :class="['bubble', m.t]">{{ m.c }}</div>
        </div>
        <div class="chat-input">
          <input
            v-model="chatInput"
            :disabled="!curChat.verified"
            :placeholder="curChat.verified ? '输入消息，约定取物地点…' : '完成验证问答后可开始对话'"
            @keydown.enter.prevent="sendChat"
          >
          <button :disabled="!curChat.verified" @click="sendChat">发送</button>
        </div>
      </div>
    </div>

    <div class="toast" :class="{ show: toastVisible }">{{ toastMsg }}</div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { getPosts, getPostDetail } from '@/api/posts'
import type { Post } from '@/api/posts'

type Status = 'find' | 'claim' | 'done'
type ChatKey = 'wang' | 'applied'

interface Item {
  id?: number
  images?: string[]
  icon: string
  name: string
  loc: string
  time: string
  cat: string
  catKey: string
  status: Status
  campus: string
  owner: string
  ownerName: string
  pub: string
  campusName: string
  desc: string
  reward?: number
}

interface Msg {
  ico: string
  cls: string
  title: string
  sub: string
  time: string
  unread: boolean
  type: 'claim' | 'sys'
  chat?: ChatKey
}

interface Question {
  q: string
  a: string
}

interface ChatMsg {
  t: 'sys' | 'me' | 'he'
  c: string
}

interface Convo {
  name: string
  av: string
  verified: boolean
  qs: Question[]
  msgs: ChatMsg[]
}

// 赏金：失主发布时设置，平台收取 10% 手续费，对外展示 = 扣除手续费后的实得金额
const FEE_RATE = 0.1

const campuses = [
  { key: 'jjl', name: '将军路校区', sub: '南京 · 江宁' },
  { key: 'tmh', name: '天目湖校区', sub: '常州 · 溧阳' },
  { key: 'mgg', name: '明故宫校区', sub: '南京 · 秦淮' },
]

const categories = [
  { key: 'all', label: '全部' },
  { key: 'electronics', label: '电子设备' },
  { key: 'documents', label: '证件' },
  { key: 'bags', label: '包袋' },
  { key: 'clothing', label: '衣物' },
  { key: 'accessories', label: '饰品' },
  { key: 'stationery', label: '文具' },
  { key: 'keys', label: '钥匙与门禁' },
  { key: 'other', label: '其他' },
]

const tagMap: Record<Status, { cls: string; txt: string }> = {
  find: { cls: 'tag-find', txt: '寻找中' },
  claim: { cls: 'tag-claim', txt: '认领中' },
  done: { cls: 'tag-done', txt: '已完成' },
}

const items = ref<Item[]>([
  {
    icon: '🎒', name: '黑色双肩背包（含电脑）', loc: '图书馆三楼自习区', time: '2026-08-20',
    cat: '包袋', catKey: 'bags', status: 'find', campus: 'jjl',
    owner: '林', ownerName: '林同学', pub: '2026-08-21', campusName: '将军路校区', reward: 50,
    desc: '8月20日下午在图书馆三楼自习区丢失一个黑色双肩背包，内有一台银色笔记本电脑（带蓝色贴纸）、若干书本和一副耳机。\n包外侧有一处轻微磨损，拉链头是金属圆环。如有拾到，请及时联系我，万分感谢！',
  },
  {
    icon: '🎧', name: 'AirPods 无线耳机', loc: '操场跑道', time: '2026-08-18',
    cat: '电子设备', catKey: 'electronics', status: 'find', campus: 'jjl',
    owner: '陈', ownerName: '陈同学', pub: '2026-08-19', campusName: '将军路校区', reward: 30,
    desc: '跑步时从口袋滑落，白色 AirPods 二代，充电盒背面有一道划痕。',
  },
  {
    icon: '🪪', name: '学生证（李某某）', loc: '食堂一楼', time: '2026-08-19',
    cat: '证件', catKey: 'documents', status: 'claim', campus: 'tmh',
    owner: '李', ownerName: '李同学', pub: '2026-08-19', campusName: '天目湖校区',
    desc: '在天目湖校区食堂一楼捡到一张学生证，已交至食堂服务台，请失主凭有效证件认领。',
  },
  {
    icon: '☂️', name: '蓝色折叠雨伞', loc: '教学楼 B 座', time: '2026-08-17',
    cat: '衣物', catKey: 'clothing', status: 'done', campus: 'mgg',
    owner: '周', ownerName: '周同学', pub: '2026-08-17', campusName: '明故宫校区',
    desc: '明故宫校区教学楼 B 座拾获一把蓝色折叠伞，伞柄是木质的，已完成交接。',
  },
  {
    icon: '🔑', name: '钥匙串（3 把钥匙）', loc: '体育馆更衣室', time: '2026-08-16',
    cat: '钥匙门禁', catKey: 'keys', status: 'find', campus: 'mgg',
    owner: '吴', ownerName: '吴同学', pub: '2026-08-16', campusName: '明故宫校区', reward: 20,
    desc: '体育馆更衣室捡到一串钥匙，共 3 把，挂着一个蓝色门禁卡套。',
  },
])

const msgs = ref<Msg[]>([
  { ico: '🙋', cls: 'ico-claim', title: '王同学 发起了认领申请', sub: '物品：黑色双肩背包（内含银色笔记本电脑）', time: '2 分钟前', unread: true, type: 'claim', chat: 'wang' },
  { ico: '✅', cls: 'ico-ok', title: '你的认领已通过', sub: '物品：学生证（李某某）· 对方已确认你的身份', time: '1 小时前', unread: true, type: 'claim' },
  { ico: '🤖', cls: 'ico-sys', title: 'AI 匹配到 1 条可能相关的拾获信息', sub: '你发布的「银色 U 盘」匹配到 1 条拾获信息，点击查看', time: '昨天 15:20', unread: false, type: 'sys' },
])

const convos: Record<ChatKey, Convo> = {
  wang: {
    name: '王同学', av: '王', verified: true,
    qs: [
      { q: '这个背包外侧有什么特征？', a: '有一处轻微磨损，拉链头是金属圆环' },
      { q: '包里的电脑是什么颜色？', a: '银色，上面贴了蓝色贴纸' },
    ],
    msgs: [
      { t: 'sys', c: '验证已通过，现在可以沟通取物地点' },
      { t: 'he', c: '东西还在我这儿，你方便的话我放图书馆一楼失物招领处' },
      { t: 'me', c: '好的！我下午两三点到，麻烦你了🙏' },
      { t: 'he', c: '没问题，我贴个便利贴写你名字' },
    ],
  },
  applied: {
    name: '林同学', av: '林', verified: false,
    qs: [
      { q: '这个背包外侧有什么特征？', a: '' },
      { q: '包里的电脑是什么颜色？', a: '' },
    ],
    msgs: [],
  },
}
// ===== 响应式状态 =====
const theme = ref('green')
const page = ref<'home' | 'detail' | 'msg' | 'publish'>('home')
const curCampus = ref('jjl')
const curCat = ref('all')
const chip = ref(0)
const searchText = ref('')

const currentDetail = ref<Item | null>(null)
const bigIcon = ref('🎒')
const thumbIcons = ['🎒', '💻', '🎧']
const activeThumb = ref(0)
const isFav = ref(false)

const maskShow = ref(false)
const reviewShow = ref(false)
const reviewApproved = ref(false)
const answer1 = ref('')
const answer2 = ref('')

const publishType = ref<'lost' | 'found'>('lost')
const descInput = ref('')
const rewardInput = ref('50')
const aiQuestions = ref<string[]>([])
const aiLoading = ref(false)

const chatShow = ref(false)
const curChat = ref<Convo | null>(null)
const chatInput = ref('')
const chatMsgsRef = ref<HTMLElement | null>(null)

const toastMsg = ref('')
const toastVisible = ref(false)
let toastTimer: ReturnType<typeof setTimeout> | undefined

// ===== 计算属性 =====
const filteredItems = computed(() =>
  items.value.filter(
    (it) =>
      (curCampus.value === 'all' || it.campus === curCampus.value) &&
      (curCat.value === 'all' || it.catKey === curCat.value),
  ),
)

const unreadCount = computed(() => msgs.value.filter((m) => m.unread).length)

const rewardValue = computed(() => {
  const raw = rewardInput.value.replace(/\D/g, '')
  return parseInt(raw || '0', 10)
})

const feeOf = (v?: number) => (v ? Math.round(v * FEE_RATE) : 0)
const netOf = (v?: number) => (v ? v - feeOf(v) : 0)

const claimBtnText = computed(() => {
  const s = currentDetail.value?.status
  return s === 'done' ? '已完成交接' : s === 'claim' ? '⏳ 认领中，等待确认' : '🔒 我要认领'
})

// ===== 方法 =====
function toast(msg: string) {
  toastMsg.value = msg
  toastVisible.value = true
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastVisible.value = false
  }, 2200)
}

function switchPage(p: 'home' | 'detail' | 'msg' | 'publish') {
  page.value = p
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// ===== 旧页面接口逻辑迁移：后端 Post -> 预览 Item 字段映射 =====
function mapPostToItem(p: Post): Item {
  return {
    id: p.id,
    images: (p.images || []).map((img) => img.url).filter(Boolean),
    icon: iconForCategory(p.category_l1),
    name: p.title || p.category_l2_label || p.category_l1_label || '未命名物品',
    loc: p.found_place?.name || p.found_region?.name || '未知地点',
    time: formatDate(p.event_start_at || p.published_at || p.created_at),
    cat: p.category_l2_label || p.category_l1_label || '其他',
    catKey: p.category_l1 || 'other',
    status: statusToPreview(p.status),
    campus: regionToCampus(p.found_region?.name),
    owner: '发',
    ownerName: '发布者',
    pub: formatDate(p.published_at || p.created_at),
    campusName: p.found_region?.name || '未知校区',
    desc: p.description || '暂无描述',
  }
}

function statusToPreview(status: string): Status {
  if (status === 'claiming') return 'claim'
  if (status === 'completed' || status === 'closed') return 'done'
  return 'find'
}

function iconForCategory(categoryL1: string): string {
  const map: Record<string, string> = {
    electronics: '📱',
    documents: '🪪',
    bags: '🎒',
    clothing: '👕',
    accessories: '⌚',
    stationery: '📚',
    keys: '🔑',
    other: '📦',
  }
  return map[categoryL1] || '📦'
}

function regionToCampus(regionName?: string): string {
  if (!regionName) return 'jjl'
  if (regionName.includes('天目湖') || regionName.includes('溧阳')) return 'tmh'
  if (regionName.includes('明故宫') || regionName.includes('秦淮')) return 'mgg'
  return 'jjl'
}

function formatDate(iso?: string | null): string {
  if (!iso) return '未知时间'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

// 迁移自旧 Home 页：列表查询 GET /posts（失败时保留内置演示数据）
async function fetchPosts() {
  try {
    const res = await getPosts({ page: 1, page_size: 50 })
    if (res.results.length) {
      items.value = res.results.map(mapPostToItem)
    }
  } catch (error) {
    console.error('获取帖子列表失败，使用内置演示数据：', error)
  }
}

onMounted(fetchPosts)

async function openDetail(it: Item) {
  currentDetail.value = it
  bigIcon.value = it.icon
  activeThumb.value = 0
  isFav.value = false
  switchPage('detail')

  // 迁移自旧 Detail 页：详情查询 GET /posts/{id}
  if (it.id != null) {
    try {
      const detail = await getPostDetail(it.id)
      currentDetail.value = mapPostToItem(detail)
    } catch (error) {
      console.error('获取详情失败：', error)
    }
  }
}

function pickThumb(i: number, icon: string) {
  activeThumb.value = i
  bigIcon.value = icon
}

function openClaimModal() {
  if (currentDetail.value?.status !== 'done') maskShow.value = true
}

function closeModal() {
  maskShow.value = false
  reviewShow.value = false
}

function toggleFav() {
  isFav.value = !isFav.value
  toast(isFav.value ? '收藏成功' : '已取消收藏')
}

function submitClaim() {
  if (!answer1.value.trim() || !answer2.value.trim()) {
    toast('请回答全部验证问题')
    return
  }
  closeModal()
  answer1.value = ''
  answer2.value = ''
  msgs.value.unshift({
    ico: '🙋',
    cls: 'ico-claim',
    title: '你 发起了认领申请',
    sub: '已提交验证答案，等待对方确认',
    time: '刚刚',
    unread: true,
    type: 'claim',
    chat: 'applied',
  })
  toast('已提交，等待发布者确认')
  setTimeout(() => toast('提示：可到「消息」页查看进度'), 2300)
}

function openReview(i: number) {
  const m = msgs.value[i]
  if (!m) return
  if (m.unread) m.unread = false
  if (m.type === 'sys') {
    toast('系统通知：暂无更多详情')
    return
  }
  if (m.chat) {
    openChat(m.chat)
    return
  }
  reviewApproved.value = false
  reviewShow.value = true
}

function approveClaim() {
  reviewApproved.value = true
  toast('已通过，双方联系方式互相可见')
}

function rejectClaim() {
  closeModal()
  toast('已拒绝该认领申请')
}

function openChat(key: ChatKey) {
  curChat.value = JSON.parse(JSON.stringify(convos[key])) as Convo
  chatInput.value = ''
  chatShow.value = true
}

function closeChat() {
  chatShow.value = false
}

function submitVerify() {
  const chat = curChat.value
  if (!chat) return
  let ok = true
  chat.qs.forEach((q) => {
    const v = (q.a || '').trim()
    if (!v) ok = false
    q.a = v
  })
  if (!ok) {
    toast('请回答全部验证问题')
    return
  }
  chat.verified = true
  chat.msgs.push({ t: 'sys', c: '验证已通过，现在可以沟通取物地点' })
  toast('验证通过，对话已开启')
}

function sendChat() {
  const chat = curChat.value
  if (!chat) return
  const v = chatInput.value.trim()
  if (!v) return
  chat.msgs.push({ t: 'me', c: v })
  chatInput.value = ''
  nextTick(() => {
    const el = chatMsgsRef.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function setPublishType(t: 'lost' | 'found') {
  publishType.value = t
  if (t === 'found') rewardInput.value = ''
}

function aiGenQuestions() {
  const desc = descInput.value.trim()
  if (!desc) {
    toast('请先填写详细描述')
    return
  }
  aiLoading.value = true
  aiQuestions.value = []
  setTimeout(() => {
    const qs: string[] = []
    if (/黑|白|银|蓝|红|绿|灰|粉|金|紫|黄/.test(desc)) qs.push('这个物品的颜色是什么？')
    if (/磨损|划痕|贴纸|破损|裂纹|污渍|掉了|缺/.test(desc)) qs.push('物品上有什么明显磨损或标记？')
    if (/内|里面|装有|含|放有|装着/.test(desc)) qs.push('物品内部装有什么？')
    if (/把|个|张|副|串|条|台|支|只/.test(desc)) qs.push('丢失的物品具体数量是多少？')
    if (/牌|型号|品牌|MacBook|iPad|AirPods|华为|小米|苹果/.test(desc)) qs.push('物品的品牌或型号是什么？')
    qs.push('你最后一次见到它是在什么位置？')
    aiQuestions.value = qs.slice(0, 3)
    aiLoading.value = false
    toast('AI 已根据描述生成 ' + aiQuestions.value.length + ' 个验证问题')
  }, 700)
}

function delQuestion(i: number) {
  aiQuestions.value.splice(i, 1)
}
</script>

<style scoped>
.preview{
  --bg:#F5F6F7;
  --card:#FFFFFF;
  --text-1:#1D2129;
  --text-2:#4E5969;
  --text-3:#86909C;
  --text-4:#C9CDD4;
  --border:#E5E6EB;
  --border-light:#F2F3F5;
  --radius:12px;
  --shadow:0 2px 8px rgba(0,0,0,.06);
  --shadow-hover:0 6px 20px rgba(0,0,0,.10);
  font-family:system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
  background:#EDEFF2;color:var(--text-1);line-height:1.6;padding:0 0 48px;
}

/* 方案A 青绿（推荐） */
.preview[data-theme="green"]{
  --brand:#00A870;
  --brand-dark:#00915F;
  --brand-light:#E8F8F2;
  --brand-text:#FFFFFF;
  --done:#1677FF;
  --done-bg:#E8F3FF;
}
/* 方案B 信任蓝 */
.preview[data-theme="blue"]{
  --brand:#1677FF;
  --brand-dark:#0E5FD8;
  --brand-light:#E8F3FF;
  --brand-text:#FFFFFF;
  --done:#00B42A;
  --done-bg:#E8FFEA;
}
/* 方案C 暖橙 */
.preview[data-theme="orange"]{
  --brand:#FF6B35;
  --brand-dark:#E85A28;
  --brand-light:#FFF3EC;
  --brand-text:#FFFFFF;
  --done:#00B42A;
  --done-bg:#E8FFEA;
}

.preview *{margin:0;padding:0;box-sizing:border-box;}

/* 顶部工具条 */
.toolbar{
  background:#fff;border-bottom:1px solid var(--border);
  padding:12px 20px;display:flex;align-items:center;gap:20px;
  flex-wrap:wrap;position:sticky;top:0;z-index:50;
}
.toolbar .group{display:flex;align-items:center;gap:8px;}
.toolbar .lbl{font-size:12px;color:var(--text-3);}
.tbtn{
  height:30px;padding:0 14px;border-radius:6px;border:1px solid var(--border);
  background:#fff;font-size:13px;color:var(--text-2);cursor:pointer;transition:all .2s;
}
.tbtn:hover{border-color:var(--brand);color:var(--brand);}
.tbtn.on{background:var(--brand);border-color:var(--brand);color:#fff;font-weight:500;}
.tbtn .rec{font-size:11px;opacity:.85;}

/* 站点头部 */
.site-head{background:#fff;padding:18px 0;border-bottom:1px solid var(--border-light);}
.site-head .inner{max-width:1080px;margin:0 auto;padding:0 20px;display:flex;align-items:center;gap:20px;}
.logo{display:flex;align-items:center;gap:10px;font-size:20px;font-weight:600;flex-shrink:0;}
.logo .mark{
  width:34px;height:34px;border-radius:9px;background:var(--brand);color:#fff;
  display:flex;align-items:center;justify-content:center;font-size:17px;font-weight:700;
  transition:background .2s;
}
.search{flex:1;display:flex;max-width:440px;}
.search input{
  flex:1;height:40px;padding:0 14px;border:1px solid var(--border);border-right:none;
  border-radius:8px 0 0 8px;font-size:14px;outline:none;transition:border-color .2s;
}
.search input:focus{border-color:var(--brand);}
.search button{
  height:40px;padding:0 22px;background:var(--brand);color:var(--brand-text);
  border:none;border-radius:0 8px 8px 0;font-size:14px;cursor:pointer;transition:background .2s;
}
.search button:hover{background:var(--brand-dark);}
.btn-pub{
  height:40px;padding:0 18px;border-radius:8px;border:1px solid var(--brand);
  background:#fff;color:var(--brand);font-size:14px;font-weight:500;cursor:pointer;transition:all .2s;
}
.btn-pub:hover{background:var(--brand-light);}
.btn-msg{
  position:relative;height:40px;width:40px;border-radius:8px;border:1px solid var(--border);
  background:#fff;font-size:17px;cursor:pointer;transition:border-color .2s;
}
.btn-msg:hover{border-color:var(--brand);}
.btn-msg .badge{
  position:absolute;top:-5px;right:-5px;min-width:17px;height:17px;padding:0 4px;
  background:#F53F3F;color:#fff;border-radius:9px;font-size:11px;line-height:17px;
  text-align:center;font-weight:600;border:2px solid #fff;
}
/* 主体布局 */
.main{max-width:1080px;margin:20px auto 0;padding:0 20px;display:flex;gap:20px;}
.side{
  width:168px;flex-shrink:0;background:#fff;border-radius:var(--radius);
  padding:12px;height:fit-content;box-shadow:var(--shadow);
}
.side .t{
  font-size:13px;font-weight:600;color:var(--text-1);padding:6px 10px 10px;
  display:flex;align-items:center;gap:6px;
}
.side .t .step{
  width:17px;height:17px;border-radius:50%;background:var(--brand);color:#fff;
  font-size:11px;display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.side .it{
  padding:9px 10px;border-radius:6px;font-size:13px;color:var(--text-2);
  cursor:pointer;transition:all .2s;
}
.side .it:hover{background:var(--border-light);}
.side .it.on{background:var(--brand-light);color:var(--brand);font-weight:500;}

.content{flex:1;min-width:0;}

/* 校区选择 */
.campus-bar{
  background:#fff;border-radius:var(--radius);padding:14px;margin-bottom:14px;box-shadow:var(--shadow);
}
.campus-bar .cap{
  font-size:13px;font-weight:600;margin-bottom:10px;display:flex;align-items:center;gap:6px;
}
.campus-bar .cap .step{
  width:17px;height:17px;border-radius:50%;background:var(--brand);color:#fff;
  font-size:11px;display:flex;align-items:center;justify-content:center;flex-shrink:0;
}
.campus-row{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;}
.campus{
  padding:12px 14px;border:1.5px solid var(--border);border-radius:10px;
  cursor:pointer;transition:all .2s;background:#fff;
}
.campus:hover{border-color:var(--brand);}
.campus.on{border-color:var(--brand);background:var(--brand-light);}
.campus .cn{font-size:14px;font-weight:600;margin-bottom:2px;}
.campus.on .cn{color:var(--brand);}
.campus .cs{font-size:12px;color:var(--text-3);}

.filter-bar{
  background:#fff;border-radius:var(--radius);padding:10px 14px;margin-bottom:14px;
  display:flex;align-items:center;gap:10px;box-shadow:var(--shadow);font-size:13px;
}
.chip{
  padding:5px 12px;border-radius:14px;background:var(--border-light);
  color:var(--text-2);cursor:pointer;transition:all .2s;
}
.chip:hover{background:var(--brand-light);color:var(--brand);}
.chip.on{background:var(--brand);color:#fff;}
.count{margin-left:auto;color:var(--text-3);font-size:12px;}

.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px;}
.card{
  background:#fff;border-radius:var(--radius);overflow:hidden;cursor:pointer;
  box-shadow:var(--shadow);transition:all .25s;
}
.card:hover{box-shadow:var(--shadow-hover);transform:translateY(-3px);}
.card .img{
  height:140px;display:flex;align-items:center;justify-content:center;
  font-size:38px;background:linear-gradient(135deg,#F7F9FB,#EDF1F5);
}
.card .body{padding:12px;}
.card .name{
  font-size:15px;font-weight:500;margin-bottom:7px;
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.card .meta{font-size:12px;color:var(--text-3);display:flex;gap:4px;margin-bottom:3px;}
.card .foot{display:flex;align-items:center;justify-content:space-between;margin-top:10px;}

.tag{
  display:inline-flex;align-items:center;gap:5px;padding:3px 9px;
  border-radius:4px;font-size:12px;font-weight:500;
}
.tag .dot{width:6px;height:6px;border-radius:50%;background:currentColor;}
.tag-find{background:#FFF7E8;color:#FF7D00;}
.tag-claim{background:var(--brand-light);color:var(--brand);}
.tag-done{background:var(--done-bg);color:var(--done);}
.cat{font-size:12px;color:var(--text-3);}
/* 详情页 */
.detail{background:#fff;border-radius:16px;padding:24px;box-shadow:var(--shadow);display:flex;gap:28px;}
.gallery{flex:0 0 400px;}
.big-img{
  height:400px;border-radius:12px;background:linear-gradient(135deg,#F7F9FB,#EDF1F5);
  display:flex;align-items:center;justify-content:center;font-size:96px;position:relative;
}
.big-img .tag{position:absolute;top:14px;left:14px;}
.thumbs{display:flex;gap:10px;margin-top:12px;}
.thumb{
  width:70px;height:70px;border-radius:8px;background:linear-gradient(135deg,#F7F9FB,#EDF1F5);
  display:flex;align-items:center;justify-content:center;font-size:24px;
  cursor:pointer;border:2px solid transparent;transition:border-color .2s;
}
.thumb.on{border-color:var(--brand);}
.big-img img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;border-radius:12px;}
.thumb img{width:100%;height:100%;object-fit:cover;border-radius:8px;display:block;}
.info{flex:1;min-width:0;display:flex;flex-direction:column;}
.info h1{font-size:23px;font-weight:600;line-height:1.4;margin-bottom:12px;}
.metas{background:#FAFBFC;border-radius:10px;padding:14px 16px;display:flex;flex-direction:column;gap:11px;}
.mrow{display:flex;align-items:center;font-size:14px;}
.mrow .k{color:var(--text-3);width:72px;flex-shrink:0;}
.mrow .v{font-weight:500;}
.owner{display:flex;align-items:center;gap:10px;margin:18px 0;}
.avatar{
  width:36px;height:36px;border-radius:50%;background:var(--brand-light);color:var(--brand);
  display:flex;align-items:center;justify-content:center;font-weight:600;
}
.oname{font-size:14px;font-weight:500;}
.otime{font-size:12px;color:var(--text-3);}
.acts{display:flex;gap:12px;}
.btn{
  height:44px;padding:0 24px;border-radius:8px;font-size:15px;font-weight:500;
  border:1px solid transparent;cursor:pointer;transition:all .2s;
}
.btn-main{background:var(--brand);color:var(--brand-text);flex:1;}
.btn-main:hover{background:var(--brand-dark);}
.btn-sec{background:#fff;border-color:var(--border);color:var(--text-1);}
.btn-sec:hover{border-color:var(--brand);color:var(--brand);}
.btn-sec.fav{color:var(--brand);border-color:var(--brand);background:var(--brand-light);}
.btn-danger{background:#fff;border-color:#F53F3F;color:#F53F3F;}
.btn-danger:hover{background:#F53F3F;color:#fff;}
.safety{
  display:flex;align-items:center;gap:6px;margin-top:16px;
  font-size:12px;color:var(--text-3);
}
.desc{
  background:#fff;border-radius:16px;padding:22px 24px;margin-top:16px;box-shadow:var(--shadow);
}
.desc h2{font-size:17px;font-weight:600;margin-bottom:12px;padding-left:10px;border-left:4px solid var(--brand);}
.desc p{font-size:14px;line-height:1.85;color:var(--text-2);white-space:pre-line;}
.back{
  display:inline-flex;align-items:center;gap:6px;margin-bottom:14px;
  font-size:13px;color:var(--text-3);cursor:pointer;transition:color .2s;
}
.back:hover{color:var(--brand);}
/* 消息页 */
.msg-wrap{max-width:760px;margin:0 auto;background:#fff;border-radius:16px;overflow:hidden;box-shadow:var(--shadow);}
.msg-head{padding:18px 22px;border-bottom:1px solid var(--border-light);display:flex;align-items:center;gap:10px;}
.msg-head h2{font-size:17px;font-weight:600;}
.msg-head .n{font-size:12px;color:var(--text-3);}
.msg-tabs{display:flex;gap:6px;padding:12px 22px;border-bottom:1px solid var(--border-light);}
.msg-tabs .mt{
  padding:6px 14px;border-radius:14px;font-size:13px;color:var(--text-2);
  cursor:pointer;transition:all .2s;
}
.msg-tabs .mt:hover{background:var(--border-light);}
.msg-tabs .mt.on{background:var(--brand-light);color:var(--brand);font-weight:500;}
.msg-item{
  display:flex;gap:14px;padding:16px 22px;border-bottom:1px solid var(--border-light);
  cursor:pointer;transition:background .2s;
}
.msg-item:hover{background:#FAFBFC;}
.msg-item.unread{background:var(--brand-light);}
.msg-item.unread:hover{background:var(--brand-light);filter:brightness(.98);}
.msg-ico{
  width:42px;height:42px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:19px;
}
.ico-claim{background:var(--brand-light);}
.ico-ok{background:#E8FFEA;}
.ico-sys{background:#E8F3FF;}
.msg-body{flex:1;min-width:0;}
.msg-top{display:flex;align-items:center;gap:8px;margin-bottom:3px;}
.msg-title{font-size:14px;font-weight:600;}
.msg-time{font-size:12px;color:var(--text-3);margin-left:auto;flex-shrink:0;}
.msg-sub{
  font-size:13px;color:var(--text-2);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.msg-item .red{width:8px;height:8px;border-radius:50%;background:#F53F3F;flex-shrink:0;align-self:center;}

/* 弹窗 */
.mask{
  position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;
  align-items:center;justify-content:center;z-index:100;padding:20px;
}
.mask.show{display:flex;}
.modal{
  background:#fff;border-radius:16px;width:100%;max-width:430px;
  overflow:hidden;box-shadow:0 12px 40px rgba(0,0,0,.2);
}
.modal .head{
  padding:16px 20px;border-bottom:1px solid var(--border-light);
  font-size:16px;font-weight:600;display:flex;align-items:center;gap:8px;
}
.modal .body{padding:20px;max-height:60vh;overflow-y:auto;}
.tip{font-size:13px;color:var(--text-3);line-height:1.7;margin-bottom:16px;}
.qa{margin-bottom:15px;}
.qa .q{font-size:14px;font-weight:500;margin-bottom:7px;display:flex;gap:7px;}
.qa .q .n{color:var(--brand);}
.qa input{
  width:100%;height:38px;padding:0 12px;border:1px solid var(--border);
  border-radius:8px;font-size:14px;outline:none;transition:border-color .2s;
}
.qa input:focus{border-color:var(--brand);}
.modal .foot{
  padding:12px 20px;background:var(--border-light);
  display:flex;justify-content:flex-end;gap:10px;
}
.modal .foot .btn{height:36px;padding:0 18px;font-size:14px;flex:none;}

/* 认领审核内容 */
.review-item{background:#FAFBFC;border-radius:8px;padding:12px 14px;margin-bottom:10px;}
.review-item .rq{font-size:13px;color:var(--text-3);margin-bottom:4px;}
.review-item .ra{font-size:14px;font-weight:500;color:var(--text-1);}
.contact-box{
  background:var(--brand-light);border-radius:10px;padding:14px;margin-top:6px;
}
.contact-box .ct{font-size:13px;font-weight:600;margin-bottom:10px;color:var(--brand);}
.crow{display:flex;align-items:center;gap:10px;padding:7px 0;font-size:14px;}
.crow .cl{color:var(--text-3);width:40px;flex-shrink:0;}
.crow .cv{flex:1;font-weight:500;}

.toast{
  position:fixed;bottom:40px;left:50%;transform:translateX(-50%) translateY(80px);
  background:var(--text-1);color:#fff;padding:12px 24px;border-radius:8px;
  font-size:14px;z-index:200;opacity:0;transition:all .3s;
}
.toast.show{transform:translateX(-50%) translateY(0);opacity:1;}

/* 赏金横幅（详情页） */
.reward-banner{
  display:flex;align-items:center;gap:14px;margin-top:14px;
  background:linear-gradient(135deg,#FFF7E8,#FFEFC7);
  border:1px solid #FFD591;border-radius:12px;padding:12px 16px;
}
.reward-banner .rm{font-size:28px;font-weight:700;color:#D4380D;line-height:1;}
.reward-banner .rt{font-size:13px;color:#874D00;font-weight:500;margin-bottom:3px;}
.reward-banner .rd{font-size:12px;color:#874D00;}
/* 发布页（赏金设置） */
.pub{padding:20px 0;}
.pub-card{background:#fff;border-radius:16px;padding:24px;box-shadow:var(--shadow);max-width:640px;margin:0 auto;}
.pub-card h2{font-size:18px;font-weight:600;margin-bottom:4px;}
.pub-card .sub{font-size:13px;color:var(--text-3);margin-bottom:20px;}
.field{margin-bottom:18px;}
.field label{display:block;font-size:14px;font-weight:500;margin-bottom:8px;}
.field .req{color:#F53F3F;margin-left:2px;}
.field input[type=text], .field textarea, .field select{
  width:100%;padding:10px 12px;border:1px solid var(--border);border-radius:8px;
  font-size:14px;outline:none;transition:border-color .2s;font-family:inherit;
}
.field input:focus, .field textarea:focus, .field select:focus{border-color:var(--brand);}
.field textarea{resize:vertical;min-height:80px;}
.radio-row{display:flex;gap:10px;}
.radio-row .r{
  flex:1;padding:11px;border:1.5px solid var(--border);border-radius:10px;
  text-align:center;cursor:pointer;font-size:13px;transition:all .2s;
}
.radio-row .r.on{border-color:var(--brand);background:var(--brand-light);color:var(--brand);font-weight:500;}
.fee-box{background:#FAFBFC;border:1px dashed var(--border);border-radius:10px;padding:14px 16px;margin-top:8px;}
.fee-row{display:flex;justify-content:space-between;font-size:13px;padding:5px 0;color:var(--text-2);}
.fee-row.total{border-top:1px solid var(--border);margin-top:6px;padding-top:10px;font-weight:600;color:var(--text-1);}
.fee-row .hl{color:#D4380D;font-weight:600;}
.fee-note{font-size:12px;color:var(--text-3);margin-top:8px;line-height:1.6;}
.fee-note b{color:#D4380D;}
.fee-row.total .hl2{color:var(--brand);font-weight:700;}

/* AI 智能匹配置顶消息 */
.pinned{
  display:flex;align-items:flex-start;gap:12px;padding:14px 22px;cursor:pointer;
  background:linear-gradient(135deg,#E8F3FF,#F4F8FF);
  border-bottom:1px solid var(--border-light);position:relative;transition:filter .2s;
}
.pinned:hover{filter:brightness(.98);}
.pin-tag{
  position:absolute;top:10px;right:14px;font-size:11px;color:#1677FF;
  background:#fff;border:1px solid #BEDAFF;border-radius:4px;padding:1px 6px;
}
.pin-ico{
  width:38px;height:38px;border-radius:50%;background:#fff;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:18px;border:1px solid #BEDAFF;
}
.pin-title{font-size:14px;font-weight:600;color:#0E42D2;display:flex;align-items:center;gap:6px;}
.pin-sub{font-size:12px;color:var(--text-2);line-height:1.65;margin-top:3px;}

/* AI 生成验证问题 */
.ai-sec{background:#FAFBFC;border:1px dashed var(--border);border-radius:10px;padding:14px 16px;margin-bottom:18px;}
.ai-sec .ah{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
.ai-sec .ah .at{font-size:14px;font-weight:500;}
.ai-sec .ah .ab{
  margin-left:auto;height:32px;padding:0 14px;border:none;border-radius:8px;
  background:var(--brand);color:#fff;font-size:13px;cursor:pointer;transition:background .2s;
}
.ai-sec .ah .ab:hover{background:var(--brand-dark);}
.ai-sec .ad{font-size:12px;color:var(--text-3);margin-bottom:10px;line-height:1.6;}
.q-list{display:flex;flex-direction:column;gap:8px;}
.q-item{
  display:flex;align-items:center;gap:9px;background:#fff;border:1px solid var(--border);
  border-radius:8px;padding:9px 12px;font-size:13px;
}
.q-item .qn{color:var(--brand);font-weight:600;flex-shrink:0;}
.q-item .qx{margin-left:auto;color:var(--text-4);cursor:pointer;font-size:15px;line-height:1;padding:0 2px;}
.q-item .qx:hover{color:#F53F3F;}
.q-empty{font-size:13px;color:var(--text-3);text-align:center;padding:8px 0;}
.ai-loading{font-size:13px;color:var(--text-3);text-align:center;padding:10px 0;}
/* 聊天抽屉 */
.chat-mask{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:120;display:none;align-items:flex-end;justify-content:center;}
.chat-mask.show{display:flex;}
.chat{
  width:100%;max-width:480px;height:80vh;background:#F5F6F7;border-radius:16px 16px 0 0;
  display:flex;flex-direction:column;overflow:hidden;box-shadow:0 -8px 40px rgba(0,0,0,.18);animation:slideUp .25s ease;
}
@keyframes slideUp{from{transform:translateY(40px);opacity:.6}to{transform:translateY(0);opacity:1}}
.chat-head{background:#fff;padding:14px 18px;border-bottom:1px solid var(--border-light);display:flex;align-items:center;gap:10px;flex-shrink:0;}
.chat-head .av{width:34px;height:34px;border-radius:50%;background:var(--brand-light);color:var(--brand);display:flex;align-items:center;justify-content:center;font-weight:600;}
.chat-head .nm{font-size:15px;font-weight:600;}
.chat-head .st{font-size:12px;color:var(--text-3);}
.chat-head .x{margin-left:auto;font-size:22px;color:var(--text-3);cursor:pointer;line-height:1;padding:0 4px;}
.verify-block{background:#fff;border-bottom:1px solid var(--border-light);padding:14px 18px;flex-shrink:0;}
.verify-block .vh{font-size:13px;font-weight:600;color:var(--brand);margin-bottom:10px;display:flex;align-items:center;gap:6px;}
.vq{background:#FAFBFC;border-radius:8px;padding:9px 12px;margin-bottom:8px;font-size:13px;}
.vq .q{color:var(--text-3);margin-bottom:3px;}
.vq .a{font-weight:500;color:var(--text-1);}
.vq input{width:100%;height:34px;padding:0 10px;border:1px solid var(--border);border-radius:6px;font-size:13px;outline:none;margin-top:5px;}
.vq input:focus{border-color:var(--brand);}
.verify-block .vt{font-size:12px;color:#00B42A;margin-top:4px;display:flex;align-items:center;gap:4px;}
.verify-block .vbtn{width:100%;height:36px;margin-top:10px;font-size:14px;border:none;border-radius:8px;background:var(--brand);color:#fff;cursor:pointer;}
.chat-msgs{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:12px;}
.bubble{max-width:74%;padding:9px 13px;border-radius:12px;font-size:14px;line-height:1.5;word-break:break-word;}
.bubble.me{align-self:flex-end;background:var(--brand);color:#fff;border-bottom-right-radius:3px;}
.bubble.he{align-self:flex-start;background:#fff;color:var(--text-1);border-bottom-left-radius:3px;box-shadow:var(--shadow);}
.bubble.sys{align-self:center;background:var(--border-light);color:var(--text-3);font-size:12px;padding:5px 12px;border-radius:10px;}
.chat-input{display:flex;gap:10px;padding:12px 14px;background:#fff;border-top:1px solid var(--border-light);flex-shrink:0;}
.chat-input input{flex:1;height:40px;padding:0 14px;border:1px solid var(--border);border-radius:20px;font-size:14px;outline:none;}
.chat-input input:focus{border-color:var(--brand);}
.chat-input input:disabled{background:#F2F3F5;cursor:not-allowed;}
.chat-input button{height:40px;padding:0 20px;border:none;border-radius:20px;background:var(--brand);color:#fff;font-size:14px;cursor:pointer;}
.chat-input button:disabled{background:var(--border);color:var(--text-3);cursor:not-allowed;}
</style>
