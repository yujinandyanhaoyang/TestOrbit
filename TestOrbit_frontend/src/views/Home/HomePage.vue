
<template>
  <div class="homepage">
    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <h1 class="welcome-title">欢迎使用 TestOrbit</h1>
        <p class="welcome-subtitle">专业的 API 测试平台，让测试变得更简单高效</p>
        <div class="welcome-actions">
          <el-button 
            type="primary" 
            size="large" 
            @click="quickStart('/Case')"
            class="action-btn"
          >
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            开始测试
          </el-button>
          <el-button 
            size="large" 
            @click="quickStart('/ProjectManage')"
            class="action-btn secondary"
          >
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            管理项目
          </el-button>
        </div>
      </div>
      <div class="welcome-illustration">
        <svg viewBox="0 0 400 300" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="50" y="50" width="300" height="200" rx="20" fill="url(#gradient1)" opacity="0.8"/>
          <rect x="80" y="80" width="240" height="20" rx="10" fill="white" opacity="0.9"/>
          <rect x="80" y="110" width="180" height="15" rx="7" fill="white" opacity="0.7"/>
          <rect x="80" y="135" width="200" height="15" rx="7" fill="white" opacity="0.5"/>
          <circle cx="300" cy="120" r="30" fill="url(#gradient2)"/>
          <defs>
            <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#667eea"/>
              <stop offset="100%" stop-color="#764ba2"/>
            </linearGradient>
            <linearGradient id="gradient2" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#f093fb"/>
              <stop offset="100%" stop-color="#f5576c"/>
            </linearGradient>
          </defs>
        </svg>
      </div>
    </div>

    <!-- 功能卡片区域 -->
    <div class="features-section">
      <h2 class="section-title">核心功能</h2>
      <div class="features-grid">
        <div class="feature-card" @click="quickStart('/Case')">
          <div class="card-icon case">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>场景用例管理</h3>
          <p>创建、管理和执行API测试用例，支持复杂的测试场景编排</p>
          <div class="card-arrow">→</div>
        </div>

        <div class="feature-card" @click="quickStart('/ProjectManage')">
          <div class="card-icon project">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>项目组管理</h3>
          <p>组织和管理测试项目，团队协作，权限控制</p>
          <div class="card-arrow">→</div>
        </div>

        <div class="feature-card" @click="quickStart('/PressureTest')">
          <div class="card-icon pressure">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>压力测试</h3>
          <p>性能测试和负载测试，评估API在高并发下的表现</p>
          <div class="card-arrow">→</div>
        </div>

        <div class="feature-card" @click="quickStart('/UserManage')">
          <div class="card-icon user">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <h3>用户管理</h3>
          <p>用户权限管理，角色分配，系统安全配置</p>
          <div class="card-arrow">→</div>
        </div>
      </div>
    </div>

    <!-- 统计信息区域 -->
    <div class="stats-section">
      <h2 class="section-title">使用统计</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ stats.totalCases }}</div>
          <div class="stat-label">总测试用例</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.totalProjects }}</div>
          <div class="stat-label">活跃项目</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.totalRuns }}</div>
          <div class="stat-label">执行次数</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ stats.successRate }}%</div>
          <div class="stat-label">成功率</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 模拟统计数据
const stats = ref({
  totalCases: 156,
  totalProjects: 12,
  totalRuns: 2847,
  successRate: 94.2
})

// 快速开始功能
const quickStart = (path: string) => {
  router.push({ path })
}

// 组件挂载时可以加载真实的统计数据
onMounted(() => {
  // 这里可以调用API获取真实的统计信息
  // loadStats()
})
</script>

<style scoped lang="scss">
.homepage {
  padding: 0; // 移除padding，因为App.vue已经有了
  max-width: 100%;
  width: 100%;
  min-height: 100%;
  
  .welcome-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 32px;
    padding: 32px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      right: 0;
      width: 200px;
      height: 200px;
      background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.1));
      border-radius: 50%;
      transform: translate(50%, -50%);
    }

    .welcome-content {
      flex: 1;
      z-index: 2;
      position: relative;

      .welcome-title {
        font-size: 32px;
        font-weight: 700;
        color: #2c3e50;
        margin: 0 0 12px 0;
        line-height: 1.2;
      }

      .welcome-subtitle {
        font-size: 16px;
        color: #666;
        margin: 0 0 24px 0;
        line-height: 1.6;
      }

      .welcome-actions {
        display: flex;
        gap: 16px;

        .action-btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 24px;
          border-radius: 12px;
          font-weight: 600;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

          .btn-icon {
            width: 20px;
            height: 20px;
          }

          &:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
          }

          &.secondary {
            background: white;
            border: 2px solid #667eea;
            color: #667eea;

            &:hover {
              background: #667eea;
              color: white;
            }
          }
        }
      }
    }

    .welcome-illustration {
      flex-shrink: 0;
      width: 400px;
      height: 300px;

      svg {
        width: 100%;
        height: 100%;
      }
    }
  }

  .section-title {
    font-size: 24px;
    font-weight: 700;
    color: #2c3e50;
    margin: 0 0 20px 0;
    text-align: center;
  }

  .features-section {
    margin-bottom: 32px;

    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 20px;

      .feature-card {
        background: white;
        padding: 24px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;

        &:hover {
          transform: translateY(-3px);
          box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);

          .card-arrow {
            transform: translateX(6px);
          }
        }

        .card-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          margin-bottom: 20px;

          svg {
            width: 28px;
            height: 28px;
            color: white;
          }

          &.case {
            background: linear-gradient(135deg, #667eea, #764ba2);
          }

          &.project {
            background: linear-gradient(135deg, #f093fb, #f5576c);
          }

          &.pressure {
            background: linear-gradient(135deg, #4facfe, #00f2fe);
          }

          &.user {
            background: linear-gradient(135deg, #43e97b, #38f9d7);
          }
        }

        h3 {
          font-size: 20px;
          font-weight: 600;
          color: #2c3e50;
          margin: 0 0 12px 0;
        }

        p {
          font-size: 14px;
          color: #666;
          line-height: 1.6;
          margin: 0 0 16px 0;
        }

        .card-arrow {
          position: absolute;
          bottom: 24px;
          right: 24px;
          font-size: 20px;
          color: #667eea;
          transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
      }
    }
  }

  .stats-section {
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 24px;

      .stat-card {
        background: white;
        padding: 32px 24px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        text-align: center;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);

        &:hover {
          transform: translateY(-3px);
        }

        .stat-number {
          font-size: 32px;
          font-weight: 700;
          color: #667eea;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          color: #666;
          text-transform: uppercase;
          letter-spacing: 1px;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .homepage {
    padding: 16px;

    .welcome-section {
      flex-direction: column;
      text-align: center;
      padding: 24px;

      .welcome-illustration {
        width: 300px;
        height: 200px;
        margin-top: 24px;
      }
    }

    .features-grid {
      grid-template-columns: 1fr;
    }

    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}
</style>