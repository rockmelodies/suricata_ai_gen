import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表板', requiresAuth: true }
      },
      {
        path: 'rules',
        name: 'Rules',
        children: [
          {
            path: 'generate',
            name: 'RuleGenerate',
            component: () => import('@/views/rules/Generate.vue'),
            meta: { title: '生成规则', requiresAuth: true }
          },
          {
            path: 'create',
            name: 'RuleCreate',
            component: () => import('@/views/rules/Create.vue'),
            meta: { title: '生成验证一体化', requiresAuth: true }
          },
          {
            path: 'list',
            name: 'RuleList',
            component: () => import('@/views/rules/List.vue'),
            meta: { title: '规则列表', requiresAuth: true }
          },
          {
            path: 'validate',
            name: 'RuleValidate',
            component: () => import('@/views/rules/Validate.vue'),
            meta: { title: '验证规则', requiresAuth: true }
          }
        ]
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/List.vue'),
        meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/Config.vue'),
        meta: { title: '系统配置', requiresAuth: true }
      },
      {
        path: 'suricata-check',
        name: 'SuricataCheck',
        component: () => import('@/views/SuricataCheck.vue'),
        meta: { title: 'Suricata引擎检查', requiresAuth: true }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - Suricata规则生成工具` : 'Suricata规则生成工具'

  // 检查是否需要登录
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn) {
      next({ name: 'Login', query: { redirect: to.fullPath } })
      return
    }

    // 检查是否需要管理员权限
    if (to.meta.requiresAdmin && !userStore.isAdmin()) {
      next({ name: 'Dashboard' })
      return
    }
  }

  // 已登录用户访问登录页，跳转到仪表板
  if (to.name === 'Login' && userStore.isLoggedIn) {
    next({ name: 'Dashboard' })
    return
  }

  next()
})

export default router
