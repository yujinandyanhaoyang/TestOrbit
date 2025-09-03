<template>
  <div class="cases-index-container">
    <div class="page-header">
      <h2 class="header-title">测试用例管理</h2>
    </div>
    <el-tabs
      v-model="editableTabsValue"
      type="card"
      class="custom-tabs"
      @tab-remove="removeTab"
      @tab-click="handleTabClick"
    >
      <!-- 第一个固定标签 - 用例列表 -->
      <el-tab-pane
        label="用例列表"
        name="cases"
        :closable="false"
      >
        <CasesList 
          @openCaseDetail="handleOpenCaseDetail"
          @openTestReport="openTestReport" 
        />
      </el-tab-pane>
      
      <!-- 其他可关闭的动态标签 -->
      <el-tab-pane
        v-for="item in editableTabs"
        :key="item.name"
        :label="item.title"
        :name="item.name"
        closable
      >
        <component 
          v-if="item.componentName" 
          :is="resolveComponent(item.componentName)"
          v-bind="item.props"
          class="tab-component"
        />
        <CaseGroupDetail 
          v-else-if="item.caseId || item.isNew" 
          :caseId="item.caseId" 
          :is-new="item.isNew"
          @case-saved="handleCaseSaved"
          class="case-group-detail"
        />
        <div v-else class="tab-content">
          <h3>{{ item.title }}</h3>
          <div>{{ item.content }}</div>
        </div>
      </el-tab-pane>
      
      <!-- 添加用例标签 - 始终位于最右端 -->
      <el-tab-pane
        name="add-case"
        :closable="false"
      >
        <template #label>
          <div class="add-tab-label">
            <el-icon><Plus /></el-icon>
            <span>添加用例</span>
          </div>
        </template>
        <!-- 这个标签页不会显示内容，因为点击时会直接创建新标签 -->
        <div></div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
// 使用新的自定义组件
import CasesList from './caseGroupList.vue'
import TestReport from './caseGroup/testReport.vue'
import CaseGroupDetail from './caseGroup/index.vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { TabPaneName } from 'element-plus'

// 定义标签页项目的类型
interface TabItem {
  title: string;       // 标签标题
  name: string;        // 标签唯一标识符
  content: string;     // 标签内容
  caseId?: number;     // 可选的用例ID，用于标识与特定用例相关的标签
  isNew?: boolean;     // 可选的新建标志，用于新建用例模式
  componentName?: string; // 可选的组件名称，用于动态渲染不同组件
  props?: Record<string, any>; // 可选的组件属性
}

// 设置初始标签索引为0（第一个用例列表标签后面的标签从1开始）
let tabIndex = 0
// 默认选中固定的用例列表标签
const editableTabsValue = ref('cases')
// 可编辑的动态标签列表（不包括第一个固定标签）
const editableTabs = ref<TabItem[]>([

])

/**
 * 添加新标签页
 * @param title 标签页标题
 * @param content 标签页内容
 * @param caseId 可选的用例ID，用于标识具体打开的用例
 * @param componentName 可选的组件名称，用于动态渲染
 * @param props 可选的传递给组件的属性
 * @param isNew 可选的新建标志，用于新建用例模式
 */
const addTab = (
  title: string = '用例详情', 
  content: string = '用例详情内容', 
  caseId?: number,
  componentName?: string,
  props?: Record<string, any>,
  isNew?: boolean
) => {
  // 如果提供了caseId，检查是否已经打开了该用例的标签
  if (caseId !== undefined) {
    // 查找是否已经有相同caseId的标签
    const existingTab = editableTabs.value.find(tab => tab.name === `case-${caseId}`)
    if (existingTab) {
      // 如果已经存在，直接切换到该标签
      editableTabsValue.value = existingTab.name
      return
    }
    
    // 使用caseId作为标签名的一部分，便于后续查找
    const newTabName = `case-${caseId}`
    
    // 添加新标签到列表
    editableTabs.value.push({
      title: `${title} #${caseId}`,
      name: newTabName,
      content: `这里是用例 #${caseId} 的详细信息`, // 实际应用中可能需要从API获取用例详情
      caseId: caseId,
      componentName: componentName,
      props: props || { caseId },
      isNew: isNew || false
    })
    
    // 自动切换到新标签
    editableTabsValue.value = newTabName
  } else {
    // 没有提供caseId，创建普通标签
    const newTabName = `tab-${++tabIndex}`
    
    // 添加新标签到列表
    editableTabs.value.push({
      title: title,
      name: newTabName,
      content: content,
      componentName: componentName,
      props: props || {},
      isNew: isNew || false
    })
    
    // 自动切换到新标签
    editableTabsValue.value = newTabName
  }
}

