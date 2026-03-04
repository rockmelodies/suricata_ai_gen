<template>
  <div class="agent-container">
    <!-- 说明卡片 -->
    <el-card class="info-card">
      <template #header>
        <div class="card-header">
          <span>🤖 Agent API</span>
          <el-tag type="success" size="small">外部可调用</el-tag>
        </div>
      </template>
      <el-alert
        title="Agent API 允许外部系统通过一次 HTTP 调用完成：规则生成 → 自动验证 → 自动优化的完整流程"
        type="info"
        :closable="false"
        style="margin-bottom: 16px"
      />
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item label="接口地址">
          <el-tag type="info">POST</el-tag>
          <code class="endpoint-code">/api/agent/run</code>
        </el-descriptions-item>
        <el-descriptions-item label="认证方式">
          <div>
            <div><el-tag size="small">方式1</el-tag> 请求头 <code>X-API-Key: &lt;AGENT_API_KEY&gt;</code></div>
            <div style="margin-top: 4px"><el-tag size="small">方式2</el-tag> 请求头 <code>Authorization: Bearer &lt;token&gt;</code></div>
          </div>
        </el-descriptions-item>
        <el-descriptions-item label="API Key 配置">
          在后端 <code>.env</code> 文件中设置 <code>AGENT_API_KEY=your_secret_key</code>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <!-- 在线测试 -->
    <el-card style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>🧪 在线测试</span>
          <el-button size="small" type="info" plain @click="showApiDoc = !showApiDoc">
            {{ showApiDoc ? '隐藏文档' : '查看文档' }}
          </el-button>
        </div>
      </template>

      <!-- API 文档 -->
      <el-collapse-transition>
        <div v-if="showApiDoc" class="api-doc">
          <el-table :data="paramDocs" border size="small" style="margin-bottom: 16px">
            <el-table-column prop="name" label="参数名" width="180" />
            <el-table-column prop="type" label="类型" width="100" />
            <el-table-column prop="required" label="必填" width="80">
              <template #default="{ row }">
                <el-tag :type="row.required ? 'danger' : 'info'" size="small">
                  {{ row.required ? '必填' : '可选' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="desc" label="说明" />
          </el-table>
        </div>
      </el-collapse-transition>

      <el-form :model="testForm" label-width="130px" size="default">
        <el-form-item label="API Key">
          <el-input v-model="testForm.apiKey" placeholder="输入 AGENT_API_KEY" show-password clearable />
        </el-form-item>
        <el-form-item label="漏洞名称" required>
          <el-input v-model="testForm.vuln_name" placeholder="如：用友NC SQL注入漏洞" clearable />
        </el-form-item>
        <el-form-item label="漏洞类型">
          <el-select v-model="testForm.vuln_type" placeholder="请选择" clearable style="width: 100%">
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
        <el-form-item label="漏洞描述" required>
          <el-input v-model="testForm.vuln_description" type="textarea" :rows="3"
            placeholder="详细描述漏洞特征、攻击方式等" />
        </el-form-item>
        <el-form-item label="POC示例">
          <el-input v-model="testForm.poc" type="textarea" :rows="2"
            placeholder="（可选）提供POC可生成更准确的规则" />
        </el-form-item>
        <el-form-item label="PCAP文件">
          <el-select v-model="testForm.pcap_filename" placeholder="选择已上传的PCAP文件（可选）" clearable
            style="width: 100%" :loading="loadingPcaps">
            <el-option v-for="p in pcapList" :key="p.filename" :label="p.filename" :value="p.filename" />
          </el-select>
          <div class="form-tip">不选则只生成规则，不进行验证</div>
        </el-form-item>
        <el-form-item label="自动优化">
          <el-switch v-model="testForm.auto_optimize" />
          <span class="switch-label">验证未匹配时自动优化规则</span>
        </el-form-item>
        <el-form-item label="最大优化轮次" v-if="testForm.auto_optimize">
          <el-input-number v-model="testForm.max_optimize_rounds" :min="1" :max="5" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="running" @click="handleRun">
            <el-icon v-if="!running"><VideoPlay /></el-icon>
            {{ running ? '执行中...' : '执行 Agent' }}
          </el-button>
          <el-button @click="fillExample">填入示例</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 执行结果 -->
    <el-card v-if="agentResult" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>📊 执行结果</span>
          <el-tag :type="agentResult.status === 'completed' ? 'success' : 'danger'" size="large">
            {{ agentResult.status === 'completed' ? '✅ 完成' : '❌ 失败' }}
          </el-tag>
        </div>
      </template>

      <!-- 执行步骤 -->
      <div class="steps-section">
        <div class="section-title">执行步骤</div>
        <el-steps :space="200" finish-status="success" style="margin: 16px 0">
          <el-step
            v-for="step in agentResult.steps"
            :key="step.step"
            :title="stepLabel(step.step)"
            :status="stepStatus(step.status)"
            :description="stepDesc(step)"
          />
        </el-steps>
      </div>

      <el-divider />

      <el-tabs v-model="resultTab">
        <el-tab-pane label="生成的规则" name="rule">
          <div v-if="agentResult.final_rule">
            <div class="result-actions">
              <el-button size="small" type="success" @click="copyRule(agentResult.final_rule)">
                <el-icon><DocumentCopy /></el-icon> 复制规则
              </el-button>
              <el-tag v-if="agentResult.optimize_history?.length" type="warning" size="small">
                经过 {{ agentResult.optimize_history.length }} 轮优化
              </el-tag>
            </div>
            <div class="rule-code">
              <pre><code>{{ agentResult.final_rule }}</code></pre>
            </div>
          </div>
          <el-empty v-else description="未生成规则" />
        </el-tab-pane>

        <el-tab-pane label="验证结果" name="validation" v-if="agentResult.validation_result">
          <el-row :gutter="20" style="margin-bottom: 16px">
            <el-col :span="8">
              <el-statistic title="告警数" :value="agentResult.validation_result.alert_count">
                <template #suffix><span style="font-size:14px"> 条</span></template>
              </el-statistic>
            </el-col>
            <el-col :span="8">
              <el-statistic title="匹配状态"
                :value="agentResult.validation_result.matched ? '成功' : '未匹配'" />
            </el-col>
            <el-col :span="8">
              <el-statistic title="SID数量"
                :value="Object.keys(agentResult.validation_result.sid_stats || {}).length">
                <template #suffix><span style="font-size:14px"> 个</span></template>
              </el-statistic>
            </el-col>
          </el-row>
          <div class="json-viewer">
            <pre><code>{{ JSON.stringify(agentResult.validation_result, null, 2) }}</code></pre>
          </div>
        </el-tab-pane>

        <el-tab-pane label="优化历史" name="optimize" v-if="agentResult.optimize_history?.length">
          <el-timeline>
            <el-timeline-item
              v-for="(h, i) in agentResult.optimize_history"
              :key="i"
              :timestamp="`第 ${h.round} 轮优化`"
              placement="top"
            >
              <el-card size="small">
                <div class="rule-code small">
                  <pre><code>{{ h.optimized_rule }}</code></pre>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-tab-pane>

        <el-tab-pane label="原始响应" name="raw">
          <div class="json-viewer">
            <pre><code>{{ JSON.stringify(agentResult, null, 2) }}</code></pre>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- curl 示例 -->
    <el-card style="margin-top: 16px">
      <template #header>
        <span>📋 调用示例</span>
      </template>
      <el-tabs v-model="exampleTab">
        <el-tab-pane label="curl" name="curl">
          <div class="code-block">
            <el-button size="small" class="copy-btn" @click="copyCurl">复制</el-button>
            <pre><code>{{ curlExample }}</code></pre>
          </div>
        </el-tab-pane>
        <el-tab-pane label="Python" name="python">
          <div class="code-block">
            <el-button size="small" class="copy-btn" @click="copyPython">复制</el-button>
            <pre><code>{{ pythonExample }}</code></pre>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { VideoPlay, DocumentCopy } from '@element-plus/icons-vue'
import { getUploadedPCAPs } from '@/api/rules'

const showApiDoc = ref(false)
const running = ref(false)
const loadingPcaps = ref(false)
const pcapList = ref<any[]>([])
const agentResult = ref<any>(null)
const resultTab = ref('rule')
const exampleTab = ref('curl')

const testForm = reactive({
  apiKey: '',
  vuln_name: '',
  vuln_type: '',
  vuln_description: '',
  poc: '',
  pcap_filename: '',
  auto_optimize: false,
  max_optimize_rounds: 2
})

const paramDocs = [
  { name: 'vuln_name', type: 'string', required: true, desc: '漏洞名称，如：用友NC SQL注入漏洞' },
  { name: 'vuln_description', type: 'string', required: true, desc: '漏洞详细描述，越详细生成的规则越准确' },
  { name: 'vuln_type', type: 'string', required: false, desc: '漏洞类型：SQL注入、命令注入、文件读取等' },
  { name: 'poc', type: 'string', required: false, desc: 'POC示例，提供后可生成更精准的规则' },
  { name: 'pcap_filename', type: 'string', required: false, desc: '已上传的PCAP文件名，不填则跳过验证步骤' },
  { name: 'auto_optimize', type: 'boolean', required: false, desc: '验证未匹配时是否自动优化规则，默认 false' },
  { name: 'max_optimize_rounds', type: 'integer', required: false, desc: '最大自动优化轮次，默认 2，最大 5' }
]

const stepLabel = (step: string) => {
  if (step === 'generate') return '生成规则'
  if (step === 'validate') return '验证规则'
  if (step.startsWith('optimize')) return `优化 ${step.replace('optimize_round_', '')} 轮`
  return step
}

const stepStatus = (status: string) => {
  if (status === 'done') return 'success'
  if (status === 'failed') return 'error'
  if (status === 'running') return 'process'
  return 'wait'
}

const stepDesc = (step: any) => {
  if (step.status === 'skipped') return step.reason || '已跳过'
  if (step.step === 'validate' && step.status === 'done') {
    return step.matched ? `匹配 ${step.alert_count} 条告警` : '未匹配'
  }
  return ''
}

const baseUrl = computed(() => window.location.origin)

const curlExample = computed(() => `curl -X POST ${baseUrl.value}/api/agent/run \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your_agent_api_key" \\
  -d '{
    "vuln_name": "用友NC SQL注入漏洞",
    "vuln_description": "用友NC系统某接口存在SQL注入漏洞",
    "vuln_type": "SQL注入",
    "pcap_filename": "attack.pcap",
    "auto_optimize": true,
    "max_optimize_rounds": 2
  }'`)

const pythonExample = computed(() => `import requests

url = "${baseUrl.value}/api/agent/run"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "your_agent_api_key"
}
payload = {
    "vuln_name": "用友NC SQL注入漏洞",
    "vuln_description": "用友NC系统某接口存在SQL注入漏洞",
    "vuln_type": "SQL注入",
    "auto_optimize": True,
    "max_optimize_rounds": 2
}

response = requests.post(url, json=payload, headers=headers)
result = response.json()
print("状态:", result["status"])
print("生成的规则:", result["final_rule"])`)

onMounted(async () => {
  loadingPcaps.value = true
  try {
    const res: any = await getUploadedPCAPs()
    if (res.success) pcapList.value = res.pcaps
  } catch {}
  loadingPcaps.value = false
})

const handleRun = async () => {
  if (!testForm.vuln_name || !testForm.vuln_description) {
    ElMessage.warning('请填写漏洞名称和漏洞描述')
    return
  }
  running.value = true
  agentResult.value = null
  try {
    const headers: any = { 'Content-Type': 'application/json' }
    if (testForm.apiKey) headers['X-API-Key'] = testForm.apiKey
    else {
      const token = localStorage.getItem('access_token')
      if (token) headers['Authorization'] = `Bearer ${token}`
    }

    const payload: any = {
      vuln_name: testForm.vuln_name,
      vuln_description: testForm.vuln_description,
      vuln_type: testForm.vuln_type || undefined,
      poc: testForm.poc || undefined,
      auto_optimize: testForm.auto_optimize,
      max_optimize_rounds: testForm.max_optimize_rounds
    }
    if (testForm.pcap_filename) payload.pcap_filename = testForm.pcap_filename

    const res = await fetch('/api/agent/run', {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    })
    const data = await res.json()
    agentResult.value = data
    resultTab.value = 'rule'

    if (data.status === 'completed') {
      ElMessage.success('Agent 执行完成')
    } else {
      ElMessage.error(data.error || 'Agent 执行失败')
    }
  } catch (e: any) {
    ElMessage.error('请求失败: ' + e.message)
  } finally {
    running.value = false
  }
}

const fillExample = () => {
  testForm.vuln_name = '用友NC SQL注入漏洞'
  testForm.vuln_type = 'SQL注入'
  testForm.vuln_description = '用友NC系统 /uapws/service/xxx 接口的 id 参数存在SQL注入漏洞，攻击者可通过构造恶意SQL语句获取数据库敏感信息'
  testForm.poc = "GET /uapws/service/xxx?id=1' OR '1'='1"
}

const handleReset = () => {
  Object.assign(testForm, {
    apiKey: '', vuln_name: '', vuln_type: '', vuln_description: '',
    poc: '', pcap_filename: '', auto_optimize: false, max_optimize_rounds: 2
  })
  agentResult.value = null
}

const copyRule = async (rule: string) => {
  try {
    await navigator.clipboard.writeText(rule)
    ElMessage.success('已复制到剪贴板')
  } catch { ElMessage.error('复制失败') }
}

const copyCurl = async () => {
  try {
    await navigator.clipboard.writeText(curlExample.value)
    ElMessage.success('已复制')
  } catch { ElMessage.error('复制失败') }
}

const copyPython = async () => {
  try {
    await navigator.clipboard.writeText(pythonExample.value)
    ElMessage.success('已复制')
  } catch { ElMessage.error('复制失败') }
}
</script>

<style scoped>
.agent-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
}

.endpoint-code {
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: monospace;
  margin-left: 8px;
  color: #409eff;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.switch-label {
  margin-left: 10px;
  font-size: 13px;
  color: #606266;
}

.api-doc {
  margin-bottom: 20px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.steps-section {
  padding: 8px 0;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  margin-bottom: 8px;
}

.result-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.rule-code {
  background: #1e1e1e;
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

.rule-code.small pre {
  font-size: 12px;
}

.json-viewer {
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
  max-height: 400px;
}

.json-viewer pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #303133;
}

.code-block {
  position: relative;
  background: #1e1e1e;
  border-radius: 6px;
  padding: 16px;
  overflow-x: auto;
}

.code-block pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.7;
  color: #d4d4d4;
  white-space: pre;
}

.copy-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  opacity: 0.7;
}

.copy-btn:hover {
  opacity: 1;
}
</style>
