
<template>
  <div class="response-viewer">
    <!-- 响应状态信息栏 -->
    <div class="response-status" :class="{ 'success': isSuccess, 'error': !isSuccess }">
      <div class="status-code">
        <span class="label">状态：</span>
        <span class="value">{{ response.status || '-' }}</span>
      </div>
      <div class="time-taken">
        <span class="label">响应时间：</span>
        <span class="value">{{ response.time || '-' }} ms</span>
      </div>
      <div class="size">
        <span class="label">大小：</span>
        <span class="value">{{ formatSize(response.size) || '-' }}</span>
      </div>
    </div>
    
    <!-- 响应内容选项卡 -->
    <el-tabs v-model="activeTab" class="response-tabs">
      <el-tab-pane label="Body" name="body">
        <!-- 响应体格式化选择器 -->
        <div class="format-selector">
          <el-radio-group v-model="bodyFormat" size="small">
            <el-radio-button label="json">格式化</el-radio-button>
            <el-radio-button label="raw">原始数据</el-radio-button>
          </el-radio-group>
          
          <el-button 
            v-if="bodyFormat === 'json'" 
            type="primary" 
            size="small" 
            plain 
            @click="copyToClipboard"
          >
            复制
          </el-button>
        </div>
        
        <!-- JSON格式响应体 -->
        <div v-if="bodyFormat === 'json'" class="json-viewer">
          <pre v-if="isValidJson">{{ formattedJson }}</pre>
          <div v-else class="json-error">
            <el-alert
              title="无法解析为JSON格式"
              type="warning"
              :closable="false"
              description='响应内容不是有效的JSON格式，请使用"原始数据"视图查看。'
              show-icon
            />
          </div>
        </div>
        
        <!-- 原始响应体 -->
        <div v-else class="raw-viewer">
          <pre>{{ response.body || '无响应数据' }}</pre>
        </div>
      </el-tab-pane>
      
    </el-tabs>
    
    <!-- 无数据状态 -->
    <div v-if="!hasResponse" class="no-response">
      <el-empty description="暂无请求响应数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineProps } from 'vue';
import { ElMessage } from 'element-plus';

// 定义响应数据接口
interface ResponseHeader {
  name: string;
  value: string;
}

interface ResponseData {
  status: number;
  time: number;
  size: number;
  body: string;
  headers: Record<string, string>;
}

// 定义组件属性
const props = defineProps<{
  responseData?: ResponseData;
}>();

// 标签页激活状态
const activeTab = ref('body');
// 响应体显示格式
const bodyFormat = ref('json');

// 响应数据
const response = computed(() => {
  return props.responseData || {
    status: 0,
    time: 0,
    size: 0,
    body: '',
    headers: {},
  };
});

// 判断是否有响应数据
const hasResponse = computed(() => {
  return !!props.responseData;
});

// 判断响应是否成功
const isSuccess = computed(() => {
  const status = response.value.status;
  return status >= 200 && status < 300;
});

// 格式化响应体为JSON
const formattedJson = computed(() => {
  if (!response.value.body) {
    return '';
  }
  
  try {
    const parsed = JSON.parse(response.value.body);
    return JSON.stringify(parsed, null, 2);
  } catch (error) {
    return '';
  }
});

// 判断响应体是否为有效的JSON
const isValidJson = computed(() => {
  if (!response.value.body) {
    return false;
  }
  
  try {
    JSON.parse(response.value.body);
    return true;
  } catch (error) {
    return false;
  }
});

// 将响应头转换为数组格式
const headersArray = computed(() => {
  const headers = response.value.headers || {};
  return Object.entries(headers).map(([name, value]) => {
    return { name, value };
  });
});

// 格式化数据大小
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  if (!bytes) return '-';
  
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 复制JSON到剪贴板
const copyToClipboard = async () => {
  if (!formattedJson.value) {
    ElMessage.warning('没有可复制的内容');
    return;
  }
  
  try {
    await navigator.clipboard.writeText(formattedJson.value);
    ElMessage.success('已复制到剪贴板');
  } catch (error) {
    console.error('复制失败:', error);
    ElMessage.error('复制失败');
  }
};

// 提供测试数据（仅用于演示）
// 实际使用时，数据应当通过props传入
if (import.meta.env.DEV && !props.responseData) {
  // 在开发环境下，如果没有提供响应数据，则使用示例数据
  const mockResponse: ResponseData = {
    status: 200,
    time: 354,
    size: 1234,
    body: JSON.stringify({
      code: 0,
      message: "操作成功",
      data: {
        id: 1001,
        name: "测试用例",
        createdAt: "2025-08-17T09:30:00.000Z"
      }
    }),
    headers: {
      "Content-Type": "application/json",
      "X-Request-ID": "abcdef123456",
      "Cache-Control": "no-cache"
    }
  };
  
  // @ts-ignore - 忽略只读属性的设置
  props.responseData = mockResponse;
}
</script>

<style scoped lang="scss">
.response-viewer {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  background-color: #fff;
  height: 100%;
  display: flex;
  flex-direction: column;
  
  .response-status {
    display: flex;
    padding: 12px 16px;
    background-color: #f5f7fa;
    border-bottom: 1px solid #dcdfe6;
    
    &.success {
      background-color: #f0f9eb;
      border-color: #e1f3d8;
    }
    
    &.error {
      background-color: #fef0f0;
      border-color: #fde2e2;
    }
    
    .status-code, .time-taken, .size {
      margin-right: 24px;
      
      .label {
        font-weight: bold;
        color: #606266;
      }
      
      .value {
        margin-left: 5px;
      }
    }
    
    .status-code .value {
      font-weight: bold;
    }
  }
  
  .response-tabs {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: calc(100% - 40px);
    
    :deep(.el-tabs__content) {
      flex: 1;
      overflow: auto;
      padding: 16px;
    }
  }
  
  .format-selector {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
  }
  
  .json-viewer, .raw-viewer {
    border: 1px solid #dcdfe6;
    border-radius: 4px;
    background-color: #f5f7fa;
    min-height: 200px;
    padding: 12px;
    overflow: auto;
    max-height: 500px;
    
    pre {
      margin: 0;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
      font-size: 14px;
      line-height: 1.5;
    }
  }
  
  .json-viewer pre {
    color: #333;
  }
  
  .no-response {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
  }
  
  .json-error {
    margin-bottom: 12px;
  }
}
</style>