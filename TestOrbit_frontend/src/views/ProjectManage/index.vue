
<template>
  <div class="contain">
        <el-card class="box-card">
        <div slot="header" class="clearfix">
            <h1>项目管理</h1>
            <el-button size="small" type="primary" style="float: right; margin: 5px 10px;" @click="add_dialogVisible = true">添加</el-button>
            <el-button size="small" type="primary" style="float: right; margin: 5px 10px;" @click="handleFilter">筛选</el-button>
        </div>
        <!--已有项目列表-->
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
            :page-sizes="[2, 4, 5, 6]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="totalProjects">
            </el-pagination>
        </div>
    </el-card>

        <!-- 编辑项目对话框 -->
        <el-dialog
            v-model="edit_dialogVisible"
            title="编辑项目"
            width="30%"
            :close-on-click-modal="false">
            <el-form :model="editForm" label-width="80px">
                <el-form-item label="项目名称">
                    <el-input v-model="editForm.name" placeholder="请输入项目名称"></el-input>
                </el-form-item>
            </el-form>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="edit_dialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="handleEditSubmit">确定</el-button>
                </span>
            </template>
        </el-dialog>


    <!--新增项目弹窗-->
    <el-dialog
      v-model="add_dialogVisible"
      title="新增项目"
      width="30%"
      :close-on-click-modal="false">
      <el-form :model="newProject" label-width="80px" class="login-form">
        <el-form-item label="项目名称">
          <el-input v-model="newProject" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item>
          <el-button @click="add_dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddSubmit" class="login-button">确定</el-button>
        </el-form-item>
      </el-form>
      </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { addProject,getProjectList,editProject,deleteProject } from '@/api/project'
import type { ProjectInfo } from '@/api/project/types'

// 使用ref并指定类型
const projectList = ref<ProjectInfo[]>([])
const currentPage = ref(1)
const pageSize = ref(10)
const totalProjects = ref(0)
const newProject = ref<string>('')

// 编辑相关的响应式数据
const edit_dialogVisible = ref(false)
const add_dialogVisible = ref(false)

const editForm = ref({
  id: 0,
  name: ''
})

// 页面加载时获取数据
onMounted(() => {
  getPageData()
})

const getPageData = async () =>{
  const response = await getProjectList(currentPage.value, pageSize.value)
  if (response.code == 200 ){
    projectList.value = response.results.data
    totalProjects.value = response.results.total
  }else{
    ElMessage.error('获取项目列表失败')
  }
}

// 处理分页显示
const handleSizeChange = (size: number) =>{
  pageSize.value = size
  getPageData()
}

const handleCurrentChange = (page:number)=> {
  currentPage.value = page
  getPageData()
}


// 打开编辑弹窗
const handleEdit = (row: ProjectInfo) => {
  editForm.value.id = row.id
  editForm.value.name = row.name
  edit_dialogVisible.value = true
}

// 处理编辑提交
const handleEditSubmit = () => {
  if (!editForm.value.name.trim()) {
    ElMessage.warning('项目名称不能为空')
    return
  }
  editProject(editForm.value.id, editForm.value.name).then((response) => {
    if (response.code === 200) {
      ElMessage.success('编辑成功')
      edit_dialogVisible.value = false
      getPageData()
    } else {
      ElMessage.error('编辑失败')
    }
  })
}

// 处理删除
const handleDelete = (row: ProjectInfo) => {
  ElMessageBox.confirm(
    `确定要删除项目 "${row.name}" 吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      // 调用删除项目的API
      const response = await deleteProject(row.id)
      if (response.code == 200 ){
        ElMessage.success('删除成功')
        getPageData() // 刷新列表
      }
    } catch (error) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {
    ElMessage.info('已取消删除')
  })
}

// 处理新增
const handleAddSubmit = () => {
  if (!newProject.value.trim()) {
    ElMessage.warning('项目名称不能为空')
    return
  }
  addProject(newProject.value).then((response) => {
    if (response.code == 201) {
      ElMessage.success('新增成功')
      add_dialogVisible.value = false
      getPageData()
    } else {
      ElMessage.error('新增失败')
    }
  })
}

// 处理筛选
const handleFilter = () => {
  // 暂时先弹窗提示
  ElMessage.info('筛选功能尚未实现，敬请期待')
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

.edit-form {
  padding: 10px;

  .edit-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
  }
}
</style>