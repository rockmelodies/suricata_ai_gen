<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6" v-for="stat in statCards" :key="stat.key">
        <el-card shadow="hover" class="stat-card-wrap">
          <el-skeleton :loading="loading" animated>
            <template #template>
              <div class="stat-card">
                <el-skeleton-item variant="circle" style="width: 48px; height: 48px;" />
                <div class="stat-content">
                  <el-skeleton-item variant="text" style="width: 60px;" />
                  <el-skeleton-item variant="h1" style="width: 80px; margin-top: 8px;" />
                </div>
              </div>
            </template>
            <template #default>
              <div class="stat-card">
                <el-icon class="stat-icon" :color="stat.color">
                  <component :is="stat.icon" />
                </el-icon>
                <div class="stat-content">
                  <div class="stat-title">{{ stat.title }}</div>
                  <div class="stat-value">{{ stats[stat.key as keyof typeof stats] }}</div>
                </div>
              </div>
            </template>
          </el-skeleton>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>🚀 快速开始</span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="$router.push('/rules/create')">
              <el-icon><MagicStick /></el-icon>
              生成验证一体化
            </el-button>
            <el-button type="success" @click="$router.push('/rules/generate')">
              <el-icon><Plus /></el-icon>
              生成规则
            </el-button>
            <el-button type="info" @click="$router.push('/rules/list')">
              <el-icon><List /></el-icon>
              规则列表
            </el-button>
            <el-button type="warning" @click="$router.push('/rules/validate')">
              <el-icon><Check /></el-icon>
              验证规则
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="24">
        <el-card>
          <template #header>
            <span>📖 使用说明</span>
          </template>
          <el-steps :active="3" finish-status="success">
            <el-step title="生成规则" description="使用AI生成Suricata规则" />
            <el-step title="验证规则" description="使用PCAP文件验证规则" />
            <el-step title="优化规则" description="根据验证结果优化规则" />
            <el-step title="导出使用" description="导出规则到生产环境" />
          </el-steps>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, shallowRef } from 'vue'
import { Document, User, Check, Setting, Plus, List, MagicStick } from '@element-plus/icons-vue'
import { getRuleList } from '@/api/rules'
import { getUserList } from '@/api/auth'

const loading = ref(true)

const statCards = [
  { key: 'totalRules', title: '规则总数', color: '#409eff', icon: shallowRef(Document) },
  { key: 'totalUsers', title: '用户总数', color: '#67c23a', icon: shallowRef(User) },
  { key: 'totalValidations', title: '验证次数', color: '#e6a23c', icon: shallowRef(Check) },
  { key: 'totalOptimizations', title: '优化次数', color: '#f56c6c', icon: shallowRef(Setting) }
]

const stats = ref({
  totalRules: 0,
  totalUsers: 0,
  totalValidations: 0,
  totalOptimizations: 0
})

onMounted(async () => {
  try {
    const [ruleRes, userRes]: any[] = await Promise.allSettled([
      getRuleList({ page: 1, per_page: 1 }),
      getUserList({ page: 1, per_page: 1 })
    ])
    if (ruleRes.status === 'fulfilled') {
      stats.value.totalRules = ruleRes.value?.total ?? 0
    }
    if (userRes.status === 'fulfilled') {
      stats.value.totalUsers = userRes.value?.total ?? 0
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card-wrap {
  transition: transform 0.2s;
}

.stat-card-wrap:hover {
  transform: translateY(-2px);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.quick-actions {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .quick-actions {
    flex-direction: column;
  }

  .quick-actions .el-button {
    width: 100%;
  }
}
</style>
