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
            @blur="updateHeaders"
            @keyup.enter="updateHeaders"
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
            @blur="updateHeaders"
            @keyup.enter="updateHeaders"
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
            @blur="updateHeaders"
            @keyup.enter="updateHeaders"
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
import { ref,  onMounted, watch } from 'vue';
import { Delete, Plus, Edit } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 定义header项的类型
interface HeaderItem {
  key: string;
  value: string;
  remark: string;
  enabled: boolean;
}

// 定义接收的props
const props = defineProps<{
  requestHeaders: Record<string, string>;
}>();

// 创建事件
const emit = defineEmits(['update:headers']);

// 初始化header数据
const headers = ref<HeaderItem[]>([]);

// 监听props变化
watch(() => props.requestHeaders, (newHeaders) => {
  // 
  
  if (newHeaders && Object.keys(newHeaders).length > 0) {
    // 转换为组件内部格式
    const convertedHeaders = Object.entries(newHeaders).map(([key, value]) => ({
      key,
      value: value || '',
      remark: '',
      enabled: true,
    }));
    
    // 合并现有的空行（用户正在编辑的）
    const emptyRows = headers.value.filter(item => item.key.trim() === '');
    headers.value = [...convertedHeaders, ...emptyRows];
    
    // 
  } else {
    // 如果没有数据，保留用户正在编辑的空行
    const emptyRows = headers.value.filter(item => item.key.trim() === '');
    headers.value = emptyRows.length > 0 ? emptyRows : [];
    // 
  }
}, { immediate: true });

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
  // 不立即触发更新，让用户先填写内容
  // updateHeaders(); // 移除这行，改为在用户输入时才触发
};

// 删除一行
const deleteRow = (index: number) => {
  headers.value.splice(index, 1);
  // 删除行时立即触发更新
  updateHeaders();
};

// 更新headers，向父组件发送更新后的数据
const updateHeaders = () => {
  emit('update:headers', getEnabledHeaders());
};

// 获取启用的headers
const getEnabledHeaders = () => {
  return headers.value
    .filter(item => {
      // 只过滤启用的且键名不为空的项
      // 允许值为空的情况（有些header只需要键名）
      return item.enabled && item.key.trim() !== '';
    })
    .reduce((result, item) => {
      result[item.key.trim()] = item.value || ''; // 确保值不为undefined
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

// 组件挂载时，如果有有效数据才发送给父组件
onMounted(() => {
  const enabledHeaders = getEnabledHeaders();
  // 只有当有有效的header数据时才通知父组件
  if (Object.keys(enabledHeaders).length > 0) {
    updateHeaders();
  }
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
