import request from '@/utils/request'
import type { RuleGenerateForm, RuleOptimizeForm, ValidationForm } from '@/types'

// 生成规则
export const generateRule = (data: RuleGenerateForm) => {
  return request.post('/rules/generate', data)
}

// 获取规则列表
export const getRuleList = (params: { page: number; per_page: number }) => {
  return request.get('/rules', { params })
}

// 获取规则详情
export const getRuleDetail = (id: number) => {
  return request.get(`/rules/${id}`)
}

// 优化规则
export const optimizeRule = (data: RuleOptimizeForm) => {
  return request.post('/rules/optimize', data)
}

// 验证规则
export const validateRule = (data: ValidationForm) => {
  return request.post('/rules/validate', data)
}

// 获取PCAP配置
export const getPCAPConfig = () => {
  return request.get('/pcap/config')
}

// 设置PCAP配置
export const setPCAPConfig = (data: { 
  default_pcap_path?: string, 
  upload_dir?: string, 
  config_file_path?: string, 
  suricata_rules_dir?: string, 
  suricata_config?: string, 
  suricata_log_dir?: string, 
  pcap_dir?: string 
}) => {
  return request.post('/pcap/config', data)
}

// 上传PCAP文件
export const uploadPCAP = (formData: FormData) => {
  return request.post('/pcap/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取已上传的PCAP文件列表
export const getUploadedPCAPs = () => {
  return request.get('/pcap/list')
}

// 删除PCAP文件
export const deletePCAP = (filename: string) => {
  return request.delete(`/pcap/delete/${filename}`)
}

// 使用上传的PCAP文件验证规则
export const validateWithUploadedPCAP = (data: { rule_content: string; rule_id?: number; pcap_filename: string }) => {
  return request.post('/pcap/validate', data)
}

// 使用多个PCAP文件验证规则
export const validateWithMultiplePCAPs = (data: { rule_content: string; rule_id?: number; pcap_filenames: string[] }) => {
  return request.post('/pcap/validate_multiple', data)
}

// 检查Suricata引擎状态
export const checkSuricataEngine = () => {
  return request.get('/suricata/check')
}
