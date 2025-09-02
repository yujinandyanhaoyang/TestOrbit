<template>
  <!-- 顶级卡片头设计 - 用户管理版本 -->
  <div class="premium-card-header">
    <!-- 背景装饰层 -->
    <div class="bg-decoration">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="header-main">
      <!-- 左侧品牌区域 -->
      <div class="brand-section">
        <div class="brand-logo">
          <div class="logo-container">
            <svg class="logo-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2"/>
            </svg>
            <div class="logo-pulse"></div>
          </div>
        </div>
        
        <div class="brand-info">
          <h1 class="brand-title">用户管理</h1>
          <p class="brand-subtitle">智能权限 · 安全管控 · 高效协作</p>
        </div>
      </div>
      
      <!-- 中间状态指示器 -->
      <div class="status-indicators">
        <div class="indicator-item">
          <div class="indicator-dot active"></div>
          <span class="indicator-label">在线用户 {{ onlineUsers }}</span>
        </div>
        <div class="indicator-separator"></div>
        <div class="indicator-item">
          <div class="indicator-dot syncing"></div>
          <span class="indicator-label">实时监控</span>
        </div>
      </div>
      
      <!-- 右侧操作区域 -->
      <div class="action-zone">
        <!-- 搜索框 -->
        <div class="search-container">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
            <path d="m21 21-4.35-4.35" stroke="currentColor" stroke-width="2"/>
          </svg>
          <input 
            :value="searchQuery"
            @input="handleSearch"
            type="text" 
            placeholder="搜索用户..." 
            class="search-input"
          />
        </div>
        
        <div class="quick-actions">
          <!-- 筛选按钮 -->
          <button class="quick-btn filter-btn" @click="$emit('filter')">
            <svg class="btn-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46" stroke="currentColor" stroke-width="2"/>
            </svg>
            <div class="btn-ripple"></div>
          </button>
        </div>
        
        <!-- 主要行动按钮 -->
        <button class="premium-cta" @click="$emit('add-user')">
          <div class="cta-bg"></div>
          <svg class="cta-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <line x1="12" y1="5" x2="12" y2="19" stroke="currentColor" stroke-width="2.5"/>
            <line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2.5"/>
          </svg>
          <span class="cta-text">添加用户</span>
          <div class="cta-shine"></div>
        </button>
      </div>
    </div>
    
    <!-- 底部装饰线 -->
    <div class="decorative-line">
      <div class="line-segment active"></div>
      <div class="line-segment"></div>
      <div class="line-segment"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  onlineUsers: number
  searchQuery?: string
}

withDefaults(defineProps<Props>(), {
  onlineUsers: 0,
  searchQuery: ''
})

const emit = defineEmits<{
  search: [query: string]
  filter: []
  'add-user': []
}>()

const handleSearch = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('search', target.value)
}
</script>

