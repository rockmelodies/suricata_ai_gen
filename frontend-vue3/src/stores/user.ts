import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, LoginForm } from '@/types'
import { login as loginApi, getCurrentUser } from '@/api/auth'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string>('')
  const isLoggedIn = ref<boolean>(false)

  // 初始化：从localStorage恢复状态
  const initFromStorage = () => {
    const storedToken = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')
    
    if (storedToken && storedUser) {
      token.value = storedToken
      user.value = JSON.parse(storedUser)
      isLoggedIn.value = true
    }
  }

  // 登录
  const login = async (loginForm: LoginForm) => {
    try {
      const res = await loginApi(loginForm)
      
      // 保存token和用户信息
      token.value = res.access_token
      user.value = res.user
      isLoggedIn.value = true

      // 持久化到localStorage
      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('user', JSON.stringify(res.user))

      ElMessage.success('登录成功')
      return true
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || '登录失败')
      return false
    }
  }

  // 登出
  const logout = () => {
    token.value = ''
    user.value = null
    isLoggedIn.value = false

    localStorage.removeItem('access_token')
    localStorage.removeItem('user')

    ElMessage.success('已退出登录')
  }

  // 检查认证状态
  const checkAuth = async () => {
    const storedToken = localStorage.getItem('access_token')
    
    if (!storedToken) {
      return false
    }

    try {
      // 验证token是否有效
      const userData = await getCurrentUser()
      user.value = userData
      isLoggedIn.value = true
      return true
    } catch (error) {
      // Token无效，清除本地存储
      logout()
      return false
    }
  }

  // 是否是管理员
  const isAdmin = () => {
    return user.value?.role === 'admin'
  }

  // 初始化
  initFromStorage()

  return {
    user,
    token,
    isLoggedIn,
    login,
    logout,
    checkAuth,
    isAdmin
  }
})
