<template>
  <el-button 
    type="primary" 
    style="margin-left: 16px" 
    @click="drawer = true"
  >
    <el-icon class="el-icon--left"><Delete /></el-icon>
    进入回收站
  </el-button>

  <el-drawer 
    v-model="drawer" 
    title="已删除用例回收站" 
    size="70%" 
    :with-header="true"
    direction="rtl"
  >
    <div class="recycle-container">
      <div class="recycle-header">
        <h3>已删除用例列表</h3>
        <div class="recycle-actions">
          <el-button type="primary" size="small" @click="handleBatchRestore" :disabled="!hasSelection">
            <el-icon class="el-icon--left"><RefreshLeft /></el-icon>
            批量恢复
          </el-button>
          <el-button type="danger" size="small" @click="handleBatchDelete" :disabled="!hasSelection">
            <el-icon class="el-icon--left"><DeleteFilled /></el-icon>
            彻底删除
          </el-button>
          <el-button type="danger" size="small" @click="handleClearAll">
            <el-icon class="el-icon--left"><DeleteFilled /></el-icon>
            清空回收站
          </el-button>
        </div>
      </div>
      
      <el-table
        ref="recycleTableRef"
        :data="recycleData"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        v-loading="loading"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column type="index" label="序号" width="80" />
        <el-table-column property="name" label="用例名称" />
        <el-table-column property="creater_name" label="创建人" width="120" />
        <el-table-column property="created" label="创建时间" width="180" />
        <el-table-column property="delete_time" label="删除时间" width="180" />
        <el-table-column fixed="right" label="操作" width="180">
          <template #default="scope">
            <el-button
              size="small"
              type="primary"
              link
              @click="handleRestore(scope.row)"
            >
              恢复
            </el-button>
            <el-button
              size="small"
              type="danger"
              link
              @click="handlePermanentDelete(scope.row)"
            >
              彻底删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-pagination
        style="margin-top: 20px; text-align: center"
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30, 50]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, computed } from 'vue'
import { Delete, RefreshLeft, DeleteFilled } from '@element-plus/icons-vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import type { TestCaseInfo } from '@/api/case/types'
import { getTestCaseList, RestoreTestCase,RealDeleteTestCase,ClearTestCase } from '@/api/case'


// 抽屉控制
const drawer = ref(false)

// 表格数据
const recycleTableRef = ref()
const recycleData = ref<TestCaseInfo[]>([])
const loading = ref(false)
const selectedItems = ref<TestCaseInfo[]>([])
const hasSelection = computed(() => selectedItems.value.length > 0)

// 分页控制
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 监听抽屉打开状态
watch(drawer, (isOpen) => {
  if (isOpen) {
    loadRecycleData()
  }
})

// 加载回收站数据
const loadRecycleData = async () => {
  loading.value = true
  try {
    // 参数中的is_deleted设置为true，表示获取回收站数据
    const response = await getTestCaseList(
      currentPage.value,
      pageSize.value,
      true // 获取已删除的数据
    )
    
    if (response.code === 200) {
      recycleData.value = response.results?.data || []
      total.value = response.results?.total || 0
      
      if (recycleData.value.length === 0) {
        ElMessage.info('回收站中暂无数据')
      }
    } else {
      ElMessage.error(response.msg || '获取回收站数据失败')
    }
  } catch (error) {
    console.error('获取回收站数据出错:', error)
    ElMessage.error('获取回收站数据失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 处理分页改变
const handleSizeChange = (size: number) => {
  pageSize.value = size
  loadRecycleData()
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
  loadRecycleData()
}

// 处理选择变化
const handleSelectionChange = (selection: TestCaseInfo[]) => {
  selectedItems.value = selection
}

// 恢复单个用例
const handleRestore = (row: TestCaseInfo) => {
  ElMessageBox.confirm(
    `确定要恢复用例"${row.name}"吗？`,
    '恢复确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    // 调用恢复API
    const response = await RestoreTestCase(row.id, 'false')
    if (response.code == 200) {
      loadRecycleData()
      ElMessage.success(`用例"${row.name}"已恢复`)
    }else{
      ElMessage.error(response.msg || '恢复用例失败')
    }

  }).catch(() => {
    // 取消操作
  })
}

// 彻底删除单个用例
const handlePermanentDelete = (row: TestCaseInfo) => {
  ElMessageBox.confirm(
    `用例"${row.name}"将被彻底删除，不可恢复！确定要继续吗？`,
    '删除警告',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'error'
    }
  ).then(async () => {
    // 调用彻底删除API
    const response = await RealDeleteTestCase(row.id,true)
    if (response.code == 200) {
      loadRecycleData()
      ElMessage.success(`用例"${row.name}"已彻底删除`)
    }else{
      ElMessage.error(response.msg || '彻底删除用例失败')
    }

  }).catch(() => {
    // 取消操作
  })
}

// 清空回收站
const handleClearAll = () => {
  ElMessageBox.confirm(
    '确定要清空回收站吗？',
    '清空确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    // 调用清空回收站API
    const response = await ClearTestCase()
    if (response.code == 200) {
      ElMessage.success(`已清空回收站`)
      loadRecycleData()
    }else{
      ElMessage.error(response.msg || '清空回收站失败')
    }
  }).catch(() => {
    // 取消操作
  })
}



//-------------------------------------------功能待实现----------------------------------------------------
// 批量恢复
const handleBatchRestore = () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请选择要恢复的用例')
    return
  }
  
  ElMessageBox.confirm(
    `确定要恢复选中的 ${selectedItems.value.length} 个用例吗？`,
    '批量恢复确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    // TODO: 调用批量恢复API
    ElMessage.success(`已恢复 ${selectedItems.value.length} 个用例————功能待实现`)
    loadRecycleData()
  }).catch(() => {
    // 取消操作
  })
}

// 批量彻底删除
const handleBatchDelete = () => {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请选择要删除的用例')
    return
  }
  
  ElMessageBox.confirm(
    `选中的 ${selectedItems.value.length} 个用例将被彻底删除，不可恢复！确定要继续吗？`,
    '批量删除警告',
    {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'error'
    }
  ).then(async () => {
    // TODO: 调用批量彻底删除API
    ElMessage.success(`已彻底删除 ${selectedItems.value.length} 个用例————功能待实现`)
    loadRecycleData()
  }).catch(() => {
    // 取消操作
  })
}
</script>

<style scoped>
.recycle-container {
  padding: 20px;
}

.recycle-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.recycle-header h3 {
  margin: 0;
  font-size: 18px;
}

.recycle-actions {
  display: flex;
  gap: 10px;
}
</style>