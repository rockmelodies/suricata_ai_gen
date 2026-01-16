// 用户相关类型
export interface User {
  id: number
  username: string
  email?: string
  role: 'admin' | 'user'
  is_active: number
  created_at: string
  updated_at: string
}

export interface LoginForm {
  username: string
  password: string
}

export interface RegisterForm {
  username: string
  password: string
  email?: string
}

export interface AuthResponse {
  access_token: string
  user: User
}

// 规则相关类型
export interface Rule {
  id: number
  vuln_name: string
  vuln_type?: string
  description: string
  original_rule: string
  current_rule: string
  created_at: string
  updated_at: string
}

export interface RuleGenerateForm {
  vuln_name: string
  vuln_description: string
  vuln_type?: string
  poc?: string
}

export interface RuleOptimizeForm {
  rule_id?: number
  current_rule: string
  feedback?: string
  validation_result?: string
}

export interface ValidationForm {
  rule_content: string
  rule_id?: number
  pcap_path: string
}

export interface ValidationResult {
  matched: boolean
  alert_count: number
  details: any
  sid_stats: any
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

export interface PaginationParams {
  page: number
  per_page: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  per_page: number
}
