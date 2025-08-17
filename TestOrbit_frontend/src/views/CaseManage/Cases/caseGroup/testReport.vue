<template>
  <div class="test-report-container">
    <div class="report-header">
      <h3>测试执行报告 #{{ reportId }}</h3>
      <el-tag :type="reportStatus === 'success' ? 'success' : reportStatus === 'fail' ? 'danger' : 'warning'">
        {{ reportStatusText }}
      </el-tag>
    </div>

    <el-descriptions :column="2" border>
      <el-descriptions-item label="报告ID">{{ reportId }}</el-descriptions-item>
      <el-descriptions-item label="执行时间">{{ executionTime }}</el-descriptions-item>
      <el-descriptions-item label="用例名称">{{ caseName }}</el-descriptions-item>
      <el-descriptions-item label="执行人">{{ executor }}</el-descriptions-item>
      <el-descriptions-item label="执行环境" :span="2">{{ environment }}</el-descriptions-item>
      <el-descriptions-item label="执行结果" :span="2">
        <el-progress 
          :percentage="successRate" 
          :status="reportStatus === 'success' ? 'success' : reportStatus === 'fail' ? 'exception' : 'warning'"
        ></el-progress>
        <div class="result-summary">
          <span>通过: {{ passCount }}</span>
          <span>失败: {{ failCount }}</span>
          <span>跳过: {{ skipCount }}</span>
          <span>总计: {{ totalSteps }}</span>
        </div>
      </el-descriptions-item>
    </el-descriptions>

    <div class="section-title">
      <h4>测试步骤执行详情</h4>
    </div>

    <el-table :data="stepResults" style="width: 100%" border>
      <el-table-column type="index" label="序号" width="80" />
      <el-table-column prop="stepName" label="步骤名称" />
      <el-table-column prop="duration" label="执行时长" width="120" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="scope">
          <el-tag
            :type="scope.row.status === 'pass' ? 'success' : scope.row.status === 'fail' ? 'danger' : 'warning'"
          >
            {{ scope.row.status === 'pass' ? '通过' : scope.row.status === 'fail' ? '失败' : '跳过' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="120">
        <template #default="scope">
          <el-button 
            type="primary" 
            link 
            size="small" 
            @click="showStepDetails(scope.row)"
          >
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="section-title">
      <h4>测试日志</h4>
    </div>
    <el-card class="log-container">
      <pre class="log-content">{{ logs }}</pre>
    </el-card>

    <div class="actions">
      <el-button type="primary">导出报告</el-button>
      <el-button>重新执行</el-button>
    </div>

    <!-- 步骤详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="currentStep ? `步骤详情: ${currentStep.stepName}` : '步骤详情'"
      width="50%"
    >
      <div v-if="currentStep">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="步骤名称">{{ currentStep.stepName }}</el-descriptions-item>
          <el-descriptions-item label="执行时长">{{ currentStep.duration }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag
              :type="currentStep.status === 'pass' ? 'success' : currentStep.status === 'fail' ? 'danger' : 'warning'"
            >
              {{ currentStep.status === 'pass' ? '通过' : currentStep.status === 'fail' ? '失败' : '跳过' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="预期结果">{{ currentStep.expectedResult }}</el-descriptions-item>
          <el-descriptions-item label="实际结果">{{ currentStep.actualResult }}</el-descriptions-item>
        </el-descriptions>

        <div v-if="currentStep.status === 'fail'" class="error-details">
          <div class="section-title">
            <h4>错误详情</h4>
          </div>
          <pre class="error-message">{{ currentStep.errorMessage }}</pre>
        </div>

        <div v-if="currentStep.screenshots && currentStep.screenshots.length > 0" class="screenshots">
          <div class="section-title">
            <h4>截图</h4>
          </div>
          <el-carousel height="300px">
            <el-carousel-item v-for="(screenshot, index) in currentStep.screenshots" :key="index">
              <div class="screenshot-container">
                <img :src="screenshot" class="screenshot-image" />
              </div>
            </el-carousel-item>
          </el-carousel>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">关闭</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'

// 接收父组件传递的属性
const props = defineProps<{
  reportId: number
}>()

// 对话框控制
const dialogVisible = ref(false)
const currentStep = ref<any>(null)

// 模拟从API获取的数据
const reportStatus = ref('success') // 可选：success, fail, warning
const caseName = ref(`API测试用例 #${props.reportId}`)
const executionTime = ref('2025-08-15 09:30:45')
const executor = ref('测试工程师')
const environment = ref('测试环境 (Test)')
const passCount = ref(8)
const failCount = ref(1)
const skipCount = ref(1)

// 计算属性
const totalSteps = computed(() => passCount.value + failCount.value + skipCount.value)
const successRate = computed(() => Math.round((passCount.value / totalSteps.value) * 100))
const reportStatusText = computed(() => {
  switch (reportStatus.value) {
    case 'success': return '通过'
    case 'fail': return '失败'
    case 'warning': return '警告'
    default: return reportStatus.value
  }
})

// 测试步骤结果
const stepResults = ref([
  {
    stepName: '初始化测试环境',
    duration: '2.5秒',
    status: 'pass',
    expectedResult: '环境初始化成功',
    actualResult: '环境初始化成功',
    screenshots: []
  },
  {
    stepName: '登录系统',
    duration: '1.8秒',
    status: 'pass',
    expectedResult: '登录成功',
    actualResult: '登录成功',
    screenshots: []
  },
  {
    stepName: '创建测试数据',
    duration: '3.2秒',
    status: 'pass',
    expectedResult: '测试数据创建成功',
    actualResult: '测试数据创建成功',
    screenshots: []
  },
  {
    stepName: '执行API调用',
    duration: '0.9秒',
    status: 'pass',
    expectedResult: 'API返回200状态码',
    actualResult: 'API返回200状态码',
    screenshots: []
  },
  {
    stepName: '验证响应数据',
    duration: '1.5秒',
    status: 'fail',
    expectedResult: '响应包含预期的数据结构',
    actualResult: '响应数据缺少必要字段',
    errorMessage: 'Error: Expected property "userId" to exist in response.\nResponse was: { "status": "success", "data": { "name": "Test User", "role": "admin" } }',
    screenshots: ['/img/screenshot1.png', '/img/screenshot2.png']
  },
  {
    stepName: '清理测试数据',
    duration: '2.0秒',
    status: 'pass',
    expectedResult: '测试数据清理成功',
    actualResult: '测试数据清理成功',
    screenshots: []
  },
  {
    stepName: '检查日志记录',
    duration: '1.1秒',
    status: 'pass',
    expectedResult: '日志记录完整',
    actualResult: '日志记录完整',
    screenshots: []
  },
  {
    stepName: '验证审计跟踪',
    duration: '1.3秒',
    status: 'pass',
    expectedResult: '审计跟踪记录存在',
    actualResult: '审计跟踪记录存在',
    screenshots: []
  },
  {
    stepName: '执行性能测试',
    duration: '0秒',
    status: 'skip',
    expectedResult: '响应时间小于500ms',
    actualResult: '步骤被跳过',
    screenshots: []
  },
  {
    stepName: '生成报告',
    duration: '1.8秒',
    status: 'pass',
    expectedResult: '报告生成成功',
    actualResult: '报告生成成功',
    screenshots: []
  }
])

// 测试日志
const logs = ref(`
[2025-08-15 09:30:45] INFO: 测试执行开始
[2025-08-15 09:30:45] INFO: 初始化测试环境
[2025-08-15 09:30:48] INFO: 环境初始化成功
[2025-08-15 09:30:48] INFO: 执行登录操作
[2025-08-15 09:30:50] INFO: 登录成功
[2025-08-15 09:30:50] INFO: 创建测试数据
[2025-08-15 09:30:53] INFO: 测试数据创建成功
[2025-08-15 09:30:53] INFO: 执行API调用
[2025-08-15 09:30:54] INFO: API返回状态码: 200
[2025-08-15 09:30:54] INFO: 验证响应数据
[2025-08-15 09:30:56] ERROR: 响应数据验证失败: 缺少必要字段 'userId'
[2025-08-15 09:30:56] INFO: 清理测试数据
[2025-08-15 09:30:58] INFO: 测试数据清理成功
[2025-08-15 09:30:58] INFO: 检查日志记录
[2025-08-15 09:30:59] INFO: 日志记录完整
[2025-08-15 09:30:59] INFO: 验证审计跟踪
[2025-08-15 09:31:00] INFO: 审计跟踪记录存在
[2025-08-15 09:31:00] INFO: 跳过性能测试
[2025-08-15 09:31:00] INFO: 生成报告
[2025-08-15 09:31:02] INFO: 报告生成成功
[2025-08-15 09:31:02] INFO: 测试执行结束，总耗时: 17.1秒
`)

// 显示步骤详情
const showStepDetails = (step: any) => {
  currentStep.value = step
  dialogVisible.value = true
}
</script>

<style scoped>
.test-report-container {
  padding: 20px;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.report-header h3 {
  margin: 0;
  color: #303133;
}

.result-summary {
  display: flex;
  justify-content: space-around;
  margin-top: 10px;
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

.log-container {
  margin-top: 10px;
  background-color: #1e1e1e;
  color: #d4d4d4;
}

.log-content {
  font-family: 'Courier New', Courier, monospace;
  white-space: pre-wrap;
  font-size: 12px;
  line-height: 1.4;
  overflow: auto;
  max-height: 300px;
  padding: 10px;
}

.actions {
  margin-top: 30px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.error-details {
  margin-top: 20px;
}

.error-message {
  background-color: #fff2f2;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  padding: 10px;
  font-family: 'Courier New', Courier, monospace;
  white-space: pre-wrap;
  color: #cf1322;
}

.screenshots {
  margin-top: 20px;
}

.screenshot-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.screenshot-image {
  max-width: 100%;
  max-height: 300px;
  object-fit: contain;
}
</style>
