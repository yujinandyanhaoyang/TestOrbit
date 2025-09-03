<template>
  <div class="case-tree-container">
    <div class="header-section">
      <div class="project-selector">
        <label class="selector-label">项目选择</label>
        <el-select
          v-model="caseModuleStore.selectedProjectId"
          placeholder="请选择所属项目组"
          class="project-select"
          clearable
          @change="handleProjectChange">
          <el-option 
            v-for="project in projectOptions" 
            :key="project.id" 
            :label="project.name" 
            :value="project.id">
          </el-option>
        </el-select>
      </div>
      <el-button 
        type="primary" 
        class="add-root-btn"
        @click="handleAddRoot"
        :icon="'Plus'"
      >
        添加根目录
      </el-button>
    </div>
    
    <div class="tree-section" v-loading="loading">
      <el-tree
        ref="treeRef"
        :data="treeData"
        node-key="id"
        :props="defaultProps"
        default-expand-all
        :expand-on-click-node="false"
        class="custom-tree"
      >
        <template #default="{ node, data }">
          <div class="tree-node-content">
            <div class="node-info" @click="handleNodeClick(data.id)">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="folder-icon">
                <path d="M3 7v10a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2H9l-2-2H5a2 2 0 0 0-2 2v0"></path>
              </svg>
              <span class="node-label">{{ node.label }}</span>
            </div>
            <div class="node-actions">
              <button
                class="action-btn add-btn"
                @click.stop="handleAddChild(data)"
                title="添加子模块"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M5 12h14"></path>
                  <path d="M12 5v14"></path>
                </svg>
              </button>
              <button
                class="action-btn edit-btn"
                @click.stop="handleEdit(data)"
                title="编辑模块"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </button>
              <button
                class="action-btn delete-btn"
                @click.stop="handleDelete(node, data)"
                title="删除模块"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3,6 5,6 21,6"></polyline>
                  <path d="m19,6v14a2,2 0 0,1-2,2H7a2,2 0 0,1-2-2V6m3,0V4a2,2 0 0,1,2-2h4a2,2 0 0,1,2,2v2"></path>
                </svg>
              </button>
            </div>
          </div>
        </template>
      </el-tree>
      
      <div v-if="!loading && treeData.length === 0" class="empty-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="empty-icon">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2v11z"></path>
        </svg>
        <p class="empty-title">暂无测试场景</p>
        <p class="empty-desc">点击上方按钮添加根目录</p>
      </div>
    </div>

    <!-- 添加或编辑模块的对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加测试模块' : '编辑测试模块'"
      width="30%"
    >
      <el-form :model="moduleForm" label-width="80px">
        <el-form-item label="所属项目">
          <el-input v-model="selectedProjectName" disabled></el-input>
        </el-form-item>
        <el-form-item v-if="dialogType === 'add' && moduleForm.parent_id" label="父模块">
          <el-input v-model="parentName" disabled></el-input>
        </el-form-item>
        <el-form-item label="模块名称">
          <el-input v-model="moduleForm.name" placeholder="请输入模块名称"></el-input>
        </el-form-item>

      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitModule">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCaseFolderTree, 
        createTestModule, 
        updateTestModule, 
        deleteTestModule ,
      } from '@/api/case/module/index'
import { convertToElTreeData } from '@/api/case/module/types'
import type { ElTreeNode, TestModuleNode } from '@/api/case/module/types'
import { useCaseModuleStore } from '@/store/caseModule'
import { getProjectList } from '@/api/project/index'

// 当前所处项目组
// 项目ID到名称的映射
const projectMap = ref<Map<number, string>>(new Map())
// 项目选项列表
const projectOptions = ref<{id: number, name: string}[]>([])

// 使用 Pinia store 管理选中状态
const caseModuleStore = useCaseModuleStore()

// 树数据
const treeData = ref<ElTreeNode[]>([])
const loading = ref(true)
const treeRef = ref()

// 树配置
const defaultProps = {
  children: 'children',
  label: 'label'
}

// 对话框控制
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const moduleForm = ref({
  id: '',
  name: '',
  parent_id: null as string | null
})
const currentNode = ref<TestModuleNode | null>(null)
const parentName = computed(() => {
  // 根据父ID在树中查找父节点名称
  if (!moduleForm.value.parent_id) return ''
  const findNode = (nodes: ElTreeNode[]): string => {
    for (const node of nodes) {
      if (node.id === moduleForm.value.parent_id) return node.label
      if (node.children) {
        const found = findNode(node.children)
        if (found) return found
      }
    }
    return ''
  }
  return findNode(treeData.value)
})

// 计算当前选中项目的名称
const selectedProjectName = computed(() => {
  if (!caseModuleStore.selectedProjectId) return '未选择项目'
  return projectMap.value.get(caseModuleStore.selectedProjectId) || `项目ID: ${caseModuleStore.selectedProjectId}`
})

