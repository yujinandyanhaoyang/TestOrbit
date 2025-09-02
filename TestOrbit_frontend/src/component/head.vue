
<template>
    <div class="header">
      <!-- 左侧标题区域 -->
      <div class="header-left">
        <div class="page-title">
          <h1>{{ pageTitle }}</h1>
          <span class="page-subtitle">{{ pageSubtitle }}</span>
        </div>
      </div>

      <!-- 右侧用户区域 -->
      <div class="header-right">
        <div class="user-section" v-if="userStore.isLoggedIn">
          <!-- 用户信息 -->
          <div class="user-info">
            <el-avatar 
              class="user-avatar" 
              :size="36"
              src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
            />
            <div class="user-details">
              <span class="username">{{ userStore.userInfo?.username || 'User' }}</span>
              <span class="user-role">测试工程师</span>
            </div>
          </div>
          
          <!-- 分隔线 -->
          <div class="divider"></div>
          
          <!-- 退出按钮 -->
          <el-button 
            type="text" 
            class="logout-btn"
            @click="handleLogout">
            <svg class="logout-icon" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <polyline points="16,17 21,12 16,7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            退出登录
          </el-button>
        </div>
        
        <!-- 未登录状态 -->
        <div class="login-section" v-else>
          <router-link to="/login" class="login-btn">登录</router-link>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import useUserStore from '@/store/user'
import { useRouter, useRoute } from 'vue-router';
import { ElMessageBox } from 'element-plus';

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();

// 根据当前路由动态设置页面标题
const pageTitle = computed(() => {
  const routeMap: Record<string, string> = {
    '/home': '工作台',
    '/ProjectManage': '项目组管理', 
    '/Case': '场景用例管理',
    '/UserManage': '用户管理',
    '/PressureTest': '压力测试'
  }
  return routeMap[route.path] || 'TestOrbit'
})

const pageSubtitle = computed(() => {
  const subtitleMap: Record<string, string> = {
    '/home': '欢迎回来，开始您的API测试之旅',
    '/ProjectManage': '创建和管理您的测试项目组',
    '/Case': '设计和执行您的API测试场景',
    '/UserManage': '系统用户权限管理',
    '/PressureTest': '性能测试和压力测试工具'
  }
  return subtitleMap[route.path] || 'API Testing Platform'
})

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
    userStore.logout();
    router.push('/login');
  }).catch(() => {
    // 取消操作，不做任何事
  });
};
</script>

<style lang="scss" scoped>
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 0 24px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative; // 改为relative，避免覆盖sidebar
  width: 100%;
  z-index: 100; // 降低z-index，确保sidebar不被覆盖
  box-shadow: 0 1px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0; // 防止被压缩

  &:hover {
    box-shadow: 0 4px 32px rgba(0, 0, 0, 0.15);
  }

  // 左侧标题区域
  .header-left {
    display: flex;
    align-items: center;

    .page-title {
      h1 {
        font-size: 24px;
        font-weight: 700;
        color: white;
        margin: 0;
        line-height: 1.2;
        letter-spacing: -0.5px;
      }

      .page-subtitle {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.7);
        font-weight: 400;
        display: block;
        margin-top: 4px;
        line-height: 1.2;
      }
    }
  }

  // 右侧用户区域
  .header-right {
    display: flex;
    justify-content: flex-end;

    .user-section {
      display: flex;
      align-items: center;
      gap: 16px;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      padding: 8px 16px;
      border-radius: 16px;
      border: 1px solid rgba(255, 255, 255, 0.15);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

      &:hover {
        background: rgba(255, 255, 255, 0.15);
        transform: translateY(-1px);
      }

      .user-info {
        display: flex;
        align-items: center;
        gap: 12px;

        .user-avatar {
          border: 2px solid rgba(255, 255, 255, 0.3);
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

          &:hover {
            border-color: rgba(255, 255, 255, 0.6);
            transform: scale(1.05);
          }
        }

        .user-details {
          display: flex;
          flex-direction: column;

          .username {
            font-size: 14px;
            font-weight: 600;
            color: white;
            line-height: 1.2;
          }

          .user-role {
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
            line-height: 1.2;
          }
        }
      }

      .divider {
        width: 1px;
        height: 24px;
        background: rgba(255, 255, 255, 0.2);
      }

      .logout-btn {
        color: rgba(255, 255, 255, 0.8);
        font-size: 14px;
        font-weight: 500;
        padding: 6px 12px;
        border-radius: 8px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        gap: 6px;

        .logout-icon {
          width: 16px;
          height: 16px;
        }

        &:hover {
          color: white;
          background: rgba(255, 255, 255, 0.1);
        }

        &:active {
          transform: scale(0.95);
        }
      }
    }

    .login-section {
      .login-btn {
        color: white;
        text-decoration: none;
        padding: 10px 24px;
        background: rgba(255, 255, 255, 0.2);
        border-radius: 12px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid rgba(255, 255, 255, 0.3);

        &:hover {
          background: rgba(255, 255, 255, 0.3);
          transform: translateY(-1px);
          box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 768px) {
  .header {
    height: 64px;
    padding: 0 12px;

    .logo-container .logo-text .logo-subtitle {
      display: none;
    }

    .user-section .user-info .user-details .user-role {
      display: none;
    }
  }
}

// 全局样式重写
:deep(.el-button.is-text) {
  border: none;
  background: none;
  padding: 0;
  
  &:hover,
  &:focus {
    background: none !important;
  }
}
</style>