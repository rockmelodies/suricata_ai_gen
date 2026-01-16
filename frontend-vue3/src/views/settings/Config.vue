<template>
  <div class="config-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>⚙️ 系统配置</span>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="config"
        :rules="rules"
        label-width="auto"
        size="large"
        :label-position="labelPosition"
      >
        <el-form-item label="默认PCAP路径" prop="default_pcap_path">
          <el-input
            v-model="config.default_pcap_path"
            placeholder="请输入PCAP文件所在目录路径"
            @blur="saveConfig"
          >
            <template #prepend>
              <el-icon><FolderOpened /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="saveConfig" plain>保存</el-button>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            默认用于规则验证的PCAP文件目录路径
          </div>
        </el-form-item>

        <el-form-item label="上传目录" prop="upload_dir">
          <el-input
            v-model="config.upload_dir"
            placeholder="请输入上传文件保存目录"
            @blur="saveConfig"
          >
            <template #prepend>
              <el-icon><Upload /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="saveConfig" plain>保存</el-button>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            上传的PCAP文件保存目录，默认为 'uploads'
          </div>
        </el-form-item>

        <el-divider />

        <h3>🔧 Suricata配置</h3>

        <el-form-item label="规则目录" prop="suricata_rules_dir">
          <el-input
            v-model="config.suricata_rules_dir"
            placeholder="请输入Suricata规则目录路径"
            @blur="saveConfig"
          >
            <template #prepend>
              <el-icon><Folder /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="saveConfig" plain>保存</el-button>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            Suricata规则文件存放目录
          </div>
        </el-form-item>

        <el-form-item label="配置文件" prop="suricata_config">
          <el-input
            v-model="config.suricata_config"
            placeholder="请输入Suricata配置文件路径"
            @blur="saveConfig"
          >
            <template #prepend>
              <el-icon><Document /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="saveConfig" plain>保存</el-button>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            Suricata配置文件路径
          </div>
        </el-form-item>

        <el-form-item label="日志目录" prop="suricata_log_dir">
          <el-input
            v-model="config.suricata_log_dir"
            placeholder="请输入Suricata日志目录路径"
            @blur="saveConfig"
          >
            <template #prepend>
              <el-icon><FolderOpened /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="saveConfig" plain>保存</el-button>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            Suricata日志文件存放目录
          </div>
        </el-form-item>

        <el-form-item label="PCAP目录" prop="pcap_dir">
          <el-input
            v-model="config.pcap_dir"
            placeholder="请输入PCAP文件目录路径"
            @blur="saveConfig"
          >
            <template #prepend>
              <el-icon><Folder /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="saveConfig" plain>保存</el-button>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            PCAP文件存放目录
          </div>
        </el-form-item>

        <el-divider />

        <h3>🔗 SSH远程验证配置</h3>

        <el-form-item label="SSH主机" prop="ssh_host">
          <el-input
            v-model="config.ssh_host"
            placeholder="请输入SSH主机地址，如：192.168.1.100"
            @blur="saveConfig"
          >
            <template #prepend>
              <el-icon><Connection /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="saveConfig" plain>保存</el-button>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            用于远程验证的SSH主机地址
          </div>
        </el-form-item>

        <el-form-item label="SSH用户" prop="ssh_user">
          <el-input
            v-model="config.ssh_user"
            placeholder="请输入SSH用户名，如：kali"
            @blur="saveConfig"
          >
            <template #prepend>
              <el-icon><User /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="saveConfig" plain>保存</el-button>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            用于远程验证的SSH用户名
          </div>
        </el-form-item>

        <el-form-item label="SSH密钥路径" prop="ssh_key">
          <el-input
            v-model="config.ssh_key"
            placeholder="请输入SSH私钥文件路径（可选）"
            @blur="saveConfig"
          >
            <template #prepend>
              <el-icon><Lock /></el-icon>
            </template>
            <template #append>
              <el-button type="primary" @click="saveConfig" plain>保存</el-button>
            </template>
          </el-input>
          <div class="form-tip">
            <el-icon><InfoFilled /></el-icon>
            SSH私钥文件路径，留空则使用密码认证
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            @click="saveConfig"
          >
            <el-icon><Check /></el-icon>
            保存所有配置
          </el-button>
          <el-button @click="resetConfig">重置</el-button>
        </el-form-item>
      </el-form>

      <el-divider />

      <div class="config-info">
        <h3>📋 配置信息</h3>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="当前默认PCAP路径">
            {{ config.default_pcap_path }}
          </el-descriptions-item>
          <el-descriptions-item label="上传目录">
            {{ config.upload_dir }}
          </el-descriptions-item>
          <el-descriptions-item label="配置文件路径">
            {{ config.config_file_path }}
          </el-descriptions-item>
          <el-descriptions-item label="Suricata规则目录">
            {{ config.suricata_rules_dir }}
          </el-descriptions-item>
          <el-descriptions-item label="Suricata配置文件">
            {{ config.suricata_config }}
          </el-descriptions-item>
          <el-descriptions-item label="Suricata日志目录">
            {{ config.suricata_log_dir }}
          </el-descriptions-item>
          <el-descriptions-item label="PCAP目录">
            {{ config.pcap_dir }}
          </el-descriptions-item>
          <el-descriptions-item label="SSH主机">
            {{ config.ssh_host || '未配置' }}
          </el-descriptions-item>
          <el-descriptions-item label="SSH用户">
            {{ config.ssh_user || '未配置' }}
          </el-descriptions-item>
          <el-descriptions-item label="SSH密钥路径">
            {{ config.ssh_key || '未配置' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Check,
  FolderOpened,
  InfoFilled,
  Upload,
  Folder,
  Document,
  Connection,
  User,
  Lock
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { getPCAPConfig, setPCAPConfig } from '@/api/rules'

const formRef = ref<FormInstance>()
const labelPosition = ref<'left' | 'top'>('left')

// 配置数据
const config = reactive({
  default_pcap_path: '/home/kali/pcap_check',
  upload_dir: 'uploads',
  config_file_path: 'pcap_config.json',
  suricata_rules_dir: 'C:\\Program Files\\Suricata\\rules',
  suricata_config: 'C:\\Program Files\\Suricata\\suricata.yaml',
  suricata_log_dir: 'C:\\Program Files\\Suricata\\log',
  pcap_dir: 'C:\\pcap_check',
  ssh_host: '',
  ssh_user: '',
  ssh_key: ''
})

// 表单验证规则
const rules: FormRules = {
  default_pcap_path: [
    { required: true, message: '请输入默认PCAP路径', trigger: 'blur' }
  ],
  upload_dir: [
    { required: true, message: '请输入上传目录', trigger: 'blur' }
  ],
  suricata_rules_dir: [
    { required: true, message: '请输入Suricata规则目录', trigger: 'blur' }
  ],
  suricata_config: [
    { required: true, message: '请输入Suricata配置文件路径', trigger: 'blur' }
  ],
  suricata_log_dir: [
    { required: true, message: '请输入Suricata日志目录', trigger: 'blur' }
  ],
  pcap_dir: [
    { required: true, message: '请输入PCAP目录', trigger: 'blur' }
  ],
  ssh_host: [
    { message: '请输入SSH主机地址', trigger: 'blur' }
  ],
  ssh_user: [
    { message: '请输入SSH用户名', trigger: 'blur' }
  ]
}

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
  loadConfig()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 加载配置
const loadConfig = async () => {
  try {
    const res: any = await getPCAPConfig()
    if (res.success) {
      config.default_pcap_path = res.config.default_pcap_path
      config.upload_dir = res.config.upload_dir
      config.config_file_path = res.config.config_file_path
      config.suricata_rules_dir = res.config.suricata_rules_dir
      config.suricata_config = res.config.suricata_config
      config.suricata_log_dir = res.config.suricata_log_dir
      config.pcap_dir = res.config.pcap_dir
      config.ssh_host = res.config.ssh_host || ''
      config.ssh_user = res.config.ssh_user || ''
      config.ssh_key = res.config.ssh_key || ''
    }
  } catch (error) {
    console.error('加载配置失败:', error)
    ElMessage.error('加载配置失败')
  }
}

// 保存配置
const saveConfig = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const res: any = await setPCAPConfig({ 
          default_pcap_path: config.default_pcap_path,
          upload_dir: config.upload_dir,
          suricata_rules_dir: config.suricata_rules_dir,
          suricata_config: config.suricata_config,
          suricata_log_dir: config.suricata_log_dir,
          pcap_dir: config.pcap_dir,
          ssh_host: config.ssh_host,
          ssh_user: config.ssh_user,
          ssh_key: config.ssh_key
        })
        if (res.success) {
          ElMessage.success(res.message)
        } else {
          ElMessage.error(res.message)
        }
      } catch (error: any) {
        ElMessage.error(error.response?.data?.error || '保存配置失败')
      }
    }
  })
}

// 重置配置
const resetConfig = () => {
  ElMessageBox.confirm(
    '确定要重置所有配置吗？此操作不可撤销。',
    '确认重置',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    config.default_pcap_path = '/home/kali/pcap_check'
    config.upload_dir = 'uploads'
    config.config_file_path = 'pcap_config.json'
    config.suricata_rules_dir = 'C:\\Program Files\\Suricata\\rules'
    config.suricata_config = 'C:\\Program Files\\Suricata\\suricata.yaml'
    config.suricata_log_dir = 'C:\\Program Files\\Suricata\\log'
    config.pcap_dir = 'C:\\pcap_check'
    config.ssh_host = ''
    config.ssh_user = ''
    config.ssh_key = ''
    ElMessage.success('配置已重置')
  }).catch(() => {
    // 用户取消操作
  })
}
</script>

<style scoped>
.config-container {
  max-width: 1200px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
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

.config-info {
  margin-top: 30px;
}

.config-info h3 {
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .el-form-item__content {
    flex-wrap: wrap;
  }
}
</style>