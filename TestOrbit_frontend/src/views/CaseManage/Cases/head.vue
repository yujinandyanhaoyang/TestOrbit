
<template>
  <div class="head-container">
    <div class="title-area">
      <h1>场景用例管理</h1>
    </div>
    <div class="action-area">
      <el-input
        placeholder="搜索用例"
        v-model="searchQuery"
        class="search-input"
        clearable
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button icon="Search" @click="handleSearch" />
          <svg  xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024"
      style="color: skyblue;">
        <path fill="currentColor" d="m795.904 750.72 124.992 124.928a32 32 0 0 1-45.248 45.248L750.656 795.904a416 416 0 1 1 45.248-45.248zM480 832a352 352 0 1 0 0-704 352 352 0 0 0 0 704">
        </path></svg>
        </template>
      </el-input>
      <el-button type="primary" @click="handleAddCase">添加用例</el-button>
      <el-dropdown :disabled="!props.hasSelection" @command="handleBatchAction">
        <el-button :disabled="!props.hasSelection">
          批量操作 <el-icon class="el-icon--right"><arrow-down /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="run">批量执行</el-dropdown-item>
            <el-dropdown-item command="export">批量导出</el-dropdown-item>
            <el-dropdown-item command="delete" divided>批量删除</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, defineEmits, defineProps } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'

// 定义组件事件
const emit = defineEmits(['search', 'add', 'batchAction'])

// 定义组件属性
const props = defineProps({
  hasSelection: {
    type: Boolean,
    default: false
  }
})

const searchQuery = ref('')

// 添加用例
const handleAddCase = () => {
  emit('add')
}

// 用例检索
const handleSearch = () => {
  // 无论输入框是否有内容，都触发搜索事件
  // 当输入为空时，传递空字符串，表示搜索所有用例
  emit('search', searchQuery.value.trim())
}

// 处理批量操作
const handleBatchAction = (command: string) => {
  emit('batchAction', command)
}

</script>

<style scoped lang="scss">
.head-container {
  height: 70px;
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0 20px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #e4e7ed;
  margin-bottom: 10px;
  
  h1 {
    font-size: 18px;
    font-weight: bold;
    margin: 0;
    color: #303133;
  }
  .action-area {
    margin-left: auto;
    display: flex;
    align-items: center;

    .search-input {
      width: 400px;
      margin-right: 30px;
    }
  }
}
</style>