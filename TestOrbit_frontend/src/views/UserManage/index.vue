
<template>
  <div class="contain">
        <el-card class="box-card">
        <div slot="header" class="clearfix">
            <h1>用户管理</h1>
            <el-button  style="float: right; padding: 15px 0" type="text">添加</el-button>
            <el-button style="float: right; padding: 15px 0" type="text">筛选</el-button>
        </div>
        <!--已有用户列表-->
        <div class="user-list">
            <el-table
            :data="userList"
            height="600"
            style="width: 100%"
            border>
                <el-table-column
                    prop="username"
                    label="账号名"
                    width="200">
                </el-table-column>
                <el-table-column
                    prop="real_name"
                    label="姓名"
                    width="200">
                </el-table-column>
                <el-table-column
                    prop="email"
                    label="邮箱地址">
                </el-table-column>
                <el-table-column
                    label="加入时间">
                    <template #default="{ row }">
                        {{ new Date(row.date_joined).toLocaleString() }}
                    </template>
                </el-table-column>
                <el-table-column
                    label="最后登录">
                    <template #default="{ row }">
                        {{ row.last_login ? new Date(row.last_login).toLocaleString() : 'null' }}
                    </template>
                </el-table-column>
                <el-table-column
                    prop="is_active"
                    label="状态">
                    <template #default="{ row }">
                        <el-tag :type="row.is_active ? 'success' : 'danger'">
                            {{ row.is_active ? '启用' : '禁用' }}
                        </el-tag>
                    </template>
                </el-table-column>
                <el-table-column
                    label="操作"
                    width="150">
                    <template #default="{ row }">
                        <el-button size="small" type="primary" @click="handleEdit(row)">编辑</el-button>
                        <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
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
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { getUserList } from '@/api/user'
import { ref, onMounted } from 'vue'
import type { UserInfo } from '@/api/user/types'
import { ElMessage, ElMessageBox } from 'element-plus'


//定义用户列表
const userList = ref<UserInfo[]>([])
// 定义总用户数
const totalUsers = ref(0)
// 当前页码
const currentPage = ref(1)
// 每页显示条数
const pageSize = ref(10)

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
      userList.value = response.results.data
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

const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  fetchUserList(newPage, pageSize.value)
}

const handleSizeChange = (newSize: number) => {
    pageSize.value = newSize
    currentPage.value = 1
    fetchUserList(1, newSize)
}

// 处理编辑用户
const handleEdit = (row: UserInfo) => {
    ElMessage.info('编辑用户: ' + row.username)
    // TODO: 实现编辑功能
}

// 处理删除用户
const handleDelete = (row: UserInfo) => {
    ElMessageBox.confirm(
        `确定要删除用户 ${row.username} 吗？`,
        '警告',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    ).then(() => {
        // TODO: 实现删除功能
        ElMessage.success('删除成功')
    }).catch(() => {
        ElMessage.info('已取消删除')
    })
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

        
    }
}


</style>
