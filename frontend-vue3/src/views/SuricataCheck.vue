<template>
  <div class="suricata-check-container">
    <el-card class="suricata-check-card">
      <template #header>
        <div class="card-header">
          <span class="title">Suricata引擎状态检查</span>
          <el-button 
            type="primary" 
            @click="checkSuricataStatus"
            :loading="loading"
          >
            {{ loading ? '检查中...' : '检查状态' }}
          </el-button>
        </div>
      </template>

      <div v-if="statusData" class="status-content">
        <!-- 操作系统信息 -->
        <el-descriptions :column="1" border>
          <el-descriptions-item label="操作系统">
            <el-tag :type="statusData.os === 'Linux' ? 'success' : statusData.os === 'Windows' ? 'warning' : 'info'">
              {{ statusData.os }}
            </el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item label="引擎可用性">
            <el-tag :type="statusData.suricata_available ? 'success' : 'danger'">
              {{ statusData.suricata_available ? '可用' : '不可用' }}
            </el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item label="引擎版本">
            <span v-if="statusData.version">{{ statusData.version }}</span>
            <span v-else class="text-muted">未获取到版本信息</span>
          </el-descriptions-item>
          
          <el-descriptions-item label="配置文件">
            <el-tag :type="statusData.config_found ? 'success' : 'warning'">
              {{ statusData.config_found ? '已找到' : '未找到' }}
            </el-tag>
            <span v-if="statusData.config_path" class="ml-10">{{ statusData.config_path }}</span>
          </el-descriptions-item>
          
          <el-descriptions-item label="规则目录">
            <el-tag :type="statusData.rules_dir_exists ? 'success' : 'warning'">
              {{ statusData.rules_dir_exists ? '存在' : '不存在' }}
            </el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item label="日志目录">
            <el-tag :type="statusData.log_dir_exists ? 'success' : 'warning'">
              {{ statusData.log_dir_exists ? '存在' : '不存在' }}
            </el-tag>
          </el-descriptions-item>
          
          <el-descriptions-item label="整体状态">
            <el-tag 
              :type="getStatusType(statusData.status)" 
              size="large"
            >
              {{ getStatusText(statusData.status) }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <!-- 消息和建议 -->
        <div class="mt-20">
          <h3>状态消息</h3>
          <el-alert 
            :title="statusData.message" 
            :type="getStatusAlertType(statusData.status)"
            :closable="false"
            show-icon
          />
        </div>

        <div v-if="statusData.recommendation" class="mt-20">
          <h3>建议</h3>
          <el-alert 
            :title="statusData.recommendation" 
            type="warning"
            :closable="false"
            show-icon
          />
        </div>

        <!-- 功能测试 -->
        <div v-if="statusData.suricata_available" class="mt-20">
          <h3>功能测试</h3>
          <el-button-group>
            <el-button type="primary" @click="testRuleSyntax">
              测试规则语法
            </el-button>
            <el-button type="info" @click="testRuleValidation">
              测试规则验证
            </el-button>
          </el-button-group>
        </div>
      </div>

      <div v-else class="no-data">
        <el-empty description="尚未检查Suricata引擎状态，请点击上方按钮进行检查" />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const statusData = ref(null)
const loading = ref(false)

const checkSuricataStatus = async () => {
  loading.value = true
  try {
    const response = await request.get('/suricata/check')
    if (response.success) {
      statusData.value = response
      ElMessage.success('状态检查完成')
    } else {
      ElMessage.error(response.message || '检查失败')
    }
  } catch (error) {
    console.error('检查Suricata状态失败:', error)
    ElMessage.error('检查失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const getStatusType = (status) => {
  switch (status) {
    case 'ready': return 'success'
    case 'partial': return 'warning'
    case 'unavailable': return 'danger'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'ready': return '就绪'
    case 'partial': return '部分就绪'
    case 'unavailable': return '不可用'
    default: return '未知'
  }
}

const getStatusAlertType = (status) => {
  switch (status) {
    case 'ready': return 'success'
    case 'partial': return 'warning'
    case 'unavailable': return 'error'
    default: return 'info'
  }
}

const testRuleSyntax = () => {
  ElMessage.info('规则语法测试功能待实现')
  // 实际的规则语法测试逻辑将在后端实现
}

const testRuleValidation = () => {
  ElMessage.info('规则验证测试功能待实现')
  // 实际的规则验证测试逻辑将在后端实现
}

// 页面加载时自动检查一次
checkSuricataStatus()
</script>

<style scoped>
.suricata-check-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.suricata-check-card {
  max-width: 1000px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.mt-20 {
  margin-top: 20px;
}

.ml-10 {
  margin-left: 10px;
}

.text-muted {
  color: #909399;
}

.no-data {
  text-align: center;
  padding: 40px 0;
}
</style>