/**
 * 移除标签页
 * @param targetName 要移除的标签名称
 */
const removeTab = (targetName: TabPaneName) => {
  // 如果固定标签不能被删除
  if (targetName === 'cases') return
  
  const tabs = editableTabs.value
  let activeName = editableTabsValue.value
  
  // 如果关闭的是当前活动的标签页，则需要切换到其他标签
  if (activeName === targetName) {
    // 查找被关闭标签的索引
    const targetIndex = tabs.findIndex(tab => tab.name === targetName)
    
    if (targetIndex !== -1) {
      // 优先选择右侧标签，如果没有则选择左侧标签
      const nextTab = tabs[targetIndex + 1] || tabs[targetIndex - 1]
      
      // 如果有其他标签存在，则切换到该标签
      if (nextTab) {
        activeName = nextTab.name
      } else {
        // 如果没有其他动态标签，则切换回固定的用例列表标签
        activeName = 'cases'
      }
    }
  }

  // 更新活动标签和标签列表
  editableTabsValue.value = activeName
  editableTabs.value = tabs.filter(tab => tab.name !== targetName)
}

/**
 * 根据组件名称解析对应的组件
 * @param componentName 组件名称
 * @returns 对应的组件
 */
const resolveComponent = (componentName: string) => {
  // 使用一个映射表来管理所有可能用到的组件
  const componentMap: Record<string, any> = {
    'CaseGroupDetail': CaseGroupDetail,  // 用例组详情组件
    'TestReport': TestReport,            // 测试报告组件
    // 可以添加更多组件...
  }

  return componentMap[componentName] || null
}

/**
 * 处理标签点击事件
 * @param tab 被点击的标签
 */
const handleTabClick = (tab: any) => {
  // 如果点击的是"添加用例"标签
  if (tab.props.name === 'add-case') {
    // 创建新用例组
    createNewCaseGroup()
    
    // 阻止切换到"添加用例"标签页，保持在之前的活动标签
    // 使用 nextTick 确保在下一个事件循环中恢复正确的标签
    setTimeout(() => {
      // 如果有动态标签存在，切换到最后一个动态标签（刚创建的）
      if (editableTabs.value.length > 0) {
        const lastTab = editableTabs.value[editableTabs.value.length - 1]
        editableTabsValue.value = lastTab.name
      } else {
        // 如果没有动态标签，切换回用例列表
        editableTabsValue.value = 'cases'
      }
    }, 0)
  }
}

/**
 * 处理从用例列表中打开用例详情的事件
 * @param caseId 要打开的用例ID
 */
const handleOpenCaseDetail = (caseId: number) => {
  // 调用openCaseGroup方法，传入用例ID
  openCaseGroup(caseId)
}

/**
 * 打开测试报告
 * @param reportId 测试报告ID
 */
const openTestReport = (reportId: number) => {
  // 使用通用的addTab方法打开测试报告
  addTab('测试报告', '', reportId, 'TestReport', { reportId })
}

/**
 * 打开用例组
 * @param caseId 用例组ID
 */
const openCaseGroup = (caseId: number) => {
  // 使用通用的addTab方法打开用例组
  addTab('用例组', '', caseId, 'CaseGroupDetail', { caseId })
}

/**
 * 创建新的用例组
 */
const createNewCaseGroup = () => {
  // 使用通用的addTab方法打开新建用例组界面
  addTab('新建用例组', '创建一个新的用例组', undefined, 'CaseGroupDetail', { isNew: true }, true)
}

/**
 * 处理用例组保存事件，从新建模式切换到编辑模式
 * @param caseId 新创建的用例ID
 */
