 <template>
    <div class="login-page">
      <div class="login-card">
        <div class="login-header">
          <h2>失物招领系统</h2>
          <p>欢迎回来，请登录您的账号</p>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          size="large"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              :prefix-icon="Lock"
              show-password
              clearable
            />
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

        <div class="login-footer">
          <el-link type="primary" :underline="false">忘记密码？</el-link>
          <span class="divider">|</span>
          <el-link type="primary" :underline="false">立即注册</el-link>
        </div>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { reactive, ref } from 'vue'
  import type { FormInstance, FormRules } from 'element-plus'
  import { User, Lock } from '@element-plus/icons-vue'
  import { ElMessage } from 'element-plus'

  const formRef = ref<FormInstance>()
  const loading = ref(false)

  const form = reactive({
    username: '',
    password: '',
  })

  const rules: FormRules = {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
    ],
    password: [
      { required: true, message: '请输入密码', trigger: 'blur' },
      { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' },
    ],
  }

  const handleLogin = async () => {
    if (!formRef.value) return

    await formRef.value.validate(async (valid) => {
      if (!valid) return

      loading.value = true
      try {
        // TODO: 这里调用真实登录接口
        await new Promise((r) => setTimeout(r, 1000))
        ElMessage.success('登录成功')
      } catch (error) {
        ElMessage.error('登录失败，请稍后重试')
      } finally {
        loading.value = false
      }
    })
  }
  </script>

  <style scoped>
  .login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 16px;
  }

  .login-card {
    width: 100%;
    max-width: 400px;
    background: #fff;
    border-radius: 12px;
    padding: 40px 36px 32px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.18);
  }

  .login-header {
    text-align: center;
    margin-bottom: 28px;
  }

  .login-header h2 {
    margin: 0 0 8px;
    color: #303133;
    font-size: 24px;
  }

  .login-header p {
    margin: 0;
    color: #909399;
    font-size: 14px;
  }

  .login-btn {
    width: 100%;
  }

  .login-footer {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
  }

  .divider {
    color: #dcdfe6;
  }
  </style>