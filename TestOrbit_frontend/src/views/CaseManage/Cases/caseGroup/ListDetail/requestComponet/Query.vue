<template>
  <div class="query-editor">
    <el-table :data="querys" border style="width: 100%">
      <!-- 启用/禁用列 -->
      <el-table-column width="50">
        <template #default="scope">
          <el-checkbox v-model="scope.row.enabled" @change="updateQuerys" />
        </template>
      </el-table-column>
      
      <!-- 键列 -->
      <el-table-column label="键" width="200">
        <template #default="scope">
          <el-input 
            v-model="scope.row.key" 
            placeholder="请输入query名称" 
            @change="updateQuerys"
            :disabled="!scope.row.enabled" 
          />
        </template>
      </el-table-column>
      
      <!-- 值列 -->
      <el-table-column label="值" width="300">
        <template #default="scope">
          <el-input 
            v-model="scope.row.value" 
            placeholder="请输入query值" 
            @change="updateQuerys"
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
            @change="updateQuerys"
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
        <el-icon><Plus /></el-icon> 添加 query
      </el-button>
      <el-button @click="bulkEdit" size="small">
        <el-icon><Edit /></el-icon> 批量编辑
      </el-button>
    </div>
    
    <!-- 批量编辑对话框 -->
    <el-dialog v-model="showBulkEditDialog" title="批量编辑 querys" width="600px">
      <el-form>
        <el-form-item>
          <el-input
            v-model="bulkEditContent"
            type="textarea"
            :rows="10"
            placeholder="每行一个query，格式：键:值"
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
import { ref, onMounted, watch } from 'vue';
import { Delete, Plus, Edit } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 定义query项的类型
interface queryItem {
  key: string;
  value: string;
  remark: string;
  enabled: boolean;
}

// 定义接收的props
const props = defineProps<{
  requestQuery?: Record<string, string>;
}>();

// 创建事件
const emit = defineEmits(['update:querys']);

// 初始化query数据
const querys = ref<queryItem[]>([]);

// 监听props变化
watch(() => props.requestQuery, (newQuery: Record<string, string> | undefined) => {
  if (newQuery && Object.keys(newQuery).length > 0) {
    console.log('Query组件接收到新的查询参数:', newQuery);
    querys.value = Object.entries(newQuery).map(([key, value]) => ({
      key,
      value: String(value), // 确保value是字符串类型
      remark: '',
      enabled: true,
    }));
  }
}, { immediate: true });

// 批量编辑相关
const showBulkEditDialog = ref(false);
const bulkEditContent = ref('');

// 添加一行
const addRow = () => {
  querys.value.push({
    key: '',
    value: '',
    remark: '',
    enabled: true,
  });
  updateQuerys();
};

// 删除一行
const deleteRow = (index: number) => {
  querys.value.splice(index, 1);
  updateQuerys();
};

// 更新querys，向父组件发送更新后的数据
const updateQuerys = () => {
  emit('update:querys', getEnabledQuerys());
};

// 获取启用的querys
const getEnabledQuerys = () => {
  return querys.value
    .filter(item => item.enabled && item.key.trim() !== '')
    .reduce((result, item) => {
      result[item.key] = item.value;
      return result;
    }, {} as Record<string, string>);
};

// 打开批量编辑对话框
const bulkEdit = () => {
  // 将现有querys转换为文本格式
  bulkEditContent.value = querys.value
    .map(item => `${item.key}: ${item.value}${item.remark ? ' // ' + item.remark : ''}`)
    .join('\n');
  showBulkEditDialog.value = true;
};

// 应用批量编辑
const applyBulkEdit = () => {
  try {
    const lines = bulkEditContent.value.split('\n').filter(line => line.trim() !== '');
    const newquerys: queryItem[] = [];
    
    lines.forEach(line => {
      // 处理注释
      const [content, comment] = line.split('//').map(part => part.trim());
      
      // 处理键值对
      if (content.includes(':')) {
        const [key, ...valueParts] = content.split(':');
        const value = valueParts.join(':').trim(); // 处理值中可能包含":"的情况
        
        newquerys.push({
          key: key.trim(),
          value,
          remark: comment || '',
          enabled: true
        });
      }
    });
    
    // 如果解析成功且有数据，则更新querys
    if (newquerys.length > 0) {
      querys.value = newquerys;
      updateQuerys();
      showBulkEditDialog.value = false;
      ElMessage.success(`成功更新 ${newquerys.length} 个querys`);
    } else {
      ElMessage.warning('未检测到有效的query内容');
    }
  } catch (error) {
    console.error('解析批量编辑内容失败:', error);
    ElMessage.error('解析批量编辑内容失败');
  }
};

// 组件挂载时，初始化发送query数据给父组件
onMounted(() => {
  updateQuerys();
});
</script>

<style scoped lang="scss">
.query-editor {
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
