<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <h2>失物招领系统</h2>
        <p>使用手机号验证码登录</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        size="large"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="phone">
          <el-input
            v-model="form.phone"
            placeholder="请输入手机号"
            :prefix-icon="Iphone"
            maxlength="11"
            clearable
          />
        </el-form-item>

        <el-form-item prop="code">
          <div class="code-row">
            <el-input
              v-model="form.code"
              placeholder="请输入验证码"
              :prefix-icon="Message"
              maxlength="6"
              clearable
            />
            <el-button
              class="code-btn"
              :disabled="countdown > 0 || sending"
              @click="handleSendCode"
            >
              {{ countdown > 0 ? countdown + 's 后重发' : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <p class="login-tip">未注册的手机号验证后将自动创建账号</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { Iphone, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { sendCode, loginByCode } from '@/api/auth'

const router = useRouter()
const route = useRoute()
const formRef = ref<FormInstance>()
const loading = ref(false)
const sending = ref(false)
const countdown = ref(0)
let timer: ReturnType<typeof setInterval> | undefined

const form = reactive({
  phone: '',
  code: '',
})

const rules: FormRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' },
  ],
  code: [
    { required: true, message: '请输入验证码', trigger: 'blur' },
    { pattern: /^\d{6}$/, message: '验证码为 6 位数字', trigger: 'blur' },
  ],
}

const handleSendCode = async () => {
  if (!/^1[3-9]\d{9}$/.test(form.phone)) {
    ElMessage.warning('请先输入正确的手机号')
    return
  }
  sending.value = true
  try {
    const res = await sendCode(form.phone)
    ElMessage.success(res.dev_code ? `验证码已发送（联调码：${res.dev_code}）` : '验证码已发送')
    startCountdown()
  } catch (error) {
    // 错误提示已由 request.ts 拦截器统一处理
  } finally {
    sending.value = false
  }
}

const startCountdown = () => {
  countdown.value = 60
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    countdown.value -= 1
    if (countdown.value <= 0 && timer) {
      clearInterval(timer)
      timer = undefined
    }
  }, 1000)
}

const handleLogin = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    loading.value = true
    try {
      await loginByCode(form.phone, form.code)
      ElMessage.success('登录成功')
      router.push((route.query.redirect as string) || '/')
    } catch (error) {
      // 错误提示已由拦截器统一处理
    } finally {
      loading.value = false
    }
  })
}

onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #EDEFF2;
  padding: 16px;
  /* 与主页面一致的主题色（品牌绿） */
  --el-color-primary: #00A870;
  --el-color-primary-light-3: #33bd97;
  --el-color-primary-light-5: #66d0b4;
  --el-color-primary-light-7: #99e0cd;
  --el-color-primary-light-8: #b3e8db;
  --el-color-primary-light-9: #e6f7f1;
  --el-color-primary-dark-2: #00915f;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 12px;
  padding: 40px 36px 32px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.login-header {
  text-align: center;
  margin-bottom: 28px;
}

.login-header h2 {
  margin: 0 0 8px;
  color: #1D2129;
  font-size: 24px;
}

.login-header p {
  margin: 0;
  color: #86909C;
  font-size: 14px;
}

.code-row {
  display: flex;
  gap: 8px;
  width: 100%;
}

.code-row .el-input {
  flex: 1;
}

.code-btn {
  flex-shrink: 0;
  width: 120px;
  color: #00A870;
  border-color: #00A870;
}

.code-btn:hover,
.code-btn:focus {
  color: #00915F;
  border-color: #00915F;
  background: #E8F8F2;
}

.login-btn {
  width: 100%;
}

.login-tip {
  text-align: center;
  color: #86909C;
  font-size: 12px;
  margin: 4px 0 0;
}
</style>
