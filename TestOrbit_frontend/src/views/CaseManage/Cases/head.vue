
<template>
  <div class="head-container">
    <div class="title-area">
      <h1>场景用例管理</h1>
      <div class="badge-container">
        <span class="status-badge">活跃</span>
      </div>
    </div>
    <div class="action-area">
      <div class="search-wrapper">
        <el-input
          placeholder="搜索用例..."
          v-model="searchQuery"
          class="search-input"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon class="search-icon"><Search /></el-icon>
          </template>
          <template #append>
            <el-button @click="handleSearch">搜索</el-button>
          </template>
        </el-input>
      </div>
      <div class="action-buttons">
        <el-dropdown 
          :disabled="!props.hasSelection" 
          @command="handleBatchAction" 
          trigger="click"
          class="batch-dropdown"
        >
          <el-button 
            :disabled="!props.hasSelection"
            class="batch-button"
          >
            批量操作 
            <el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="run">
                <el-icon><VideoPlay /></el-icon>
                批量执行
              </el-dropdown-item>
              <el-dropdown-item command="export">
                <el-icon><Download /></el-icon>
                批量导出
              </el-dropdown-item>
              <el-dropdown-item command="delete" divided>
                <el-icon><Delete /></el-icon>
                批量删除
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
  
  <!-- 批量运行模式选择对话框 -->
  <el-dialog
    v-model="showRunModeDialog"
    title="选择运行模式"
    width="400px"
    :close-on-click-modal="false"
  >
    <div class="run-mode-selector">
      <p>您已选择 <strong>{{ selectedCount }}</strong> 个用例，请选择运行模式：</p>
      
      <el-radio-group v-model="selectedRunMode" class="run-mode-options">
        <div class="radio-wrapper">
          <el-radio :label="0" class="run-mode-option">
            <div class="mode-info">
              <div class="mode-title">并行运行</div>
            </div>
          </el-radio>
        </div>
        <div class="radio-wrapper">
          <el-radio :label="1" class="run-mode-option">
            <div class="mode-info">
              <div class="mode-title">串行运行</div>
            </div>
          </el-radio>
        </div>
      </el-radio-group>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="showRunModeDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchRun">
          开始执行
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import { ArrowDown, Search, VideoPlay, Download, Delete } from '@element-plus/icons-vue'

// 定义组件事件
const emit = defineEmits(['search', 'batchAction', 'batchRun'])

// 定义组件属性
const props = defineProps({
  hasSelection: {
    type: Boolean,
    default: false
  },
  selectedCount: {
    type: Number,
    default: 0
  }
})

const searchQuery = ref('')

// 批量运行模式选择对话框
const showRunModeDialog = ref(false)
const selectedRunMode = ref(0) // 默认选择并行模式 (0=并行, 1=串行)

// 用例检索
const handleSearch = () => {
  // 无论输入框是否有内容，都触发搜索事件
  // 当输入为空时，传递空字符串，表示搜索所有用例
  emit('search', searchQuery.value.trim())
}

// 处理批量操作
const handleBatchAction = (command: string) => {
  if (command === 'run') {
    // 显示运行模式选择对话框
    showRunModeDialog.value = true
  } else {
    // 其他操作直接传递给父组件
    emit('batchAction', command)
  }
}

// 确认批量运行 - 用户选择运行模式后的处理
const confirmBatchRun = () => {
  // 关闭对话框
  showRunModeDialog.value = false
  
  // 发送批量运行事件并传递选择的运行模式
  emit('batchRun', selectedRunMode.value)
}

</script>

<style scoped lang="scss">
.head-container {
  height: 80px;
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0 24px;
  background-color: white;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 16px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  transition: all 0.3s ease;
  
  .title-area {
    display: flex;
    align-items: center;
    
    h1 {
      font-size: 20px;
      font-weight: 600;
      margin: 0;
      color: #2c3e50;
      letter-spacing: 0.5px;
    }
    
    .badge-container {
      margin-left: 12px;
      
      .status-badge {
        background-color: #10b981;
        color: white;
        font-size: 12px;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: 500;
      }
    }
  }
  
  .action-area {
    margin-left: auto;
    display: flex;
    align-items: center;
    gap: 16px;

    .search-wrapper {
      .search-input {
        width: 320px;
        border-radius: 8px;
        
        :deep(.el-input__inner) {
          height: 40px;
          border-radius: 8px;
          transition: all 0.3s;
          
          &:focus, &:hover {
            box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
          }
        }
        
        :deep(.el-input__prefix) {
          color: #909399;
        }
      }
    }
    
    .action-buttons {
      display: flex;
      gap: 12px;
      
      .add-case-button {
        height: 40px;
        border-radius: 8px;
        padding: 0 20px;
        font-weight: 500;
        transition: all 0.3s;
        background-color: #409EFF;
        border: none;
        display: flex;
        align-items: center;
        gap: 6px;
        
        &:hover {
          background-color: #66b1ff;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
        }
        
        .icon {
          font-size: 16px;
        }
      }
      
      .batch-dropdown {
        .batch-button {
          height: 40px;
          border-radius: 8px;
          padding: 0 20px;
          font-weight: 500;
          transition: all 0.3s;
          background-color: #f5f7fa;
          color: #606266;
          border-color: #dcdfe6;
          
          &:hover:not(:disabled) {
            color: #409EFF;
            border-color: #c6e2ff;
            background-color: #ecf5ff;
          }
          
          &:disabled {
            opacity: 0.7;
          }
        }
      }
    }
  }
  
  // 响应式调整
  @media (max-width: 900px) {
    flex-direction: column;
    height: auto;
    padding: 16px;
    align-items: flex-start;
    
    .title-area {
      margin-bottom: 16px;
    }
    
    .action-area {
      width: 100%;
      flex-direction: column;
      gap: 12px;
      
      .search-wrapper .search-input {
        width: 100%;
      }
      
      .action-buttons {
        width: 100%;
        justify-content: space-between;
      }
    }
  }
}

/* 批量运行模式选择对话框样式 */
.run-mode-selector {
  .run-mode-options {
    margin-top: 20px;
    display: flex;
    flex-direction: column;
    
    .radio-wrapper {
      margin-bottom: 15px;
    }
    
    .run-mode-option {
      display: flex;
      align-items: center;
      width: 100%;
      padding: 15px;
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      transition: all 0.3s ease;
      margin: 0;
      
      &:hover {
        border-color: #409eff;
        background-color: #f0f9ff;
      }
      
      // 修改Radio布局，使其与内容垂直居中
      :deep(.el-radio__input) {
        height: 100%;
        display: flex;
        align-items: center;
      }
      
      :deep(.el-radio__label) {
        padding-left: 12px;
        display: flex;
        align-items: center;
        height: 100%;
      }
      
      .mode-info {
        margin-left: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        
        .mode-title {
          font-weight: 600;
          font-size: 16px;
          color: #303133;
          margin-bottom: 5px;
        }
        
        .mode-desc {
          font-size: 14px;
          color: #606266;
          line-height: 1.4;
        }
      }
    }
    
    // 选中状态样式
    .el-radio.is-checked .run-mode-option {
      border-color: #409eff;
      background-color: #ecf5ff;
      box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
    }
  }
}
</style>