<style scoped lang="scss">
// 顶级设计系统 - 用户管理版本
:root {
  // 主品牌色彩系统
  --brand-primary: #007AFF;
  --brand-secondary: #5856D6;
  --brand-accent: #FF2D92;
  
  // 高端渐变系统
  --premium-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --glass-gradient: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
  --aurora-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  
  // 现代表面系统
  --surface-glass: rgba(255, 255, 255, 0.8);
  --surface-blur: rgba(255, 255, 255, 0.95);
  --surface-card: #ffffff;
  --surface-elevated: #fafafa;
  
  // 精确文字层次
  --text-hero: #1d1d1f;
  --text-primary: #1d1d1f;
  --text-secondary: #86868b;
  --text-tertiary: #a1a1a6;
  
  // 现代阴影系统
  --shadow-soft: 0 2px 20px rgba(0, 0, 0, 0.04);
  --shadow-medium: 0 8px 30px rgba(0, 0, 0, 0.12);
  --shadow-strong: 0 16px 40px rgba(0, 0, 0, 0.16);
  --shadow-glass: 0 8px 32px rgba(31, 38, 135, 0.37);
  
  // 精细边框系统
  --border-subtle: rgba(0, 0, 0, 0.06);
  --border-light: rgba(0, 0, 0, 0.1);
  --border-medium: rgba(0, 0, 0, 0.15);
  
  // 现代圆角系统
  --radius-xs: 4px;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 24px;
  --radius-2xl: 32px;
  --radius-full: 9999px;
  
  // 动效缓动函数
  --ease-out-quart: cubic-bezier(0.25, 1, 0.5, 1);
  --ease-out-expo: cubic-bezier(0.19, 1, 0.22, 1);
  --ease-spring: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.premium-card-header {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: var(--radius-2xl);
  border: 1px solid rgba(255, 255, 255, 0.15);
  padding: 32px 40px;
  margin-bottom: 32px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
  
  // 深色渐变玻璃效果
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 100%);
    z-index: 1;
  }
  
  // 背景装饰层
  .bg-decoration {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    overflow: hidden;
    z-index: 0;
    
    .gradient-orb {
      position: absolute;
      border-radius: 50%;
      filter: blur(60px);
      opacity: 0.6;
      animation: float 20s ease-in-out infinite;
      
      &.orb-1 {
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, #667eea 0%, transparent 70%);
        top: -150px;
        right: -100px;
        animation-delay: 0s;
      }
      
      &.orb-2 {
        width: 200px;
        height: 200px;
        background: radial-gradient(circle, #764ba2 0%, transparent 70%);
        bottom: -100px;
        left: -50px;
        animation-delay: -7s;
      }
      
      &.orb-3 {
        width: 150px;
        height: 150px;
        background: radial-gradient(circle, #f093fb 0%, transparent 70%);
        top: 50%;
        left: 30%;
        animation-delay: -14s;
      }
    }
  }
  
  // 主要内容区域
  .header-main {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 32px;
  }
  
  // 品牌区域
  .brand-section {
    display: flex;
    align-items: center;
    gap: 20px;
    flex: 1;
    
    .brand-logo {
      .logo-container {
        position: relative;
        width: 56px;
        height: 56px;
        background: var(--premium-gradient);
        border-radius: var(--radius-lg);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: var(--shadow-medium);
        
        .logo-icon {
          width: 28px;
          height: 28px;
          color: white;
          z-index: 2;
        }
        
        .logo-pulse {
          position: absolute;
          top: -2px;
          left: -2px;
          right: -2px;
          bottom: -2px;
          background: var(--aurora-gradient);
          border-radius: var(--radius-lg);
          opacity: 0;
          animation: pulse-glow 2s ease-in-out infinite;
        }
      }
    }
    
    .brand-info {
      .brand-title {
        font-size: 32px;
        font-weight: 700;
        color: white;
        margin: 0;
        letter-spacing: -0.5px;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }
      
      .brand-subtitle {
        font-size: 15px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.8);
        margin: 4px 0 0 0;
        letter-spacing: 0.3px;
      }
    }
  }
  
  // 状态指示器
  .status-indicators {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 20px;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: var(--radius-full);
    border: 1px solid rgba(255, 255, 255, 0.2);
    
    .indicator-item {
      display: flex;
      align-items: center;
      gap: 8px;
      
      .indicator-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        position: relative;
        
        &.active {
          background: #34c759;
          box-shadow: 0 0 0 2px rgba(52, 199, 89, 0.2);
          
          &::after {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            border: 1px solid #34c759;
            border-radius: 50%;
            animation: ping 2s cubic-bezier(0, 0, 0.2, 1) infinite;
          }
        }
        
        &.syncing {
          background: #007AFF;
          animation: pulse-dot 1.5s ease-in-out infinite;
        }
      }
      
      .indicator-label {
        font-size: 13px;
        font-weight: 500;
        color: rgba(255, 255, 255, 0.8);
        white-space: nowrap;
      }
    }
    
    .indicator-separator {
      width: 1px;
      height: 16px;
      background: rgba(255, 255, 255, 0.2);
    }
  }
  
  // 操作区域
  .action-zone {
    display: flex;
    align-items: center;
    gap: 16px;
    
    .search-container {
      position: relative;
      width: 280px;

      .search-icon {
        position: absolute;
        left: 16px;
        top: 50%;
        transform: translateY(-50%);
        width: 18px;
        height: 18px;
        color: rgba(255, 255, 255, 0.6);
        z-index: 1;
      }

      .search-input {
        width: 100%;
        padding: 14px 16px 14px 48px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: var(--radius-lg);
        font-size: 14px;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        color: white;
        transition: all 0.3s ease;

        &::placeholder {
          color: rgba(255, 255, 255, 0.6);
        }

        &:focus {
          outline: none;
          border-color: rgba(255, 255, 255, 0.4);
          box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
          background: rgba(255, 255, 255, 0.2);
        }
      }
    }
    
    .quick-actions {
      display: flex;
      gap: 8px;
      
      .quick-btn {
        width: 44px;
        height: 44px;
        border: none;
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(10px);
        border-radius: var(--radius-md);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s var(--ease-out-expo);
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(255, 255, 255, 0.2);
        
        .btn-icon {
          width: 18px;
          height: 18px;
          color: rgba(255, 255, 255, 0.8);
          z-index: 2;
          transition: color 0.2s ease;
        }
        
        .btn-ripple {
          position: absolute;
          top: 50%;
          left: 50%;
          width: 0;
          height: 0;
          background: rgba(255, 255, 255, 0.2);
          border-radius: 50%;
          transform: translate(-50%, -50%);
          transition: all 0.3s ease;
        }
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
          background: rgba(255, 255, 255, 0.25);
          
          .btn-icon {
            color: white;
          }
          
          .btn-ripple {
            width: 100%;
            height: 100%;
          }
        }
        
        &:active {
          transform: translateY(0);
        }
      }
    }
    
    // 主要行动按钮
    .premium-cta {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 14px 24px;
      background: var(--premium-gradient);
      border: none;
      border-radius: var(--radius-lg);
      color: white;
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      position: relative;
      overflow: hidden;
      box-shadow: var(--shadow-medium);
      transition: all 0.3s var(--ease-out-expo);
      
      .cta-bg {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: var(--aurora-gradient);
        opacity: 0;
        transition: opacity 0.3s ease;
      }
      
      .cta-icon {
        width: 18px;
        height: 18px;
        z-index: 2;
      }
      
      .cta-text {
        z-index: 2;
        letter-spacing: 0.3px;
      }
      
      .cta-shine {
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent, rgba(255,255,255,0.4), transparent);
        transform: rotate(-45deg) translateX(-100%);
        transition: transform 0.6s ease;
      }
      
      &:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: var(--shadow-strong);
        
        .cta-bg {
          opacity: 1;
        }
        
        .cta-shine {
          transform: rotate(-45deg) translateX(200%);
        }
      }
      
      &:active {
        transform: translateY(-1px) scale(1);
      }
    }
  }
  
  // 装饰线
  .decorative-line {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    display: flex;
    z-index: 2;
    
    .line-segment {
      flex: 1;
      height: 100%;
      background: rgba(255, 255, 255, 0.2);
      
      &.active {
        background: var(--premium-gradient);
        position: relative;
        
        &::after {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          height: 100%;
          width: 0;
          background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
          animation: scan 2s ease-in-out infinite;
        }
      }
      
      &:not(:last-child) {
        margin-right: 1px;
      }
    }
  }
}

