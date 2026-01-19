<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#409eff"><Document /></el-icon>
            <div class="stat-content">
              <div class="stat-title">规则总数</div>
              <div class="stat-value">{{ stats.totalRules }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#67c23a"><User /></el-icon>
            <div class="stat-content">
              <div class="stat-title">用户总数</div>
              <div class="stat-value">{{ stats.totalUsers }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#e6a23c"><Check /></el-icon>
            <div class="stat-content">
              <div class="stat-title">验证次数</div>
              <div class="stat-value">{{ stats.totalValidations }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <el-card shadow="hover">
          <div class="stat-card">
            <el-icon class="stat-icon" color="#f56c6c"><Setting /></el-icon>
            <div class="stat-content">
              <div class="stat-title">优化次数</div>
              <div class="stat-value">{{ stats.totalOptimizations }}</div>
            </div>
          </div>
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
import { ref, onMounted } from 'vue'
import { Document, User, Check, Setting, Plus, List } from '@element-plus/icons-vue'
import { getRuleList } from '@/api/rules'
import { getUserList } from '@/api/auth'

const stats = ref({
  totalRules: 0,
  totalUsers: 0,
  totalValidations: 0,
  totalOptimizations: 0
})

onMounted(async () => {
  try {
    // 获取规则数量
    const ruleRes: any = await getRuleList({ page: 1, per_page: 1 })
    stats.value.totalRules = ruleRes.total || 0

    // 获取用户数量
    const userRes: any = await getUserList({ page: 1, per_page: 1 })
    stats.value.totalUsers = userRes.total || 0
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  font-size: 48px;
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
