<template>
  <div class="case-manage-container">
    <!--左侧菜单栏-->
    <div class="sidebar-panel">
      <!-- 顶部导航栏 -->
      <div class="nav-header">
        <div class="nav-item" @click="$router.push('/home')" title="返回主页">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon">
            <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9 22 9 12 15 12 15 22"></polyline>
          </svg>
          <span class="nav-label">主页</span>
        </div>
        
        <div class="nav-item" :class="{ 'active': showRecycle }" @click="openRecycleBin" title="回收站">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon">
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"></path>
            <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          </svg>
          <span class="nav-label">回收站</span>
          <span class="nav-badge" v-if="recycleBinCount > 0">{{ recycleBinCount }}</span>
        </div>
        
        <div class="nav-item" :class="{ 'active': !showRecycle }" @click="showRecycle = false" title="添加目录">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="nav-icon">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            <line x1="12" y1="11" x2="12" y2="17"></line>
            <line x1="9" y1="14" x2="15" y2="14"></line>
          </svg>
          <span class="nav-label">文件</span>
        </div>
      </div>
      
      <!-- 内容区域 - 仅显示文件夹组件，回收站已移至抽屉中 -->
      <div class="sidebar-content">
        <!-- 文件夹树组件 -->
        <div class="content-section">
          <Folder />
        </div>
      </div>
    </div>
    <!--内容区-->
    <div class="content-panel">
      <PageManage />
    </div>

    <!-- 回收站抽屉组件 -->
    <el-drawer 
      v-model="recycleDrawer" 
      title="已删除用例回收站" 
      size="70%" 
      :with-header="true"
      direction="rtl"
      @closed="loadRecycleBinCount"
    >
      <div class="recycle-container">
        <Recycle />
      </div>
    </el-drawer>
  </div>
</template>


<script lang="ts" setup>
//引入组件
import { ref, onMounted, provide } from 'vue'
import Folder from './CombineFolder/CaseTree.vue'
import Recycle from './Cases/recyclePage.vue'
import PageManage from './Cases/index.vue'
import { getCaseGroupList } from '@/api/case/caseGroup'

// 控制视图切换
const showRecycle = ref(false)

// 回收站抽屉控制
const recycleDrawer = ref(false)

// 回收站数量统计
const recycleBinCount = ref(0)

// 打开回收站抽屉
const openRecycleBin = () => {
  recycleDrawer.value = true
  showRecycle.value = true // 保持向后兼容
  loadRecycleBinCount() // 刷新数量
}

// 获取回收站中项目数量
const loadRecycleBinCount = async () => {
  try {
    // 获取回收站数据，只需要总数
    const response = await getCaseGroupList(1, 1, true)
    if (response.code === 200) {
      recycleBinCount.value = response.results?.total || 0
    }
  } catch (error) {
    console.error('获取回收站数量出错:', error)
  }
}

// 切换回收站视图 (保留原方法以保持兼容)
const toggleRecycleView = () => {
  showRecycle.value = !showRecycle.value
}

// 组件挂载时加载回收站数量
onMounted(() => {
  loadRecycleBinCount()
})

// 向子组件提供回收站抽屉控制
provide('recycleDrawer', recycleDrawer)
</script>

<style scoped lang="scss">
.case-manage-container {
  display: flex;
  height: 100vh; // 使用视口高度确保占满全屏
  background-color: #f7f8fa; // 更现代、柔和的背景色
  overflow: hidden; // 防止外层滚动
}

.sidebar-panel {
  width: 320px;
  flex-shrink: 0; 
  display: flex;
  flex-direction: column;
  background-color: #ffffff;
  border-right: 1px solid #e8eaec;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  
  // 顶部导航栏
  .nav-header {
    display: flex;
    justify-content: space-around;
    align-items: center;
    height: 64px;
    padding: 0 10px;
    background: linear-gradient(to right, #0052d9, #0072de); // 腾讯蓝色渐变
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    
    .nav-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 8px 12px;
      border-radius: 8px;
      cursor: pointer;
      color: rgba(255, 255, 255, 0.85);
      transition: all 0.3s ease;
      
      .nav-icon {
        width: 22px;
        height: 22px;
        margin-bottom: 4px;
      }
      
      .nav-label {
        font-size: 12px;
        font-weight: 500;
      }
      
      &:hover {
        background-color: rgba(255, 255, 255, 0.15);
        transform: translateY(-2px);
      }
      
      &.active {
        background-color: rgba(255, 255, 255, 0.2);
        color: #ffffff;
      }
      
      .nav-badge {
        position: absolute;
        top: 0;
        right: 0;
        background-color: #ff4d4f;
        color: white;
        border-radius: 10px;
        padding: 0 6px;
        font-size: 10px;
        line-height: 16px;
        font-weight: bold;
        min-width: 16px;
        text-align: center;
        box-shadow: 0 0 0 2px #0052d9;
        transform: translate(30%, -30%);
        transition: all 0.3s;
      }
    }
  }
  
  // 内容区域
  .sidebar-content {
    flex: 1;
    padding: 20px;
    overflow: hidden;
    position: relative;
    
    .content-section {
      height: 100%;
      transition: opacity 0.3s ease, transform 0.3s ease;
      
      &.hidden {
        display: none;
      }
    }
  }
}

.content-panel {
  flex: 1; // 占据剩余所有空间
  padding: 20px;
  overflow-y: auto; // 内容超出时，仅内容区滚动
  display: flex;
  flex-direction: column;
}

// 这里我们可以移除之前的侧边栏相关样式，因为我们已经使用了新的导航样式

// 添加媒体查询，让导航在小屏幕上也能正常工作
@media (max-width: 768px) {
  .sidebar-panel {
    width: 280px;
    
    .nav-header {
      height: 56px;
      
      .nav-item {
        padding: 6px 8px;
        
        .nav-icon {
          width: 18px;
          height: 18px;
        }
        
        .nav-label {
          font-size: 11px;
        }
      }
    }
    
    .sidebar-content {
      padding: 15px;
    }
  }
}

// 添加动画效果
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.content-section {
  animation: fadeIn 0.3s ease-out;
}

// 使用 :deep() 来影响子组件的根元素
:deep(.el-tree) {
  background-color: transparent;
}
</style>