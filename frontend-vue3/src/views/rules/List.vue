<template>
  <div class="rule-list-container">
    <el-card>
      <template #header>
        <div class="list-header">
          <span>📋 规则列表</span>
          <el-button
            type="primary"
            @click="$router.push('/rules/generate')"
          >
            <el-icon><Plus /></el-icon>
            生成新规则
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" style="margin-bottom: 16px">
        <el-form-item label="漏洞名称">
          <el-input
            v-model="searchForm.keyword"
            placeholder="请输入关键词"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 表格 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        border
        :max-height="tableHeight"
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="vuln_name" label="漏洞名称" :min-width="isMobile ? 100 : 150" show-overflow-tooltip />
        <el-table-column prop="vuln_type" label="漏洞类型" :width="isMobile ? 80 : 100" />
        <el-table-column prop="description" label="描述" :min-width="isMobile ? 100 : 120" show-overflow-tooltip />
        <el-table-column prop="created_at" label="创建时间" :width="isMobile ? 120 : 150" />
        <el-table-column label="操作" :width="isMobile ? 180 : 300" fixed="right">
          <template #default="{ row }">
            <el-button-group class="button-group">
              <el-button
                type="primary"
                size="small"
                @click="handleView(row)"
              >
                <el-icon><View /></el-icon>
                <span v-if="!isMobile">查看</span>
              </el-button>
              <el-button
                type="success"
                size="small"
                @click="handleCopy(row.current_rule)"
              >
                <el-icon><DocumentCopy /></el-icon>
                <span v-if="!isMobile">复制</span>
              </el-button>
              <el-button
                type="info"
                size="small"
                @click="handleValidate(row)"
              >
                <el-icon><VideoPlay /></el-icon>
                <span v-if="!isMobile">验证</span>
              </el-button>
              <el-button
                type="warning"
                size="small"
                @click="handleOptimize(row)"
              >
                <el-icon><EditPen /></el-icon>
                <span v-if="!isMobile">优化</span>
              </el-button>
            </el-button-group>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.per_page"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 16px; justify-content: flex-end"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 规则详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      :title="`规则详情 - ID: ${currentRule?.id}`"
      width="800px"
    >
      <el-descriptions :column="1" border v-if="currentRule">
        <el-descriptions-item label="漏洞名称">
          {{ currentRule.vuln_name }}
        </el-descriptions-item>
        <el-descriptions-item label="漏洞类型">
          {{ currentRule.vuln_type || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="描述">
          {{ currentRule.description }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ currentRule.created_at }}
        </el-descriptions-item>
        <el-descriptions-item label="更新时间">
          {{ currentRule.updated_at }}
        </el-descriptions-item>
      </el-descriptions>

      <div style="margin-top: 20px">
        <h4>当前规则：</h4>
        <div class="rule-code">
          <pre><code>{{ currentRule?.current_rule }}</code></pre>
        </div>
      </div>

      <template #footer>
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button
          type="success"
          @click="handleCopy(currentRule?.current_rule || '')"
        >
          <el-icon><DocumentCopy /></el-icon>
          复制规则
        </el-button>
      </template>
    </el-dialog>

    <!-- 验证规则对话框 -->
    <el-dialog
      v-model="showValidateDialog"
      title="验证规则"
      width="800px"
    >
      <el-form label-width="100px">
        <el-form-item label="规则内容">
          <el-input
            v-model="validateForm.rule_content"
            type="textarea"
            :rows="3"
            readonly
          />
        </el-form-item>
        <el-form-item label="PCAP路径">
          <el-input
            v-model="validateForm.pcap_path"
            placeholder="请输入PCAP文件所在目录路径"
          >
            <template #prepend>
              <el-icon><FolderOpened /></el-icon>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            Windows: C:\pcap_check | Linux: /home/kali/pcap_check
          </div>
        </el-form-item>
      </el-form>

      <!-- 验证结果 -->
      <div v-if="validationResult" class="validation-result">
        <el-divider>验证结果</el-divider>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-statistic title="总告警数" :value="validationResult.alert_count">
              <template #suffix>
                <span style="font-size: 16px; margin-left: 4px">条</span>
              </template>
            </el-statistic>
          </el-col>
          <el-col :span="8">
            <el-statistic
              title="匹配状态"
              :value="validationResult.matched ? '成功' : '失败'"
            />
          </el-col>
          <el-col :span="8">
            <el-statistic
              title="SID统计"
              :value="Object.keys(validationResult.sid_stats || {}).length"
            >
              <template #suffix>
                <span style="font-size: 16px; margin-left: 4px">个</span>
              </template>
            </el-statistic>
          </el-col>
        </el-row>
        
        <!-- 引擎状态信息 -->
        <div v-if="validationResult.engine_status" class="engine-status-info" style="margin-top: 16px;">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="引擎状态">
              <el-tag :type="getStatusTagType(validationResult.engine_status)">
                {{ getEngineStatusText(validationResult.engine_status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="执行状态">
              <el-tag :type="validationResult.success ? 'success' : 'danger'">
                {{ validationResult.success ? '成功' : '失败' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="是否匹配">
              <el-tag :type="validationResult.matched ? 'success' : 'info'">
                {{ validationResult.matched ? '是' : '否' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <!-- 执行详情 -->
        <div v-if="validationResult.execution_details" class="execution-details" style="margin-top: 16px;">
          <el-collapse>
            <el-collapse-item title="执行详情" name="execution">
              <el-descriptions :column="1" border>
                <el-descriptions-item 
                  v-for="(value, key) in validationResult.execution_details" 
                  :key="key" 
                  :label="formatDetailKey(key)"
                >
                  <span v-if="typeof value === 'object'">{{ JSON.stringify(value, null, 2) }}</span>
                  <span v-else>{{ value }}</span>
                </el-descriptions-item>
              </el-descriptions>
            </el-collapse-item>
          </el-collapse>
        </div>

        <el-tabs v-model="activeTab" style="margin-top: 16px">
          <el-tab-pane label="📝 告警详情" name="details">
            <div v-if="validationResult.details" class="details-content">
              <el-alert
                :title="`共检测到 ${validationResult.alert_count} 条告警`"
                type="info"
                :closable="false"
                style="margin-bottom: 16px"
              />
              <div class="json-viewer">
                <pre><code>{{ JSON.stringify(validationResult.details, null, 2) }}</code></pre>
              </div>
            </div>
            <el-empty v-else description="暂无详细信息" />
          </el-tab-pane>

          <el-tab-pane label="📊 SID统计" name="sid_stats">
            <div v-if="validationResult.sid_stats && Object.keys(validationResult.sid_stats).length > 0">
              <el-table :data="sidStatsData" border style="width: 100%">
                <el-table-column prop="sid" label="SID" width="150" />
                <el-table-column prop="count" label="出现次数" width="120">
                  <template #default="{ row }">
                    <el-tag type="success">{{ row.count }}</el-tag>
                  </template>
                </el-table-column>
                <el-table-column prop="percentage" label="占比" width="120">
                  <template #default="{ row }">
                    {{ row.percentage }}%
                  </template>
                </el-table-column>
                <el-table-column label="进度">
                  <template #default="{ row }">
                    <el-progress
                      :percentage="row.percentage"
                      :color="customColors"
                    />
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <el-empty v-else description="暂无SID统计数据" />
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <el-button @click="showValidateDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="validating"
          @click="handleValidateSubmit"
        >
          开始验证
        </el-button>
      </template>
    </el-dialog>

    <!-- 优化规则对话框 -->
    <el-dialog
      v-model="showOptimizeDialog"
      title="优化规则"
      width="800px"
    >
      <el-form label-width="100px">
        <el-form-item label="当前规则">
          <el-input
            v-model="optimizeForm.current_rule"
            type="textarea"
            :rows="3"
            readonly
          />
        </el-form-item>
        <el-form-item label="优化建议">
          <el-input
            v-model="optimizeForm.feedback"
            type="textarea"
            :rows="3"
            placeholder="请描述您希望如何优化这条规则（可选）"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showOptimizeDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="optimizing"
          @click="handleOptimizeSubmit"
        >
          开始优化
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Plus,
  Search,
  View,
  DocumentCopy,
  EditPen,
  VideoPlay,
  FolderOpened,
  InfoFilled
} from '@element-plus/icons-vue'
import type { Rule } from '@/types'
import { getRuleList, optimizeRule, validateRule, getPCAPConfig } from '@/api/rules'

const loading = ref(false)
const optimizing = ref(false)
const showDetailDialog = ref(false)
const showOptimizeDialog = ref(false)
const tableData = ref<Rule[]>([])
const currentRule = ref<Rule | null>(null)
const validating = ref(false)
const showValidateDialog = ref(false)
const validateForm = reactive({
  rule_content: '',
  pcap_path: '', // 初始化为空，稍后从API获取
  rule_id: undefined as number | undefined
})
const validationResult = ref<any>(null)
const activeTab = ref('details')
const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 }
]
const tableHeight = ref(400)
const isMobile = ref(false)

const searchForm = reactive({
  keyword: ''
})

const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

const optimizeForm = reactive({
  rule_id: undefined as number | undefined,
  current_rule: '',
  feedback: ''
})

// 响应式处理
const handleResize = () => {
  const windowWidth = window.innerWidth
  const windowHeight = window.innerHeight
  
  isMobile.value = windowWidth < 768
  tableHeight.value = windowHeight > 800 ? 500 : windowHeight - 400
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
  fetchRules()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const fetchRules = async () => {
  loading.value = true
  try {
    const res: any = await getRuleList({
      page: pagination.page,
      per_page: pagination.per_page
    })
    
    tableData.value = res.rules || []
    pagination.total = res.total || 0
  } catch (error: any) {
    ElMessage.error('加载规则列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  fetchRules()
}

const handleReset = () => {
  searchForm.keyword = ''
  pagination.page = 1
  fetchRules()
}

const handleView = (row: Rule) => {
  currentRule.value = row
  showDetailDialog.value = true
}

const handleCopy = async (ruleContent: string) => {
  try {
    await navigator.clipboard.writeText(ruleContent)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

// 计算SID统计表格数据
const sidStatsData = computed(() => {
  if (!validationResult.value?.sid_stats) return []

  const stats = validationResult.value.sid_stats
  const total = validationResult.value.alert_count

  return Object.entries(stats).map(([sid, count]) => ({
    sid,
    count,
    percentage: total > 0 ? ((count as number / total) * 100).toFixed(1) : 0
  }))
})

// 引擎状态文本映射
const engineStatusMap: Record<string, string> = {
  'not_started': '未开始',
  'invalid_input': '输入无效',
  'invalid_pcap_path': 'PCAP路径无效',
  'suricata_not_found': 'Suricata未找到',
  'config_missing': '配置文件缺失',
  'log_dir_missing': '日志目录缺失',
  'ssh_config_missing': 'SSH配置缺失',
  'executing': '执行中',
  'no_pcap_files': '未找到PCAP文件',
  'ssh_execution_failed': 'SSH执行失败',
  'execution_failed': '执行失败',
  'timeout': '执行超时',
  'validation_success': '验证成功',
  'no_alerts_detected': '未检测到告警',
  'internal_error': '内部错误'
}

// 根据引擎状态返回标签类型
const getStatusTagType = (status: string) => {
  switch (status) {
    case 'validation_success':
      return 'success'
    case 'executing':
      return 'warning'
    case 'not_started':
    case 'no_alerts_detected':
      return 'info'
    default:
      return 'danger'
  }
}

// 获取引擎状态文本
const getEngineStatusText = (status: string) => {
  return engineStatusMap[status] || status
}

// 格式化详情键名
const formatDetailKey = (key: string) => {
  const keyMap: Record<string, string> = {
    'suricata_available': 'Suricata可用',
    'attempted_command': '尝试命令',
    'platform': '平台',
    'config_file': '配置文件',
    'config_exists': '配置存在',
    'log_dir': '日志目录',
    'log_dir_exists': '日志目录存在',
    'pcap_path': 'PCAP路径',
    'rule_file': '规则文件',
    'current_pcap': '当前PCAP',
    'executed_command': '执行命令',
    'return_code': '返回码',
    'stderr': '错误输出',
    'stdout': '标准输出',
    'remote_execution': '远程执行',
    'ssh_host': 'SSH主机',
    'ssh_user': 'SSH用户',
    'ssh_key': 'SSH密钥'
  }
  return keyMap[key] || key
}

const handleValidate = async (row: Rule) => {
  validateForm.rule_content = row.current_rule
  validateForm.rule_id = row.id
  
  // 获取最新的PCAP配置
  try {
    const res: any = await getPCAPConfig()
    if (res.success) {
      validateForm.pcap_path = res.config.default_pcap_path
    }
  } catch (error) {
    console.error('获取PCAP配置失败:', error)
  }
  
  showValidateDialog.value = true
}

const handleValidateSubmit = async () => {
  validating.value = true
  try {
    const res: any = await validateRule(validateForm)
    validationResult.value = res.validation_result
    
    if (res.validation_result.matched) {
      ElMessage.success(`验证成功！匹配到 ${res.validation_result.alert_count} 条告警`)
    } else {
      ElMessage.warning('验证完成，未匹配到告警')
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '验证失败')
  } finally {
    validating.value = false
  }
}

const handleOptimize = (row: Rule) => {
  optimizeForm.rule_id = row.id
  optimizeForm.current_rule = row.current_rule
  optimizeForm.feedback = ''
  showOptimizeDialog.value = true
}

const handleOptimizeSubmit = async () => {
  optimizing.value = true
  try {
    const res: any = await optimizeRule(optimizeForm)
    ElMessage.success('优化成功！')
    
    // 显示优化后的规则
    ElMessage({
      message: `优化后的规则：${res.optimized_rule}`,
      type: 'success',
      duration: 5000,
      showClose: true
    })
    
    showOptimizeDialog.value = false
    fetchRules()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '优化失败')
  } finally {
    optimizing.value = false
  }
}

const handlePageChange = (page: number) => {
  pagination.page = page
  fetchRules()
}

const handleSizeChange = (size: number) => {
  pagination.per_page = size
  pagination.page = 1
  fetchRules()
}


</script>

<style scoped>
.rule-list-container {
  max-width: 100%;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
}

.rule-code {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
  overflow-x: auto;
  max-height: 400px;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.details-content {
  padding: 16px 0;
}

.json-viewer {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
  overflow-x: auto;
  max-height: 500px;
}

.json-viewer pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
}

.button-group {
  display: flex;
  flex-wrap: nowrap;
  gap: 2px;
}

.button-group .el-button {
  margin: 0;
  min-width: auto;
  padding-left: 8px;
  padding-right: 8px;
}

@media (max-width: 768px) {
  .button-group {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .button-group .el-button {
    flex: 1;
    min-width: 35px;
    max-width: 50px;
    padding-left: 4px;
    padding-right: 4px;
    font-size: 12px;
  }
  
  .button-group .el-button span {
    display: none;
  }
  
  .list-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .el-form-item__content {
    flex-wrap: wrap;
  }
}
</style>
