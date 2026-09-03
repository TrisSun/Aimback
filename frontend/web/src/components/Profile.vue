<template>
  <div class="profile-page">
    <div class="profile-card">
      <div class="profile-head">
        <h2>个人中心</h2>
        <el-link type="primary" :underline="false" @click="goBack">← 返回首页</el-link>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-width="88px" size="large">
        <el-form-item label="手机号">
          <el-input :model-value="form.phone" disabled />
        </el-form-item>

        <el-form-item label="头像">
          <el-input v-model="form.avatar" placeholder="请输入头像图片 URL" clearable />
        </el-form-item>

        <el-form-item label="昵称" prop="nickname">
          <el-input v-model="form.nickname" placeholder="请输入昵称" maxlength="32" clearable />
        </el-form-item>

        <el-form-item label="联系方式" prop="contact">
          <el-input v-model="form.contact" placeholder="微信号 / 其他联系方式" maxlength="64" clearable />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存修改</el-button>
          <el-button @click="handleLogout">退出登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'
import { getProfile, updateProfile } from '@/api/auth'

const router = useRouter()
const formRef = ref<FormInstance>()
const saving = ref(false)

const form = reactive({
  phone: '',
  nickname: '',
  avatar: '',
  contact: '',
})

const rules: FormRules = {
  nickname: [{ max: 32, message: '昵称最多 32 个字符', trigger: 'blur' }],
  contact: [{ max: 64, message: '联系方式最多 64 个字符', trigger: 'blur' }],
}

const loadProfile = async () => {
  try {
    const p = await getProfile()
    form.phone = p.username || ''
    form.nickname = p.nickname || ''
    form.avatar = p.avatar || ''
  } catch (error) {
    // 401 已由 request.ts 拦截器跳转 /login
    console.error('获取个人信息失败：', error)
  }
}

const handleSave = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      await updateProfile({
        nickname: form.nickname,
        avatar: form.avatar,
        contact: form.contact,
      })
      ElMessage.success('保存成功')
    } catch (error) {
      // 错误提示已由拦截器统一处理
    } finally {
      saving.value = false
    }
  })
}

const handleLogout = () => {
  localStorage.removeItem('token')
  ElMessage.success('已退出登录')
  router.push('/login')
}

const goBack = () => router.push('/')

onMounted(loadProfile)
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: #f5f6f7;
  padding: 24px 16px;
}

.profile-card {
  max-width: 560px;
  margin: 0 auto;
  background: #fff;
  border-radius: 12px;
  padding: 28px 28px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.profile-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.profile-head h2 {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}
</style>
