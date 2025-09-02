
<template>
  <div class="pressure-test-container">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <svg class="title-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          压力测试
        </h1>
        <p class="page-description">评估API在高并发场景下的性能表现，发现系统瓶颈</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" size="large" @click="startNewTest">
          <svg class="btn-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="5,3 19,12 5,21" fill="currentColor"/>
          </svg>
          新建测试
        </el-button>
      </div>
    </div>

    <!-- 快速统计卡片 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon running">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.runningTests }}</div>
          <div class="stat-label">运行中测试</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon completed">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polyline points="20,6 9,17 4,12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.completedTests }}</div>
          <div class="stat-label">已完成测试</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon performance">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 3v18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 12l4-4 4 4 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.avgResponseTime }}ms</div>
          <div class="stat-label">平均响应时间</div>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon success-rate">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stats.successRate }}%</div>
          <div class="stat-label">成功率</div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧测试配置 -->
      <div class="test-configuration">
        <div class="config-card">
          <div class="card-header">
            <h3 class="card-title">
              <svg class="card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1" stroke="currentColor" stroke-width="2"/>
              </svg>
              测试配置
            </h3>
            <el-button type="text" @click="editConfiguration">编辑</el-button>
          </div>
          
          <div class="config-content">
            <div class="config-item">
              <label class="config-label">目标URL</label>
              <div class="config-value">{{ config.targetUrl }}</div>
            </div>
            
            <div class="config-item">
              <label class="config-label">并发用户数</label>
              <div class="config-value">{{ config.concurrentUsers }} 用户</div>
            </div>
            
            <div class="config-item">
              <label class="config-label">测试持续时间</label>
              <div class="config-value">{{ config.duration }} 分钟</div>
            </div>
            
            <div class="config-item">
              <label class="config-label">请求间隔</label>
              <div class="config-value">{{ config.interval }} 秒</div>
            </div>
            
            <div class="config-item">
              <label class="config-label">测试场景</label>
              <div class="config-value">{{ config.scenario }}</div>
            </div>
          </div>
        </div>

        <!-- 测试历史 -->
        <div class="history-card">
          <div class="card-header">
            <h3 class="card-title">
              <svg class="card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              测试历史
            </h3>
            <el-button type="text" @click="viewAllHistory">查看全部</el-button>
          </div>
          
          <div class="history-list">
            <div 
              v-for="test in recentTests" 
              :key="test.id" 
              class="history-item"
              @click="viewTestDetails(test)"
            >
              <div class="test-status" :class="test.status">
                <div class="status-indicator"></div>
              </div>
              <div class="test-info">
                <div class="test-name">{{ test.name }}</div>
                <div class="test-time">{{ formatTime(test.createdAt) }}</div>
              </div>
              <div class="test-result">
                <div class="result-value">{{ test.successRate }}%</div>
                <div class="result-label">成功率</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧实时监控 -->
      <div class="real-time-monitoring">
        <!-- 性能图表 -->
        <div class="chart-card">
          <div class="card-header">
            <h3 class="card-title">
              <svg class="card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 3v18h18" stroke="currentColor" stroke-width="2"/>
                <path d="M7 12l4-4 4 4 4-4" stroke="currentColor" stroke-width="2"/>
              </svg>
              实时性能监控
            </h3>
            <div class="chart-controls">
              <el-button-group size="small">
                <el-button :class="{ 'is-active': activeChart === 'response' }" @click="switchChart('response')">
                  响应时间
                </el-button>
                <el-button :class="{ 'is-active': activeChart === 'throughput' }" @click="switchChart('throughput')">
                  吞吐量
                </el-button>
                <el-button :class="{ 'is-active': activeChart === 'errors' }" @click="switchChart('errors')">
                  错误率
                </el-button>
              </el-button-group>
            </div>
          </div>
          
          <div class="chart-container">
            <!-- 这里可以集成 ECharts 或其他图表库 -->
            <div class="chart-placeholder">
              <div class="chart-content">
                <svg class="chart-icon" viewBox="0 0 200 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <defs>
                    <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stop-color="#667eea" stop-opacity="0.8"/>
                      <stop offset="100%" stop-color="#667eea" stop-opacity="0.1"/>
                    </linearGradient>
                  </defs>
                  <path d="M 10,90 Q 50,20 100,45 T 190,30" stroke="#667eea" stroke-width="3" fill="none"/>
                  <path d="M 10,90 Q 50,20 100,45 T 190,30 L 190,100 L 10,100 Z" fill="url(#chartGradient)"/>
                  <circle cx="10" cy="90" r="4" fill="#667eea"/>
                  <circle cx="100" cy="45" r="4" fill="#667eea"/>
                  <circle cx="190" cy="30" r="4" fill="#667eea"/>
                </svg>
                <div class="chart-info">
                  <div class="current-value">
                    <span class="value">{{ getCurrentChartValue() }}</span>
                    <span class="unit">{{ getCurrentChartUnit() }}</span>
                  </div>
                  <div class="chart-description">{{ getChartDescription() }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 系统资源监控 -->
        <div class="resource-card">
          <div class="card-header">
            <h3 class="card-title">
              <svg class="card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="2" y="4" width="20" height="16" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M7 15h.01M11 15h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              </svg>
              系统资源
            </h3>
          </div>
          
          <div class="resource-metrics">
            <div class="metric-item">
              <div class="metric-label">CPU 使用率</div>
              <div class="metric-progress">
                <el-progress 
                  :percentage="systemMetrics.cpu" 
                  :color="getProgressColor(systemMetrics.cpu)"
                  :show-text="false"
                />
                <span class="metric-value">{{ systemMetrics.cpu }}%</span>
              </div>
            </div>
            
            <div class="metric-item">
              <div class="metric-label">内存使用率</div>
              <div class="metric-progress">
                <el-progress 
                  :percentage="systemMetrics.memory" 
                  :color="getProgressColor(systemMetrics.memory)"
                  :show-text="false"
                />
                <span class="metric-value">{{ systemMetrics.memory }}%</span>
              </div>
            </div>
            
            <div class="metric-item">
              <div class="metric-label">网络I/O</div>
              <div class="metric-progress">
                <el-progress 
                  :percentage="systemMetrics.network" 
                  :color="getProgressColor(systemMetrics.network)"
                  :show-text="false"
                />
                <span class="metric-value">{{ systemMetrics.network }}%</span>
              </div>
            </div>
            
            <div class="metric-item">
              <div class="metric-label">磁盘I/O</div>
              <div class="metric-progress">
                <el-progress 
                  :percentage="systemMetrics.disk" 
                  :color="getProgressColor(systemMetrics.disk)"
                  :show-text="false"
                />
                <span class="metric-value">{{ systemMetrics.disk }}%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 详细结果分析 -->
        <div class="results-card">
          <div class="card-header">
            <h3 class="card-title">
              <svg class="card-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M9 11H7a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2zM17 7h-2a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2z" stroke="currentColor" stroke-width="2"/>
              </svg>
              结果分析
            </h3>
          </div>
          
          <div class="results-content">
            <div class="result-summary">
              <div class="summary-item">
                <div class="summary-label">最大并发数</div>
                <div class="summary-value">{{ testResults.maxConcurrency }}</div>
              </div>
              
              <div class="summary-item">
                <div class="summary-label">峰值QPS</div>
                <div class="summary-value">{{ testResults.peakQPS }}</div>
              </div>
              
              <div class="summary-item">
                <div class="summary-label">P95响应时间</div>
                <div class="summary-value">{{ testResults.p95ResponseTime }}ms</div>
              </div>
              
              <div class="summary-item">
                <div class="summary-label">错误总数</div>
                <div class="summary-value error">{{ testResults.totalErrors }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 测试配置对话框 -->
    <el-dialog
      v-model="showConfigDialog"
      title="测试配置"
      width="600px"
      :before-close="handleConfigClose"
    >
      <div class="config-dialog">
        <el-form :model="editConfig" label-width="120px">
          <el-form-item label="目标URL">
            <el-input v-model="editConfig.targetUrl" placeholder="请输入测试目标URL" />
          </el-form-item>
          
          <el-form-item label="并发用户数">
            <el-input-number v-model="editConfig.concurrentUsers" :min="1" :max="10000" />
          </el-form-item>
          
          <el-form-item label="持续时间(分钟)">
            <el-input-number v-model="editConfig.duration" :min="1" :max="180" />
          </el-form-item>
          
          <el-form-item label="请求间隔(秒)">
            <el-input-number v-model="editConfig.interval" :min="0.1" :max="60" :step="0.1" />
          </el-form-item>
          
          <el-form-item label="测试场景">
            <el-select v-model="editConfig.scenario" placeholder="请选择测试场景">
              <el-option label="负载测试" value="load" />
              <el-option label="压力测试" value="stress" />
              <el-option label="峰值测试" value="spike" />
              <el-option label="容量测试" value="volume" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showConfigDialog = false">取消</el-button>
          <el-button type="primary" @click="saveConfiguration">保存配置</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'

// 响应式数据
const stats = reactive({
  runningTests: 2,
  completedTests: 47,
  avgResponseTime: 156,
  successRate: 98.7
})

const config = reactive({
  targetUrl: 'https://api.testorbit.com/v1/users',
  concurrentUsers: 100,
  duration: 5,
  interval: 1.0,
  scenario: '负载测试'
})

const editConfig = reactive({ ...config })

const systemMetrics = reactive({
  cpu: 45,
  memory: 62,
  network: 28,
  disk: 15
})

const testResults = reactive({
  maxConcurrency: 150,
  peakQPS: 1247,
  p95ResponseTime: 234,
  totalErrors: 12
})

const recentTests = ref([
  {
    id: 1,
    name: '用户API负载测试',
    status: 'completed',
    successRate: 99.2,
    createdAt: new Date(Date.now() - 1000 * 60 * 30) // 30分钟前
  },
  {
    id: 2,
    name: '订单API压力测试',
    status: 'running',
    successRate: 97.8,
    createdAt: new Date(Date.now() - 1000 * 60 * 10) // 10分钟前
  },
  {
    id: 3,
    name: '支付API峰值测试',
    status: 'failed',
    successRate: 85.4,
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2小时前
  }
])

// 控制状态
const showConfigDialog = ref(false)
const activeChart = ref('response')

// 定时器
let metricsInterval: number | null = null

// 计算属性和方法
const getCurrentChartValue = () => {
  const values = {
    response: 156,
    throughput: 1247,
    errors: 2.3
  }
  return values[activeChart.value as keyof typeof values]
}

const getCurrentChartUnit = () => {
  const units = {
    response: 'ms',
    throughput: 'req/s',
    errors: '%'
  }
  return units[activeChart.value as keyof typeof units]
}

const getChartDescription = () => {
  const descriptions = {
    response: '平均响应时间趋势',
    throughput: '每秒请求处理量',
    errors: '请求错误率变化'
  }
  return descriptions[activeChart.value as keyof typeof descriptions]
}

const getProgressColor = (percentage: number) => {
  if (percentage < 50) return '#10b981'
  if (percentage < 80) return '#f59e0b'
  return '#ef4444'
}

const formatTime = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / (1000 * 60))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (minutes < 1440) return `${Math.floor(minutes / 60)}小时前`
  return `${Math.floor(minutes / 1440)}天前`
}

