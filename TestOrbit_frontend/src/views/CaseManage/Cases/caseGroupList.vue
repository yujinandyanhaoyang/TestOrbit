<template>
  <div class="case-container" 
    v-loading.fullscreen.lock="isRunning" 
    :element-loading-text="loadingText" 
    element-loading-background="rgba(0, 0, 0, 0.8)"
    :element-loading-icon="Loading"
    element-loading-svg-view-box="-10, -10, 50, 50">
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
          <el-button type="primary"  size="small" @click="handleRun(scope.row.id)">执行</el-button>
          <el-button type="info"  size="small" @click="openCaseDetail(scope.row.id)">编辑</el-button>
          <el-button   size="small" @click="handleCopy(scope.row.id)">复制</el-button>
          <el-button type="success"  size="small" @click="openTestReport(scope.row.id)">报告</el-button>
          <el-button type="danger"  size="small" @click="handleDelete(scope.row.id)">删除</el-button>
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

    <!-- 批量运行模式选择对话框 -->
    <el-dialog
      v-model="showRunModeDialog"
      title="选择运行模式"
      width="400px"
      :close-on-click-modal="false"
    >
      <div class="run-mode-selector">
        <p>您已选择 <strong>{{ multipleSelection.length }}</strong> 个用例，请选择运行模式：</p>
        
        <el-radio-group v-model="selectedRunMode" class="run-mode-options">
          <el-radio :label="0" class="run-mode-option">
            <div class="mode-info">
              <div class="mode-title">🚀 并行运行</div>
              <div class="mode-desc">多个用例同时执行，速度更快</div>
            </div>
          </el-radio>
          <el-radio :label="1" class="run-mode-option">
            <div class="mode-info">
              <div class="mode-title">📝 串行运行</div>
              <div class="mode-desc">用例按顺序逐个执行，更稳定</div>
            </div>
          </el-radio>
        </el-radio-group>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showRunModeDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmBatchRun">
            开始执行
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch } from 'vue'
import type { TableInstance } from 'element-plus'
import { ElMessage } from 'element-plus'
import { Loading } from '@element-plus/icons-vue'
import type { CaseGroupInfo, CaseGroupListResponse } from '@/api/case/caseGroup/types'
import { getCaseGroupList, DeleteCaseGroup, CopyCaseGroup,runCaseGroup } from '@/api/case/caseGroup'
// 使用 Pinia store 管理模块ID
import { useCaseModuleStore } from '@/store/caseModule'

//引入自定义顶部功能组件
import Head from './head.vue'

// 暴露方法给父组件，用于打开用例详情和测试报告
const emit = defineEmits(['openCaseDetail', 'openTestReport'])

// 选择行范围
const selectable = (row: CaseGroupInfo) => true
// 分页相关
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

// 获取数据参数
const is_delete = ref(false)
// 页面加载状态
const isRunning = ref(false)
// 加载提示信息
const loadingText = ref('用例执行中，请稍候...')
// 模拟进度
const currentProgress = ref(0)
let progressInterval: number | null = null
// 使用 Pinia store 获取模块ID
const caseModuleStore = useCaseModuleStore()
// 表格实例
const tableData = ref<CaseGroupInfo[]>()
const multipleTableRef = ref<TableInstance>()
const multipleSelection = ref<CaseGroupInfo[]>([])

