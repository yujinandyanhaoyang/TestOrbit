<template>
  <div class="header-editor">
    <el-table :data="headers" border style="width: 100%">
      <!-- 启用/禁用列 -->
      <el-table-column width="50">
        <template #default="scope">
          <el-checkbox v-model="scope.row.enabled" @change="updateHeaders" />
        </template>
      </el-table-column>
      
      <!-- 键列 -->
      <el-table-column label="键" width="200">
        <template #default="scope">
          <el-input 
            v-model="scope.row.key" 
            placeholder="请输入header名称" 
            @change="updateHeaders"
            :disabled="!scope.row.enabled" 
          />
        </template>
      </el-table-column>
      
      <!-- 值列 -->
      <el-table-column label="值" width="300">
        <template #default="scope">
          <el-input 
            v-model="scope.row.value" 
            placeholder="请输入header值" 
            @change="updateHeaders"
            :disabled="!scope.row.enabled" 
          />
        </template>
      </el-table-column>
      
      <!-- 描述列 -->
      <el-table-column label="描述">
        <template #default="scope">
          <el-input 
            v-model="scope.row.remark" 
            placeholder="可选描述" 
            @change="updateHeaders"
            :disabled="!scope.row.enabled" 
          />
        </template>
      </el-table-column>
      
      <!-- 操作列 -->
      <el-table-column width="70">
        <template #default="scope">
          <el-button 
            type="danger" 
            icon="Delete" 
            circle 
            size="small"
            @click="deleteRow(scope.$index)" 
          />
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 底部操作区 -->
    <div class="action-bar">
      <el-button type="primary" @click="addRow" size="small">
        <el-icon><Plus /></el-icon> 添加 Header
      </el-button>
      <el-button @click="bulkEdit" size="small">
        <el-icon><Edit /></el-icon> 批量编辑
      </el-button>
    </div>
    
    <!-- 批量编辑对话框 -->
    <el-dialog v-model="showBulkEditDialog" title="批量编辑 Headers" width="600px">
      <el-form>
        <el-form-item>
          <el-input
            v-model="bulkEditContent"
            type="textarea"
            :rows="10"
            placeholder="每行一个header，格式：键:值"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showBulkEditDialog = false">取消</el-button>
          <el-button type="primary" @click="applyBulkEdit">应用</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { ref, defineEmits, onMounted } from 'vue';
import { Delete, Plus, Edit } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 定义header项的类型
interface HeaderItem {
  key: string;
  value: string;
  remark: string;
  enabled: boolean;
}

// 创建事件
const emit = defineEmits(['update:headers']);

// 初始化header数据
const headers = ref<HeaderItem[]>([
  {
    key: 'Content-Type',
    value: 'application/json',
    remark: '指定请求体的内容类型',
    enabled: true,
  },
  {
    key: 'Authorization',
    value: 'Bearer token',
    remark: '身份验证token',
    enabled: false,
  },
]);

// 批量编辑相关
const showBulkEditDialog = ref(false);
const bulkEditContent = ref('');

// 添加一行
const addRow = () => {
  headers.value.push({
    key: '',
    value: '',
    remark: '',
    enabled: true,
  });
  updateHeaders();
};

// 删除一行
const deleteRow = (index: number) => {
  headers.value.splice(index, 1);
  updateHeaders();
};

// 更新headers，向父组件发送更新后的数据
const updateHeaders = () => {
  emit('update:headers', getEnabledHeaders());
};

// 获取启用的headers
const getEnabledHeaders = () => {
  return headers.value
    .filter(item => item.enabled && item.key.trim() !== '')
    .reduce((result, item) => {
      result[item.key] = item.value;
      return result;
    }, {} as Record<string, string>);
};

// 打开批量编辑对话框
const bulkEdit = () => {
  // 将现有headers转换为文本格式
  bulkEditContent.value = headers.value
    .map(item => `${item.key}: ${item.value}${item.remark ? ' // ' + item.remark : ''}`)
    .join('\n');
  showBulkEditDialog.value = true;
};

// 应用批量编辑
const applyBulkEdit = () => {
  try {
    const lines = bulkEditContent.value.split('\n').filter(line => line.trim() !== '');
    const newHeaders: HeaderItem[] = [];
    
    lines.forEach(line => {
      // 处理注释
      const [content, comment] = line.split('//').map(part => part.trim());
      
      // 处理键值对
      if (content.includes(':')) {
        const [key, ...valueParts] = content.split(':');
        const value = valueParts.join(':').trim(); // 处理值中可能包含":"的情况
        
        newHeaders.push({
          key: key.trim(),
          value,
          remark: comment || '',
          enabled: true
        });
      }
    });
    
    // 如果解析成功且有数据，则更新headers
    if (newHeaders.length > 0) {
      headers.value = newHeaders;
      updateHeaders();
      showBulkEditDialog.value = false;
      ElMessage.success(`成功更新 ${newHeaders.length} 个headers`);
    } else {
      ElMessage.warning('未检测到有效的header内容');
    }
  } catch (error) {
    console.error('解析批量编辑内容失败:', error);
    ElMessage.error('解析批量编辑内容失败');
  }
};

// 组件挂载时，初始化发送header数据给父组件
onMounted(() => {
  updateHeaders();
});
</script>

<style scoped lang="scss">
.header-editor {
  width: 100%;
  
  .action-bar {
    margin-top: 10px;
    display: flex;
    justify-content: flex-start;
    gap: 10px;
  }
}

:deep(.el-table .cell) {
  padding: 2px 5px;
}

:deep(.el-input__wrapper) {
  padding: 0 10px;
}

:deep(.el-input.is-disabled .el-input__wrapper) {
  background-color: #f5f7fa;
}
</style>
