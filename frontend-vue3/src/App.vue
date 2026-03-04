<template>
  <!-- 认证初始化完成前显示全局 loading 防止闪烁 -->
  <div v-if="!isReady" class="app-loading">
    <div class="app-loading-inner">
      <div class="app-loading-spinner"></div>
      <p>正在加载...</p>
    </div>
  </div>
  <router-view v-else />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const isReady = ref(false)

onMounted(async () => {
  // 应用启动时验证登录状态，完成后才展示页面
  await userStore.checkAuth()
  isReady.value = true
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
}

#app {
  width: 100%;
  min-height: 100vh;
}

.app-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f2f5;
}

.app-loading-inner {
  text-align: center;
  color: #909399;
}

.app-loading-inner p {
  margin-top: 12px;
  font-size: 14px;
}

.app-loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e4e7ed;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
