
<template>
  <div class="user-manage-container">
    <!-- 页面头部组件 -->
    <PageHeader
      :online-users="userList.filter(user => user.is_active).length"
      :search-query="searchQuery"
      @search="handleSearch"
      @filter="handleFilter"
      @add-user="openAddDialog"
    />

    <!-- 主要内容卡片 -->
    <div class="main-card">
      <!-- 表格容器 -->
      <div class="table-container">
        <el-table
          :data="userList"
          class="modern-table"
          height="600"
          style="width: 100%"
          :header-cell-style="{ 
            background: '#f8fafc',
            color: '#475569',
            fontWeight: '600',
            fontSize: '14px',
            borderBottom: '1px solid #e2e8f0'
          }"
          :cell-style="{ 
            borderBottom: '1px solid #f1f5f9',
            padding: '16px 12px'
          }"
          :row-style="{ height: '60px' }"
        >
          <el-table-column
            label="序号"
            width="80"
            align="center"
          >
            <template #default="scope">
              <div class="sequence-number">
                {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column
            prop="username"
            label="用户信息"
            min-width="200"
            header-align="center"
            class-name="user-info-column"
          >
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-avatar">
                  <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2"/>
                    <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </div>
                <div class="user-details">
                  <div class="user-name">{{ row.username }}</div>
                  <div class="user-email">{{ row.email }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column
            prop="phone"
            label="手机号"
            width="140"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <div class="phone-number">{{ row.phone || '--' }}</div>
            </template>
          </el-table-column>
          
          <el-table-column
            label="加入时间"
            width="180"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <div class="date-info">
                <svg class="date-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2" stroke="currentColor" stroke-width="2"/>
                  <line x1="16" y1="2" x2="16" y2="6" stroke="currentColor" stroke-width="2"/>
                  <line x1="8" y1="2" x2="8" y2="6" stroke="currentColor" stroke-width="2"/>
                  <line x1="3" y1="10" x2="21" y2="10" stroke="currentColor" stroke-width="2"/>
                </svg>
                {{ new Date(row.date_joined).toLocaleDateString() }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column
            label="最后登录"
            width="180"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <div class="date-info">
                <svg class="date-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                  <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2"/>
                </svg>
                {{ row.last_login ? new Date(row.last_login).toLocaleDateString() : '未登录' }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column
            label="所属项目"
            min-width="200"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <div class="projects-tags">
                <template v-if="row.projects.length > 0">
                  <span 
                    v-for="project in row.projects.slice(0, 2)" 
                    :key="project.id" 
                    class="project-tag"
                  >
                    {{ project.name }}
                  </span>
                  <span v-if="row.projects.length > 2" class="more-projects">
                    +{{ row.projects.length - 2 }}
                  </span>
                </template>
                <span v-else class="no-projects">未分配项目</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column
            label="状态"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              <div class="status-badge" :class="row.is_active ? 'active' : 'inactive'">
                <div class="status-dot"></div>
                <span class="status-text">{{ row.is_active ? '启用' : '禁用' }}</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column
            label="操作"
            width="180"
            align="center"
            fixed="right"
          >
            <template #default="{ row }">
              <div class="action-buttons">
                <button class="table-btn edit" @click="handleEdit(row)">
                  <svg class="btn-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" stroke="currentColor" stroke-width="2"/>
                    <path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  编辑
                </button>
                
                <el-switch 
                  v-model="row.is_active" 
                  @change="() => updateStatus(row)"
                  :loading="row.statusLoading"
                  class="status-switch"
                  size="small"
                />
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 分页器 -->
      <div class="pagination-container">
        <el-pagination
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          :current-page="currentPage"
          :page-sizes="[10, 20, 30, 50]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalUsers"
          background
        />
      </div>
    </div>

    <!-- 用户信息对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '新增用户' : '编辑用户'"
      width="540px"
      :close-on-click-modal="false"
      class="modern-dialog"
    >
      <div class="dialog-content">
        <el-form :model="userForm" label-width="100px" class="user-form">
          <el-form-item label="姓名">
            <el-input 
              v-model="userForm.username" 
              placeholder="请输入姓名" 
              :disabled="dialogType === 'edit'"
              class="form-input"
            />
          </el-form-item>
          
          <el-form-item label="邮箱">
            <el-input 
              v-model="userForm.email" 
              placeholder="请输入邮箱地址"
              class="form-input"
            />
          </el-form-item>
          
          <el-form-item label="手机号">
            <el-input 
              v-model="userForm.phone" 
              placeholder="请输入手机号"
              class="form-input"
            />
          </el-form-item>
          
          <el-form-item v-if="dialogType === 'add'" label="密码">
            <el-input 
              v-model="userForm.password" 
              type="password" 
              placeholder="请输入初始密码" 
              show-password
              class="form-input"
            />
          </el-form-item>
          
          <el-form-item v-if="dialogType !== 'add'" label="所属项目">
            <el-select
              v-model="selectedProjectIds"
              multiple
              placeholder="请选择所属项目组"
              style="width: 100%"
              class="form-select"
            >
              <el-option 
                v-for="project in projectOptions" 
                :key="project.id" 
                :label="project.name" 
                :value="project.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible = false">
            取消
          </el-button>
          <el-button type="primary" @click="handleSubmit">
            {{ dialogType === 'add' ? '创建用户' : '保存更改' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { getUserList,updateUserStatus,updateUserInfo,addUser } from '@/api/user/index'
import { getProjectList } from '@/api/project/index'
import { ref, onMounted } from 'vue'
import type { UserInfo } from '@/api/user/types'
import type { ProjectInfo } from '@/api/project/types'
import { ElMessage } from 'element-plus'
import PageHeader from './PageHeader.vue'


//定义用户列表
const userList = ref<UserInfo[]>([])
// 定义总用户数
const totalUsers = ref(0)
// 搜索查询
const searchQuery = ref('')
// 当前页码
const currentPage = ref(1)
// 每页显示条数
const pageSize = ref(10)
// 项目ID到名称的映射
const projectMap = ref<Map<number, string>>(new Map())
// 项目选项列表
const projectOptions = ref<{id: number, name: string}[]>([])
// 选中的项目ID列表
const selectedProjectIds = ref<number[]>([])

// 对话框相关的响应式数据
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')  // 用于区分是新增还是编辑

// 用户基础信息表单
const userForm = ref({
  id: 0,
  username: '',
  email: '',
  phone: '',
  is_active: true,
  password: '',
  projects: [] // 用户所属项目组
})

// 获取项目列表并构建映射
const fetchProjects = async () => {
  try {
    const response = await getProjectList(1, 1000) // 获取所有项目，假设不超过1000个
    
    if (response.code == 200) {
      // 清空现有数据
      projectOptions.value = []
      
      // 创建映射和选项列表
      response.results.data.forEach((project: ProjectInfo) => {
        // 更新映射
        projectMap.value.set(project.id, project.name)
        
        // 添加到选项列表
        projectOptions.value.push({
          id: project.id,
          name: project.name
        })
      })
    } else {
      ElMessage.warning('获取项目列表失败，可能无法显示完整的项目名称')
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.warning('获取项目列表失败，可能无法显示完整的项目名称')
  }
}

//
onMounted(() => {
    fetchProjects()
    fetchUserList(1, 10)  // 初始加载第一页，每页10条数据
})

//定义获取用户信息方法
const fetchUserList = async (page: number, pageSize: number) => {
  try {
    const response = await getUserList(page, pageSize)

    // 检查响应是否成功
    if (response.code == 200) {
      // 为每个用户对象添加前端临时状态属性
      userList.value = response.results.data.map((user: any) => ({
        ...user,
        statusLoading: false  // 添加状态加载标志
      }))
      totalUsers.value = response.results.total
    //   console.log('用户列表:', userList.value)
    } else {
      // 如果后端返回了错误信息
      ElMessage.error(response.msg || '获取用户列表失败')
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败，请稍后重试')
  }
}

// 处理分页
const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  fetchUserList(newPage, pageSize.value)
}

const handleSizeChange = (newSize: number) => {
    pageSize.value = newSize
    currentPage.value = 1
    fetchUserList(1, newSize)
}

// 处理搜索
const handleSearch = (query: string) => {
  searchQuery.value = query
  // 这里可以添加搜索逻辑
  console.log('搜索查询:', query)
}

// 打开添加用户对话框
const openAddDialog = () => {
    dialogType.value = 'add'
    // 清空表单
    userForm.value = {
        id: 0,
        username: '',
        email: '',
        is_active: true,
        phone: '',
        password: '',
        projects: []
    }
    // 清空选中的项目
    selectedProjectIds.value = []
    dialogVisible.value = true
}

// 处理编辑用户
const handleEdit = (row: UserInfo) => {
    dialogType.value = 'edit'
    // 填充表单数据
    userForm.value = {
        id: row.id,
        username: row.username,
        email: row.email,
        is_active: row.is_active,
        phone: row.phone,
        password: '', // 密码留空，编辑时不修改密码
        projects: [] // 不直接使用row.projects，因为格式已更改
    }
    // 设置选中的项目ID
    selectedProjectIds.value = row.projects.map(p => p.id)
    dialogVisible.value = true
}

// 更新用户状态
const updateStatus = async (row: any) => {
    // 记录当前状态值，因为v-model会立即更新UI
    const currentStatus = row.is_active
    
    // 添加临时loading状态属性
    row.statusLoading = true
    
    try {
        // 发送API请求
        const response = await updateUserStatus(row.id, currentStatus)
        
        if (response && response.code === 200) {
            ElMessage.success('用户状态更新成功')
            // 刷新用户列表以获取最新数据
            await fetchUserList(currentPage.value, pageSize.value)
        } else {
            // 如果API请求返回错误，恢复UI状态
            row.is_active = !currentStatus
            ElMessage.error(response?.msg || '更新用户状态失败')
        }
    } catch (error) {
        // 发生错误时恢复UI状态
        row.is_active = !currentStatus
        ElMessage.error('更新用户状态失败，请稍后重试')
        console.error('更新用户状态错误:', error)
    } finally {
        // 无论成功还是失败，都要关闭loading状态
        row.statusLoading = false
    }
}

// 提交用户信息 - 处理新增和编辑
const handleSubmit = async () => {
    // 表单验证
    if (!userForm.value.username.trim()) {
        ElMessage.warning('姓名不能为空')
        return
    }
    if (!userForm.value.email.trim()) {
        ElMessage.warning('邮箱不能为空')
        return
    }
    
    // 如果是新增用户，需要验证密码
    if (dialogType.value === 'add' && !userForm.value.password.trim()) {
        ElMessage.warning('密码不能为空')
        return
    }
    
    try {
        let response
        
        if (dialogType.value === 'add') {
            // 新增用户
            response = await addUser({
                username: userForm.value.username,
                email: userForm.value.email,
                phone: userForm.value.phone,
                password: userForm.value.password,
                is_active: userForm.value.is_active,
                projects: selectedProjectIds.value // 使用选中的项目ID
            })
        } else {
            // 编辑用户
            response = await updateUserInfo({
                id: userForm.value.id,
                email: userForm.value.email,
                phone: userForm.value.phone,
                is_active: userForm.value.is_active,
                projects: selectedProjectIds.value // 使用选中的项目ID
            })
        }
        
        if ( response.code === 200 || response.code === 201) {
            ElMessage.success(dialogType.value === 'add' ? '添加用户成功' : '更新用户成功')
            dialogVisible.value = false
            // 刷新用户列表
            fetchUserList(currentPage.value, pageSize.value)
        } else {
            ElMessage.error(response?.msg || (dialogType.value === 'add' ? '添加用户失败' : '更新用户失败'))
        }
    } catch (error) {
        console.error('操作失败:', error)
        ElMessage.error(dialogType.value === 'add' ? '添加用户失败，请稍后重试' : '更新用户失败，请稍后重试')
    }
}

// 处理筛选
const handleFilter = () => {
  // 暂时先弹窗提示
  ElMessage.info('筛选功能尚未实现，敬请期待')
}


</script>

<style scoped lang="scss">
// 设计系统变量
:root {
  --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --surface-primary: #ffffff;
  --surface-secondary: #f8fafc;
  --surface-tertiary: #f1f5f9;
  --text-primary: #1e293b;
  --text-secondary: #64748b;
  --text-muted: #94a3b8;
  --border-light: #e2e8f0;
  --border-medium: #cbd5e1;
  --success-color: #10b981;
  --error-color: #ef4444;
  --warning-color: #f59e0b;
  --info-color: #3b82f6;
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --border-radius-sm: 8px;
  --border-radius-md: 12px;
  --border-radius-lg: 16px;
  --border-radius-xl: 20px;
}

.user-manage-container {
  padding: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  min-height: 100vh;

  // 页面头部
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 32px;
    padding: 32px;
    background: var(--surface-primary);
    border-radius: var(--border-radius-xl);
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border-light);
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: var(--primary-gradient);
    }

    .header-left {
      flex: 1;

      .page-title {
        display: flex;
        align-items: center;
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 8px;

        .title-icon-wrapper {
          width: 48px;
          height: 48px;
          border-radius: var(--border-radius-md);
          background: var(--primary-gradient);
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 16px;
          position: relative;
          overflow: hidden;

          &::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
            transform: rotate(-45deg);
            animation: shimmer 2s infinite;
          }

          .title-icon {
            width: 24px;
            height: 24px;
            color: white;
            position: relative;
            z-index: 1;
          }
        }
      }

      .page-description {
        font-size: 16px;
        color: var(--text-secondary);
        margin: 0 0 16px 0;
        font-weight: 500;
      }

      .header-meta {
        display: flex;
        gap: 24px;
        margin-top: 12px;

        .meta-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 14px;
          color: var(--text-muted);
          font-weight: 500;

          .meta-icon {
            width: 16px;
            height: 16px;
            opacity: 0.7;
          }
        }
      }
    }

    .header-actions {
      display: flex;
      flex-direction: column;
      gap: 16px;
      align-items: flex-end;

      .search-container {
        position: relative;
        width: 320px;

        .search-icon {
          position: absolute;
          left: 16px;
          top: 50%;
          transform: translateY(-50%);
          width: 18px;
          height: 18px;
          color: var(--text-muted);
          z-index: 1;
        }

        .search-input {
          width: 100%;
          padding: 14px 16px 14px 48px;
          border: 1px solid var(--border-light);
          border-radius: var(--border-radius-md);
          font-size: 14px;
          background: var(--surface-secondary);
          color: var(--text-primary);
          transition: all 0.2s ease;

          &::placeholder {
            color: var(--text-muted);
          }

          &:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            background: white;
          }
        }
      }

      .button-group {
        display: flex;
        gap: 12px;

        .action-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 20px;
          border-radius: var(--border-radius-md);
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.3s ease;
          border: none;
          position: relative;
          overflow: hidden;

          .btn-icon {
            width: 16px;
            height: 16px;
            z-index: 2;
          }

          &.secondary {
            background: var(--surface-secondary);
            color: var(--text-secondary);
            border: 1px solid var(--border-medium);
            backdrop-filter: blur(10px);

            &:hover {
              background: var(--surface-tertiary);
              color: var(--text-primary);
              transform: translateY(-2px);
              box-shadow: var(--shadow-md);
              border-color: #667eea;
            }
          }

          &.primary {
            background: var(--primary-gradient);
            color: white;
            box-shadow: var(--shadow-sm);
            position: relative;

            .btn-shine {
              position: absolute;
              top: -50%;
              left: -50%;
              width: 200%;
              height: 200%;
              background: linear-gradient(45deg, transparent, rgba(255,255,255,0.3), transparent);
              transform: rotate(-45deg);
              transition: all 0.3s ease;
              opacity: 0;
            }

            &:hover {
              transform: translateY(-2px);
              box-shadow: var(--shadow-lg);

              .btn-shine {
                opacity: 1;
                animation: shine 0.6s ease-out;
              }
            }
          }

          &:active {
            transform: translateY(0);
          }
        }
      }
    }
  }

  // 统计卡片
  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    margin-bottom: 32px;

    .stat-card {
      display: flex;
      align-items: center;
      padding: 24px;
      background: var(--surface-primary);
      border-radius: var(--border-radius-lg);
      box-shadow: var(--shadow-md);
      border: 1px solid var(--border-light);
      transition: all 0.3s ease;
      position: relative;
      overflow: hidden;

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: var(--primary-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
      }

      &:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-xl);

        &::before {
          opacity: 1;
        }
      }

      .stat-icon {
        width: 60px;
        height: 60px;
        border-radius: var(--border-radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 20px;
        position: relative;

        svg {
          width: 28px;
          height: 28px;
          color: white;
        }

        &.total {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        &.active {
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }

        &.projects {
          background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        }

        &.inactive {
          background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
        }
      }

      .stat-content {
        flex: 1;

        .stat-value {
          font-size: 32px;
          font-weight: 800;
          color: var(--text-primary);
          line-height: 1.2;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 14px;
          color: var(--text-secondary);
          font-weight: 500;
          margin-bottom: 8px;
        }

        .stat-trend {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 12px;
          font-weight: 600;

          .trend-icon {
            width: 12px;
            height: 12px;
          }

          &.positive {
            color: var(--success-color);
          }

          &.negative {
            color: var(--error-color);
          }

          &.neutral {
            color: var(--text-muted);
          }
        }
      }
    }
  }

  // 主要内容卡片
  .main-card {
    background: var(--surface-primary);
    border-radius: var(--border-radius-xl);
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border-light);
    overflow: hidden;

    .table-container {
      // 自定义表格样式
      :deep(.modern-table) {
        border: none;

        .el-table__header {
          th {
            background: var(--surface-secondary) !important;
            border: none;
            font-weight: 600;
            color: var(--text-primary);
          }
        }

        .el-table__body {
          tr {
            transition: all 0.2s ease;

            &:hover {
              background: var(--surface-secondary);
            }

            td {
              border: none;
              border-bottom: 1px solid var(--surface-tertiary);
            }
          }
        }

        // 移除默认边框
        &::before {
          display: none;
        }

        // 特定列的表头居中样式
        .user-info-column {
          .cell {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
          }
        }
      }

      // 序号样式
      .sequence-number {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: var(--surface-secondary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 600;
        color: var(--text-secondary);
        margin: 0 auto;
      }

      // 用户信息样式
      .user-info {
        display: flex;
        align-items: center;

        .user-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: var(--primary-gradient);
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 12px;

          svg {
            width: 20px;
            height: 20px;
            color: white;
          }
        }

        .user-details {
          .user-name {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 2px;
          }

          .user-email {
            font-size: 13px;
            color: var(--text-secondary);
          }
        }
      }

      // 手机号样式
      .phone-number {
        font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
        font-size: 14px;
        color: var(--text-secondary);
      }

      // 日期信息样式
      .date-info {
        display: flex;
        align-items: center;
        font-size: 14px;
        color: var(--text-secondary);

        .date-icon {
          width: 14px;
          height: 14px;
          margin-right: 6px;
          opacity: 0.7;
        }
      }

      // 项目标签样式
      .projects-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;

        .project-tag {
          padding: 4px 10px;
          background: rgba(102, 126, 234, 0.1);
          color: #667eea;
          border-radius: var(--border-radius-sm);
          font-size: 12px;
          font-weight: 500;
          border: 1px solid rgba(102, 126, 234, 0.2);
        }

        .more-projects {
          padding: 4px 8px;
          background: var(--surface-tertiary);
          color: var(--text-muted);
          border-radius: var(--border-radius-sm);
          font-size: 12px;
          font-weight: 500;
        }

        .no-projects {
          color: var(--text-muted);
          font-size: 14px;
          font-style: italic;
        }
      }

      // 状态徽章样式
      .status-badge {
        display: flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;

        .status-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }

        &.active {
          background: rgba(16, 185, 129, 0.1);
          color: var(--success-color);

          .status-dot {
            background: var(--success-color);
          }
        }

        &.inactive {
          background: rgba(239, 68, 68, 0.1);
          color: var(--error-color);

          .status-dot {
            background: var(--error-color);
          }
        }
      }

      // 操作按钮样式
      .action-buttons {
        display: flex;
        align-items: center;
        gap: 12px;

        .table-btn {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 8px 12px;
          border: none;
          border-radius: var(--border-radius-sm);
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;

          .btn-icon {
            width: 14px;
            height: 14px;
          }

          &.edit {
            background: rgba(59, 130, 246, 0.1);
            color: var(--info-color);
            border: 1px solid rgba(59, 130, 246, 0.2);

            &:hover {
              background: rgba(59, 130, 246, 0.2);
              transform: translateY(-1px);
            }
          }
        }

        .status-switch {
          :deep(.el-switch__core) {
            height: 20px;
            border-radius: 10px;

            &::after {
              width: 16px;
              height: 16px;
              top: 2px;
              left: 2px;
            }
          }

          :deep(.el-switch.is-checked .el-switch__core::after) {
            left: calc(100% - 18px);
          }
        }
      }
    }

    // 分页器样式
    .pagination-container {
      padding: 24px 32px;
      border-top: 1px solid var(--border-light);
      display: flex;
      justify-content: center;

      :deep(.el-pagination) {
        .btn-prev,
        .btn-next,
        .el-pager li {
          border: 1px solid var(--border-light);
          border-radius: var(--border-radius-sm);
          margin: 0 2px;
          transition: all 0.2s ease;

          &:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-sm);
          }
        }

        .el-pager li.is-active {
          background: var(--primary-gradient);
          border-color: transparent;
          color: white;
        }

        .el-pagination__sizes,
        .el-pagination__jump {
          .el-select,
          .el-input {
            .el-input__inner {
              border-radius: var(--border-radius-sm);
              border-color: var(--border-light);
            }
          }
        }
      }
    }
  }

  // 对话框样式
  :deep(.modern-dialog) {
    .el-dialog {
      border-radius: var(--border-radius-xl);
      overflow: hidden;
      box-shadow: var(--shadow-xl);

      .el-dialog__header {
        background: var(--surface-secondary);
        padding: 24px 32px 20px;
        border-bottom: 1px solid var(--border-light);

        .el-dialog__title {
          font-size: 20px;
          font-weight: 700;
          color: var(--text-primary);
        }

        .el-dialog__close {
          font-size: 20px;
          color: var(--text-muted);

          &:hover {
            color: var(--text-primary);
          }
        }
      }

      .el-dialog__body {
        padding: 32px;
      }

      .el-dialog__footer {
        padding: 20px 32px 32px;
        border-top: 1px solid var(--border-light);
      }
    }
  }

  .dialog-content {
    .user-form {
      .el-form-item {
        margin-bottom: 24px;

        .el-form-item__label {
          font-weight: 600;
          color: var(--text-primary);
        }

        :deep(.form-input) {
          .el-input__inner {
            border-radius: var(--border-radius-md);
            border-color: var(--border-light);
            padding: 12px 16px;
            height: auto;
            transition: all 0.2s ease;

            &:focus {
              border-color: #667eea;
              box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
          }
        }

        :deep(.form-select) {
          .el-select__tags {
            .el-tag {
              background: rgba(102, 126, 234, 0.1);
              border-color: rgba(102, 126, 234, 0.2);
              color: #667eea;
              border-radius: var(--border-radius-sm);
            }
          }
        }
      }
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;

    .dialog-btn {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 24px;
      border-radius: var(--border-radius-md);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.3s ease;
      border: none;
      min-width: 120px;
      justify-content: center;

      .btn-icon {
        width: 16px;
        height: 16px;
        flex-shrink: 0;
      }

      &.secondary {
        background: var(--surface-secondary);
        color: var(--text-secondary);
        border: 2px solid var(--border-medium);

        &:hover {
          background: var(--surface-tertiary);
          color: var(--text-primary);
          border-color: #667eea;
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
      }

      &.primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: 2px solid transparent;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
          background: linear-gradient(135deg, #5a6fd8 0%, #6b4190 100%);
        }
      }

      &:active {
        transform: translateY(0);
      }
    }
  }
}

// 动画定义
@keyframes shimmer {
  0% { transform: translateX(-100%) rotate(-45deg); }
  100% { transform: translateX(200%) rotate(-45deg); }
}

@keyframes shine {
  0% { transform: translateX(-100%) rotate(-45deg); opacity: 0; }
  50% { opacity: 1; }
  100% { transform: translateX(200%) rotate(-45deg); opacity: 0; }
}

// 响应式设计
@media (max-width: 1200px) {
  .user-manage-container {
    .stats-cards {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}

@media (max-width: 768px) {
  .user-manage-container {
    padding: 16px;

    .page-header {
      flex-direction: column;
      gap: 20px;
      padding: 24px;

      .header-actions {
        align-self: stretch;

        .action-btn {
          flex: 1;
          justify-content: center;
        }
      }
    }

    .stats-cards {
      grid-template-columns: 1fr;
      gap: 16px;

      .stat-card {
        padding: 20px;
      }
    }

    .main-card {
      .table-container {
        overflow-x: auto;

        :deep(.modern-table) {
          min-width: 800px;
        }
      }

      .pagination-container {
        padding: 20px 16px;
      }
    }

    :deep(.modern-dialog .el-dialog) {
      width: 95% !important;
      margin: 5vh auto;

      .el-dialog__header,
      .el-dialog__body,
      .el-dialog__footer {
        padding-left: 20px;
        padding-right: 20px;
      }
    }
  }
}

@media (max-width: 480px) {
  .user-manage-container {
    .dialog-footer {
      flex-direction: column;

      .dialog-btn {
        justify-content: center;
      }
    }
  }
}
</style>
