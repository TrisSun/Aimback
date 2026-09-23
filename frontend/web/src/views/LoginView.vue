<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ApiError } from '@/api/http'
import { useAuth } from '@/composables/useAuth'

const route = useRoute()
const router = useRouter()
const { login, requestCode } = useAuth()

const form = reactive({ phone: '', code: '' })
const loading = ref(false)
const sending = ref(false)
const hint = ref('')

const PHONE_RE = /^1[3-9]\d{9}$/

async function send() {
  if (!PHONE_RE.test(form.phone)) {
    ElMessage.warning('请输入 11 位手机号')
    return
  }
  sending.value = true
  try {
    const result = await requestCode(form.phone)
    hint.value = result.dev_code
      ? `开发模式验证码：${result.dev_code}`
      : '验证码已发送'
    ElMessage.success(hint.value)
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '发送失败')
  } finally {
    sending.value = false
  }
}

async function submit() {
  if (!PHONE_RE.test(form.phone) || !form.code) {
    ElMessage.warning('请填写手机号和验证码')
    return
  }
  loading.value = true
  try {
    await login(form.phone, form.code)
    ElMessage.success('登录成功')
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    await router.replace(redirect)
  } catch (error) {
    ElMessage.error(error instanceof ApiError ? error.message : '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login">
    <form class="panel" @submit.prevent="submit">
      <h1>手机号登录</h1>
      <p class="sub">验证码登录，新号码会自动注册</p>
      <label>
        手机号
        <input v-model="form.phone" maxlength="11" placeholder="11 位手机号" />
      </label>
      <label class="code-row">
        验证码
        <span class="code-fields">
          <input v-model="form.code" maxlength="6" placeholder="6 位验证码" />
          <button type="button" :disabled="sending" @click="send">获取验证码</button>
        </span>
      </label>
      <p v-if="hint" class="hint">{{ hint }}</p>
      <button class="submit" :disabled="loading">进入 Aimback</button>
      <RouterLink to="/" class="back">返回首页</RouterLink>
    </form>
  </div>
</template>

<style scoped>
.login {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: #f4f5f7;
}
.panel {
  width: min(420px, 92vw);
  background: #fff;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  gap: 14px;
}
h1 {
  margin: 0;
}
.sub,
.hint,
.back {
  color: #888;
  font-size: 13px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
}
input,
button {
  border-radius: 10px;
  border: 1px solid #e5e5e5;
  padding: 10px 12px;
  font-size: 14px;
}
.code-fields {
  display: flex;
  gap: 8px;
}
.code-fields input {
  flex: 1;
}
.submit,
.code-fields button {
  background: #ff6b35;
  color: #fff;
  border: 0;
  cursor: pointer;
}
.back {
  text-align: center;
}
</style>
