import request from '@/utils/request'
import type { LoginForm, RegisterForm, AuthResponse, User } from '@/types'

// 用户登录
export const login = (data: LoginForm) => {
  return request.post<any, AuthResponse>('/auth/login', data)
}

// 用户注册
export const register = (data: RegisterForm) => {
  return request.post<any, AuthResponse>('/auth/register', data)
}

// 获取当前用户信息
export const getCurrentUser = () => {
  return request.get<any, User>('/auth/me')
}

// 获取用户列表
export const getUserList = (params: { page: number; per_page: number }) => {
  return request.get('/users', { params })
}

// 获取用户详情
export const getUserDetail = (id: number) => {
  return request.get(`/users/${id}`)
}

// 更新用户信息
export const updateUser = (id: number, data: any) => {
  return request.put(`/users/${id}`, data)
}

// 删除用户
export const deleteUser = (id: number) => {
  return request.delete(`/users/${id}`)
}
