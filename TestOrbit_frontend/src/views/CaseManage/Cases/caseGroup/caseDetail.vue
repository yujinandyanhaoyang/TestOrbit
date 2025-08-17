
<template>
  <div class="case-detail-container">
    <div class="case-header">
      <h3>用例详情 #{{ caseId }}</h3>
      <el-tag v-if="caseStatus === 'active'" type="success">活跃</el-tag>
      <el-tag v-else-if="caseStatus === 'deprecated'" type="info">已废弃</el-tag>
      <el-tag v-else type="warning">草稿</el-tag>
    </div>

    <el-descriptions :column="2" border>
      <el-descriptions-item label="用例ID">{{ caseId }}</el-descriptions-item>
      <el-descriptions-item label="创建时间">{{ formattedCreatedTime }}</el-descriptions-item>
      <el-descriptions-item label="用例名称">{{ caseName }}</el-descriptions-item>
      <el-descriptions-item label="最后更新">{{ formattedUpdatedTime }}</el-descriptions-item>
      <el-descriptions-item label="所属项目" :span="2">
        <el-tag size="small">{{ projectName }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="测试描述" :span="2">
        {{ description }}
      </el-descriptions-item>
    </el-descriptions>

    <div class="section-title">
      <h4>测试步骤</h4>
    </div>
    <el-steps direction="vertical" :active="steps.length">
      <el-step 
        v-for="(step, index) in steps" 
        :key="index" 
        :title="`步骤 ${index + 1}: ${step.title}`" 
        :description="step.description"
      />
    </el-steps>

    <div class="section-title">
      <h4>预期结果</h4>
    </div>
    <el-card class="expected-result">
      {{ expectedResult }}
    </el-card>

    <div class="section-title">
      <h4>附件</h4>
    </div>
    <div class="attachments-list">
      <el-empty v-if="attachments.length === 0" description="暂无附件" />
      <el-table v-else :data="attachments" style="width: 100%">
        <el-table-column prop="name" label="文件名" />
        <el-table-column prop="size" label="大小" width="120" />
        <el-table-column prop="uploadTime" label="上传时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="scope">
            <el-button type="primary" link size="small">下载</el-button>
            <el-button type="danger" link size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="actions">
      <el-button type="primary">编辑用例</el-button>
      <el-button>执行测试</el-button>
      <el-button type="danger">删除用例</el-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'

// 接收父组件传递的属性
const props = defineProps<{
  caseId: number
}>()

// 模拟从 API 获取数据，实际应用中应该通过 API 调用获取
const caseName = ref(`测试用例 ${props.caseId}`)
const caseStatus = ref('active') // 可选值：active, deprecated, draft
const projectName = ref('TestOrbit项目')
const description = ref('这是一个测试用例的详细描述，包含了用例的背景、目的和测试范围。')
const createdTime = ref(new Date(2025, 7, 10)) // 月份从0开始，7表示8月
const updatedTime = ref(new Date())
const expectedResult = ref('测试应当成功通过，所有API返回正确的数据结构和状态码。')

const steps = ref([
  { title: '准备测试环境', description: '确保测试环境已经配置正确，包括必要的依赖和配置。' },
  { title: '初始化测试数据', description: '创建测试所需的样本数据，包括用户账户和测试项目。' },
  { title: '执行API调用', description: '向指定的API端点发送请求并验证响应。' },
  { title: '验证测试结果', description: '检查返回的数据结构和状态码是否符合预期。' },
  { title: '清理测试数据', description: '测试完成后，清理测试过程中创建的数据。' }
])

const attachments = ref([
  { name: '测试用例截图.png', size: '256KB', uploadTime: '2025-08-10 14:30' },
  { name: '测试数据.json', size: '4KB', uploadTime: '2025-08-11 09:15' },
])

// 格式化日期
const formattedCreatedTime = computed(() => {
  return formatDate(createdTime.value)
})

const formattedUpdatedTime = computed(() => {
  return formatDate(updatedTime.value)
})

// 简单的日期格式化函数
function formatDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// 在实际应用中，这里可以添加更多的功能，比如：
// 1. 加载数据的方法
// 2. 保存编辑的方法
// 3. 执行测试的方法
// 4. 处理附件的方法
</script>

<style scoped>
.case-detail-container {
  padding: 20px;
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.case-header h3 {
  margin: 0;
  color: #303133;
}

.section-title {
  margin: 25px 0 15px;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.section-title h4 {
  margin: 0;
  color: #303133;
  font-weight: 500;
}

.expected-result {
  margin-top: 10px;
  background-color: #f8f8f8;
}

.attachments-list {
  margin-top: 10px;
}

.actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>