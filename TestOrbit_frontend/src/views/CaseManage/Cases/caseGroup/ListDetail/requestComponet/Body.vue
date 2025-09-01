
<template>
    <div class="body-editor">
        <!-- Content Type 选择器 -->
        <div class="content-type-selector">
            <el-radio-group v-model="contentType" size="small" @change="onContentTypeChange">
                <el-radio-button label="json">JSON</el-radio-button>
                <el-radio-button label="form-data" disabled>Form Data</el-radio-button>
                <el-radio-button label="x-www-form-urlencoded" disabled>x-www-form-urlencoded</el-radio-button>
                <el-radio-button label="raw" disabled>Raw</el-radio-button>
                <el-radio-button label="binary" disabled>Binary</el-radio-button>
            </el-radio-group>
            
            <div class="right-actions">
                <el-tooltip content="格式化JSON" placement="top">
                    <el-button 
                        type="primary" 
                        :icon="Document" 
                        size="small" 
                        plain
                        @click="formatJson"
                        :disabled="contentType !== 'json'"
                    >格式化</el-button>
                </el-tooltip>
            </div>
        </div>
        
        <!-- JSON编辑器 -->
        <div v-if="contentType === 'json'" class="json-editor-container">
            <el-input
                v-model="jsonContent"
                type="textarea"
                :rows="10"
                placeholder="请输入JSON格式的请求体内容"
                :class="{ 'is-invalid': !isValidJson }"
                @input="validateJson"
                @change="emitBodyChange"
            />
            
            <div v-if="!isValidJson" class="json-error">
                <el-alert
                    title="JSON格式无效"
                    type="error"
                    :description="jsonError"
                    show-icon
                    :closable="false"
                />
            </div>
        </div>
        
        <!-- 其他类型的编辑器（暂不实现） -->
        <div v-else class="other-editor-placeholder">
            <el-empty description="此请求体类型暂未实现" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted} from 'vue';
import { Document } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

// 定义接收的props
const props = defineProps<{
  requestBody?: any;
}>();

// 定义事件
const emit = defineEmits(['update:body', 'update:contentType']);

// 内容类型
const contentType = ref('json');
// JSON编辑器内容
const jsonContent = ref('{}');
// JSON验证状态
const isValidJson = ref(true);
// JSON错误信息
const jsonError = ref('');

// 监听props变化，初始化请求体内容
watch(() => props.requestBody, (newBody) => {
  if (newBody && Object.keys(newBody).length > 0) {
    // console.log('Body组件接收到新的请求体:', newBody);
    try {
      jsonContent.value = JSON.stringify(newBody, null, 2);
      isValidJson.value = true;
      jsonError.value = '';
    } catch (error) {
      console.error('请求体JSON序列化失败:', error);
      jsonContent.value = String(newBody);
    }
  }
}, { immediate: true });

// 监听内容类型变化
const onContentTypeChange = (type: string) => {
  // 更新内容类型
  emit('update:contentType', getContentTypeHeader(type));
};

// 根据类型获取对应的Content-Type头
const getContentTypeHeader = (type: string): string => {
  switch (type) {
    case 'json':
      return 'application/json';
    case 'form-data':
      return 'multipart/form-data';
    case 'x-www-form-urlencoded':
      return 'application/x-www-form-urlencoded';
    case 'raw':
      return 'text/plain';
    case 'binary':
      return 'application/octet-stream';
    default:
      return 'application/json';
  }
};

// 验证JSON格式
const validateJson = () => {
  if (!jsonContent.value.trim()) {
    isValidJson.value = true;
    jsonError.value = '';
    return;
  }

  try {
    JSON.parse(jsonContent.value);
    isValidJson.value = true;
    jsonError.value = '';
  } catch (error: any) {
    isValidJson.value = false;
    jsonError.value = error.message || '无效的JSON格式';
  }
};

// 格式化JSON
const formatJson = () => {
  try {
    const parsed = JSON.parse(jsonContent.value);
    jsonContent.value = JSON.stringify(parsed, null, 2);
    isValidJson.value = true;
    jsonError.value = '';
    ElMessage.success('JSON格式化成功');
  } catch (error: any) {
    ElMessage.error(`无法格式化：${error.message || '无效的JSON格式'}`);
  }
};

// 向父组件发送请求体更新
const emitBodyChange = () => {
  if (!isValidJson.value) {
    return;
  }
  
  try {
    const bodyData = jsonContent.value.trim() ? JSON.parse(jsonContent.value) : {};
    emit('update:body', bodyData);
  } catch (error) {
    console.error('解析JSON失败:', error);
  }
};

// 监听JSON内容变化
watch(jsonContent, validateJson, { immediate: true });

// 组件挂载时初始化
onMounted(() => {
  // 发送初始内容类型
  emit('update:contentType', getContentTypeHeader(contentType.value));
  
  // 验证初始JSON
  validateJson();
  
  // 发送初始请求体
  if (isValidJson.value && jsonContent.value.trim()) {
    try {
      const bodyData = JSON.parse(jsonContent.value);
      emit('update:body', bodyData);
    } catch (error) {
      console.error('解析初始JSON失败:', error);
    }
  }
});
</script>

<style scoped lang="scss">
.body-editor {
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  
  .content-type-selector {
    padding: 10px;
    background-color: #f5f7fa;
    border-bottom: 1px solid #dcdfe6;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .json-editor-container {
    padding: 10px;
    
    :deep(.el-textarea__inner) {
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
      font-size: 14px;
      line-height: 1.6;
      padding: 10px;
      min-height: 300px;
    }
    
    :deep(.el-textarea__inner.is-invalid) {
      border-color: #f56c6c;
    }
  }
  
  .json-error {
    margin-top: 10px;
  }
  
  .other-editor-placeholder {
    padding: 50px 0;
  }
  
  .right-actions {
    display: flex;
    gap: 10px;
  }
}
</style>