const handleCaseSaved = (caseId: number) => {
  // 查找当前打开的新建标签
  const currentTabIndex = editableTabs.value.findIndex(tab => tab.name === editableTabsValue.value)
  
  if (currentTabIndex !== -1) {
    // 获取当前标签
    const currentTab = editableTabs.value[currentTabIndex]
    
    // 如果当前是新建模式，切换到编辑模式
    if (currentTab.isNew) {
      // 修改标签标题和属性，转为编辑模式
      currentTab.title = `用例组 #${caseId}`
      currentTab.isNew = false
      currentTab.caseId = caseId
      currentTab.props = { caseId, isNew: false }
      
      // 更新标签页列表
      editableTabs.value[currentTabIndex] = currentTab
      
      ElMessage.success(`用例组 #${caseId} 创建成功，已切换至编辑模式`)
    }
  }
}
</script>



<style scoped lang="scss">
.cases-index-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #f7f9fc;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  max-width: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

.page-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding: 0 10px;

  .header-title {
    margin: 0;
    color: #2c3e50;
    font-size: 22px;
    font-weight: 600;
  }
}

.custom-tabs {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  max-width: 100%;
  overflow: hidden;

  :deep(.el-tabs__header) {
    margin: 0 0 15px;
    border-bottom: 1px solid #e4e7ed;
    position: relative;

    .el-tabs__nav-wrap {
      position: relative;
      overflow: hidden; /* 防止标签溢出 */
    }

    .el-tabs__nav {
      border: none;
      flex-wrap: nowrap; /* 确保标签不换行 */
      
      .el-tabs__item {
        border: none;
        border-bottom: 2px solid transparent;
        color: #606266;
        font-weight: 500;
        transition: all 0.3s ease;
        padding: 0 20px;
        height: 48px;
        line-height: 48px;
        white-space: nowrap; /* 防止标签文字换行 */
        overflow: hidden;
        text-overflow: ellipsis;

        &:hover {
          color: var(--el-color-primary);
        }

        &.is-active {
          color: var(--el-color-primary);
          border-bottom-color: var(--el-color-primary);
          background-color: transparent;
        }

        // 为"添加用例"标签添加特殊样式
        &[aria-controls="pane-add-case"] {
          margin-left: 10px; // 与其他标签保持一定距离
          border: 1px dashed #d9d9d9;
          border-radius: 6px;
          background-color: #fafafa;
          
          &:hover {
            border-color: var(--el-color-primary);
            background-color: rgba(var(--el-color-primary-rgb), 0.05);
            border-style: solid;
          }

          &.is-active {
            // 添加用例标签不应该有激活状态，因为它只是一个操作按钮
            color: #606266;
            border-bottom: 2px solid transparent;
            background-color: #fafafa;
          }
        }
      }
    }
  }

  .add-tab-label {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #909399;
    transition: all 0.3s ease;

    .el-icon {
      font-size: 16px;
    }

    &:hover {
      color: var(--el-color-primary);
    }
  }

  :deep(.el-tabs__content) {
    flex: 1;
    padding: 0;
    overflow-y: auto;
    
    // 为标签页内容设置容器约束
    .el-tab-pane {
      width: 100%;
      max-width: 100%;
      overflow: hidden;
    }
  }
}

.tab-content {
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 控制子组件的宽度和布局 */
.case-group-detail, .tab-component {
  width: 100%;
  max-width: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

/* 确保CaseGroupDetail组件内的表格等元素不会超出容器 */
.case-group-detail {
  :deep(.el-table) {
    max-width: 100%;
    overflow-x: auto;
  }
  
  :deep(.el-form) {
    max-width: 100%;
    overflow: hidden;
  }
  
  /* 控制内部容器的最大宽度 */
  :deep(.case-detail-container) {
    max-width: 100%;
    overflow-x: auto;
  }
}

/* 响应式设计 - 处理小屏幕设备 */
@media (max-width: 768px) {
  .cases-index-container {
    padding: 10px;
  }
  
  .page-header {
    .header-title {
      font-size: 18px;
    }
  }
  
  .custom-tabs {
    :deep(.el-tabs__header) {
      .el-tabs__item {
        padding: 0 12px;
        font-size: 14px;
      }
    }
  }
  
  .case-group-detail {
    :deep(.el-table) {
      font-size: 12px;
    }
  }
}

/* 处理超宽屏幕 */
@media (min-width: 1920px) {
  .case-group-detail {
    :deep(.case-detail-container) {
      max-width: 1800px;
      margin: 0 auto;
    }
  }
}
</style>
