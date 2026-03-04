import axios, { AxiosInstance, AxiosResponse } from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

// 创建axios实例
const service: AxiosInstance = axios.create({
  baseURL: '/api', // Vite代理会转发到后端
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 防止重复弹出 session 过期弹框
let isSessionExpiredShowing = false

// 延迟导入 router，避免循环依赖
const getRouter = async () => {
  const { default: router } = await import('@/router')
  return router
}

// 处理 session 失效
const handleSessionExpired = async () => {
  if (isSessionExpiredShowing) return
  isSessionExpiredShowing = true

  // 清除本地存储
  localStorage.removeItem('access_token')
  localStorage.removeItem('user')

  try {
    await ElMessageBox.alert(
      '您的登录已过期，请重新登录',
      '登录已过期',
      {
        confirmButtonText: '重新登录',
        type: 'warning',
        showClose: false
      }
    )
  } finally {
    isSessionExpiredShowing = false
    const router = await getRouter()
    const currentPath = router.currentRoute.value.fullPath
    // 跳转到登录页并携带当前路径，登录后可以回来
    router.push({
      name: 'Login',
      query: { redirect: currentPath !== '/login' ? currentPath : undefined }
    })
  }
}

// 请求拦截器
service.interceptors.request.use(
  (config) => {
    // 从localStorage获取token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    return response.data
  },
  (error) => {
    if (error.response) {
      const status = error.response.status
      const message = error.response.data?.message || error.response.data?.error || '请求失败'

      switch (status) {
        case 401:
          // session 过期，优雅处理
          handleSessionExpired()
          break
        case 403:
          ElMessage.error('权限不足，无法执行此操作')
          break
        case 404:
          ElMessage.error('请求的资源不存在')
          break
        case 500:
          ElMessage.error(`服务器内部错误：${message}`)
          break
        case 502:
        case 503:
          ElMessage.error('服务暂时不可用，请稍后重试')
          break
        default:
          ElMessage.error(message)
      }
    } else if (error.request) {
      ElMessage.error('网络连接失败，请检查您的网络')
    } else {
      ElMessage.error('请求配置错误')
    }
    return Promise.reject(error)
  }
)

export default service
