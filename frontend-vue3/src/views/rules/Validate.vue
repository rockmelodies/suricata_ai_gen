<template>
  <div class="validate-container">
    <el-card>
      <template #header>
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <span>✅ 验证Suricata规则</span>
          <div>
            <el-button @click="openPCAPListDialog" size="small" type="info" plain>
              <el-icon><List /></el-icon>
              已上传文件
            </el-button>
            <el-button @click="openPCAPUploadDialog" size="small" type="primary" plain>
              <el-icon><Upload /></el-icon>
              上传PCAP
            </el-button>
          </div>
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
        <el-form-item label="规则内容" prop="rule_content">
          <el-input
            v-model="form.rule_content"
            type="textarea"
            :rows="6"
            placeholder="请输入要验证的Suricata规则"
          />
        </el-form-item>

        <el-form-item label="PCAP路径" prop="pcap_path">
          <el-input
            v-model="form.pcap_path"
            placeholder="请输入PCAP文件所在目录路径"
            @blur="handleSavePCAPConfig"
          >
            <template #prepend>
              <el-icon><FolderOpened /></el-icon>
            </template>
            <template #append>
              <div style="display: flex; gap: 2px;">
                <el-button type="primary" @click="handleSavePCAPConfig" plain>保存</el-button>
                <el-dropdown>
                  <el-button type="primary" plain>
                    更多操作<el-icon><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="openPCAPUploadDialog">
                        <el-icon><Upload /></el-icon>
                        上传PCAP文件
                      </el-dropdown-item>
                      <el-dropdown-item @click="openPCAPListDialog">
                        <el-icon><List /></el-icon>
                        已上传文件
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
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
          >
            <el-icon v-if="!validating"><Check /></el-icon>
            {{ validating ? '验证中...' : '开始验证' }}
          </el-button>
          <el-button @click="handleReset">重置</el-button>
          <el-button @click="handleLoadFromList">
            <el-icon><List /></el-icon>
            从列表加载
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 验证结果 -->
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

      <el-tabs v-model="activeTab">
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

    <!-- 从列表选择规则对话框 -->
    <el-dialog
      v-model="showSelectDialog"
      title="选择规则"
      width="800px"
    >
      <el-table
        :data="rulesList"
        border
        @row-click="handleSelectRule"
        style="cursor: pointer"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="vuln_name" label="漏洞名称" min-width="200" />
        <el-table-column prop="vuln_type" label="类型" width="120" />
        <el-table-column prop="created_at" label="创建时间" width="180" />
      </el-table>

      <template #footer>
        <el-button @click="showSelectDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- PCAP上传对话框 -->
    <el-dialog
      v-model="showPCAPUploadDialog"
      title="上传PCAP文件"
      width="500px"
    >
      <div style="text-align: center; padding: 20px 0;">
        <el-upload
          drag
          :auto-upload="false"
          :show-file-list="false"
          accept=".pcap"
          :on-change="(file) => {
            const event = { target: { files: [file.raw] } } as unknown as Event;
            handleFileChange(event);
          }"
        >
          <el-icon class="el-icon--upload"><Upload /></el-icon>
          <div class="el-upload__text">
            将PCAP文件拖到此处，或<em>点击上传</em>
          </div>
          <template #tip>
            <div class="el-upload__tip">
              只能上传PCAP格式的文件
            </div>
          </template>
        </el-upload>
      </div>
      
      <template #footer>
        <el-button @click="closePCAPUploadDialog">关闭</el-button>
      </template>
    </el-dialog>

    <!-- PCAP文件列表对话框 -->
    <el-dialog
      v-model="showPCAPListDialog"
      title="已上传的PCAP文件"
      width="800px"
    >
      <el-table
        :data="uploadedPCAPs"
        v-loading="loadingPCAPs"
        border
        style="width: 100%"
      >
        <el-table-column prop="filename" label="文件名" width="250" show-overflow-tooltip />
        <el-table-column prop="size" label="大小" width="120">
          <template #default="{ row }">
            {{ Math.round(row.size / 1024) }} KB
          </template>
        </el-table-column>
        <el-table-column prop="upload_time" label="上传时间" width="180">
          <template #default="{ row }">
            {{ new Date(row.upload_time * 1000).toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="handleValidateWithUploadedPCAP(row.filename)"
            >
              <el-icon><Check /></el-icon>
              验证
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="handleDeletePCAP(row.filename)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <template #footer>
        <el-button @click="showPCAPListDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Check,
  FolderOpened,
  InfoFilled,
  List,
  Upload,
  ArrowDown,
  Delete
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { ValidationForm, ValidationResult } from '@/types'
import { validateRule, getRuleList, getPCAPConfig, setPCAPConfig, uploadPCAP, getUploadedPCAPs, deletePCAP, validateWithUploadedPCAP } from '@/api/rules'

const formRef = ref<FormInstance>()
const validating = ref(false)
const validationResult = ref<ValidationResult | null>(null)
const activeTab = ref('details')
const showSelectDialog = ref(false)
const rulesList = ref<any[]>([])
const labelPosition = ref<'left' | 'top'>('left')

// PCAP管理相关
const pcapConfig = ref({ default_pcap_path: '/home/kali/pcap_check' })
const uploadedPCAPs = ref<any[]>([])
const showPCAPUploadDialog = ref(false)
const showPCAPListDialog = ref(false)
const fileInputRef = ref<HTMLInputElement>()
const uploading = ref(false)
const loadingPCAPs = ref(false)

const form = reactive<ValidationForm>({
  rule_content: '',
  pcap_path: '/home/kali/pcap_check'
})

// 响应式处理
const handleResize = () => {
  if (window.innerWidth < 768) {
    labelPosition.value = 'top'
  } else {
    labelPosition.value = 'left'
  }
}

onMounted(async () => {
  handleResize()
  window.addEventListener('resize', handleResize)
  
  try {
    // 获取PCAP配置
    const configRes: any = await getPCAPConfig()
    if (configRes.success) {
      pcapConfig.value = configRes.config
      form.pcap_path = configRes.config.default_pcap_path
    }
    
    // 获取已上传的PCAP文件列表
    const pcapRes: any = await getUploadedPCAPs()
    if (pcapRes.success) {
      uploadedPCAPs.value = pcapRes.pcaps
    }
  } catch (error) {
    console.error('初始化PCAP配置失败:', error)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const rules: FormRules = {
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

const handleValidate = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      validating.value = true
      try {
        const res: any = await validateRule(form)
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

const handleReset = () => {
  formRef.value?.resetFields()
  validationResult.value = null
}

const handleLoadFromList = async () => {
  try {
    const res: any = await getRuleList({ page: 1, per_page: 50 })
    rulesList.value = res.rules || []
    showSelectDialog.value = true
  } catch (error) {
    ElMessage.error('加载规则列表失败')
  }
}

const handleSelectRule = (row: any) => {
  form.rule_content = row.current_rule
  showSelectDialog.value = false
  ElMessage.success('已加载规则')
}

// 保存PCAP配置
const handleSavePCAPConfig = async () => {
  try {
    const res: any = await setPCAPConfig({ default_pcap_path: form.pcap_path })
    if (res.success) {
      ElMessage.success(res.message)
    } else {
      ElMessage.error(res.message)
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '保存配置失败')
  }
}

// 上传PCAP文件
const handleFileChange = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) {
    return
  }
  
  if (!file.name.toLowerCase().endsWith('.pcap')) {
    ElMessage.error('只支持PCAP格式文件')
    return
  }
  
  const formData = new FormData()
  formData.append('file', file)
  
  uploading.value = true
  try {
    const res: any = await uploadPCAP(formData)
    if (res.success) {
      ElMessage.success(res.message)
      
      // 更新已上传文件列表
      await loadUploadedPCAPs()
      
      // 清空输入框
      if (target) {
        target.value = ''
      }
    } else {
      ElMessage.error(res.message)
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 加载已上传的PCAP文件列表
const loadUploadedPCAPs = async () => {
  loadingPCAPs.value = true
  try {
    const res: any = await getUploadedPCAPs()
    if (res.success) {
      uploadedPCAPs.value = res.pcaps
    }
  } catch (error) {
    ElMessage.error('加载PCAP文件列表失败')
  } finally {
    loadingPCAPs.value = false
  }
}

// 删除PCAP文件
const handleDeletePCAP = async (filename: string) => {
  try {
    const res: any = await deletePCAP(filename)
    if (res.success) {
      ElMessage.success(res.message)
      await loadUploadedPCAPs()
    } else {
      ElMessage.error(res.message)
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '删除失败')
  }
}

// 使用上传的PCAP文件验证规则
const handleValidateWithUploadedPCAP = async (filename: string) => {
  if (!form.rule_content) {
    ElMessage.warning('请先输入规则内容')
    return
  }
  
  validating.value = true
  try {
    const res: any = await validateWithUploadedPCAP({
      rule_content: form.rule_content,
      rule_id: undefined, // 如果需要可以从规则列表中获取
      pcap_filename: filename
    })
    
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

// 打开PCAP上传对话框
const openPCAPUploadDialog = () => {
  showPCAPUploadDialog.value = true
}

// 打开PCAP文件列表对话框
const openPCAPListDialog = () => {
  loadUploadedPCAPs()
  showPCAPListDialog.value = true
}

// 关闭PCAP上传对话框
const closePCAPUploadDialog = () => {
  showPCAPUploadDialog.value = false
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}
</script>

<style scoped>
.validate-container {
  max-width: 1200px;
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
    margin-bottom: 16px;
  }
  
  .el-col:last-child {
    margin-bottom: 0;
  }
}
</style>
