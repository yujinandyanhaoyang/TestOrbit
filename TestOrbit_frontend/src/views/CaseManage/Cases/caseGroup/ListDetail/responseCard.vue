<template>
  <el-tabs type="border-card" class="demo-tabs">
    <el-tab-pane label="响应结果">
        <Response :responseData="responseData"/>
    </el-tab-pane>
    <el-tab-pane label="请求详情">
      <RequestMessage :requestData="requestData" />
    </el-tab-pane>
    <el-tab-pane label="控制台详情">
      <ConsoleDetail />
    </el-tab-pane>
    <el-tab-pane label="参数提取结果">
      <ParamExtract />
    </el-tab-pane>
  </el-tabs>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
// 引入自定义组件
import Response from './responseComponent/response.vue';
import RequestMessage from './responseComponent/requestMessage.vue';
import ConsoleDetail from './responseComponent/consoleDetail.vue';
import ParamExtract from './responseComponent/paramExtract.vue';

// 定义接收的props
const props = defineProps<{
  apiResponse?: {
    code: number;
    msg: string | null;
    results?: {
      message?: string;  // 添加message字段
      request_log?: {
        url: string;
        method: string;
        response: any;
        res_header: Record<string, string>;
        header: Record<string, string>;
        body: any;
        spend_time: number;
        results: any;
      }
    };
    success: boolean;
  }
}>();

// 计算响应数据，用于Response组件
const responseData = ref({
  status: 0,
  time: 0,
  size: 0,
  body: '',
  headers: {}
});

// 计算请求详情数据，用于RequestMessage组件
const requestData = ref({
  url: '',
  method: '',
  headers: {},
  body: {}
});

// 监听 apiResponse 变化，更新响应和请求数据
import { watch } from 'vue';

// 当props.apiResponse变化时更新组件数据
watch(() => props.apiResponse, (newValue) => {
  if (newValue) {

    const requestLog = newValue.results?.request_log;
    if (requestLog) {
      // 更新响应数据 - 修复状态码映射
      responseData.value = {
        status: requestLog.results ? (newValue.success ? 200 : 500) : 0, // 基于success状态判断
        time: (requestLog.spend_time || 0) * 1000, // 转换为毫秒
        size: JSON.stringify(newValue).length, // 计算完整响应的大小
        body: JSON.stringify(newValue, null, 2), // 🔥 显示完整的 apiResponse，格式化输出
        headers: requestLog.res_header || {}
      };
      
      // 更新请求数据
      requestData.value = {
        url: requestLog.url || '',
        method: requestLog.method || '',
        headers: requestLog.header || {},
        body: requestLog.body || {}
      };
      

    } else {
      // 如果没有request_log，也要尝试显示基础信息
      console.warn('⚠️ 没有找到request_log，使用基础响应信息');
      responseData.value = {
        status: newValue.success ? 200 : (newValue.code || 500),
        time: 0,
        size: JSON.stringify(newValue).length,
        body: JSON.stringify(newValue, null, 2), // 🔥 显示完整的 apiResponse
        headers: {}
      };
    }
  } else {
    // 清空数据
    responseData.value = {
      status: 0,
      time: 0,
      size: 0,
      body: '',
      headers: {}
    };
  }
}, { immediate: true });

</script>

<style>
.demo-tabs > .el-tabs__content {
  padding: 32px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}
.demo-tabs .custom-tabs-label .el-icon {
  vertical-align: middle;
}
.demo-tabs .custom-tabs-label span {
  vertical-align: middle;
  margin-left: 4px;
}
</style>
