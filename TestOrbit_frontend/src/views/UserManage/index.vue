
<template>
  <div class="contain">
        <el-card class="box-card">
        <div slot="header" class="clearfix">
            <h1>用户管理</h1>
            <el-button size="small" type="primary" style="float: right; margin: 5px 10px;" @click="openAddDialog">添加</el-button>
            <el-button size="small" type="primary" style="float: right; margin: 5px 10px;" @click="handleFilter">筛选</el-button>
        </div>
        <!--已有用户列表-->
        <el-divider></el-divider>
        <div class="user-list">
            <el-table
            :data="userList"
            height="600"
            style="width: 100%"
            border
            table-layout="fixed"
            :header-cell-style="{background:'#f5f7fa'}"
            overflow-hidden>
            <el-table-column
                    label="序号"
                    width="60"
                    align="center">
                    <template #default="scope">
                        {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
                    </template>
                </el-table-column>
                <el-table-column
                    prop="username"
                    label="账号名"
                    show-overflow-tooltip>
                </el-table-column>
                <el-table-column
                    prop="real_name"
                    label="姓名"
                    show-overflow-tooltip>
                </el-table-column>
                <el-table-column
                    prop="email"
                    label="邮箱地址"
                    show-overflow-tooltip>
                </el-table-column>
                <el-table-column
                    label="加入时间"
                    show-overflow-tooltip>
                    <template #default="{ row }">
                        {{ new Date(row.date_joined).toLocaleString() }}
                    </template>
                </el-table-column>
                <el-table-column
                    label="最后登录"
                    show-overflow-tooltip>
                    <template #default="{ row }">
                        {{ row.last_login ? new Date(row.last_login).toLocaleString() : '未登录过' }}
                    </template>
                </el-table-column>
                <el-table-column
                    prop="is_active"
                    label="状态"
                    align="center">
                    <template #default="{ row }">
                        <el-tag :type="row.is_active ? 'success' : 'danger'">
                            {{ row.is_active ? '启用' : '禁用' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column
                    label="操作"
                    align="center"
                    fixed="right">
                    <template #default="{ row }">
                        <el-button size="small" type="primary" @click="handleEdit(row)">修改</el-button>
                        <el-switch 
                          style="padding: 0 10px;" 
                          v-model="row.is_active" 
                          @change="() => updateStatus(row)"
                          :loading="row.statusLoading"
                          active-color="#13ce66"
                          inactive-color="#ff4949"
                        ></el-switch>
                    </template>
                </el-table-column>
            </el-table>
            <!---底部分页-->
            <el-pagination
            style="display: flex; justify-content: center; margin: 20px 0;"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[10, 20, 30, 50]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalUsers">
            </el-pagination>
        </div>

        <!-- 用户信息对话框 - 用于新增和编辑 -->
        <el-dialog
            v-model="dialogVisible"
            :title="dialogType === 'add' ? '新增用户' : '编辑用户'"
            width="30%"
            :close-on-click-modal="false">
            <el-form :model="userForm" label-width="80px">
                <el-form-item label="账号名">
                    <el-input v-model="userForm.username" placeholder="请输入账号名" :disabled="dialogType === 'edit'"></el-input>
                </el-form-item>
                <el-form-item label="姓名">
                    <el-input v-model="userForm.real_name" placeholder="请输入姓名"></el-input>
                </el-form-item>
                <el-form-item label="邮箱">
                    <el-input v-model="userForm.email" placeholder="请输入邮箱"></el-input>
                </el-form-item>
                
                <!-- <el-form-item v-if="dialogType === 'add'" label="密码">
                    <el-input v-model="userForm.password" type="password" placeholder="请输入密码" show-password></el-input>
                </el-form-item> -->
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="dialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="handleSubmit">{{ dialogType === 'add' ? '创建' : '保存' }}</el-button>
                </span>
            </template>
        </el-dialog>


    </el-card>
  </div>
</template>

<script setup lang="ts">
import { getUserList,updateUserStatus,updateUserInfo,addUser } from '@/api/user/index'
import { ref, onMounted } from 'vue'
import type { UserInfo } from '@/api/user/types'
import { ElMessage } from 'element-plus'


//定义用户列表
const userList = ref<UserInfo[]>([])
// 定义总用户数
const totalUsers = ref(0)
// 当前页码
const currentPage = ref(1)
// 每页显示条数
const pageSize = ref(10)

// 对话框相关的响应式数据
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')  // 用于区分是新增还是编辑

// 用户基础信息表单
const userForm = ref({
  id: 0,
  username: '',
  real_name: '',
  email: '',
  is_active: true,
//   password: ''  // 添加密码字段，仅用于新增用户。待后端完善功能
})

//
onMounted(() => {
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

// 打开添加用户对话框
const openAddDialog = () => {
    dialogType.value = 'add'
    // 清空表单
    userForm.value = {
        id: 0,
        username: '',
        real_name: '',
        email: '',
        is_active: true,
        // password: ''
    }
    dialogVisible.value = true
}

// 处理编辑用户
const handleEdit = (row: UserInfo) => {
    dialogType.value = 'edit'
    // 填充表单数据
    userForm.value = {
        id: row.id,
        username: row.username,
        real_name: row.real_name,
        email: row.email,
        is_active: row.is_active,
        // password: '' // 密码留空，编辑时不修改密码
    }
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
        ElMessage.warning('账号名不能为空')
        return
    }
    if (!userForm.value.real_name.trim()) {
        ElMessage.warning('姓名不能为空')
        return
    }
    if (!userForm.value.email.trim()) {
        ElMessage.warning('邮箱不能为空')
        return
    }
    
    // // 如果是新增用户，需要验证密码
    // if (dialogType.value === 'add' && !userForm.value.password.trim()) {
    //     ElMessage.warning('密码不能为空')
    //     return
    // }
    
    try {
        let response
        
        if (dialogType.value === 'add') {
            // 新增用户
            response = await addUser({
                username: userForm.value.username,
                real_name: userForm.value.real_name,
                email: userForm.value.email,
                // password: userForm.value.password,
                is_active: userForm.value.is_active
            })
        } else {
            // 编辑用户
            response = await updateUserInfo({
                id: userForm.value.id,
                real_name: userForm.value.real_name,
                email: userForm.value.email,
                is_active: userForm.value.is_active
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
.contain{
    height: 100%;
    width: 100%;
    .header{
        font-size: 10px;
        font-weight: bold;
        margin: 10px 0;
        h1{
            font-size: 24px;
            font-weight: bold;
            margin: 0;
        }
    }
    .user-list{
        height: 800px;
        background-color: #fff;
        overflow: hidden;
        width: 100%;
    }
}


</style>
