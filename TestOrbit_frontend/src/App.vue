
<template>
  <div class="app-container">
    <!-- 左侧菜单栏 -->
    <Sidebar v-if="shouldShowSidebar" />
    
    <!-- 右侧主内容区域 -->
    <div 
      class="main-content" 
      :class="{ 'with-sidebar': shouldShowSidebar }"
      :style="mainContentStyle"
    >
      <!-- 顶部头部 -->
      <Header v-if="shouldShowHeader" />
      
      <!-- 页面内容区域 -->
      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Header from '@/component/head.vue'
import Sidebar from '@/component/sidebar.vue'
import { useLayoutStore } from '@/store/layout'

const route = useRoute()
const layoutStore = useLayoutStore()

// 判断是否显示侧边栏（登录页不显示）
const shouldShowSidebar = computed(() => {
  return route.path !== '/login'
})

// 判断是否显示头部（登录页不显示）  
const shouldShowHeader = computed(() => {
  return route.path !== '/login'
})

// 动态计算主内容区域的左边距
const mainContentStyle = computed(() => {
  if (!shouldShowSidebar.value) return {}
  
  return {
    marginLeft: `${layoutStore.sidebarWidth}px`
  }
})
</script>

<style lang="scss">
// 使用现代的 @use 语法替代已弃用的 @import
@use '@/assets/style/reset.scss';

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f7fa;
  color: #333;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.app-container {
  display: flex;
  min-height: 100vh;
  width: 100%;
  background: #f5f7fa;
  position: relative;

  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: #f5f7fa;

    .page-content {
      flex: 1;
      padding: 24px;
      overflow-y: auto;
      min-height: 0; // 重要：允许flex子元素收缩
      
      // 确保内容区域有合适的最大宽度
      max-width: 100%;
      
      // 防止内容溢出
      word-wrap: break-word;
      overflow-wrap: break-word;
      
      // 确保背景色一致
      background: #f5f7fa;
    }
  }
}

// 响应式设计
@media (max-width: 1024px) {
  .app-container .main-content .page-content {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .app-container {
    .main-content {
      margin-left: 0 !important; // 移动端不使用侧边栏margin
      
      .page-content {
        padding: 12px;
      }
    }
  }
}

// 确保全局滚动条样式
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
  
  &:hover {
    background: #a8a8a8;
  }
}

// Element Plus 全局样式覆盖
:deep(.el-button) {
  font-weight: 500;
}

:deep(.el-avatar) {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>