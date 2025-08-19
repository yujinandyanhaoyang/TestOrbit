
<template>
  <div class="request-message">
    <div v-if="hasRequestData" class="request-details">
      <!-- 请求URL和方法 -->
      <div class="section url-method">
        <div class="method-label" :class="methodClass">{{ request.method }}</div>
        <div class="url">{{ request.url }}</div>
      </div>
      
      <!-- 请求头 -->
      <div class="section headers">
        <h3>请求头</h3>
        <el-table v-if="headersArray.length > 0" :data="headersArray" stripe style="width: 100%">
          <el-table-column prop="name" label="名称" width="180" />
          <el-table-column prop="value" label="值" />
        </el-table>
        <div v-else class="empty-message">无请求头信息</div>
      </div>
      
      <!-- 请求体 -->
      <div class="section body">
        <h3>请求体</h3>
        <div v-if="hasBody" class="body-content">
          <el-tabs v-model="bodyViewMode">
            <el-tab-pane label="格式化" name="formatted">
              <pre>{{ formattedBody }}</pre>
            </el-tab-pane>
            <el-tab-pane label="原始数据" name="raw">
              <pre>{{ rawBody }}</pre>
            </el-tab-pane>
          </el-tabs>
        </div>
        <div v-else class="empty-message">无请求体信息</div>
      </div>
    </div>
    
    <div v-else class="no-data">
      <el-empty description="暂无请求数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed  } from 'vue';

// 定义请求数据接口
interface RequestData {
  url: string;
  method: string;
  headers: Record<string, string>;
  body: any;
}

// 定义组件属性
const props = defineProps<{
  requestData?: RequestData;
}>();

// 请求体查看模式
const bodyViewMode = ref('formatted');

// 请求数据
const request = computed(() => {
  return props.requestData || {
    url: '',
    method: '',
    headers: {},
    body: {}
  };
});

// 是否有请求数据
const hasRequestData = computed(() => {
  return !!props.requestData && !!props.requestData.url;
});

// 请求头转换为数组格式
const headersArray = computed(() => {
  const headers = request.value.headers || {};
  return Object.entries(headers).map(([name, value]) => {
    return { name, value };
  });
});

// 请求体格式化
const formattedBody = computed(() => {
  const body = request.value.body;
  if (!body) return '';
  
  try {
    if (typeof body === 'string') {
      // 尝试解析JSON字符串
      const parsed = JSON.parse(body);
      return JSON.stringify(parsed, null, 2);
    } else {
      // 直接格式化对象
      return JSON.stringify(body, null, 2);
    }
  } catch (error) {
    return typeof body === 'string' ? body : JSON.stringify(body);
  }
});

// 原始请求体
const rawBody = computed(() => {
  const body = request.value.body;
  if (!body) return '';
  return typeof body === 'string' ? body : JSON.stringify(body);
});

// 是否有请求体
const hasBody = computed(() => {
  const body = request.value.body;
  return body && (typeof body === 'string' ? body.length > 0 : Object.keys(body).length > 0);
});

// 请求方法对应的样式类
const methodClass = computed(() => {
  const method = request.value.method.toLowerCase();
  return {
    'get': 'method-get',
    'post': 'method-post',
    'put': 'method-put',
    'delete': 'method-delete',
    'patch': 'method-patch'
  }[method] || 'method-other';
});
</script>

<style scoped lang="scss">
.request-message {
  width: 100%;
  
  .section {
    margin-bottom: 20px;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    padding: 16px;
    background-color: #fff;
    
    h3 {
      margin-top: 0;
      margin-bottom: 16px;
      font-size: 16px;
      color: #303133;
    }
  }
  
  .url-method {
    display: flex;
    align-items: center;
    
    .method-label {
      padding: 4px 8px;
      border-radius: 4px;
      font-weight: bold;
      color: white;
      margin-right: 10px;
      
      &.method-get {
        background-color: #67c23a;
      }
      
      &.method-post {
        background-color: #409eff;
      }
      
      &.method-put {
        background-color: #e6a23c;
      }
      
      &.method-delete {
        background-color: #f56c6c;
      }
      
      &.method-patch {
        background-color: #909399;
      }
      
      &.method-other {
        background-color: #909399;
      }
    }
    
    .url {
      flex: 1;
      word-break: break-all;
      font-family: monospace;
    }
  }
  
  .body-content {
    pre {
      margin: 0;
      padding: 10px;
      background-color: #f5f7fa;
      border-radius: 4px;
      white-space: pre-wrap;
      word-wrap: break-word;
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
      font-size: 14px;
      line-height: 1.5;
      color: #333;
    }
  }
  
  .empty-message {
    color: #909399;
    font-style: italic;
    padding: 10px 0;
  }
  
  .no-data {
    padding: 40px 0;
  }
}
</style>