// 事件处理函数
const startNewTest = () => {
  console.log('开始新的压力测试')
  // 这里实现开始测试的逻辑
}

const editConfiguration = () => {
  Object.assign(editConfig, config)
  showConfigDialog.value = true
}

const saveConfiguration = () => {
  Object.assign(config, editConfig)
  showConfigDialog.value = false
  console.log('配置已保存:', config)
}

const handleConfigClose = () => {
  showConfigDialog.value = false
}

const switchChart = (chartType: string) => {
  activeChart.value = chartType
}

const viewTestDetails = (test: any) => {
  console.log('查看测试详情:', test)
  // 这里实现查看详情的逻辑
}

const viewAllHistory = () => {
  console.log('查看全部历史')
  // 这里实现查看全部历史的逻辑
}

// 模拟实时数据更新
const updateMetrics = () => {
  // 模拟CPU使用率变化
  systemMetrics.cpu = Math.max(20, Math.min(90, systemMetrics.cpu + (Math.random() - 0.5) * 10))
  systemMetrics.memory = Math.max(30, Math.min(95, systemMetrics.memory + (Math.random() - 0.5) * 8))
  systemMetrics.network = Math.max(10, Math.min(80, systemMetrics.network + (Math.random() - 0.5) * 15))
  systemMetrics.disk = Math.max(5, Math.min(60, systemMetrics.disk + (Math.random() - 0.5) * 12))
  
  // 模拟统计数据变化
  stats.avgResponseTime = Math.max(50, Math.min(500, stats.avgResponseTime + (Math.random() - 0.5) * 20))
}

