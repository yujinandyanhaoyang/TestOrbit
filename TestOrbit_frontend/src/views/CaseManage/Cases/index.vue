<template>
  <div class="page-header">
    <h2>测试用例管理</h2>
    <div class="action-buttons">
      <el-button 
        type="primary" 
        size="small" 
        @click="addTab('新建用例', '请在此创建新的测试用例')"
      >
        <el-icon class="el-icon--left"><Plus /></el-icon>
        新建用例
      </el-button>
    </div>
  </div>
  <el-tabs
    v-model="editableTabsValue"
    type="card"
    class="demo-tabs"
    @tab-remove="removeTab"
  >
    <!-- 第一个固定标签 - 用例列表 -->
    <el-tab-pane
      label="用例列表"
      name="cases"
      :closable="false"
    >
      <!-- 传递事件处理函数，以便从列表打开用例详情和测试报告 -->
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
      <!-- 使用动态组件根据标签类型显示不同的组件 -->
      <component 
        v-if="item.componentName" 
        :is="resolveComponent(item.componentName)"
        v-bind="item.props"
      />
      <!-- 使用caseDetail组件显示用例详情 -->
      <CaseDetail 
        v-else-if="item.caseId" 
        :caseId="item.caseId" 
      />
      <!-- 默认情况下显示内容文本 -->
      <div v-else class="tab-content">
        <h3>{{ item.title }}</h3>
        <div>{{ item.content }}</div>
      </div>
    </el-tab-pane>
  </el-tabs>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
// 使用新的自定义组件
import CasesList from './caseGroupList.vue'
import TestReport from './caseGroup/testReport.vue'
import CaseGroupDetail from './caseGroup/index.vue'
import { Plus } from '@element-plus/icons-vue'
import type { TabPaneName } from 'element-plus'

// 定义标签页项目的类型
interface TabItem {
  title: string;       // 标签标题
  name: string;        // 标签唯一标识符
  content: string;     // 标签内容
  caseId?: number;     // 可选的用例ID，用于标识与特定用例相关的标签
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
 */
const addTab = (
  title: string = '用例详情', 
  content: string = '用例详情内容', 
  caseId?: number,
  componentName?: string,
  props?: Record<string, any>
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
      props: props || { caseId }
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
      props: props
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
 * 处理从用例列表中打开用例详情的事件
 * @param caseId 要打开的用例ID
 */
const handleOpenCaseDetail = (caseId: number) => {
  // 调用openCaseGroup方法，传入用例ID
  // console.log('打开用例详情(Cases/index):', caseId);
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
 * @param groupId 用例组ID
 */
const openCaseGroup = (groupId: number) => {
  // 使用通用的addTab方法打开用例组
  addTab('用例组', '', groupId, 'CaseGroupDetail', { groupId })
}
</script>



<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  color: #303133;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.demo-tabs {
  border-radius: 4px;
  background-color: #fff;
}

.demo-tabs > .el-tabs__content {
  padding: 20px;
  color: #303133;
  font-size: 14px;
}

.tab-content {
  padding: 15px;
}

.tab-content h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #409EFF;
  font-weight: 500;
  border-bottom: 1px solid #EBEEF5;
  padding-bottom: 10px;
}

.case-info {
  background-color: #F5F7FA;
  padding: 15px;
  border-radius: 4px;
  margin-top: 10px;
}

.case-id {
  font-weight: bold;
  margin-bottom: 10px;
}

.case-description {
  color: #606266;
  line-height: 1.6;
}
</style>
