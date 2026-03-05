<template>
  <div class="create-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🎯 规则生成与验证一体化</span>
        </div>
      </template>

      <el-row :gutter="20">
        <!-- 左侧：生成规则 (AI生成Suricata规则) -->
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card shadow="never">
            <template #header>
              <div class="section-header">
                <span>🤖 AI生成规则</span>
              </div>
            </template>

            <el-form
              ref="formRef"
              :model="form"
              :rules="rules"
              label-width="auto"
              size="large"
              :label-position="labelPosition"
            >
              <el-form-item label="漏洞名称" prop="vuln_name">
                <el-input
                  v-model="form.vuln_name"
                  placeholder="请输入漏洞名称，如：用友NC SQL注入漏洞"
                  clearable
                />
              </el-form-item>

              <el-form-item label="漏洞类型" prop="vuln_type">
                <el-select
                  v-model="form.vuln_type"
                  placeholder="请选择漏洞类型"
                  clearable
                  style="width: 100%"
                >
                  <el-option label="SQL注入" value="SQL注入" />
                  <el-option label="命令注入" value="命令注入" />
                  <el-option label="文件读取" value="文件读取" />
                  <el-option label="目录遍历" value="目录遍历" />
                  <el-option label="路径遍历" value="路径遍历" />
                  <el-option label="服务端请求伪造(SSRF)" value="服务端请求伪造(SSRF)" />
                  <el-option label="文件上传" value="文件上传" />
                  <el-option label="未授权访问" value="未授权访问" />
                  <el-option label="权限绕过" value="权限绕过" />
                </el-select>
              </el-form-item>

              <el-form-item label="漏洞描述" prop="vuln_description">
                <el-input
                  v-model="form.vuln_description"
                  type="textarea"
                  :rows="4"
                  placeholder="请详细描述漏洞特征、攻击方式等信息"
                />
              </el-form-item>

              <el-form-item label="POC示例">
                <el-input
                  v-model="form.poc"
                  type="textarea"
                  :rows="3"
                  placeholder="（可选）提供POC示例可以帮助生成更准确的规则"
                />
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  :loading="generating"
                  @click="handleGenerate"
                  style="width: 100%"
                >
                  <el-icon v-if="!generating"><MagicStick /></el-icon>
                  {{ generating ? '生成中...' : '🤖 AI生成规则' }}
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>

        <!-- 右侧：验证规则 (PCAP验证) -->
        <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12">
          <el-card shadow="never">
            <template #header>
              <div class="section-header">
                <span>✅ 验证规则</span>
              </div>
            </template>

            <el-form
              ref="validateFormRef"
              :model="validateForm"
              :rules="validateRules"
              label-width="auto"
              size="large"
              :label-position="labelPosition"
            >
              <el-form-item label="规则内容" prop="rule_content">
                <el-input
                  v-model="validateForm.rule_content"
                  type="textarea"
                  :rows="6"
                  placeholder="请输入要验证的Suricata规则，或从左侧生成结果获取"
                />
              </el-form-item>

              <el-form-item label="PCAP路径" prop="pcap_path">
                <el-input
                  v-model="validateForm.pcap_path"
                  placeholder="请输入PCAP文件所在目录路径"
                >
                  <template #prepend>
                    <el-icon><FolderOpened /></el-icon>
                  </template>
                  <template #append>
                    <el-button @click="refreshPCAPConfig">刷新</el-button>
                  </template>
                </el-input>
                <div class="form-tip">
                  <el-icon><InfoFilled /></el-icon>
                  Windows: C:\pcap_check | Linux: /home/kali/pcap_check
                </div>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="primary"
                  :loading="validating"
                  @click="handleValidate"
                  style="width: 100%"
                >
                  <el-icon v-if="!validating"><Check /></el-icon>
                  {{ validating ? '验证中...' : '🔍 开始验证' }}
                </el-button>
              </el-form-item>

              <el-form-item>
                <el-button
                  type="success"
                  plain
                  @click="loadGeneratedRule"
                  :disabled="!generatedRule"
                  style="width: 100%"
                >
                  <el-icon><DocumentCopy /></el-icon>
                  从生成结果加载
                </el-button>
              </el-form-item>
            </el-form>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 生成结果区域 -->
    <el-card v-if="generatedRule" style="margin-top: 20px">
      <template #header>
        <div class="result-header">
          <span>✨ 生成结果 (ID: {{ ruleId }})</span>
          <div class="result-actions">
            <el-button type="success" size="small" @click="handleCopy">
              <el-icon><DocumentCopy /></el-icon>
              复制规则
            </el-button>
            <el-button type="warning" size="small" @click="loadGeneratedRule">
              <el-icon><DocumentCopy /></el-icon>
              加载到验证区
            </el-button>
          </div>
        </div>
      </template>

      <div class="rule-result">
        <el-alert
          title="生成成功"
          type="success"
          :closable="false"
          style="margin-bottom: 16px"
        >
          <template #default>
            <p>规则ID: {{ ruleId }}</p>
            <p>请仔细检查生成的规则是否符合要求</p>
          </template>
        </el-alert>

        <div class="rule-code">
          <pre><code>{{ generatedRule }}</code></pre>
        </div>
      </div>
    </el-card>

    <!-- 验证结果区域 -->
    <el-card v-if="validationResult" style="margin-top: 20px">
      <template #header>
        <div class="result-header">
          <span>📊 验证结果</span>
          <el-tag
            :type="validationResult.matched ? 'success' : 'info'"
            size="large"
          >
            {{ validationResult.matched ? '✅ 匹配成功' : '⚠️ 未匹配' }}
          </el-tag>
        </div>
      </template>

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

      <!-- 详细信息 -->
      <el-divider />

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

        <el-tab-pane label="🛠️ 原始数据" name="raw">
          <div class="json-viewer">
            <pre><code>{{ JSON.stringify(validationResult, null, 2) }}</code></pre>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, onActivated } from 'vue'