// 加载测试文件树
const loadTreeData = async (projectId?: number) => {
  loading.value = true
  try {
    // 如果有选中的项目ID，则传递给API
    const response = await getCaseFolderTree(projectId)
    if (response.success) {
      treeData.value = convertToElTreeData(response.results)
    } else {
      ElMessage.error('加载测试文件树失败')
    }
  } catch (error) {
    console.error('加载测试文件树出错', error)
    ElMessage.error('加载测试文件树失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 添加根目录
const handleAddRoot = () => {
  dialogType.value = 'add'
  moduleForm.value = {
    id: '',
    name: '',
    parent_id: null
  }
  dialogVisible.value = true
}

// 添加子节点
const handleAddChild = (data: ElTreeNode) => {
  dialogType.value = 'add'
  moduleForm.value = {
    id: '',
    name: '',
    parent_id: data.id || null
  }
  dialogVisible.value = true
}

// 编辑节点
const handleEdit = (data: ElTreeNode) => {
  dialogType.value = 'edit'
  moduleForm.value = {
    id: data.id || '',
    name: data.label,
    parent_id: data.data?.parent_id || null
  }
  currentNode.value = data.data
  dialogVisible.value = true
}

// 删除节点
const handleDelete = (node: any, data: ElTreeNode) => {
  ElMessageBox.confirm(
    `确定要删除模块"${data.label}"吗？${data.children?.length ? '删除后其所有子模块也将一并删除！' : ''}`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      const response = await deleteTestModule(data.id || '')
      if (response.success) {
        ElMessage.success('删除成功')
        // 重新加载树，使用当前选中的项目ID
        loadTreeData(caseModuleStore.selectedProjectId || undefined)
      } else {
        ElMessage.error(response.msg || '删除失败')
      }
    } catch (error) {
      console.error('删除模块出错', error)
      ElMessage.error('删除失败，请稍后重试')
    }
  }).catch(() => {
    // 取消删除
  })
}

// 提交模块（添加或更新）
const submitModule = async () => {
  if (!moduleForm.value.name.trim()) {
    ElMessage.warning('模块名称不能为空')
    return
  }
  
  // 如果是添加操作且没有选择项目，提示用户
  if (dialogType.value === 'add' && !caseModuleStore.selectedProjectId) {
    ElMessage.warning('请先选择一个项目')
    return
  }

  try {
    let response
    if (dialogType.value === 'add') {
      // 将项目ID一并传递
      response = await createTestModule(
        moduleForm.value.name, 
        moduleForm.value.parent_id,
        caseModuleStore.selectedProjectId || undefined
      )
    } else {
      response = await updateTestModule(moduleForm.value.id, moduleForm.value.name)
    }

    if (response.success) {
      ElMessage.success(dialogType.value === 'add' ? '添加成功' : '更新成功')
      dialogVisible.value = false
      // 重新加载树
      loadTreeData(caseModuleStore.selectedProjectId || undefined)
    } else {
      ElMessage.error(response.msg || (dialogType.value === 'add' ? '添加失败' : '更新失败'))
    }
  } catch (error) {
    console.error('操作失败', error)
    ElMessage.error(dialogType.value === 'add' ? '添加失败，请稍后重试' : '更新失败，请稍后重试')
  }
}

// 获取项目列表
const fetchProjects = async () => {
  try {
    const response = await getProjectList(1, 1000) // 获取所有项目，假设不超过1000个
    
    if (response.code == 200) {
      // 清空现有数据
      projectOptions.value = []
      
      // 创建映射和选项列表
      response.results.data.forEach((project: any) => {
        // 更新映射
        projectMap.value.set(project.id, project.name)
        
        // 添加到选项列表
        projectOptions.value.push({
          id: project.id,
          name: project.name
        })
      })
      
      // 🔥 默认选中第一个项目（如果当前没有选中任何项目或选中的项目不在列表中）
      if (projectOptions.value.length > 0) {
        const currentProjectExists = projectOptions.value.some(p => p.id === caseModuleStore.selectedProjectId)
        
        if (!caseModuleStore.selectedProjectId || !currentProjectExists) {
          const firstProject = projectOptions.value[0]

          caseModuleStore.setSelectedProjectId(firstProject.id)
          // 立即加载数据，因为这是初始化
          loadTreeData(firstProject.id)
        } else {
          // 如果已有有效的选中项目，加载该项目数据

          loadTreeData(caseModuleStore.selectedProjectId)
        }
      }
    } else {
      ElMessage.warning('获取项目列表失败')
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
    ElMessage.warning('获取项目列表失败')
  }
}

// 处理项目选择变更
const handleProjectChange = (projectId: number | null) => {

  // 只更新store中的项目ID，让watch监听器处理数据加载
  caseModuleStore.setSelectedProjectId(projectId)
}

// 监听store中项目ID的变化
watch(() => caseModuleStore.selectedProjectId, (newVal, oldVal) => {

  // 只有在真正发生变化时才加载数据（避免初始化时的空加载）
  if (newVal !== oldVal && newVal !== null) {
    loadTreeData(newVal)
  } else if (newVal === null) {
    // 如果清空选择，加载默认树
    loadTreeData()
  }
}, { immediate: false })

onMounted(() => {
  // 先获取项目列表，fetchProjects内部会自动选择第一个项目并加载对应的树数据
  fetchProjects()
})

// 处理节点点击
const handleNodeClick = (id: string) => {
  // 更新 store 中的选中模块ID
  caseModuleStore.setSelectedModuleId(id)
}

</script>

<style scoped lang="scss">
// 设计系统变量（与 head 组件保持一致，使用 Element Plus 主题变量）
:root {
  --primary-color: var(--el-color-primary);
  --primary-light: var(--el-color-primary-light-9);
  --success-color: #4caf50;
  --warning-color: #ff9800;
  --error-color: #f44336;
  --text-primary: #303133;    // 与 head 中标题颜色一致
  --text-secondary: #606266;  // 与 head 中次要文字一致
  --text-disabled: #909399;
  --background-primary: #ffffff;
  --background-secondary: #f5f7fa; // 与 head 背景一致
  --border-color: #e4e7ed;         // 与 head 边框一致
  --border-radius: 8px;
  --shadow-light: 0 2px 4px rgba(0, 0, 0, 0.08);
  --shadow-medium: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.case-tree-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--background-primary);
  border-radius: var(--border-radius);
  overflow: hidden;
  
  .header-section {
    padding: 16px;
  background: var(--background-secondary);
  border-bottom: 1px solid var(--border-color);
    
    .project-selector {
      margin-bottom: 12px;
      
      .selector-label {
        display: block;
        font-size: 13px;
        font-weight: 600;
        color: var(--text-secondary);
        margin-bottom: 8px;
      }
      
      .project-select {
        width: 100%;
        
        :deep(.el-input__inner) {
          border-radius: 6px;
          border-color: var(--border-color);
          transition: all 0.2s ease;
          
          &:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 2px var(--primary-light);
          }
        }
      }
    }
    
    .add-root-btn {
      width: 100%;
      height: 38px;
      border-radius: 6px;
      font-weight: 500;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.2s ease;
      
      .btn-icon {
        width: 16px;
        height: 16px;
      }
      
      &:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-medium);
      }
    }
  }
  
  .tree-section {
    flex: 1;
    padding: 12px 16px;
    overflow: auto;
    
    .custom-tree {
      background: transparent;
      
      :deep(.el-tree-node) {
        .el-tree-node__content {
          height: 40px;
          padding: 0 8px;
          border-radius: 6px;
          margin-bottom: 2px;
          transition: all 0.2s ease;
          
          &:hover {
            background-color: var(--primary-light);
          }
          
          .el-tree-node__expand-icon {
            color: var(--text-secondary);
            font-size: 14px;
            
            &.expanded {
              transform: rotate(90deg);
            }
          }
        }
        
        &.is-current > .el-tree-node__content {
          background-color: var(--primary-light);
          border: 1px solid var(--el-color-primary-light-7);
        }
      }
    }
    
    .tree-node-content {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 4px;
      
      .node-info {
        display: flex;
        align-items: center;
        flex: 1;
        cursor: pointer;
        padding: 4px 0;
        
        .folder-icon {
          color: var(--primary-color);
          margin-right: 8px;
          flex-shrink: 0;
        }
        
        .node-label {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
          transition: color 0.2s ease;
        }
        
        &:hover .node-label {
          color: var(--primary-color);
        }
      }
      
      .node-actions {
        display: flex;
        gap: 4px;
        opacity: 0;
        transition: opacity 0.2s ease;
        
        .action-btn {
          width: 28px;
          height: 28px;
          border: none;
          border-radius: 4px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: all 0.2s ease;
          background: transparent;
          
          &:hover {
            transform: translateY(-1px);
            box-shadow: var(--shadow-light);
          }
          
          &.add-btn {
            color: var(--success-color);
            
            &:hover {
              background: rgba(76, 175, 80, 0.08);
            }
          }
          
          &.edit-btn {
            color: var(--warning-color);
            
            &:hover {
              background: rgba(255, 152, 0, 0.08);
            }
          }
          
          &.delete-btn {
            color: var(--error-color);
            
            &:hover {
              background: rgba(244, 67, 54, 0.08);
            }
          }
        }
      }
      
      &:hover .node-actions {
        opacity: 1;
      }
    }
    
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 200px;
      text-align: center;
      
      .empty-icon {
        color: var(--text-disabled);
        margin-bottom: 16px;
      }
      
      .empty-title {
        font-size: 16px;
        font-weight: 500;
        color: var(--text-secondary);
        margin: 0 0 8px 0;
      }
      
      .empty-desc {
        font-size: 14px;
        color: var(--text-disabled);
        margin: 0;
      }
    }
  }
}

// 加载动画优化
:deep(.el-loading-mask) {
  border-radius: var(--border-radius);
  background-color: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
}

// 响应式设计
@media (max-width: 768px) {
  .case-tree-container {
    .header-section {
      padding: 12px;
      
      .add-root-btn {
        height: 36px;
        font-size: 14px;
      }
    }
    
    .tree-section {
      padding: 8px 12px;
      
      .tree-node-content {
        .node-actions .action-btn {
          width: 32px;
          height: 32px;
        }
      }
    }
  }
}
</style>
