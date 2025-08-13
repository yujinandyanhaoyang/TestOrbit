
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
            :data="projectList"
            height="600"
            style="width: 100%"
            border
            stripe
            highlight-current-row>
                <el-table-column
                    label="序号"
                    width="80"
                    align="center">
                    <template #default="scope">
                        {{ (currentPage - 1) * pageSize + scope.$index + 1 }}
                    </template>
                </el-table-column>
                <el-table-column
                    prop="name"
                    label="项目名称"
                    min-width="200"
                    show-overflow-tooltip>
                </el-table-column> 
                <el-table-column
                    label="操作"
                    width="200"
                    align="center">
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
            :total="totalProjects">
            </el-pagination>
        </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 定义项目类型
interface Project {
  id: number
  name: string
}

// 使用ref并指定类型
const projectList = ref<Project[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalProjects = ref(0)

// 模拟项目数据
const mockProjects: Project[] = Array.from({ length: 25 }, (_, index) => ({
  id: index + 1,
  name: `项目 ${index + 1}`
}))

// 获取分页数据
const getPageData = () => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  projectList.value = mockProjects.slice(start, end)
  totalProjects.value = mockProjects.length
}

onMounted(() => {
  getPageData()
})

// 处理页码变化
const handleCurrentChange = (newPage: number) => {
  currentPage.value = newPage
  getPageData()
}

// 处理每页条数变化
const handleSizeChange = (newSize: number) => {
  pageSize.value = newSize
  currentPage.value = 1
  getPageData()
}

// 处理编辑项目
const handleEdit = (row: Project) => {
  ElMessage.info(`准备编辑项目: ${row.name}`)
  // TODO: 实现编辑功能
}

// 处理删除项目
const handleDelete = (row: Project) => {
  ElMessageBox.confirm(
    `确定要删除项目 "${row.name}" 吗？`,
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
.container {
  display: flex;
  flex-direction: column;
  min-height: 100vh; // 确保容器至少占满整个视口高度

  .top {
    background-color: skyblue;
    padding: 20px;
    text-align: center;
  }
  .main {
    display: flex;
    height: 800px; // 设置主内容区的高度

    .left {
      width: 300px;
      height: 100%;
      padding: 0;
      margin: 0;
      background-color: #fff;
      
      .el-menu {
        width: 100%;
        height: 100%;
        border-right: none;
      }
    }
    .right {
      flex: 1;
      padding: 0 5px;
      background-color: #fff;
      border-left: 5px solid #e6e6e6;  // 添加灰色边框线
    }
  }
}
</style>