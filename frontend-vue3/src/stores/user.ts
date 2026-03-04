import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, LoginForm } from '@/types'
import { login as loginApi, getCurrentUser } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string>('')
  const isLoggedIn = ref<boolean>(false)
  // 标记初始化是否完成（防止路由守卫在验证完成前跳转）
  const isAuthInitialized = ref<boolean>(false)

  // 解析 JWT token 的过期时间（本地检测，不发请求）
  const isTokenExpired = (jwtToken: string): boolean => {
    try {
      const payload = JSON.parse(atob(jwtToken.split('.')[1]))
      // exp 为 Unix 秒时间戳
      return payload.exp ? payload.exp * 1000 < Date.now() : false
    } catch {
      return true // 解析失败认为已过期
    }
  }

  // 清除登录状态（不弹消息）
  const clearAuth = () => {
    token.value = ''
    user.value = null
    isLoggedIn.value = false
    isAuthInitialized.value = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  }

  // 登录
  const login = async (loginForm: LoginForm) => {
    try {
      const res = await loginApi(loginForm)

      // 保存token和用户信息
      token.value = res.access_token
      user.value = res.user
      isLoggedIn.value = true
      isAuthInitialized.value = true

      // 持久化到localStorage
      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('user', JSON.stringify(res.user))

      ElMessage.success('登录成功')
      return true
    } catch (error: any) {
      const msg = error.response?.data?.message || error.response?.data?.error || '登录失败，请检查用户名和密码'
      ElMessage.error(msg)
      return false
    }
  }

  // 登出
  const logout = (showMessage = true) => {
    clearAuth()
    if (showMessage) {
      ElMessage.success('已退出登录')
    }
  }

  // 检查认证状态（应用启动时调用）
  const checkAuth = async () => {
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (!storedToken) {
      isAuthInitialized.value = true
      return false
    }

    // 先在本地检测 token 是否过期，避免不必要的网络请求
    if (isTokenExpired(storedToken)) {
      clearAuth()
      isAuthInitialized.value = true
      return false
    }

    // 先从本地恢复状态，使页面能快速渲染
    if (storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
      isLoggedIn.value = true
    }

    try {
      // 异步验证 token 是否在服务端有效
      const userData = await getCurrentUser()
      user.value = userData
      isLoggedIn.value = true
      // 同步更新本地缓存的用户信息
      localStorage.setItem('user', JSON.stringify(userData))
      isAuthInitialized.value = true
      return true
    } catch (error) {
      // Token 服务端已失效
      clearAuth()
      isAuthInitialized.value = true
      return false
    }
  }

  // 是否是管理员
  const isAdmin = () => {
    return user.value?.role === 'admin'
  }

  return {
    user,
    token,
    isLoggedIn,
    isAuthInitialized,
    login,
    logout,
    checkAuth,
    isAdmin,
    clearAuth
  }
})
