<template>
  <div class="case-container">
    <!-- 顶部操作区 -->
    <Head 
      @search="searchCasesByName" 
      @add="handleAddCase"
      @batch-action="handleBatchAction"
      :has-selection="multipleSelection.length > 0"
    />
    <!-- 场景用例表格 -->
    <el-table
      ref="multipleTableRef"
      :data="tableData"
      row-key="id"
      style="width: 100%"
      table-layout="fixed"
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" :selectable="selectable" width="40" />
      <el-table-column type="index" label="序号" width="80" align="center" />
      <el-table-column property="name" sortable label="用例名称" />
      <el-table-column property="status" sortable label="状态" />
      <el-table-column property="creater_name" sortable label="创建人" />
      <el-table-column property="updater_name" sortable label="修改人" />
      <el-table-column property="latest_run_time" sortable label="执行完成时间" />
      <el-table-column property="created" sortable label="创建时间" />
      <el-table-column property="updated" sortable label="修改时间" />
      <el-table-column fixed="right" label="操作" min-width="200">
        <template #default="scope">
          <el-button type="primary" text size="small" @click="openTestReport(scope.row.id)">执行</el-button>
          <el-button type="primary" text size="small" @click="openCaseDetail(scope.row.id)">编辑</el-button>
          <el-button type="primary" text size="small" @click="handleCopy(scope.row.id)">复制</el-button>
          <el-button type="primary" text size="small" @click="openTestReport(scope.row.id)">报告</el-button>
          <el-button type="danger" text size="small" @click="handleDelete(scope.row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!--底部分页-->
    <el-pagination
      style="display: flex; justify-content: center; margin: 20px 0;"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-sizes="[2, 4, 5, 15]"
      :page-size="pageSize"
      layout="total, sizes, prev, pager, next, jumper"
      :total="total">
    </el-pagination>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import type { TableInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import type { TestCaseInfo, TestCaseListResponse } from '@/api/case/types'
import { getTestCaseList, DeleteTestCase, CopyTestCase } from '@/api/case'
// 使用 Pinia store 管理模块ID
import { useCaseModuleStore } from '@/store/caseModule'

//引入自定义顶部功能组件
import Head from './head.vue'

// 暴露方法给父组件，用于打开用例详情和测试报告
const emit = defineEmits(['openCaseDetail', 'openTestReport'])

// 选择行范围
const selectable = (row: TestCaseInfo) => true
// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 获取数据参数
const is_delete = ref(false)
// 使用 Pinia store 获取模块ID
const caseModuleStore = useCaseModuleStore()
// 表格实例
const tableData = ref<TestCaseInfo[]>()
const multipleTableRef = ref<TableInstance>()
const multipleSelection = ref<TestCaseInfo[]>([])

// 处理分页显示
const handleSizeChange = (size: number) =>{
  pageSize.value = size
  getCaseListData()
}

const handleCurrentChange = (page:number)=> {
  currentPage.value = page
  getCaseListData()
}

onMounted(() => {
  // 初始化数据
  // 初始化模块ID
  caseModuleStore.selectedModuleId = ''
  getCaseListData()
})

// 监听模块ID变化，自动加载对应的用例列表
watch(() => caseModuleStore.selectedModuleId, (newModuleId) => {
  if (newModuleId) {
    getCaseListData()
  } else {
    // 如果没有选中模块，清空表格数据
    tableData.value = []
    total.value = 0
  }
})

/**
 * 获取测试用例列表通用函数
 * 根据不同参数获取不同场景下的用例列表数据
 */
const getCaseListData = async() => {
  try {
    const response: TestCaseListResponse = await getTestCaseList(
      currentPage.value,
      pageSize.value,
      is_delete.value,
      undefined,
      caseModuleStore.selectedModuleId, // 使用 store 中的模块ID
    )
    if (response.code === 200) {
      total.value = response.results?.total || 0
      tableData.value = response.results?.data || []
      
      if (tableData.value.length === 0) {
        ElMessage.info('当前模块下暂无用例数据')
      }
    } else {
      ElMessage.error(response.msg || '获取用例数据失败')
    }
  } catch (error) {
    console.error('获取用例数据出错:', error)
    ElMessage.error('获取用例数据失败，请稍后重试')
  }
}

// 按名称搜索用例
const searchCasesByName = async (name: string) => {
  try {
    const response: TestCaseListResponse = await getTestCaseList(
      currentPage.value,
      pageSize.value,
      is_delete.value,
      name,
      caseModuleStore.selectedModuleId, // 使用 store 中的模块ID
    )
    if (response.code === 200) {
      total.value = response.results?.total || 0
      tableData.value = response.results?.data || []
      if (tableData.value.length === 0) {
        ElMessage.info('未找到匹配的用例数据')
      }
    } else {
      ElMessage.error(response.msg || '获取用例数据失败')
    }
  } catch (error) {
    console.error('获取用例数据出错:', error)
    ElMessage.error('获取用例数据失败，请稍后重试')
  }
}

// 处理选择变化-后期绑定批量执行-批量导出-批量删除
const handleSelectionChange = (val: TestCaseInfo[]) => {
  multipleSelection.value = val
}

// 删除场景用例
const handleDelete = async(id:number) =>{
  const response = await DeleteTestCase(id)
  if (response.code == 200) {
    // 弹窗提示删除成功
    ElMessage.success('删除成功')
    getCaseListData()
  }
}

// 复制场景用例
const handleCopy = async(id:number) =>{
  const response = await CopyTestCase(id)
  if (response.code == 200) {
    // 弹窗提示复制成功
    ElMessage.success('复制成功')
    getCaseListData()
  }
}

// 添加新用例
const handleAddCase = () => {
  // TODO: 实现添加用例逻辑
  ElMessage.info('添加用例功能尚未实现')
  // 可以在这里打开添加用例的对话框或跳转到添加用例页面
}

// 处理批量操作
const handleBatchAction = () => {
  // 检查是否有选中项
  if (multipleSelection.value.length === 0) {
    ElMessage.warning('请先选择要操作的用例')
    return
  }
  
  // TODO: 显示批量操作菜单
  ElMessage.info(`已选中 ${multipleSelection.value.length} 项，批量操作功能尚未实现`)
}

// 打开用例详情（集成到父组件中的标签系统）
const openCaseDetail = (caseId: number) => {
  emit('openCaseDetail', caseId)
}

// 打开测试报告（集成到父组件中的标签系统）
const openTestReport = (reportId: number) => {
  emit('openTestReport', reportId)
}
</script>

<style scoped lang="scss">
.case-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  
  /* 确保表格区域占据剩余空间 */
  .el-table {
    flex: 1;
    overflow: auto;
  }
  
  /* 分页控件样式 */
  .el-pagination {
    margin-top: 10px;
  }
}
</style>