// 批量运行模式选择对话框
const showRunModeDialog = ref(false)
const selectedRunMode = ref(0) // 默认选择并行模式 (0=并行, 1=串行)

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
    const response: CaseGroupListResponse = await getCaseGroupList(
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
    const response: CaseGroupListResponse = await getCaseGroupList(
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
const handleSelectionChange = (val: CaseGroupInfo[]) => {
  multipleSelection.value = val
}

// 删除场景用例
const handleDelete = async(id:number) =>{
  const response = await DeleteCaseGroup(id)
  if (response.code == 200) {
    // 弹窗提示删除成功
    ElMessage.success('删除成功')
    getCaseListData()
  }
}

// 复制场景用例
const handleCopy = async(id:number) =>{
  const response = await CopyCaseGroup(id)
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
const handleBatchAction = async (actionType: string) => {
  // 检查是否有选中项
  if (multipleSelection.value.length === 0) {
    ElMessage.warning('请先选择要操作的用例')
    return
  }
  
  // 根据操作类型执行不同的批量操作
  switch (actionType) {
    case 'run':
      // 显示运行模式选择对话框
      showRunModeDialog.value = true;
      break;
    case 'delete':
      // TODO: 实现批量删除
      ElMessage.info('批量删除功能尚未实现');
      break;
    case 'export':
      // TODO: 实现批量导出
      ElMessage.info('批量导出功能尚未实现');
      break;
    default:
      ElMessage.info(`已选中 ${multipleSelection.value.length} 项，请选择具体的批量操作`);
  }
}

// 确认批量运行 - 用户选择运行模式后的处理
const confirmBatchRun = async () => {
  // 关闭对话框
  showRunModeDialog.value = false;
  
  // 执行批量运行
  await handleBatchRun(selectedRunMode.value);
}

// 批量运行用例 - 修改为接受运行模式参数
const handleBatchRun = async (parallel: number = 0) => {
  try {
    // 获取选中的用例ID
    const caseIds = multipleSelection.value.map(item => item.id);
    const modeText = parallel === 0 ? '并行' : '串行';
    
    // 更新加载提示
    loadingText.value = `准备${modeText}执行 ${caseIds.length} 个用例...`;
    isRunning.value = true;
    
    // 启动进度模拟
    startProgressSimulation();
    
    // 使用用户选择的执行模式
    const response = await runCaseGroup(caseIds, parallel);

    if (response.code === 200) {
      // 停止进度模拟
      stopProgressSimulation();
      
      // 更新加载提示
      loadingText.value = `所有用例${modeText}执行完成，正在刷新数据...`;
      
      // 延迟一下，让用户看到执行完成的提示
      await new Promise(resolve => setTimeout(resolve, 800));
      
      ElMessage.success(`成功${modeText}执行 ${caseIds.length} 个用例`);
      getCaseListData();
      
      // TODO: 批量执行完成后可以考虑打开批量报告页面
    } else {
      ElMessage.error(response.msg || `${modeText}执行用例失败`);
    }
  } catch (error) {
    console.error('批量执行用例出错:', error);
    ElMessage.error('批量执行用例时发生错误，请稍后重试');
  } finally {
    // 无论执行成功还是失败，都需要关闭加载状态
    stopProgressSimulation(); // 确保进度模拟被停止
    isRunning.value = false;
    // 重置加载提示文本
    loadingText.value = '用例执行中，请稍候...';
  }
}

// 打开用例详情（集成到父组件中的标签系统）
const openCaseDetail = (caseId: number) => {
  // console.log('打开用例详情(caseGroupList):', caseId);
  emit('openCaseDetail', caseId)
}

// 开始进度模拟
const startProgressSimulation = () => {
  // 重置进度
  currentProgress.value = 0;
  
  // 清除可能存在的旧定时器
  if (progressInterval !== null) {
    window.clearInterval(progressInterval);
  }
  
  // 创建新的定时器，模拟进度增加
  progressInterval = window.setInterval(() => {
    // 进度从0增加到95%，留出5%给最后的完成操作
    if (currentProgress.value < 95) {
      // 非线性增长，开始快，接近结束时变慢
      const increment = currentProgress.value < 60 ? 5 : (currentProgress.value < 80 ? 2 : 1);
      currentProgress.value += increment;
      
      // 更新加载文本，包含进度
      loadingText.value = `用例执行中，已完成 ${currentProgress.value}%...`;
    }
  }, 300);
};

// 停止进度模拟
const stopProgressSimulation = () => {
  if (progressInterval !== null) {
    window.clearInterval(progressInterval);
    progressInterval = null;
  }
  
  // 完成进度
  currentProgress.value = 100;
};

// 运行用例
const handleRun = async (id: number) => {
  try {
    // 获取要运行的用例名称（用于显示在加载提示中）
    const caseToRun = tableData.value?.find(item => item.id === id);
    const caseName = caseToRun?.name || '当前用例';
    
    // 设置页面为加载中状态，禁用所有交互，并显示正在执行的用例名称
    loadingText.value = `正在执行用例: ${caseName}，请稍候...`;
    isRunning.value = true;
    
    // 启动进度模拟
    startProgressSimulation();
    
    // 默认使用并行模式，parallel=0
    const response = await runCaseGroup([id], 0);

    if (response.code === 200) {
      // 停止进度模拟
      stopProgressSimulation();
      
      // 更新加载提示
      loadingText.value = '用例执行完成，正在生成报告...';
      
      // 延迟一下，让用户看到执行完成的提示
      await new Promise(resolve => setTimeout(resolve, 800));
      
      ElMessage.success('用例执行成功');
      getCaseListData();
      
      // 执行成功后打开报告页面
      openTestReport(id);
    } else {
      ElMessage.error(response.msg || '用例执行失败');
    }
  } catch (error) {
    console.error('执行用例出错:', error);
    ElMessage.error('执行用例时发生错误，请稍后重试');
  } finally {
    // 无论执行成功还是失败，都需要关闭加载状态
    stopProgressSimulation(); // 确保进度模拟被停止
    isRunning.value = false;
    // 重置加载提示文本
    loadingText.value = '用例执行中，请稍候...';
  }
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

/* 全局样式，改变加载动画样式 */
:deep(.el-loading-mask) {
  .el-loading-spinner {
    .el-loading-text {
      color: #409EFF;
      font-size: 18px;
      margin-top: 15px;
      text-shadow: 0 0 10px rgba(0,0,0,0.5);
    }
    
    .loading-icon {
      font-size: 30px;
      animation: spin 1.5s linear infinite;
    }
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 批量运行模式选择对话框样式 */
.run-mode-selector {
  .run-mode-options {
    margin-top: 20px;
    
    .run-mode-option {
      display: block;
      margin-bottom: 15px;
      padding: 15px;
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      transition: all 0.3s ease;
      
      &:hover {
        border-color: #409eff;
        background-color: #f0f9ff;
      }
      
      .mode-info {
        margin-left: 10px;
        
        .mode-title {
          font-weight: 600;
          font-size: 16px;
          color: #303133;
          margin-bottom: 5px;
        }
        
        .mode-desc {
          font-size: 14px;
          color: #606266;
          line-height: 1.4;
        }
      }
    }
    
    // 选中状态样式
    :deep(.el-radio__input.is-checked + .el-radio__label) .run-mode-option {
      border-color: #409eff;
      background-color: #ecf5ff;
    }
  }
}
</style>
