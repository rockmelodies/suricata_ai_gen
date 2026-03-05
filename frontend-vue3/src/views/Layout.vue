<template>
  <el-container class="layout-container">
    <el-aside :width="collapsed ? '64px' : '200px'" class="sidebar">
      <div class="logo">
        <transition name="logo-fade">
          <h3 v-if="!collapsed" key="full">🛡️ Suricata</h3>
          <h3 v-else key="icon" style="text-align: center;">🛡️</h3>
        </transition>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        :collapse="collapsed"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409eff"
      >
        <el-menu-item index="/dashboard">
          <el-icon><House /></el-icon>
          <span>仪表板</span>
        </el-menu-item>

        <el-sub-menu index="rules">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>规则管理</span>
          </template>
          <el-menu-item index="/rules/create">生成验证一体化</el-menu-item>
          <el-menu-item index="/rules/generate">生成规则</el-menu-item>
          <el-menu-item index="/rules/list">规则列表</el-menu-item>
          <el-menu-item index="/rules/validate">验证规则</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/agent">
          <el-icon><Connection /></el-icon>
          <span>Agent API</span>
        </el-menu-item>

        <el-menu-item v-if="userStore.isAdmin()" index="/agent/manage">
          <el-icon><Key /></el-icon>
          <span>Agent 管理</span>
        </el-menu-item>

        <el-menu-item v-if="userStore.isAdmin()" index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>

        <el-menu-item index="/suricata-check">
          <el-icon><Monitor /></el-icon>
          <span>引擎状态检查</span>
        </el-menu-item>
        <el-menu-item index="/settings">
          <el-icon><Setting /></el-icon>
          <span>系统配置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <el-button @click="toggleSidebar" size="default" :icon="collapsed ? Expand : Fold" link />
          <!-- 面包屑导航 -->
          <el-breadcrumb separator="/" class="breadcrumb" v-if="breadcrumbs.length > 1">
            <el-breadcrumb-item
              v-for="(item, index) in breadcrumbs"
              :key="index"
              :to="item.path && index < breadcrumbs.length - 1 ? { path: item.path } : undefined"
            >
              {{ item.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
          <span class="page-title" v-else>{{ pageTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand" trigger="click">
            <span class="user-dropdown">
              <el-avatar :size="28" class="user-avatar">
                {{ userStore.user?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="username-text">{{ userStore.user?.username }}</span>
              <el-tag
                :type="userStore.isAdmin() ? 'danger' : 'info'"
                size="small"
                class="role-tag"
              >
                {{ userStore.isAdmin() ? '管理员' : '普通用户' }}
              </el-tag>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item disabled>
                  <el-icon><User /></el-icon>
                  <span style="margin-left: 6px;">{{ userStore.user?.username }}</span>
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'
import {
  House,
  Document,
  User,
  ArrowDown,
  SwitchButton,
  Setting,
  Expand,
  Fold,
  Monitor,
  Connection,
  Key
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)

const pageTitle = computed(() => {
  return route.meta.title as string || '仪表板'
})

// 面包屑导航计算
const breadcrumbs = computed(() => {
  const crumbs = [{ title: '首页', path: '/dashboard' }]
  const title = route.meta.title as string
  if (title && title !== '仪表板') {
    crumbs.push({ title, path: '' })
  }
  return crumbs
})

const collapsed = ref(false)

const toggleSidebar = () => {
  collapsed.value = !collapsed.value
}

const handleCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm(
        '确定要退出登录吗？',
        '退出确认',
        {
          confirmButtonText: '退出',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
      userStore.logout()
      router.push('/login')
    } catch {
      // 用户取消，不做任何操作
    }
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  overflow-x: hidden;
  transition: width 0.3s ease;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b2f3a;
  overflow: hidden;
}

.logo h3 {
  color: #fff;
  margin: 0;
  font-size: 18px;
  white-space: nowrap;
}

.logo-fade-enter-active,
.logo-fade-leave-active {
  transition: opacity 0.2s;
}
.logo-fade-enter-from,
.logo-fade-leave-to {
  opacity: 0;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.breadcrumb {
  margin-left: 8px;
}

.page-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-left: 8px;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 6px;
  transition: background-color 0.2s;
  outline: none;
}

.user-dropdown:hover {
  background-color: #f5f7fa;
}

.user-avatar {
  background-color: #409eff;
  color: #fff;
  font-size: 13px;
  font-weight: bold;
  flex-shrink: 0;
}

.username-text {
  font-size: 14px;
  color: #303133;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.role-tag {
  flex-shrink: 0;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
