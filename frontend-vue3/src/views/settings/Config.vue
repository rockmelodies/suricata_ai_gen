<template>
  <div class="config-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>⚙️ 系统配置</span>
        </div>
      </template>

      <div class="config-section">
        <h3>🔒 环境变量配置说明</h3>
        <p>系统现在完全通过环境变量进行配置，所有敏感配置都应在 <code>.env</code> 文件中设置。</p>
        
        <el-alert
          title="重要提醒"
          type="info"
          description="所有Suricata相关配置现在都通过环境变量管理，无需在页面上进行配置。修改配置需要重启后端服务才能生效。"
          show-icon
          :closable="false"
          style="margin: 16px 0;"
        />

        <el-descriptions :column="1" border>
          <el-descriptions-item label="环境变量文件">
            <el-tag type="info">.env</el-tag>
            <div class="desc-detail">
              位于后端项目根目录，包含所有环境变量配置
            </div>
          </el-descriptions-item>
          
          <el-descriptions-item label="Suricata规则目录">
            <el-tag type="success">SURICATA_RULES_DIR</el-tag>
            <div class="desc-detail">
              默认值: /var/lib/suricata/rules
            </div>
          </el-descriptions-item>
          
          <el-descriptions-item label="Suricata配置文件">
            <el-tag type="success">SURICATA_CONFIG_PATH</el-tag>
            <div class="desc-detail">
              默认值: /etc/suricata/suricata.yaml
            </div>
          </el-descriptions-item>
          
          <el-descriptions-item label="Suricata日志目录">
            <el-tag type="success">SURICATA_LOG_DIR</el-tag>
            <div class="desc-detail">
              默认值: /var/log/suricata
            </div>
          </el-descriptions-item>
          
          <el-descriptions-item label="AI API密钥">
            <el-tag type="warning">AI_API_KEY</el-tag>
            <div class="desc-detail">
              用于AI模型的API密钥
            </div>
          </el-descriptions-item>
          
          <el-descriptions-item label="AI模型">
            <el-tag type="warning">AI_MODEL</el-tag>
            <div class="desc-detail">
              默认值: 360gpt-pro
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <el-divider />

      <div class="config-section">
        <h3>📝 配置步骤</h3>
        <el-steps :active="4" finish-status="success" simple style="margin: 20px 0;">
          <el-step title="创建文件" description="在后端根目录创建 .env 文件" />
          <el-step title="添加变量" description="添加所需的环境变量" />
          <el-step title="填写值" description="填入正确的配置值" />
          <el-step title="重启服务" description="重启后端服务使配置生效" />
        </el-steps>

        <div class="sample-config">
          <h4>示例 .env 配置：</h4>
          <pre>{{ sampleEnvConfig }}</pre>
        </div>
      </div>

      <el-divider />

      <div class="config-section">
        <h3>🔄 服务状态</h3>
        <el-button type="primary" @click="checkSuricataStatus" :loading="checking">
          检查Suricata引擎状态
        </el-button>
        
        <div v-if="suricataStatus" class="status-result" style="margin-top: 20px;">
          <el-card shadow="never" :class="suricataStatus.status === 'ready' ? 'success-card' : suricataStatus.status === 'partial' ? 'warning-card' : 'error-card'">
            <div class="status-header">
              <el-tag 
                :type="suricataStatus.status === 'ready' ? 'success' : suricataStatus.status === 'partial' ? 'warning' : 'danger'"
                size="large"
              >
                {{ getStatusText(suricataStatus.status) }}
              </el-tag>
            </div>
            <div class="status-details">
              <p><strong>操作系统:</strong> {{ suricataStatus.os || '未知' }}</p>
              <p><strong>Suricata可用:</strong> 
                <el-tag :type="suricataStatus.suricata_available ? 'success' : 'danger'">
                  {{ suricataStatus.suricata_available ? '是' : '否' }}
                </el-tag>
              </p>
              <p v-if="suricataStatus.version"><strong>版本:</strong> {{ suricataStatus.version }}</p>
              <p><strong>配置文件找到:</strong> 
                <el-tag :type="suricataStatus.config_found ? 'success' : 'danger'">
                  {{ suricataStatus.config_found ? '是' : '否' }}
                </el-tag>
              </p>
              <p v-if="suricataStatus.config_path"><strong>配置路径:</strong> {{ suricataStatus.config_path }}</p>
              <p><strong>规则目录存在:</strong> 
                <el-tag :type="suricataStatus.rules_dir_exists ? 'success' : 'danger'">
                  {{ suricataStatus.rules_dir_exists ? '是' : '否' }}
                </el-tag>
              </p>
              <p><strong>日志目录存在:</strong> 
                <el-tag :type="suricataStatus.log_dir_exists ? 'success' : 'danger'">
                  {{ suricataStatus.log_dir_exists ? '是' : '否' }}
                </el-tag>
              </p>
              <p v-if="suricataStatus.message"><strong>消息:</strong> {{ suricataStatus.message }}</p>
              <p v-if="suricataStatus.recommendation"><strong>建议:</strong> {{ suricataStatus.recommendation }}</p>
            </div>
          </el-card>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled, Check } from '@element-plus/icons-vue'
