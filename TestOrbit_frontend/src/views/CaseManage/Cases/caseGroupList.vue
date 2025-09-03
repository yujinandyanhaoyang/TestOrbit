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
      @batch-run="handleBatchRun"
      :has-selection="multipleSelection.length > 0"
      :selected-count="multipleSelection.length"
    />
    <!-- 场景用例表格 -->
    <el-table
      v-if="tableData !== undefined"
      ref="multipleTableRef"
      :data="tableData"
      row-key="id"
      style="width: 100%;"
      table-layout="fixed"
      @selection-change="handleSelectionChange"
      border="false"
      highlight-current-row
      :header-row-style="{height: '48px'}"
      :row-style="{height: '48px'}"
    >
      <el-table-column type="selection" :selectable="selectable" width="36" />
      <el-table-column type="index" label="序号" width="50" align="center" />
      <el-table-column property="name" sortable label="用例名称" min-width="120" show-overflow-tooltip>
        <template #default="scope">
          <div class="case-name">
            <span class="case-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
            </span>
            <span>{{ scope.row.name }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column property="status" sortable label="状态" min-width="90">
        <template #default="scope">
          <!-- 根据状态动态显示不同样式 -->
          <span class="status" :class="getStatusClass(scope.row.status)">
            {{ getStatusText(scope.row.status) }}
          </span>
        </template>
      </el-table-column>
      
      <el-table-column property="creater_name" sortable label="创建人" width="100">
        <template #default="scope">
          <div class="user-info">
            <span class="user-avatar" :title="scope.row.creater_name">{{ getInitials(scope.row.creater_name) }}</span>
            <span class="user-name">{{ scope.row.creater_name }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column property="updater_name" sortable label="修改人" width="100">
        <template #default="scope">
          <div class="user-info">
            <span class="user-avatar" :title="scope.row.updater_name">{{ getInitials(scope.row.updater_name) }}</span>
            <span class="user-name">{{ scope.row.updater_name }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column property="latest_run_time" sortable label="执行时间" width="125">
        <template #default="scope">
          <div class="time-info" :title="scope.row.latest_run_time">
            <span class="time-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </span>
            <span>{{ formatTime(scope.row.latest_run_time) }}</span>
          </div>
        </template>
      </el-table-column>
      
      <el-table-column property="created" sortable label="创建时间" width="125">
        <template #default="scope">
          <span :title="scope.row.created">{{ formatDate(scope.row.created) }}</span>
        </template>
      </el-table-column>
      
      <el-table-column property="updated" sortable label="修改时间" width="125">
        <template #default="scope">
          <span :title="scope.row.updated">{{ formatDate(scope.row.updated) }}</span>
        </template>
      </el-table-column>
      
      <el-table-column fixed="right" label="操作" min-width="180">
        <template #default="scope">
          <div class="action-buttons">
            <el-tooltip content="执行" placement="top" :show-after="300">
              <el-button circle type="primary" size="small" @click="handleRun(scope.row.id)">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="5 3 19 12 5 21 5 3"></polygon>
                </svg>
              </el-button>
            </el-tooltip>
            
            <el-tooltip content="编辑" placement="top" :show-after="300">
              <el-button circle type="info" size="small" @click="openCaseDetail(scope.row.id)">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
              </el-button>
            </el-tooltip>
            
            <el-tooltip content="复制" placement="top" :show-after="300">
              <el-button circle size="small" @click="handleCopy(scope.row.id)">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                </svg>
              </el-button>
            </el-tooltip>
            
            <el-tooltip content="报告" placement="top" :show-after="300">
              <el-button circle type="success" size="small" @click="openTestReport(scope.row.id)">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                  <polyline points="14 2 14 8 20 8"></polyline>
                  <line x1="16" y1="13" x2="8" y2="13"></line>
                  <line x1="16" y1="17" x2="8" y2="17"></line>
                </svg>
              </el-button>
            </el-tooltip>
            
            <el-tooltip content="删除" placement="top" :show-after="300">
              <el-button circle type="danger" size="small" @click="handleDelete(scope.row.id)">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  <line x1="10" y1="11" x2="10" y2="17"></line>
                  <line x1="14" y1="11" x2="14" y2="17"></line>
                </svg>
              </el-button>
            </el-tooltip>
          </div>
        </template>
      </el-table-column>
    </el-table>
    
    <!--底部分页-->
    <el-pagination
      style="display: flex; justify-content: center; margin: 20px 0;"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-sizes="[10, 20, 30, 50]"
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

// 获取状态对应的样式类
const getStatusClass = (status: any): string => {
  if (status === null || status === undefined) return 'pending';
  
  const statusNum = Number(status);
  if (isNaN(statusNum)) return 'pending';
  
  switch (statusNum) {
    case 0: return 'pending';     // WAITING - 等待执行
    case 1: return 'failed';      // FAILED - 执行失败
    case 2: return 'running';     // RUNNING - 正在执行
    case 3: return 'passed';      // FINISH - 执行完成
    case 4: return 'passed';      // SUCCESS - 执行成功
    case 5: return 'skipped';     // SKIP - 跳过执行
    case 6: return 'interrupted'; // INTERRUPT - 手动中断
    case 7: return 'disabled';    // DISABLED - 已禁用
    case 8: return 'failed';      // FAILED_STOP - 失败并停止
    default: return 'pending';
  }
}

// 获取状态文本
const getStatusText = (status: any): string => {
  if (status === null || status === undefined) return '等待执行';
  
  const statusNum = Number(status);
  if (isNaN(statusNum)) return '未知状态';
  
  switch (statusNum) {
    case 0: return '等待执行';   // WAITING
    case 1: return '执行失败';   // FAILED
    case 2: return '执行中';     // RUNNING
    case 3: return '执行完成';   // FINISH
    case 4: return '执行成功';   // SUCCESS
    case 5: return '跳过执行';   // SKIP
    case 6: return '手动中断';   // INTERRUPT
    case 7: return '已禁用';     // DISABLED
    case 8: return '失败停止';   // FAILED_STOP
    default: return '未知状态';
  }
}

// 获取用户名首字母
const getInitials = (name: any): string => {
  if (!name) return '?';
  // 确保 name 是字符串类型
  const nameStr = String(name);
  return nameStr.charAt(0).toUpperCase();
}

// 格式化执行时间 - 更紧凑显示
const formatTime = (time: any): string => {
  if (!time) return '未执行';
  // 确保 time 是字符串类型
  const timeStr = String(time);
  // 显示年-月-日 时:分
  try {
    const date = new Date(timeStr);
    if (isNaN(date.getTime())) return timeStr.substring(0, 10);
    
    // 格式化为 年-月-日 时:分
    return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')} ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
  } catch (e) {
    // 如果解析失败，返回原始字符串的前10个字符
    return timeStr.substring(0, 10);
  }
}

// 格式化日期（创建/更新时间）
const formatDate = (date: any): string => {
  if (!date) return '';
  // 确保 date 是字符串类型
  const dateStr = String(date);
  // 显示年-月-日
  try {
    const dateObj = new Date(dateStr);
    if (isNaN(dateObj.getTime())) return dateStr.substring(0, 10);
    
    // 始终显示年-月-日，统一格式并补零
    return `${dateObj.getFullYear()}-${(dateObj.getMonth() + 1).toString().padStart(2, '0')}-${dateObj.getDate().toString().padStart(2, '0')}`;
  } catch (e) {
    // 如果解析失败，返回原始字符串的前10个字符
    return dateStr.substring(0, 10);
  }
}

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
      
      // 确保表格数据始终为数组，并处理可能的 null 值
      if (Array.isArray(response.results?.data)) {
        tableData.value = response.results.data;
      } else {
        tableData.value = [];
      }
      
      // 确保表格数据中的每一项都是有效对象，避免 null 或 undefined 导致的错误
      if (tableData.value && tableData.value.length > 0) {
        tableData.value = tableData.value.map(item => {
          // 如果某一项是 null 或 undefined，返回空对象
          return item || {};
        });
      }
      
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
  padding: 0 0.5rem;
  
  /* 确保表格区域占据剩余空间 - 使用 Google/Apple 风格 */
  .el-table {
    flex: 1;
    overflow: hidden !important; /* 完全隐藏所有滚动条 */
    border-radius: 12px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
    margin-bottom: 1rem;
    min-height: 180px; /* 确保表格至少有一定高度，即使只有一行数据 */
    
    /* 自定义表头样式 */
    :deep(.el-table__header-wrapper) {
      .el-table__header {
        th {
          background-color: rgba(250, 250, 252, 0.8);
          font-weight: 500;
          color: #333;
          font-size: 14px;
          padding: 16px 0;
          border-bottom: 1px solid #f0f0f0;
          letter-spacing: 0.2px;
          
          .cell {
            display: flex;
            align-items: center;
            transition: color 0.2s ease;
          }
          
          &.is-sortable {
            .cell {
              cursor: pointer;
              
              &:hover {
                color: #409EFF;
              }
            }
          }
        }
      }
    }
    
    /* 表格行样式 */
    :deep(.el-table__body-wrapper) {
      /* 确保空表格也显示一定高度 */
      min-height: 100px;
      overflow-y: hidden !important; /* 强制隐藏垂直滚动条 */
      
      .el-table__row {
        transition: all 0.3s ease;
        height: 48px !important; /* 强制设置行高 */
        
        td {
          padding: 14px 0;
          border: none;
          height: 48px !important; /* 强制设置单元格高度 */
          
          .cell {
            font-size: 14px;
            line-height: 1.5;
            color: #262626;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
          }
        }
        
        /* 隔行变色 - 轻微的颜色差异 */
        &:nth-child(even) {
          background-color: rgba(250, 250, 252, 0.5);
        }
        
        /* 悬停效果 */
        &:hover td {
          background-color: rgba(64, 158, 255, 0.05) !important;
        }
      }
    }
    
    /* 状态列样式 */
    :deep(.el-table__row .cell:has(span.status)) {
      .status {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        
        &.passed {
          background-color: rgba(103, 194, 58, 0.1);
          color: #67c23a;
        }
        
        &.failed {
          background-color: rgba(245, 108, 108, 0.1);
          color: #f56c6c;
        }
        
        &.pending {
          background-color: rgba(230, 162, 60, 0.1);
          color: #e6a23c;
        }
        
        &.running {
          background-color: rgba(64, 158, 255, 0.1);
          color: #409EFF;
        }
        
        &.skipped {
          background-color: rgba(144, 147, 153, 0.1);
          color: #909399;
        }
        
        &.interrupted {
          background-color: rgba(255, 140, 0, 0.1);
          color: #ff8c00;
        }
        
        &.disabled {
          background-color: rgba(192, 196, 204, 0.1);
          color: #c0c4cc;
        }
      }
    }
    
    /* 操作列按钮样式 */
    :deep(.el-table__fixed-right) {
      .cell {
        display: flex;
        gap: 8px;
        align-items: center;
        
        .el-button {
          padding: 6px 12px;
          border-radius: 6px;
          transition: all 0.2s ease;
          font-weight: 400;
          
          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 3px 6px rgba(0, 0, 0, 0.1);
          }
        }
      }
    }
  }
  
  /* 分页控件样式 - Apple 风格 */
  .el-pagination {
    margin-top: 20px;
    padding: 5px 0;
    justify-content: center;
    background-color: transparent;
    
    :deep(.el-pagination__total, .el-pagination__jump) {
      color: #606266;
      font-size: 13px;
    }
    
    :deep(.el-pager li) {
      margin: 0 3px;
      min-width: 30px;
      height: 30px;
      border-radius: 6px;
      font-weight: 400;
      transition: all 0.2s;
      
      &:hover:not(.is-active) {
        color: #409EFF;
      }
      
      &.is-active {
        background-color: #409EFF;
        color: white;
        font-weight: 500;
        box-shadow: 0 2px 8px rgba(64, 158, 255, 0.35);
      }
    }
    
    :deep(.btn-prev, .btn-next) {
      border-radius: 6px;
      padding: 0 5px;
      height: 30px;
      
      &:hover {
        color: #409EFF;
      }
      
      &:disabled {
        color: #c0c4cc;
      }
    }
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

/* 用例名称样式 */
.case-name {
  display: flex;
  align-items: center;
  gap: 8px;
  
  .case-icon {
    color: #409EFF;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* 用户信息样式 - 更紧凑 */
.user-info {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  
  .user-avatar {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background-color: #f0f7ff;
    color: #409EFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    font-size: 12px;
    cursor: help; /* 显示为提示鼠标，暗示有tooltip */
    transition: transform 0.2s ease;
    flex-shrink: 0;
    
    &:hover {
      transform: scale(1.1);
    }
  }
  
  .user-name {
    font-size: 14px;
    color: #333;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

/* 时间信息样式 - 更紧凑 */
.time-info {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  
  .time-icon {
    color: #909399;
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

/* 状态标签样式 - 更紧凑 */
.status {
  padding: 3px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
  
  &.passed {
    background-color: rgba(103, 194, 58, 0.1);
    color: #67c23a;
    border: 1px solid rgba(103, 194, 58, 0.2);
  }
  
  &.failed {
    background-color: rgba(245, 108, 108, 0.1);
    color: #f56c6c;
    border: 1px solid rgba(245, 108, 108, 0.2);
  }
  
  &.pending {
    background-color: rgba(230, 162, 60, 0.1);
    color: #e6a23c;
    border: 1px solid rgba(230, 162, 60, 0.2);
  }
  
  &.running {
    background-color: rgba(64, 158, 255, 0.1);
    color: #409EFF;
    border: 1px solid rgba(64, 158, 255, 0.2);
  }
  
  &.skipped {
    background-color: rgba(144, 147, 153, 0.1);
    color: #909399;
    border: 1px solid rgba(144, 147, 153, 0.2);
  }
  
  &.interrupted {
    background-color: rgba(255, 140, 0, 0.1);
    color: #ff8c00;
    border: 1px solid rgba(255, 140, 0, 0.2);
  }
  
  &.disabled {
    background-color: rgba(192, 196, 204, 0.1);
    color: #c0c4cc;
    border: 1px solid rgba(192, 196, 204, 0.2);
  }
}

/* 操作按钮样式 - 更好的布局 */
.action-buttons {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  justify-content: flex-start;
  align-items: center;
  
  .el-button {
    padding: 6px;
    height: 30px;
    width: 30px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    
    svg {
      transition: transform 0.15s ease;
    }
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
      
      svg {
        transform: scale(1.2);
      }
    }
    
    &:active {
      transform: translateY(0px);
    }
  }
}

/* 确保固定列（操作列）样式正确 */
:deep(.el-table__fixed-right) {
  .el-table__fixed-header-wrapper th:last-child,
  .el-table__fixed-body-wrapper td:last-child {
    padding-right: 12px !important;
  }
  
  .cell {
    padding: 0 8px;
  }
}

/* 全局样式 - 彻底隐藏 Element Plus 表格的所有垂直滚动条 */
:deep(.el-table) {
  overflow: hidden !important;
}

:deep(.el-table__header-wrapper),
:deep(.el-table__body-wrapper),
:deep(.el-table__fixed-header-wrapper),
:deep(.el-table__fixed-body-wrapper),
:deep(.el-table__fixed-right-patch),
:deep(.el-scrollbar),
:deep(.el-scrollbar__wrap),
:deep(.el-scrollbar__view) {
  overflow-y: hidden !important;
  overflow-x: hidden !important;
}

/* 隐藏滚动条轨道 */
:deep(.el-scrollbar__bar) {
  display: none !important;
}

/* 确保表格内容不会超出容器 */
:deep(.el-table__inner-wrapper) {
  overflow: hidden !important;
}
</style>
