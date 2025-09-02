
<template>
  <div class="project-manage-container">
    <!-- 页面头部组件 -->
    <PageHeader
      :total-projects="totalProjects"
      @filter="handleFilter"
      @add-project="add_dialogVisible = true"
    />

    <!-- 主要内容卡片 -->
    <div class="main-card">
      <!-- 表格容器 -->
      <div class="table-container">
        <el-table
          :data="projectList"
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
            prop="name"
            label="项目名称"
            min-width="200"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <div class="project-info">
                <div class="project-details">
                  <div class="project-name">{{ row.name }}</div>
                  <div class="project-description">API测试项目</div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column
            label="创建时间"
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
                {{ new Date().toLocaleDateString() }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column
            label="状态"
            width="120"
            align="center"
          >
            <template #default="{ row }">
              <div class="status-badge active">
                <div class="status-dot"></div>
                <span class="status-text">进行中</span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column
            label="操作"
            width="200"
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
                
                <button class="table-btn delete" @click="handleDelete(row)">
                  <svg class="btn-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <polyline points="3,6 5,6 21,6" stroke="currentColor" stroke-width="2"/>
                    <path d="m19,6v14a2,2 0 0,1-2,2H7a2,2 0 0,1-2-2V6m3,0V4a2,2 0 0,1,2-2h4a2,2 0 0,1,2,2v2" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  删除
                </button>
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
          :page-sizes="[5, 10, 20, 50]"
          :page-size="pageSize"
          layout="total, sizes, prev, pager, next, jumper"
          :total="totalProjects"
          background
        />
      </div>
    </div>

    <!-- 项目信息对话框 -->
    <el-dialog
      v-model="edit_dialogVisible"
      title="编辑项目"
      width="540px"
      :close-on-click-modal="false"
      class="modern-dialog"
    >
      <div class="dialog-content">
        <el-form :model="editForm" label-width="100px" class="project-form">
          <el-form-item label="项目名称">
            <el-input 
              v-model="editForm.name" 
              placeholder="请输入项目名称"
              class="form-input"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="edit_dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleEditSubmit">保存更改</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 新增项目对话框 -->
    <el-dialog
      v-model="add_dialogVisible"
      title="新增项目"
      width="540px"
      :close-on-click-modal="false"
      class="modern-dialog"
    >
      <div class="dialog-content">
        <el-form :model="{ name: newProject }" label-width="100px" class="project-form">
          <el-form-item 
          header-align="center"
          class-name="user-info-column"
          label="项目名称">
            <el-input 
              v-model="newProject" 
              placeholder="请输入项目名称"
              class="form-input"
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="add_dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleAddSubmit">创建项目</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { addProject,getProjectList,editProject,deleteProject } from '@/api/project'
import type { ProjectInfo } from '@/api/project/types'
import PageHeader from './PageHeader.vue'

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
  }).catch((error) => {
    console.error('编辑项目失败:', error)
    ElMessage.error('编辑失败，请稍后重试')
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
      newProject.value = '' // 清空输入框
      getPageData()
    } else {
      ElMessage.error('新增失败')
    }
  }).catch((error) => {
    console.error('新增项目失败:', error)
    ElMessage.error('新增失败，请稍后重试')
  })
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

.project-manage-container {
  padding: 24px;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  min-height: 100vh;

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

      // 项目信息样式
      .project-info {
        display: flex;
        align-items: center;

        .project-avatar {
          width: 40px;
          height: 40px;
          border-radius: var(--border-radius-md);
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

        .project-details {
          .project-name {
            font-size: 15px;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 2px;
          }

          .project-description {
            font-size: 13px;
            color: var(--text-secondary);
          }
        }
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

          &.delete {
            background: rgba(239, 68, 68, 0.1);
            color: var(--error-color);
            border: 1px solid rgba(239, 68, 68, 0.2);

            &:hover {
              background: rgba(239, 68, 68, 0.2);
              transform: translateY(-1px);
            }
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
    .project-form {
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
      transition: all 0.2s ease;
      border: none;

      .btn-icon {
        width: 16px;
        height: 16px;
      }

      &.secondary {
        background: var(--surface-secondary);
        color: var(--text-secondary);
        border: 1px solid var(--border-medium);

        &:hover {
          background: var(--surface-tertiary);
          color: var(--text-primary);
        }
      }

      &.primary {
        background: var(--primary-gradient);
        color: white;

        &:hover {
          transform: translateY(-1px);
          box-shadow: var(--shadow-md);
        }
      }

      &:active {
        transform: translateY(0);
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .project-manage-container {
    padding: 16px;

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
  .project-manage-container {
    .dialog-footer {
      flex-direction: column;

      .dialog-btn {
        justify-content: center;
      }
    }
  }
}
</style>