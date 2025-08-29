<template>
  <el-tabs type="border-card" class="demo-tabs">
    <el-tab-pane label="Header">
        <Header 
        :requestHeaders="requestHeaders"
        @update:headers="updateHeaders" />
    </el-tab-pane>
    <el-tab-pane label="Query">
      <Query :requestQuery="requestQuery" @update:querys="updateQuerys" />
    </el-tab-pane>
    <el-tab-pane label="Body">
      <Body :requestBody="requestBody" @update:body="updateBody" @update:contentType="updateContentType" />
    </el-tab-pane>
    <el-tab-pane label="前置处理器">
      <BeforeProcessor @update:beforeScript="updateBeforeScript" />
    </el-tab-pane>
    <el-tab-pane label="后置处理器">
      <AfterProcessor @update:afterScript="updateAfterScript" />
    </el-tab-pane>
    <el-tab-pane label="断言">
      <Assert @update:assert="updateAssert" />
    </el-tab-pane>
  </el-tabs>
</template>

<script lang="ts" setup>
// 引入自定义组件
import { ref, onMounted, watch } from 'vue';
import Header from './requestComponet/Header.vue'
import Query from './requestComponet/Query.vue'
import Body from './requestComponet/Body.vue'
import BeforeProcessor from './requestComponet/BeforeProcessor.vue'
import AfterProcessor from './requestComponet/AfterProcessor.vue'
import Assert from './requestComponet/Assert.vue'

import type { HeaderSourceItem, QuerySourceItem, ApiStepParams, CaseStep } from '@/api/case/caseStep/types';

// 定义接收的props
const props = defineProps<{
  stepParams?: CaseStep;
}>(); 

// 定义事件
const emit = defineEmits(['update:requestConfig']);

const requestBody = ref<any>({}) // 默认请求体
const requestHeaders = ref<Record<string, string>>({}) // 默认请求头
const requestQuery = ref<Record<string, string>>({}) // 默认请求查询参数

// 请求配置数据
const requestConfig = ref({
  headers: [] as HeaderSourceItem[],
  querys: [] as QuerySourceItem[],
  body: {},
  contentType: 'application/json',
  beforeScript: '',
  afterScript: ''
});

// 当接收到步骤参数时，初始化请求配置
onMounted(() => {
  if (props.stepParams) {
    initRequestConfig(props.stepParams);
  }
});

// 监听步骤参数变化
watch(() => props.stepParams, (newParams) => {
  if (newParams) {
    console.log('ParamCard接收到新的步骤参数:', newParams);
    initRequestConfig(newParams);
  }
}, { deep: true });

// 初始化请求配置
const initRequestConfig = (caseStep: CaseStep) => {
  // console.log('初始化请求配置，解析步骤数据:', caseStep);
  
  // CaseStep 对象包含 params 字段，它是 ApiStepParams 类型
  if (caseStep.params) {
    console.log('处理步骤参数:', caseStep.params);
    
    // 处理请求头 - 转换为Header组件期望的格式
    if (caseStep.params.header_source && Array.isArray(caseStep.params.header_source)) {
      // 转换ExtendedHeaderParam为Record<string, string>格式
      const headersObj: Record<string, string> = {};
      caseStep.params.header_source.forEach(header => {
        headersObj[header.name] = header.value;
      });
      requestHeaders.value = headersObj;
      console.log('设置headers为Record格式:', requestHeaders.value);
      console.log('requestHeaders.value的类型:', typeof requestHeaders.value);
      console.log('requestHeaders.value的keys:', Object.keys(requestHeaders.value));
    } else {
      console.log('没有header_source数据或格式不正确');
      // 设置为空对象，确保有默认值
      requestHeaders.value = {};
    }
    
    // 处理查询参数 - 转换为Query组件期望的格式
    if (caseStep.params.query_source && Array.isArray(caseStep.params.query_source)) {
      // 转换ExtendedQueryParam为Record<string, string>格式
      const queryObj: Record<string, string> = {};
      caseStep.params.query_source.forEach(query => {
        queryObj[query.name] = query.value;
      });
      requestQuery.value = queryObj;
      console.log('设置querys为Record格式:', requestQuery.value);
      console.log('requestQuery.value的类型:', typeof requestQuery.value);
      console.log('requestQuery.value的keys:', Object.keys(requestQuery.value));
    } else {
      console.log('没有query_source数据或格式不正确');
      // 设置为空对象，确保有默认值
      requestQuery.value = {};
    }
    
    // 处理请求体
    if (caseStep.params.body_source) {
      requestBody.value = caseStep.params.body_source;
      console.log('设置body:', caseStep.params.body_source);
      console.log('requestBody.value的类型:', typeof requestBody.value);
    } else {
      console.log('没有body_source数据');
      requestBody.value = {};
    }
    
    // 处理前置处理器脚本
    // 注意：before_script 可能不在 ApiStepParams 类型定义中，但实际数据可能有此字段
    if ('before_script' in caseStep.params) {
      // 使用类型断言访问可能不在类型定义中的字段
      const beforeScript = (caseStep.params as any).before_script;
      requestConfig.value.beforeScript = beforeScript;
      console.log('设置beforeScript:', beforeScript);
    }
    
    // 处理后置处理器脚本
    if ('after_script' in caseStep.params) {
      const afterScript = (caseStep.params as any).after_script;
      requestConfig.value.afterScript = afterScript;
      console.log('设置afterScript:', afterScript);
    }
  } else {
    console.warn('步骤参数中没有找到params字段:', caseStep);
  }
  
  // 通知子组件更新
  emitUpdate();
};

// 更新请求头
const updateHeaders = (headers: Record<string, string>) => {
  // 转换为API需要的格式
  requestConfig.value.headers = Object.entries(headers).map(([name, value], index) => ({
    id: Date.now() + index,
    name,
    value,
    type: { type: 'string', auto: true }
  }));
  
  emitUpdate();
};

// 更新查询参数
const updateQuerys = (querys: Record<string, string>) => {
  // 转换为API需要的格式
  requestConfig.value.querys = Object.entries(querys).map(([name, value], index) => ({
    id: Date.now() + index,
    name,
    value,
    type: { type: 'string', auto: false }
  }));
  
  emitUpdate();
};

// 更新请求体
const updateBody = (body: any) => {
  requestConfig.value.body = body;
  emitUpdate();
};

// 更新内容类型
const updateContentType = (contentType: string) => {
  requestConfig.value.contentType = contentType;
  emitUpdate();
};

// 更新前置处理器脚本
const updateBeforeScript = (script: string) => {
  requestConfig.value.beforeScript = script;
  emitUpdate();
};

// 更新后置处理器脚本
const updateAfterScript = (script: string) => {
  requestConfig.value.afterScript = script;
  emitUpdate();
};

// 更新断言
const updateAssert = (assert: string) => {
  alert("待更新")
};

// 向父组件发送更新
const emitUpdate = () => {
  emit('update:requestConfig', { ...requestConfig.value });
};

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
