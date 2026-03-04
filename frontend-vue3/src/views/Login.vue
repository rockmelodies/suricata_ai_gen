<template>
  <div class="login-container">
    <div class="login-bg"></div>
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <div class="logo-icon">🛡️</div>
          <h2>Suricata 规则生成工具</h2>
          <p>基于AI的智能规则生成平台</p>
        </div>
      </template>

      <el-form
        ref="loginFormRef"
        :model="loginForm"
        :rules="rules"
        label-width="0"
        size="large"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="用户名"
            prefix-icon="User"
            clearable
            autofocus
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            style="width: 100%"
            :loading="loading"
            native-type="submit"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登 录' }}
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 可折叠的默认账号提示 -->
      <div class="tips">
        <el-collapse>
          <el-collapse-item name="hint">
            <template #title>
              <span class="hint-title">💡 查看默认账号</span>
            </template>
            <div class="hint-content">
              <p>管理员：<code>admin</code> / <code>admin123</code></p>
              <p class="hint-warn">请登录后尽快修改默认密码</p>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import type { FormInstance, FormRules } from 'element-plus'
import type { LoginForm } from '@/types'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const loginFormRef = ref<FormInstance>()
const loading = ref(false)

const loginForm = reactive<LoginForm>({
  username: '',
  password: ''
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const success = await userStore.login(loginForm)
        if (success) {
          // 登录成功，跳转到之前的页面或首页
          const redirect = route.query.redirect as string || '/'
          router.push(redirect)
        }
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  inset: 0;
  background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.login-card {
  width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  position: relative;
  z-index: 1;
}

.card-header {
  text-align: center;
  padding: 8px 0;
}

.logo-icon {
  font-size: 48px;
  margin-bottom: 12px;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); }
}

.card-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 22px;
  font-weight: 600;
}

.card-header p {
  margin: 0;
  color: #909399;
  font-size: 13px;
}

.tips {
  margin-top: 12px;
}

.hint-title {
  font-size: 13px;
  color: #909399;
}

.hint-content {
  padding: 8px 4px;
}

.hint-content p {
  font-size: 13px;
  color: #606266;
  margin: 4px 0;
}

.hint-content code {
  background: #f0f2f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: monospace;
  color: #e6a23c;
}

.hint-warn {
  color: #e6a23c !important;
  font-size: 12px !important;
}
</style>
