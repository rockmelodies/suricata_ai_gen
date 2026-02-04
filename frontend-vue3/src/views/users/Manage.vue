<template>
  <div class="user-manage-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>👥 用户管理</span>
          <el-button 
            type="primary" 
            @click="showAddUser"
          >
            <el-icon><Plus /></el-icon>
            新增用户
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" style="margin-bottom: 20px">
        <el-form-item label="用户名">
          <el-input
            v-model="searchForm.username"
            placeholder="请输入用户名"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input
            v-model="searchForm.email"
            placeholder="请输入邮箱"
            clearable
            style="width: 200px"
          />
        </el-form-item>
        <el-form-item label="角色">
          <el-select
            v-model="searchForm.role"
            placeholder="请选择角色"
            clearable
            style="width: 120px"
          >
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">
            <el-icon><Search /></el-icon>
            搜索
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 用户表格 -->
      <el-table
        v-loading="loading"
        :data="tableData"
        border
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="avatar" label="头像" width="80">
          <template #default="{ row }">
            <el-avatar :src="row.avatar || defaultAvatar" :size="40" />
          </template>
        </el-table-column>
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="email" label="邮箱" width="200" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
              {{ row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'warning'">
              {{ row.status === 'active' ? '激活' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column prop="updated_at" label="更新时间" width="180" />
        <el-table-column label="操作"  fixed="right">
          <template #default="{ row }">
            <el-button-group class="button-group">
              <el-button
                type="primary"
                size="small"
                @click="handleEdit(row)"
              >
                <el-icon><Edit /></el-icon>
                <span v-if="!isMobile">编辑</span>
              </el-button>
              <el-button
                :type="row.status === 'active' ? 'warning' : 'success'"
                size="small"
                :disabled="row.id === userStore.user?.id"
                @click="handleToggleStatus(row)"
              >
                <el-icon><component :is="row.status === 'active' ? 'CircleCheck' : 'CircleCheckFilled'" /></el-icon>
                <span v-if="!isMobile">{{ row.status === 'active' ? '禁用' : '激活' }}</span>
              </el-button>
              <el-button
                type="info"
                size="small"
                @click="handleResetPassword(row)"
              >
                <el-icon><Lock /></el-icon>
                <span v-if="!isMobile">重置密码</span>
              </el-button>
              <el-button
                type="danger"
                size="small"
                :disabled="row.id === 1 || row.id === userStore.user?.id"
                @click="handleDelete(row)"
              >
                <el-icon><Delete /></el-icon>
                <span v-if="!isMobile">删除</span>
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
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 新增/编辑用户对话框 -->
    <el-dialog
      v-model="showUserDialog"
      :title="editingUser ? '编辑用户' : '新增用户'"
      width="600px"
    >
      <el-form
        ref="userFormRef"
        :model="userForm"
        :rules="userFormRules"
        label-width="100px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="userForm.username"
            :disabled="!!editingUser"
            placeholder="请输入用户名"
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="userForm.email"
            type="email"
            placeholder="请输入邮箱"
          />
        </el-form-item>

        <el-form-item label="角色" prop="role">
          <el-radio-group v-model="userForm.role">
            <el-radio label="admin">管理员</el-radio>
            <el-radio label="user">普通用户</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="userForm.status"
            active-value="active"
            inactive-value="inactive"
            inline-prompt
            active-text="激活"
            inactive-text="禁用"
          />
        </el-form-item>

        <el-form-item label="头像">
          <div class="avatar-upload">
            <el-upload
              class="avatar-uploader"
              :action="`${apiBase}/upload/avatar`"
              :headers="authHeaders"
              :show-file-list="false"
              :on-success="handleAvatarSuccess"
              :before-upload="beforeAvatarUpload"
            >
              <el-avatar
                :src="userForm.avatar || defaultAvatar"
                :size="80"
                class="avatar-uploader-icon"
              />
            </el-upload>
            <el-button
              v-if="userForm.avatar"
              type="danger"
              size="small"
              @click="clearAvatar"
              style="margin-left: 10px;"
            >
              清除头像
            </el-button>
          </div>
        </el-form-item>

        <el-form-item v-if="!editingUser" label="密码" prop="password">
          <el-input
            v-model="userForm.password"
            type="password"
            show-password
            placeholder="请输入密码"
          />
        </el-form-item>

        <el-form-item v-if="editingUser" label="新密码">
          <el-input
            v-model="userForm.new_password"
            type="password"
            show-password
            placeholder="留空则不修改密码"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showUserDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSaveUser">保存</el-button>
      </template>
    </el-dialog>

    <!-- 重置密码对话框 -->
    <el-dialog
      v-model="showResetPasswordDialog"
      title="重置用户密码"
      width="500px"
    >
      <el-form :model="passwordForm" :rules="passwordFormRules" label-width="100px">
        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            show-password
            placeholder="请输入新密码"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm_password">
          <el-input
            v-model="passwordForm.confirm_password"
            type="password"
            show-password
            placeholder="请确认新密码"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showResetPasswordDialog = false">取消</el-button>
        <el-button type="primary" @click="handleConfirmResetPassword">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Edit,
  CircleCheck,
  CircleCheckFilled,
  Lock,
  Delete,
  User,
  Avatar
} from '@element-plus/icons-vue'
import { getUserList, createUser, updateUser, deleteUser, resetUserPassword } from '@/api/auth'
import { useUserStore } from '@/stores/user'
import type { FormInstance, FormRules } from 'element-plus'

const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const showUserDialog = ref(false)
const showResetPasswordDialog = ref(false)
const editingUser = ref<any>(null)

// 表格数据
const tableData = ref<any[]>([])
const pagination = reactive({
  page: 1,
  per_page: 20,
  total: 0
})

// 搜索表单
const searchForm = reactive({
  username: '',
  email: '',
  role: ''
})

// 用户表单
const userForm = reactive({
  id: undefined,
  username: '',
  email: '',
  role: 'user',
  status: 'active' as 'active' | 'inactive',
  avatar: '',
  password: '',
  new_password: ''
})

// 密码表单
const passwordForm = reactive({
  user_id: 0,
  new_password: '',
  confirm_password: ''
})

// 表单引用
const userFormRef = ref<FormInstance>()

// 默认头像
const defaultAvatar = 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'

// 认证头部
const authHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('access_token')}`
}))

// API基础URL
const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'

// 表单验证规则
const userFormRules = computed(() => {
  return {
    username: [
      { required: true, message: '请输入用户名', trigger: 'blur' },
      { min: 3, max: 20, message: '用户名长度在3-20个字符', trigger: 'blur' }
    ],
    email: [
      { required: true, message: '请输入邮箱', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
    ],
    password: [
      { required: !editingUser.value, message: '请输入密码', trigger: 'blur' },
      { min: 6, max: 20, message: '密码长度在6-20个字符', trigger: 'blur' }
    ]
  }
})

const passwordFormRules: FormRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, max: 20, message: '密码长度在6-20个字符', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 加载用户列表
const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      per_page: pagination.per_page,
      ...searchForm
    }
    const res: any = await getUserList(params)
    tableData.value = res.users || []
    pagination.total = res.total || 0
  } catch (error) {
    console.error('加载用户列表失败:', error)
    ElMessage.error('加载用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  fetchUsers()
}

// 重置搜索
const handleReset = () => {
  searchForm.username = ''
  searchForm.email = ''
  searchForm.role = ''
  pagination.page = 1
  fetchUsers()
}

// 分页变化
const handleSizeChange = (size: number) => {
  pagination.per_page = size
  pagination.page = 1
  fetchUsers()
}

const handlePageChange = (page: number) => {
  pagination.page = page
  fetchUsers()
}

// 显示新增用户对话框
const showAddUserDialog = ref(false)

// 监听新增用户按钮点击，显示用户对话框
const showAddUser = () => {
  // 重置编辑状态
  editingUser.value = null
  // 重置表单
  resetUserForm()
  // 显示对话框
  showUserDialog.value = true
}

// 编辑用户
const handleEdit = (row: any) => {
  editingUser.value = row
  Object.assign(userForm, {
    id: row.id,
    username: row.username,
    email: row.email,
    role: row.role,
    status: row.status,
    avatar: row.avatar || ''
  })
  showUserDialog.value = true
}

// 激活/禁用用户
const handleToggleStatus = async (row: any) => {
  try {
    // 防止禁用自己的账户
    if (row.id === userStore.user?.id) {
      ElMessage.error('不能禁用当前登录的用户')
      return
    }
    
    await ElMessageBox.confirm(
      `确定要${row.status === 'active' ? '禁用' : '激活'}用户 "${row.username}" 吗？`,
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res: any = await updateUser(row.id, {
      status: row.status === 'active' ? 'inactive' : 'active'
    })

    if (res.success) {
      ElMessage.success(`${row.status === 'active' ? '禁用' : '激活'}成功`)
      fetchUsers()
    } else {
      ElMessage.error(res.message || '操作失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('切换用户状态失败:', error)
      ElMessage.error('操作失败')
    }
  }
}

// 删除用户
const handleDelete = async (row: any) => {
  try {
    // 防止删除自己（当前登录用户）
    if (row.id === userStore.user?.id) {
      ElMessage.error('不能删除当前登录的用户')
      return
    }
    
    // 防止删除最高管理员（ID为1的用户）
    if (row.id === 1) {
      ElMessage.error('不能删除超级管理员用户')
      return
    }
    
    await ElMessageBox.confirm(
      `确定要删除用户 "${row.username}" 吗？此操作不可恢复！`,
      '警告',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    const res: any = await deleteUser(row.id)

    if (res.success) {
      ElMessage.success('删除成功')
      fetchUsers()
    } else {
      ElMessage.error(res.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除用户失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

// 重置密码
const handleResetPassword = (row: any) => {
  passwordForm.user_id = row.id
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
  showResetPasswordDialog.value = true
}

// 上传头像成功
const handleAvatarSuccess = (response: any, uploadFile: any) => {
  if (response.success && response.url) {
    userForm.avatar = response.url
    ElMessage.success('头像上传成功')
  } else {
    ElMessage.error(response.message || '头像上传失败')
  }
}

// 上传头像前验证
const beforeAvatarUpload = (file: File) => {
  const isJPG = file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/gif'
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isJPG) {
    ElMessage.error('头像图片只能是 JPG/PNG/GIF 格式!')
  }
  if (!isLt2M) {
    ElMessage.error('头像图片大小不能超过 2MB!')
  }
  return isJPG && isLt2M
}

// 清除头像
const clearAvatar = () => {
  userForm.avatar = ''
}

// 保存用户
const handleSaveUser = async () => {
  if (!userFormRef.value) return

  await userFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        let res: any
        if (editingUser.value) {
          // 更新用户
          const updateData: any = {
            email: userForm.email,
            role: userForm.role,
            status: userForm.status,
            avatar: userForm.avatar
          }
          if (userForm.new_password) {
            updateData.password = userForm.new_password
          }
          res = await updateUser(editingUser.value.id, updateData)
        } else {
          // 创建用户
          res = await createUser({
            username: userForm.username,
            email: userForm.email,
            password: userForm.password,
            role: userForm.role,
            status: userForm.status,
            avatar: userForm.avatar
          })
        }

        if (res.success) {
          ElMessage.success(`${editingUser.value ? '编辑' : '新增'}用户成功`)
          showUserDialog.value = false
          resetUserForm()
          fetchUsers()
        } else {
          ElMessage.error(res.message || `${editingUser.value ? '编辑' : '新增'}失败`)
        }
      } catch (error: any) {
        console.error(`${editingUser.value ? '编辑' : '新增'}用户失败:`, error)
        ElMessage.error(error.response?.data?.message || `${editingUser.value ? '编辑' : '新增'}失败`)
      }
    }
  })
}

// 确认重置密码
const handleConfirmResetPassword = async () => {
  if (!passwordForm.new_password || !passwordForm.confirm_password) {
    ElMessage.error('请填写完整信息')
    return
  }

  if (passwordForm.new_password !== passwordForm.confirm_password) {
    ElMessage.error('两次输入的密码不一致')
    return
  }

  try {
    const res: any = await resetUserPassword(passwordForm.user_id, {
      new_password: passwordForm.new_password
    })

    if (res.success) {
      ElMessage.success('密码重置成功')
      showResetPasswordDialog.value = false
    } else {
      ElMessage.error(res.message || '密码重置失败')
    }
  } catch (error: any) {
    console.error('重置密码失败:', error)
    ElMessage.error(error.response?.data?.message || '密码重置失败')
  }
}

// 重置表单
const resetUserForm = () => {
  Object.assign(userForm, {
    id: undefined,
    username: '',
    email: '',
    role: 'user',
    status: 'active',
    avatar: '',
    password: '',
    new_password: ''
  })
  editingUser.value = null
}

// 初始化
fetchUsers()
</script>

<style scoped>
.user-manage-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
}

.avatar-upload {
  display: flex;
  align-items: center;
}

.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}

.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}

.avatar-uploader-icon {
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  width: 80px;
  height: 80px;
  font-size: 28px;
  color: #8c939d;
  background-color: #f5f7fa;
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
}
</style>