<template>
  <div class="manage-container">
    <!-- API Key 管理 -->
    <el-card>
      <template #header>
        <div class="card-header">
          <span>🔑 Agent API Key 管理</span>
          <el-button type="primary" size="small" @click="showCreateDialog = true">
            生成新 Key
          </el-button>
        </div>
      </template>

      <el-alert
        title="API Key 用于外部系统调用 Agent API。每个 Key 只在生成时显示一次，请妥善保存。"
        type="warning" :closable="false" style="margin-bottom: 16px"
      />

      <el-table :data="keyList" v-loading="loadingKeys" border>
        <el-table-column prop="label" label="名称" min-width="140" />
        <el-table-column prop="key_preview" label="Key（已脱敏）" min-width="160">
          <template #default="{ row }">
            <code class="key-preview">{{ row.key_preview }}</code>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="last_used" label="最后使用" width="180">
          <template #default="{ row }">
            <span :class="row.last_used ? '' : 'text-muted'">
              {{ row.last_used || '从未使用' }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" align="center">
          <template #default="{ row }">
            <el-popconfirm
              title="确定删除此 Key？删除后无法恢复，使用该 Key 的调用将失败。"
              confirm-button-text="删除"
              cancel-button-text="取消"
              confirm-button-type="danger"
              @confirm="handleDelete(row.id)"
            >
              <template #reference>
                <el-button type="danger" size="small" plain>删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="!loadingKeys && keyList.length === 0" description="暂无 API Key，点击「生成新 Key」创建" />
    </el-card>

    <!-- 服务管理 -->
    <el-card style="margin-top: 16px">
      <template #header>
        <span>⚙️ 服务管理</span>
      </template>

      <el-descriptions :column="2" border size="small" style="margin-bottom: 20px">
        <el-descriptions-item label="API Key 配置">
          <el-tag :type="configStatus?.config_status?.agent_api_key_configured ? 'success' : 'warning'" size="small">
            {{ configStatus?.config_status?.agent_api_key_configured ? '环境变量已配置' : '仅使用数据库 Key' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Suricata 引擎">
          <el-tag :type="configStatus?.config_status?.suricata_available ? 'success' : 'danger'" size="small">
            {{ configStatus?.config_status?.suricata_available ? '可用' : '不可用' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="LLM Provider">
          <el-tag type="info" size="small">{{ configStatus?.config_status?.llm_provider || '-' }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Suricata 配置文件">
          <code class="path-code">{{ configStatus?.config_status?.suricata_config || '-' }}</code>
        </el-descriptions-item>
      </el-descriptions>

      <el-divider content-position="left">服务操作</el-divider>

      <div class="service-actions">
        <el-popconfirm
          title="确定重启后端服务？重启期间 API 将短暂不可用（约2-5秒）。"
          confirm-button-text="确认重启"
          cancel-button-text="取消"
          confirm-button-type="warning"
          @confirm="handleRestart"
        >
          <template #reference>
            <el-button type="warning" :loading="restarting">
              <el-icon><RefreshRight /></el-icon>
              重启后端服务
            </el-button>
          </template>
        </el-popconfirm>
        <span class="action-tip">重启后配置变更（如新增环境变量）将生效</span>
      </div>
    </el-card>

    <!-- 生成 Key 对话框 -->
    <el-dialog v-model="showCreateDialog" title="生成新 API Key" width="440px" :close-on-click-modal="false">
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="Key 名称">
          <el-input v-model="createForm.label" placeholder="如：生产环境、测试系统" clearable />
          <div class="form-tip">用于区分不同调用方，不填则自动生成</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">生成</el-button>
      </template>
    </el-dialog>

    <!-- 新 Key 展示对话框 -->
    <el-dialog v-model="showNewKeyDialog" title="🎉 API Key 已生成" width="520px" :close-on-click-modal="false" :close-on-press-escape="false">
      <el-alert
        title="请立即复制并妥善保存，此 Key 只显示一次，关闭后无法再次查看！"
        type="error" :closable="false" style="margin-bottom: 16px"
      />
      <div class="new-key-box">
        <code class="new-key-text">{{ newKeyValue }}</code>
        <el-button size="small" type="primary" @click="copyNewKey">复制</el-button>
      </div>
      <div style="margin-top: 12px; font-size: 13px; color: #606266;">
        使用方式：在请求头中添加 <code>X-API-Key: {{ newKeyValue }}</code>
      </div>
      <template #footer>
        <el-button type="primary" @click="showNewKeyDialog = false">我已保存，关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { RefreshRight } from '@element-plus/icons-vue'

const loadingKeys = ref(false)
const creating = ref(false)
const restarting = ref(false)
const keyList = ref<any[]>([])
const configStatus = ref<any>(null)
const showCreateDialog = ref(false)
const showNewKeyDialog = ref(false)
const newKeyValue = ref('')
const createForm = ref({ label: '' })

const authHeader = () => {
  const token = localStorage.getItem('access_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

const loadKeys = async () => {
  loadingKeys.value = true
  try {
    const res = await fetch('/api/agent/keys', { headers: authHeader() })
    const data = await res.json()
    if (data.success) keyList.value = data.keys
    else ElMessage.error(data.error || '加载失败')
  } catch {
    ElMessage.error('请求失败')
  } finally {
    loadingKeys.value = false
  }
}

const loadConfigStatus = async () => {
  try {
    const res = await fetch('/api/agent/status')
    configStatus.value = await res.json()
  } catch {}
}

onMounted(() => {
  loadKeys()
  loadConfigStatus()
})

const handleCreate = async () => {
  creating.value = true
  try {
    const res = await fetch('/api/agent/keys', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ label: createForm.value.label })
    })
    const data = await res.json()
    if (data.success) {
      showCreateDialog.value = false
      createForm.value.label = ''
      newKeyValue.value = data.key
      showNewKeyDialog.value = true
      await loadKeys()
    } else {
      ElMessage.error(data.error || '生成失败')
    }
  } catch {
    ElMessage.error('请求失败')
  } finally {
    creating.value = false
  }
}

const handleDelete = async (keyId: string) => {
  try {
    const res = await fetch(`/api/agent/keys/${keyId}`, {
      method: 'DELETE',
      headers: authHeader()
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success('已删除')
      await loadKeys()
    } else {
      ElMessage.error(data.error || '删除失败')
    }
  } catch {
    ElMessage.error('请求失败')
  }
}

const handleRestart = async () => {
  restarting.value = true
  try {
    const res = await fetch('/api/agent/restart', {
      method: 'POST',
      headers: authHeader()
    })
    const data = await res.json()
    if (data.success) {
      ElMessage.success(data.message)
      setTimeout(() => {
        loadConfigStatus()
        restarting.value = false
      }, 5000)
    } else {
      ElMessage.error(data.error || '重启失败')
      restarting.value = false
    }
  } catch {
    ElMessage.warning('服务正在重启，请稍候...')
    setTimeout(() => {
      loadConfigStatus()
      restarting.value = false
    }, 5000)
  }
}

const copyText = async (text: string) => {
  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(text)
    return
  }
  const ta = document.createElement('textarea')
  ta.value = text
  ta.style.cssText = 'position:fixed;opacity:0;top:0;left:0'
  document.body.appendChild(ta)
  ta.focus()
  ta.select()
  document.execCommand('copy')
  document.body.removeChild(ta)
}

const copyNewKey = async () => {
  try {
    await copyText(newKeyValue.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}
</script>

<style scoped>
.manage-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
}

.key-preview {
  background: #f0f2f5;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: monospace;
  color: #409eff;
  letter-spacing: 1px;
}

.path-code {
  font-family: monospace;
  font-size: 12px;
  color: #606266;
}

.text-muted {
  color: #c0c4cc;
  font-size: 13px;
}

.service-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-tip {
  font-size: 13px;
  color: #909399;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.new-key-box {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #1e1e1e;
  border-radius: 6px;
  padding: 12px 16px;
}

.new-key-text {
  flex: 1;
  font-family: monospace;
  font-size: 14px;
  color: #4ec9b0;
  word-break: break-all;
  letter-spacing: 0.5px;
}
</style>
