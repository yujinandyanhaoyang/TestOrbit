<template>
  <div class="sidebar" :class="{ 'sidebar-collapsed': layoutStore.sidebarCollapsed }">
    <!-- 侧边栏头部 -->
    <div class="sidebar-header">
      <div class="logo-container" @click="goHome">
        <div class="logo-icon">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
            <path d="M12 6v6l4 2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="12" cy="12" r="2" fill="currentColor"/>
          </svg>
        </div>
        <div class="logo-text" v-show="!layoutStore.sidebarCollapsed">
          <span class="logo-name">TestOrbit</span>
          <span class="logo-subtitle">API Testing</span>
        </div>
      </div>
      
      <!-- 折叠按钮 -->
      <button class="collapse-btn" @click="toggleCollapse">
        <svg 
          viewBox="0 0 24 24" 
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
          :class="{ 'rotate-180': layoutStore.sidebarCollapsed }"
        >
          <path d="M15 18l-6-6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <!-- 菜单导航 -->
    <nav class="sidebar-nav">
      <div class="nav-section">
        <h3 class="nav-title" v-show="!layoutStore.sidebarCollapsed">主要功能</h3>
        
        <router-link 
          to="/home" 
          class="nav-item" 
          active-class="nav-active"
          @click="changeActive('/home')"
        >
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="9,22 9,12 15,12 15,22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="nav-text" v-show="!layoutStore.sidebarCollapsed">首页</span>
        </router-link>

        <router-link 
          to="/ProjectManage" 
          class="nav-item" 
          active-class="nav-active"
          @click="changeActive('/ProjectManage')"
        >
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="nav-text" v-show="!layoutStore.sidebarCollapsed">项目组管理</span>
        </router-link>

        <router-link 
          to="/Case" 
          class="nav-item" 
          active-class="nav-active"
          @click="changeActive('/Case')"
        >
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="14,2 14,8 20,8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="10,9 9,9 8,9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="nav-text" v-show="!layoutStore.sidebarCollapsed">场景用例管理</span>
        </router-link>

        <router-link 
          to="/PressureTest" 
          class="nav-item" 
          active-class="nav-active"
          @click="changeActive('/PressureTest')"
        >
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="nav-text" v-show="!layoutStore.sidebarCollapsed">压力测试</span>
        </router-link>
      </div>

      <div class="nav-section">
        <h3 class="nav-title" v-show="!layoutStore.sidebarCollapsed">系统管理</h3>
        
        <router-link 
          to="/UserManage" 
          class="nav-item" 
          active-class="nav-active"
          @click="changeActive('/UserManage')"
        >
          <div class="nav-icon">
            <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="12" cy="7" r="4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <span class="nav-text" v-show="!layoutStore.sidebarCollapsed">用户管理</span>
        </router-link>
      </div>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import useUserStore from '@/store/user'
import { useLayoutStore } from '@/store/layout'

const router = useRouter()
const userStore = useUserStore()
const layoutStore = useLayoutStore()

// 折叠/展开侧边栏
const toggleCollapse = () => {
  layoutStore.toggleSidebar()
}

// 跳转具体功能页面（从HomePage迁移过来的功能）
const changeActive = (path: string) => {
  router.push({ path })
  handleNavClick() // 调用原有的导航点击处理
}

// 导航点击处理（移动端自动收起）
const handleNavClick = () => {
  // 移动端点击导航后自动收起侧边栏
  if (window.innerWidth <= 768) {
    layoutStore.setSidebarCollapsed(true)
  }
}

// 返回首页
const goHome = () => {
  router.push('/home')
}

// 退出登录处理
const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗?',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {
    // 取消操作
  })
}
</script>

<style lang="scss" scoped>
.sidebar {
  width: 280px;
  min-height: 100vh;
  background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 4px 0 20px rgba(0, 0, 0, 0.1);

  &.sidebar-collapsed {
    width: 80px;
  }

  // 侧边栏头部
  .sidebar-header {
    padding: 20px 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    display: flex;
    align-items: center;
    justify-content: space-between;
    min-height: 72px;

    .logo-container {
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      padding: 8px;
      border-radius: 12px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      flex: 1;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }

      .logo-icon {
        width: 36px;
        height: 36px;
        background: linear-gradient(135deg, #3498db, #2980b9);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);

        svg {
          width: 20px;
          height: 20px;
        }
      }

      .logo-text {
        display: flex;
        flex-direction: column;

        .logo-name {
          font-size: 18px;
          font-weight: 700;
          color: white;
          line-height: 1.2;
        }

        .logo-subtitle {
          font-size: 11px;
          color: rgba(255, 255, 255, 0.6);
          font-weight: 500;
        }
      }
    }

    .collapse-btn {
      width: 32px;
      height: 32px;
      background: rgba(255, 255, 255, 0.1);
      border: none;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.1);
      }

      svg {
        width: 16px;
        height: 16px;
        color: white;
        transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);

        &.rotate-180 {
          transform: rotate(180deg);
        }
      }
    }
  }

  // 导航菜单
  .sidebar-nav {
    flex: 1;
    padding: 24px 0;
    overflow-y: auto;

    .nav-section {
      margin-bottom: 32px;

      .nav-title {
        font-size: 12px;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.5);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 16px 24px;
        line-height: 1;
      }

      .nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 24px;
        margin: 4px 12px;
        border-radius: 12px;
        color: rgba(255, 255, 255, 0.8);
        text-decoration: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;

        &:hover {
          color: white;
          background: rgba(255, 255, 255, 0.1);
          transform: translateX(4px);
        }

        &.nav-active {
          color: white;
          background: linear-gradient(135deg, #3498db, #2980b9);
          box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);

          &::before {
            content: '';
            position: absolute;
            left: -12px;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 24px;
            background: #3498db;
            border-radius: 2px;
          }
        }

        .nav-icon {
          width: 20px;
          height: 20px;
          display: flex;
          align-items: center;
          justify-content: center;
          flex-shrink: 0;

          svg {
            width: 20px;
            height: 20px;
          }
        }

        .nav-text {
          font-size: 14px;
          font-weight: 500;
          white-space: nowrap;
        }
      }
    }
  }

  // 侧边栏底部
  .sidebar-footer {
    padding: 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.1);

    .user-section {
      display: flex;
      align-items: center;
      gap: 12px;
      background: rgba(255, 255, 255, 0.05);
      padding: 12px;
      border-radius: 12px;
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        background: rgba(255, 255, 255, 0.1);
      }

      .user-avatar {
        flex-shrink: 0;
        
        :deep(.el-avatar) {
          border: 2px solid rgba(255, 255, 255, 0.2);
        }
      }

      .user-info {
        flex: 1;
        min-width: 0;

        .username {
          display: block;
          font-size: 14px;
          font-weight: 600;
          color: white;
          line-height: 1.2;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .user-role {
          display: block;
          font-size: 12px;
          color: rgba(255, 255, 255, 0.6);
          line-height: 1.2;
        }
      }

      .logout-btn {
        color: rgba(255, 255, 255, 0.7);
        padding: 8px;
        border-radius: 8px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        flex-shrink: 0;

        .logout-icon {
          width: 16px;
          height: 16px;
        }

        &:hover {
          color: white;
          background: rgba(255, 255, 255, 0.1);
        }
      }
    }
  }
}

// 滚动条样式
.sidebar-nav {
  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;

    &:hover {
      background: rgba(255, 255, 255, 0.3);
    }
  }
}

// 全局样式重写
:deep(.el-button.is-text) {
  border: none;
  background: none;
  
  &:hover,
  &:focus {
    background: none !important;
  }
}
</style>