// 高级动画系统
@keyframes float {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  25% { transform: translate(10px, -10px) rotate(1deg); }
  50% { transform: translate(-5px, 5px) rotate(-1deg); }
  75% { transform: translate(-10px, -5px) rotate(0.5deg); }
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0; transform: scale(1); }
  50% { opacity: 0.3; transform: scale(1.1); }
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(1.2); }
}

@keyframes ping {
  0% { transform: scale(1); opacity: 1; }
  75%, 100% { transform: scale(2); opacity: 0; }
}

@keyframes scan {
  0% { width: 0; left: 0; }
  50% { width: 100%; left: 0; }
  100% { width: 0; left: 100%; }
}

// 现代响应式设计
@media (max-width: 1200px) {
  .premium-card-header {
    .action-zone {
      .search-container {
        width: 240px;
      }
    }
  }
}

@media (max-width: 1024px) {
  .premium-card-header {
    padding: 24px 32px;
    
    .header-main {
      gap: 20px;
    }
    
    .status-indicators {
      display: none;
    }
    
    .brand-section .brand-info .brand-title {
      font-size: 28px;
    }
    
    .action-zone {
      .search-container {
        width: 200px;
      }
    }
  }
}

@media (max-width: 768px) {
  .premium-card-header {
    padding: 20px 24px;
    border-radius: var(--radius-xl);
    
    .header-main {
      flex-direction: column;
      align-items: flex-start;
      gap: 20px;
    }
    
    .brand-section {
      align-self: stretch;
      
      .brand-info .brand-title {
        font-size: 24px;
      }
    }
    
    .action-zone {
      align-self: stretch;
      flex-wrap: wrap;
      gap: 12px;
      
      .search-container {
        flex: 1;
        min-width: 200px;
      }
      
      .premium-cta {
        flex-shrink: 0;
      }
    }
  }
}

@media (max-width: 480px) {
  .premium-card-header {
    padding: 16px 20px;
    
    .brand-section {
      gap: 16px;
      
      .brand-logo .logo-container {
        width: 48px;
        height: 48px;
        
        .logo-icon {
          width: 24px;
          height: 24px;
        }
      }
      
      .brand-info {
        .brand-title {
          font-size: 22px;
        }
        
        .brand-subtitle {
          font-size: 14px;
        }
      }
    }
    
    .action-zone {
      .quick-actions {
        .quick-btn {
          width: 40px;
          height: 40px;
          
          .btn-icon {
            width: 16px;
            height: 16px;
          }
        }
      }
      
      .premium-cta {
        padding: 12px 20px;
        font-size: 14px;
        
        .cta-icon {
          width: 16px;
          height: 16px;
        }
      }
      
      .search-container {
        .search-input {
          padding: 12px 14px 12px 44px;
        }
      }
    }
  }
}
</style>