// 生命周期
onMounted(() => {
  // 启动实时数据更新
  metricsInterval = setInterval(updateMetrics, 2000)
})

onUnmounted(() => {
  // 清理定时器
  if (metricsInterval) {
    clearInterval(metricsInterval)
  }
})
</script>

<style scoped lang="scss">
.pressure-test-container {
  padding: 24px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 32px;
    padding: 32px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);

    .header-content {
      .page-title {
        display: flex;
        align-items: center;
        margin: 0 0 12px 0;
        font-size: 32px;
        font-weight: 700;
        color: #1a1a1a;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;

        .title-icon {
          width: 36px;
          height: 36px;
          margin-right: 12px;
          color: #667eea;
        }
      }

      .page-description {
        margin: 0;
        font-size: 16px;
        color: #64748b;
        line-height: 1.6;
      }
    }

    .header-actions {
      .el-button {
        height: 48px;
        padding: 0 32px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s ease;

        .btn-icon {
          width: 18px;
          height: 18px;
          margin-right: 8px;
        }

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
        }
      }
    }
  }

  .stats-overview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 24px;
    margin-bottom: 32px;

    .stat-card {
      display: flex;
      align-items: center;
      padding: 28px;
      background: white;
      border-radius: 16px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
      transition: all 0.3s ease;

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
      }

      .stat-icon {
        width: 56px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 14px;
        margin-right: 20px;

        svg {
          width: 28px;
          height: 28px;
          color: white;
        }

        &.running {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        &.completed {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        &.performance {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }

        &.success-rate {
          background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        }
      }

      .stat-content {
        .stat-value {
          font-size: 32px;
          font-weight: 700;
          color: #1a1a1a;
          line-height: 1.2;
          margin-bottom: 4px;
        }

        .stat-label {
          font-size: 14px;
          color: #64748b;
          font-weight: 500;
        }
      }
    }
  }

  .main-content {
    display: grid;
    grid-template-columns: 400px 1fr;
    gap: 32px;

    .test-configuration {
      display: flex;
      flex-direction: column;
      gap: 24px;

      .config-card,
      .history-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        overflow: hidden;

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 24px;
          border-bottom: 1px solid #f1f5f9;

          .card-title {
            display: flex;
            align-items: center;
            margin: 0;
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;

            .card-icon {
              width: 20px;
              height: 20px;
              margin-right: 10px;
              color: #667eea;
            }
          }

          .el-button {
            padding: 8px 16px;
            font-size: 14px;
            color: #667eea;

            &:hover {
              background: #f8fafc;
            }
          }
        }

        .config-content {
          padding: 24px;

          .config-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #f8fafc;

            &:last-child {
              border-bottom: none;
            }

            .config-label {
              font-size: 14px;
              color: #64748b;
              font-weight: 500;
            }

            .config-value {
              font-size: 14px;
              color: #1a1a1a;
              font-weight: 600;
            }
          }
        }

        .history-list {
          padding: 16px 24px 24px;

          .history-item {
            display: flex;
            align-items: center;
            padding: 16px;
            margin-bottom: 12px;
            border-radius: 12px;
            background: #f8fafc;
            cursor: pointer;
            transition: all 0.2s ease;

            &:hover {
              background: #e2e8f0;
              transform: translateX(4px);
            }

            &:last-child {
              margin-bottom: 0;
            }

            .test-status {
              margin-right: 16px;

              .status-indicator {
                width: 12px;
                height: 12px;
                border-radius: 50%;
                
                .history-item .test-status.completed & {
                  background: #10b981;
                }
                
                .history-item .test-status.running & {
                  background: #f59e0b;
                  animation: pulse 2s infinite;
                }
                
                .history-item .test-status.failed & {
                  background: #ef4444;
                }
              }
            }

            .test-info {
              flex: 1;

              .test-name {
                font-size: 14px;
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 4px;
              }

              .test-time {
                font-size: 12px;
                color: #64748b;
              }
            }

            .test-result {
              text-align: right;

              .result-value {
                font-size: 16px;
                font-weight: 700;
                color: #10b981;
              }

              .result-label {
                font-size: 11px;
                color: #64748b;
                margin-top: 2px;
              }
            }
          }
        }
      }
    }

    .real-time-monitoring {
      display: flex;
      flex-direction: column;
      gap: 24px;

      .chart-card,
      .resource-card,
      .results-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        overflow: hidden;

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 24px;
          border-bottom: 1px solid #f1f5f9;

          .card-title {
            display: flex;
            align-items: center;
            margin: 0;
            font-size: 18px;
            font-weight: 600;
            color: #1a1a1a;

            .card-icon {
              width: 20px;
              height: 20px;
              margin-right: 10px;
              color: #667eea;
            }
          }

          .chart-controls {
            .el-button-group .el-button {
              padding: 6px 12px;
              font-size: 12px;
              border-color: #e2e8f0;
              color: #64748b;

              &.is-active {
                background: #667eea;
                border-color: #667eea;
                color: white;
              }
            }
          }
        }
      }

      .chart-card {
        .chart-container {
          padding: 24px;
          height: 320px;

          .chart-placeholder {
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;

            .chart-content {
              text-align: center;

              .chart-icon {
                margin-bottom: 16px;
              }

              .chart-info {
                .current-value {
                  font-size: 28px;
                  font-weight: 700;
                  color: #1a1a1a;
                  margin-bottom: 8px;

                  .unit {
                    font-size: 16px;
                    color: #64748b;
                    margin-left: 4px;
                  }
                }

                .chart-description {
                  font-size: 14px;
                  color: #64748b;
                }
              }
            }
          }
        }
      }

      .resource-card {
        .resource-metrics {
          padding: 24px;

          .metric-item {
            margin-bottom: 20px;

            &:last-child {
              margin-bottom: 0;
            }

            .metric-label {
              font-size: 14px;
              color: #64748b;
              margin-bottom: 8px;
              font-weight: 500;
            }

            .metric-progress {
              display: flex;
              align-items: center;

              :deep(.el-progress) {
                flex: 1;
                margin-right: 16px;

                .el-progress-bar__outer {
                  background: #f1f5f9;
                  border-radius: 8px;
                  height: 8px;
                }

                .el-progress-bar__inner {
                  border-radius: 8px;
                }
              }

              .metric-value {
                font-size: 14px;
                font-weight: 600;
                color: #1a1a1a;
                min-width: 40px;
              }
            }
          }
        }
      }

      .results-card {
        .results-content {
          padding: 24px;

          .result-summary {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;

            .summary-item {
              padding: 16px;
              background: #f8fafc;
              border-radius: 12px;
              text-align: center;

              .summary-label {
                font-size: 12px;
                color: #64748b;
                margin-bottom: 8px;
                font-weight: 500;
              }

              .summary-value {
                font-size: 24px;
                font-weight: 700;
                color: #1a1a1a;

                &.error {
                  color: #ef4444;
                }
              }
            }
          }
        }
      }
    }
  }

  // 对话框样式
  :deep(.el-dialog) {
    border-radius: 16px;
    overflow: hidden;

    .el-dialog__header {
      padding: 24px 24px 16px;
      border-bottom: 1px solid #f1f5f9;

      .el-dialog__title {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a1a;
      }
    }

    .el-dialog__body {
      padding: 24px;

      .config-dialog {
        .el-form-item {
          margin-bottom: 24px;

          .el-form-item__label {
            color: #374151;
            font-weight: 500;
          }

          .el-input,
          .el-select {
            .el-input__inner,
            .el-select__input {
              border-radius: 8px;
              border-color: #e2e8f0;

              &:focus {
                border-color: #667eea;
              }
            }
          }
        }
      }
    }

    .el-dialog__footer {
      padding: 16px 24px 24px;
      border-top: 1px solid #f1f5f9;

      .dialog-footer {
        .el-button {
          padding: 10px 24px;
          border-radius: 8px;
          font-weight: 500;

          &.el-button--primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
          }
        }
      }
    }
  }

  // 动画
  @keyframes pulse {
    0%, 100% {
      opacity: 1;
    }
    50% {
      opacity: 0.5;
    }
  }

  // 响应式设计
  @media (max-width: 1200px) {
    .main-content {
      grid-template-columns: 1fr;
      
      .test-configuration {
        order: 2;
      }
      
      .real-time-monitoring {
        order: 1;
      }
    }
  }

  @media (max-width: 768px) {
    padding: 16px;

    .page-header {
      flex-direction: column;
      align-items: stretch;
      gap: 20px;

      .header-actions {
        align-self: flex-start;
      }
    }

    .stats-overview {
      grid-template-columns: 1fr;
    }

    .main-content {
      gap: 20px;
    }
  }
}
</style>