import { checkSuricataEngine } from '@/api/rules'

// 示例环境变量配置
const sampleEnvConfig = `# AI配置
AI_API_KEY=your_api_key_here
AI_MODEL=360gpt-pro

# Suricata配置
SURICATA_RULES_DIR=/var/lib/suricata/rules
SURICATA_CONFIG_PATH=/etc/suricata/suricata.yaml
SURICATA_LOG_DIR=/var/log/suricata

# 数据库配置
DB_PATH=./suricata_rules.db`;

// 状态检查相关
const checking = ref(false)
const suricataStatus = ref(null)

// 检查Suricata状态
const checkSuricataStatus = async () => {
  checking.value = true
  try {
    const res: any = await checkSuricataEngine()
    suricataStatus.value = res
    if (res.status === 'ready') {
      ElMessage.success('Suricata引擎准备就绪')
    } else if (res.status === 'partial') {
      ElMessage.warning('Suricata引擎部分可用')
    } else {
      ElMessage.error(res.message || 'Suricata引擎不可用')
    }
  } catch (error) {
    console.error('检查Suricata状态失败:', error)
    ElMessage.error('检查状态失败')
  } finally {
    checking.value = false
  }
}

// 获取状态文本
const getStatusText = (status: string) => {
  const statusMap: Record<string, string> = {
    'ready': '引擎就绪',
    'partial': '部分可用',
    'unavailable': '不可用'
  }
  return statusMap[status] || status
}

// 响应式处理
const handleResize = () => {
  // 这里可以根据需要添加响应式处理逻辑
}

// 组件挂载时的初始化
// 由于现在配置通过环境变量管理，不需要加载配置
</script>

<style scoped>
.config-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
}

.config-section {
  margin-bottom: 30px;
}

.config-section h3 {
  margin-bottom: 15px;
  color: #303133;
}

.config-section p {
  color: #606266;
  line-height: 1.6;
}

.desc-detail {
  margin-top: 8px;
  font-size: 13px;
  color: #909399;
}

.sample-config {
  margin-top: 15px;
}

.sample-config h4 {
  margin-bottom: 10px;
  color: #303133;
}

pre {
  background-color: #f5f5f5;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 15px;
  overflow-x: auto;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #303133;
  line-height: 1.5;
}

.status-result {
  margin-top: 20px;
}

.success-card {
  border: 1px solid #67c23a;
  background-color: #f0f9ff;
}

.warning-card {
  border: 1px solid #e6a23c;
  background-color: #fdf6ec;
}

.error-card {
  border: 1px solid #f56c6c;
  background-color: #fef0f0;
}

.status-header {
  margin-bottom: 10px;
}

.status-details p {
  margin: 8px 0;
  font-size: 14px;
}

.code-block {
  background-color: #f8f8f8;
  border-radius: 4px;
  padding: 10px;
  font-family: monospace;
  font-size: 14px;
  margin: 10px 0;
  overflow-x: auto;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .config-container {
    padding: 10px;
  }
  
  pre {
    font-size: 12px;
    padding: 10px;
  }
}
</style>