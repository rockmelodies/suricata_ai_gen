<template>
  <div class="dashboard">

    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="6" v-for="stat in statCards" :key="stat.key">
        <el-card shadow="never" class="stat-card-wrap" :style="{ borderTop: `3px solid ${stat.color}` }">
          <el-skeleton :loading="loading" animated>
            <template #template>
              <div class="stat-card">
                <el-skeleton-item variant="circle" style="width: 52px; height: 52px;" />
                <div class="stat-content">
                  <el-skeleton-item variant="text" style="width: 60px;" />
                  <el-skeleton-item variant="h1" style="width: 80px; margin-top: 8px;" />
                </div>
              </div>
            </template>
            <template #default>
              <div class="stat-card">
                <div class="stat-icon-wrap" :style="{ background: stat.bg }">
                  <el-icon :size="28" :color="stat.color">
                    <component :is="stat.icon" />
                  </el-icon>
                </div>
                <div class="stat-content">
                  <div class="stat-title">{{ stat.title }}</div>
                  <div class="stat-value" :style="{ color: stat.color }">
                    {{ stats[stat.key as keyof typeof stats] }}
                  </div>
                </div>
              </div>
            </template>
          </el-skeleton>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 -->
    <div class="section-title">快捷操作</div>
    <el-row :gutter="16">
      <el-col :xs="12" :sm="8" :md="8" :lg="24/5" :xl="24/5" v-for="action in quickActions" :key="action.path">
        <div class="action-card" @click="$router.push(action.path)">
          <div class="action-icon-wrap" :style="{ background: action.bg }">
            <el-icon :size="30" :color="action.color">
              <component :is="action.icon" />
            </el-icon>
          </div>
          <div class="action-label">{{ action.label }}</div>
          <div class="action-desc">{{ action.desc }}</div>
          <el-icon class="action-arrow" :size="14" color="#c0c4cc"><ArrowRight /></el-icon>
        </div>
      </el-col>
    </el-row>

    <!-- 使用说明 -->
    <div class="section-title">使用流程</div>
    <el-card shadow="never" class="steps-card">
      <el-steps :active="4" finish-status="success" align-center>
        <el-step title="生成规则">
          <template #icon>
            <el-icon><MagicStick /></el-icon>
          </template>
          <template #description>使用 AI 生成 Suricata 规则</template>
        </el-step>
        <el-step title="验证规则">
          <template #icon>
            <el-icon><VideoPlay /></el-icon>
          </template>
          <template #description>使用 PCAP 文件验证规则</template>
        </el-step>
        <el-step title="优化规则">
          <template #icon>
            <el-icon><EditPen /></el-icon>
          </template>
          <template #description>根据验证结果优化规则</template>
        </el-step>
        <el-step title="导出使用">
          <template #icon>
            <el-icon><Upload /></el-icon>
          </template>
          <template #description>导出规则到生产环境</template>
        </el-step>
      </el-steps>
    </el-card>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, shallowRef } from 'vue'
import {
  Document, User, Check, Setting,
  Plus, List, MagicStick, Connection,
  ArrowRight, VideoPlay, EditPen, Upload
} from '@element-plus/icons-vue'
import { getRuleList } from '@/api/rules'
import { getUserList } from '@/api/auth'

const loading = ref(true)

const statCards = [
  { key: 'totalRules',       title: '规则总数', color: '#409eff', bg: '#ecf5ff', icon: shallowRef(Document) },
  { key: 'totalUsers',       title: '用户总数', color: '#67c23a', bg: '#f0f9eb', icon: shallowRef(User) },
  { key: 'totalValidations', title: '验证次数', color: '#e6a23c', bg: '#fdf6ec', icon: shallowRef(Check) },
  { key: 'totalOptimizations', title: '优化次数', color: '#f56c6c', bg: '#fef0f0', icon: shallowRef(Setting) }
]

const quickActions = [
  { path: '/rules/create',   label: '生成验证一体化', desc: 'AI生成并自动验证', color: '#409eff', bg: '#ecf5ff', icon: shallowRef(MagicStick) },
  { path: '/rules/generate', label: '生成规则',       desc: '使用AI生成规则',   color: '#67c23a', bg: '#f0f9eb', icon: shallowRef(Plus) },
  { path: '/rules/list',     label: '规则列表',       desc: '查看所有规则',     color: '#606266', bg: '#f4f4f5', icon: shallowRef(List) },
  { path: '/rules/validate', label: '验证规则',       desc: '使用PCAP验证',     color: '#e6a23c', bg: '#fdf6ec', icon: shallowRef(Check) },
  { path: '/agent',          label: 'Agent API',      desc: '外部系统调用',     color: '#9b59b6', bg: '#f5eeff', icon: shallowRef(Connection) },
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
    if (ruleRes.status === 'fulfilled') stats.value.totalRules = ruleRes.value?.total ?? 0
    if (userRes.status === 'fulfilled') stats.value.totalUsers = userRes.value?.total ?? 0
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
  background: #f5f7fa;
  min-height: 100%;
}

/* 统计卡片 */
.stat-card-wrap {
  margin-bottom: 0;
  border-radius: 10px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card-wrap:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

:deep(.stat-card-wrap .el-card__body) {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
  min-width: 0;
}

.stat-title {
  font-size: 13px;
  color: #909399;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 30px;
  font-weight: 700;
  line-height: 1;
}

/* 分区标题 */
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin: 24px 0 12px;
  padding-left: 10px;
  border-left: 3px solid #409eff;
}

/* 快捷操作卡片 */
.action-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px 16px 16px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  text-align: center;
  position: relative;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid #ebeef5;
  margin-bottom: 0;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: transparent;
}

.action-icon-wrap {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 4px;
}

.action-label {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.action-desc {
  font-size: 12px;
  color: #909399;
}

.action-arrow {
  position: absolute;
  top: 12px;
  right: 12px;
  opacity: 0;
  transition: opacity 0.2s;
}

.action-card:hover .action-arrow {
  opacity: 1;
}

/* 流程步骤 */
.steps-card {
  border-radius: 10px;
}

:deep(.steps-card .el-card__body) {
  padding: 24px 32px;
}

@media (max-width: 768px) {
  .dashboard {
    padding: 16px;
  }

  .action-card {
    padding: 16px 10px 12px;
  }

  .action-icon-wrap {
    width: 48px;
    height: 48px;
  }
}
</style>
