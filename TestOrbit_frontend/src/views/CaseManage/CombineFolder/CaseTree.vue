<template>
  <div class="case-tree-container">
    <div class="header">
      <el-select
        v-model="caseModuleStore.selectedProjectId"
        placeholder="请选择所属项目组"
        style="width: 100%"
        clearable
        @change="handleProjectChange">
        <el-option 
          v-for="project in projectOptions" 
          :key="project.id" 
          :label="project.name" 
          :value="project.id">
        </el-option>
      </el-select>
      <el-button type="primary" size="small" @click="handleAddRoot">添加根目录</el-button>
    </div>
    
    <div class="tree-container" v-loading="loading">
      <el-tree
        ref="treeRef"
        :data="treeData"
        node-key="id"
        :props="defaultProps"
        default-expand-all
        :expand-on-click-node="false"
      >
        <template #default="{ node, data }">
          <span class="custom-tree-node">
            <span @click="handleNodeClick(data.id)">{{ node.label }}</span>
            <span class="node-actions">
              <el-button
                type="primary"
                link
                size="small"
                @click="handleAddChild(data)"
              >
                添加
              </el-button>
              <el-button
                type="primary"
                link
                size="small"
                @click="handleEdit(data)"
              >
                编辑
              </el-button>
              <el-button
                type="danger"
                link
                size="small"
                @click="handleDelete(node, data)"
              >
                删除
              </el-button>
            </span>
          </span>
        </template>
      </el-tree>
      
      <div v-if="!loading && treeData.length === 0" class="empty-tip">
        暂无测试场景，请添加根目录
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
          console.log(`🎯 自动选中第一个项目: ${firstProject.name} (ID: ${firstProject.id})`)
          caseModuleStore.setSelectedProjectId(firstProject.id)
          // 立即加载数据，因为这是初始化
          loadTreeData(firstProject.id)
        } else {
          // 如果已有有效的选中项目，加载该项目数据
          console.log(`📌 保持当前选中项目: ID ${caseModuleStore.selectedProjectId}`)
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
  console.log(`🔄 用户手动选择项目: ${projectId}`)
  // 只更新store中的项目ID，让watch监听器处理数据加载
  caseModuleStore.setSelectedProjectId(projectId)
}

// 监听store中项目ID的变化
watch(() => caseModuleStore.selectedProjectId, (newVal, oldVal) => {
  console.log(`📊 Store中项目ID变化: ${oldVal} -> ${newVal}`)
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
.case-tree-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    margin-bottom: 10px;
    
    h2 {
      margin: 0;
    }
  }
  
  .tree-container {
    flex: 1;
    overflow: auto;
    padding: 10px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    
    .empty-tip {
      padding: 20px;
      text-align: center;
      color: #909399;
    }
  }
}

.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
  
  .node-actions {
    display: none;
  }
  
  &:hover .node-actions {
    display: inline-block;
  }
}
</style>
