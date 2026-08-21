  <template>
    <div class="page">
      <div class="form-card">
        <div class="header">
          <h1>失物招领 · 发布信息</h1>
          <p>捡到或丢失了东西？填一下，说不定马上就能找到</p>
        </div>

        <el-form
          :model="form"
          label-position="top"
          class="form"
        >
          <!-- 类型切换 -->
          <div class="type-switch">
            <div
              class="type-btn"
              :class="{ active: form.type === 'lost' }"
              @click="form.type = 'lost'"
            >
              我丢了东西
            </div>
            <div
              class="type-btn"
              :class="{ active: form.type === 'found' }"
              @click="form.type = 'found'"
            >
              我捡到了东西
            </div>
          </div>

          <el-form-item label="物品名称">
            <el-input
              v-model="form.name"
              placeholder="比如：黑色钱包、校园卡、雨伞…"
              size="large"
            />
          </el-form-item>

          <el-form-item label="分类">
            <el-select
              v-model="form.category"
              placeholder="请选择分类"
              size="large"
              class="full-width"
            >
              <el-option label="证件" value="证件" />
              <el-option label="钱包" value="钱包" />
              <el-option label="电子产品" value="电子产品" />
              <el-option label="钥匙" value="钥匙" />
              <el-option label="衣物" value="衣物" />
              <el-option label="其他" value="其他" />
            </el-select>
          </el-form-item>

          <el-form-item label="详细描述">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="4"
              placeholder="描述一下物品的外观、特征、丢失/捡到的具体时间地点…"
            />
          </el-form-item>

          <div class="row">
            <el-form-item label="地点">
              <el-input
                v-model="form.location"
                placeholder="比如：图书馆三楼"
                size="large"
              />
            </el-form-item>
            <el-form-item label="时间">
              <el-date-picker
                v-model="form.date"
                type="date"
                placeholder="选择日期"
                size="large"
                class="full-width"
              />
            </el-form-item>
          </div>

          <el-form-item label="联系方式">
            <el-input
              v-model="form.contact"
              placeholder="手机号 / 微信 / QQ"
              size="large"
            />
          </el-form-item>

          <el-form-item>
            <div class="actions">
              <el-button type="primary" size="large" @click="submit">
                发布信息
              </el-button>
              <el-button size="large" @click="reset">重置</el-button>
            </div>
          </el-form-item>
        </el-form>
      </div>
    </div>
  </template>

  <script setup>
  import { reactive } from 'vue'
  import { ElMessage } from 'element-plus'

  const form = reactive({
    type: 'lost',
    name: '',
    category: '',
    description: '',
    location: '',
    date: '',
    contact: '',
  })

  function submit() {
    if (!form.name || !form.category || !form.contact) {
      ElMessage.warning('请至少填写物品名称、分类和联系方式')
      return
    }
    ElMessage.success('发布成功！')
    console.log('提交的数据：', form)
  }

  function reset() {
    Object.assign(form, {
      type: 'lost',
      name: '',
      category: '',
      description: '',
      location: '',
      date: '',
      contact: '',
    })
  }
  </script>

  <style scoped>
  * {
    box-sizing: border-box;
  }

  .page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }

  .form-card {
    width: 100%;
    max-width: 560px;
    background: #fff;
    border-radius: 16px;
    padding: 40px 44px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  }

  .header {
    text-align: center;
    margin-bottom: 28px;
  }

  .header h1 {
    margin: 0;
    font-size: 24px;
    color: #2c3e50;
  }

  .header p {
    margin: 8px 0 0;
    color: #909399;
    font-size: 14px;
  }

  .type-switch {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
  }

  .type-btn {
    flex: 1;
    text-align: center;
    padding: 14px 0;
    border-radius: 10px;
    cursor: pointer;
    color: #606266;
    background: #f4f4f5;
    font-size: 15px;
    transition: all 0.2s;
    user-select: none;
  }

  .type-btn.active {
    background: #409eff;
    color: #fff;
    font-weight: 600;
  }

  .form {
    width: 100%;
  }

  .row {
    display: flex;
    gap: 16px;
  }

  .row .el-form-item {
    flex: 1;
  }

  .full-width {
    width: 100%;
  }

  .actions {
    display: flex;
    gap: 12px;
    width: 100%;
  }

  .actions .el-button {
    flex: 1;
  }

  @media (max-width: 600px) {
    .row {
      flex-direction: column;
      gap: 0;
    }
  }
  </style>