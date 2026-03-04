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
  // 用于防止 checkAuth 重复执行
  let checkAuthPromise: Promise<boolean> | null = null

  // 解析 token 的过期时间（本地检测，不发请求）
  // 支持自定义格式: base64(user_id:expire:sig)
  const isTokenExpired = (tokenStr: string): boolean => {
    try {
      // 尝试自定义格式: base64(user_id:expire:sig)
      const decoded = atob(tokenStr.replace(/-/g, '+').replace(/_/g, '/'))
      const parts = decoded.split(':')
      if (parts.length >= 2) {
        const expire = parseInt(parts[1])
        if (!isNaN(expire)) {
          return expire * 1000 < Date.now()
        }
      }
      // 尝试 JWT 格式
      const payload = JSON.parse(atob(tokenStr.split('.')[1]))
      return payload.exp ? payload.exp * 1000 < Date.now() : false
    } catch {
      // 解析失败时不认为过期，让服务端验证
      return false
    }
  }

  // 清除登录状态（不弹消息）
  const clearAuth = () => {
    token.value = ''
    user.value = null
    isLoggedIn.value = false
    isAuthInitialized.value = false
    checkAuthPromise = null
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
  // 使用锁机制防止重复执行
  const checkAuth = async (): Promise<boolean> => {
    // 如果已经初始化完成，直接返回当前登录状态
    if (isAuthInitialized.value) {
      return isLoggedIn.value
    }

    // 如果有正在进行的检查，返回当前的 promise
    if (checkAuthPromise) {
      return checkAuthPromise
    }

    // 创建新的检查 promise
    checkAuthPromise = doCheckAuth()
    return checkAuthPromise
  }

  // 实际的认证检查逻辑
  const doCheckAuth = async (): Promise<boolean> => {
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (!storedToken) {
      isAuthInitialized.value = true
      checkAuthPromise = null
      return false
    }

    // 先在本地检测 token 是否过期，避免不必要的网络请求
    if (isTokenExpired(storedToken)) {
      clearAuth()
      isAuthInitialized.value = true
      checkAuthPromise = null
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
      checkAuthPromise = null
      return true
    } catch (error) {
      // Token 服务端已失效
      clearAuth()
      isAuthInitialized.value = true
      checkAuthPromise = null
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