import { ElMessage } from 'element-plus'
import {
  MagicStick,
  DocumentCopy,
  Check,
  FolderOpened,
  InfoFilled
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { RuleGenerateForm, ValidationForm, ValidationResult } from '@/types'
import { generateRule, getPCAPConfig } from '@/api/rules'
import { validateRule } from '@/api/rules'

const formRef = ref<FormInstance>()
const validateFormRef = ref<FormInstance>()
const generating = ref(false)
const validating = ref(false)
const generatedRule = ref('')
const ruleId = ref<number>()
const validationResult = ref<ValidationResult | null>(null)
const activeTab = ref('details')
const labelPosition = ref<'left' | 'top'>('left')

// 响应式处理
const handleResize = () => {
  if (window.innerWidth < 768) {
    labelPosition.value = 'top'
  } else {
    labelPosition.value = 'left'
  }
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
  // 页面加载时获取PCAP配置
  refreshPCAPConfig()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 刷新PCAP配置
const refreshPCAPConfig = async () => {
  try {
    const res: any = await getPCAPConfig()
    if (res.success) {
      validateForm.pcap_path = res.config.default_pcap_path
      ElMessage.success('PCAP配置已更新')
    }
  } catch (error) {
    console.error('获取PCAP配置失败:', error)
    ElMessage.error('获取PCAP配置失败')
  }
}

// 当组件被激活时（例如从其他页面返回）
onActivated(() => {
  // 获取最新PCAP配置
  refreshPCAPConfig()
})

const form = reactive<RuleGenerateForm>({
  vuln_name: '',
  vuln_description: '',
  vuln_type: '',
  poc: ''
})

const validateForm = reactive<ValidationForm>({
  rule_content: '',
  pcap_path: '', // 初始化为空，稍后从API获取
  rule_id: undefined
})

const rules: FormRules = {
  vuln_name: [
    { required: true, message: '请输入漏洞名称', trigger: 'blur' }
  ],
  vuln_description: [
    { required: true, message: '请输入漏洞描述', trigger: 'blur' },
    { min: 10, message: '漏洞描述至少10个字符', trigger: 'blur' }
  ]
}

const validateRules: FormRules = {
  rule_content: [
    { required: true, message: '请输入规则内容', trigger: 'blur' }
  ],
  pcap_path: [
    { required: true, message: '请输入PCAP路径', trigger: 'blur' }
  ]
}

const customColors = [
  { color: '#f56c6c', percentage: 20 },
  { color: '#e6a23c', percentage: 40 },
  { color: '#5cb87a', percentage: 60 },
  { color: '#1989fa', percentage: 80 },
  { color: '#6f7ad3', percentage: 100 }
]

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

const handleGenerate = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      generating.value = true
      try {
        const res: any = await generateRule(form)
        generatedRule.value = res.generated_rule
        ruleId.value = res.rule_id
        ElMessage.success('规则生成成功！')
        
        // 自动加载到验证区
        validateForm.rule_content = res.generated_rule
        validateForm.rule_id = res.rule_id
      } catch (error: any) {
        ElMessage.error(error.response?.data?.error || '生成失败')
      } finally {
        generating.value = false
      }
    }
  })
}

const handleValidate = async () => {
  if (!validateFormRef.value) return

  await validateFormRef.value.validate(async (valid) => {
    if (valid) {
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
  })
}

const handleCopy = async () => {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(generatedRule.value)
    } else {
      const ta = document.createElement('textarea')
      ta.value = generatedRule.value
      ta.style.cssText = 'position:fixed;opacity:0;top:0;left:0'
      document.body.appendChild(ta)
      ta.focus(); ta.select()
      document.execCommand('copy')
      document.body.removeChild(ta)
    }
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败')
  }
}

const loadGeneratedRule = () => {
  if (generatedRule.value) {
    validateForm.rule_content = generatedRule.value
    validateForm.rule_id = ruleId.value
    ElMessage.success('规则已加载到验证区')
  }
}

const handleReset = () => {
  formRef.value?.resetFields()
  validateFormRef.value?.resetFields()
  generatedRule.value = ''
  ruleId.value = undefined
  validationResult.value = null
}
</script>

<style scoped>
.create-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
}

.form-tip {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
  font-size: 12px;
  color: #909399;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-actions {
  display: flex;
  gap: 8px;
}

.rule-result {
  margin-top: 16px;
}

.rule-code {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
  overflow-x: auto;
}

.rule-code pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
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

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .result-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .el-form-item__content {
    flex-wrap: wrap;
  }
  
  .el-row {
    flex-direction: column;
  }
  
  .el-col {
    width: 100%;
    margin-bottom: 20px;
  }
  
  .el-col:last-child {
    margin-bottom: 0;
  }
}
</style>