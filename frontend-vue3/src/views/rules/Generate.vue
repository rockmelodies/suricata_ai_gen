<template>
  <div class="generate-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🤖 AI生成Suricata规则</span>
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
          >
            <el-icon v-if="!generating"><MagicStick /></el-icon>
            {{ generating ? '生成中...' : '🤖 AI生成规则' }}
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 生成结果 -->
    <el-card v-if="generatedRule" style="margin-top: 20px">
      <template #header>
        <div class="result-header">
          <span>✨ 生成结果</span>
          <div>
            <el-button
              type="success"
              size="small"
              @click="handleCopy"
            >
              <el-icon><DocumentCopy /></el-icon>
              复制规则
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="showValidateDialog = true"
            >
              <el-icon><Check /></el-icon>
              验证规则
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

    <!-- 验证对话框 -->
    <el-dialog
      v-model="showValidateDialog"
      title="验证规则"
      width="600px"
    >
      <el-form label-width="100px">
        <el-form-item label="PCAP路径">
          <el-input
            v-model="pcapPath"
            placeholder="PCAP文件路径，如：/home/kali/pcap_check"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showValidateDialog = false">取消</el-button>
        <el-button
          type="primary"
          :loading="validating"
          @click="handleValidate"
        >
          开始验证
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { MagicStick, DocumentCopy, Check } from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import type { RuleGenerateForm } from '@/types'
import { generateRule, getPCAPConfig } from '@/api/rules'
import { validateRule } from '@/api/rules'
import { useRouter } from 'vue-router'

const router = useRouter()
const formRef = ref<FormInstance>()
const generating = ref(false)
const validating = ref(false)
const generatedRule = ref('')
const ruleId = ref<number>()
const showValidateDialog = ref(false)
const pcapPath = ref('') // 初始化为空，稍后从API获取
const labelPosition = ref<'left' | 'top'>('left')

const form = reactive<RuleGenerateForm>({
  vuln_name: '',
  vuln_description: '',
  vuln_type: '',
  poc: ''
})

// 响应式处理
const handleResize = () => {
  if (window.innerWidth < 768) {
    labelPosition.value = 'top'
  } else {
    labelPosition.value = 'left'
  }
}

// 加载PCAP配置
const loadPCAPConfig = async () => {
  try {
    const res: any = await getPCAPConfig()
    if (res.success) {
      pcapPath.value = res.config.default_pcap_path
    }
  } catch (error) {
    console.error('获取PCAP配置失败:', error)
  }
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize)
  // 页面加载时获取PCAP配置
  loadPCAPConfig()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
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
      } catch (error: any) {
        ElMessage.error(error.response?.data?.error || '生成失败')
      } finally {
        generating.value = false
      }
    }
  })
}

const handleReset = () => {
  formRef.value?.resetFields()
  generatedRule.value = ''
  ruleId.value = undefined
}

const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(generatedRule.value)
    ElMessage.success('已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const handleValidate = async () => {
  if (!generatedRule.value) return

  validating.value = true
  try {
    const res: any = await validateRule({
      rule_content: generatedRule.value,
      rule_id: ruleId.value,
      pcap_path: pcapPath.value
    })

    const result = res.validation_result
    if (result.matched) {
      ElMessage.success(`验证成功！匹配到 ${result.alert_count} 条告警`)
    } else {
      ElMessage.warning('验证完成，未匹配到告警')
    }

    showValidateDialog.value = false
    
    // 跳转到验证页面查看详细结果
    router.push('/rules/validate')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.error || '验证失败')
  } finally {
    validating.value = false
  }
}
</script>

<style scoped>
.generate-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rule-result {
  margin-top: 16px;
}

.rule-code {
  background-color: #1e1e1e;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
}

.rule-code pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #d4d4d4;
  white-space: pre-wrap;
  word-break: break-all;
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
}
</style>
