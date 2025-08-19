<template>
  <div class="case-tree-container">
    <div class="header">
      <h2>场景测试文件</h2>
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
        <el-form-item label="模块名称">
          <el-input v-model="moduleForm.name" placeholder="请输入模块名称"></el-input>
        </el-form-item>
        <el-form-item v-if="dialogType === 'add' && moduleForm.parent_id" label="父模块">
          <el-input v-model="parentName" disabled></el-input>
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
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getCaseFolderTree, 
        createTestModule, 
        updateTestModule, 
        deleteTestModule ,
      } from '@/api/case/module/index'
import { convertToElTreeData } from '@/api/case/module/types'
import type { ElTreeNode, TestModuleNode } from '@/api/case/module/types'
import { useCaseModuleStore } from '@/store/caseModule'

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

// 加载测试文件树
const loadTreeData = async () => {
  loading.value = true
  try {
    const response = await getCaseFolderTree()
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
        // 重新加载树
        loadTreeData()
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

  try {
    let response
    if (dialogType.value === 'add') {
      response = await createTestModule(moduleForm.value.name, moduleForm.value.parent_id)
    } else {
      response = await updateTestModule(moduleForm.value.id, moduleForm.value.name)
    }

    if (response.success) {
      ElMessage.success(dialogType.value === 'add' ? '添加成功' : '更新成功')
      dialogVisible.value = false
      // 重新加载树
      loadTreeData()
    } else {
      ElMessage.error(response.msg || (dialogType.value === 'add' ? '添加失败' : '更新失败'))
    }
  } catch (error) {
    console.error('操作失败', error)
    ElMessage.error(dialogType.value === 'add' ? '添加失败，请稍后重试' : '更新失败，请稍后重试')
  }
}

onMounted(() => {
  loadTreeData()
})

// 使用 Pinia store 管理选中的模块ID
const caseModuleStore = useCaseModuleStore()

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
