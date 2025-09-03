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
      <BeforeProcessor/>
    </el-tab-pane>
    <el-tab-pane label="后置处理器">
      <AfterProcessor />
    </el-tab-pane>
    <el-tab-pane label="断言">
      <Assert 
        :stepId="props.stepParams?.step_id"
        :initialAssertions="assertions"
        @update:assert="updateAssert" />
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

import type {  CaseStep, Rule, ApiStepParams } from '@/api/case/caseStep/types';

// 定义接收的props
const props = defineProps<{
  stepParams?: CaseStep;
}>(); 

// 定义事件
const emit = defineEmits(['newstep']);

// 初始化状态标志，防止初始化期间触发不必要的emit
const isInitializing = ref(false);
const requestBody = ref<any>({}) // 默认请求体
const requestHeaders = ref<Record<string, string>>({}) // 默认请求头
const requestQuery = ref<Record<string, string>>({}) // 默认请求查询参数
const assertions = ref<Rule[]>([]) // 断言规则列表

// 请求配置数据
const stepParams = ref<CaseStep>({
  step_id: 0,
  step_name: '',
  step_order: 0,
  type: 'api',
  enabled: true,
  status: 0,
  controller_data: null,
  retried_times: null,
  results: {
    message: null,
    request_log: {
      url: '',
      body: {},
      header: {},
      method: '',
      results: null,
      response: null,
      res_header: {},
      spend_time: 0
    }
  },
  params: {
    host: '',
    path: '',
    method: 'GET',
    timeout: 30000,
    body_mode: 0,
    host_type: 0,
    query_mode: 0,
    body_source: {},
    expect_mode: 0,
    header_mode: 0,
    output_mode: 0,
    query_source: [],
    ban_redirects: false,
    expect_source: [],
    header_source: [],
    output_source: []
  },
  timeout: null,
  source: null,
  assertions: []
});

// 监听步骤参数变化，统一处理初始化
watch(() => props.stepParams, (newParams, oldParams) => {
  if (newParams) {
    // 只有当步骤ID真正变化时才初始化，避免无意义的重复初始化
    const newStepId = newParams.step_id || (newParams as any).id || 0;
    const oldStepId = oldParams?.step_id || (oldParams as any)?.id || 0;
    
    if (newStepId !== oldStepId) {
      // 
      initRequestConfig(newParams);
    } else {

    }
  }
}, { deep: true }); // 移除 immediate: true

// 组件挂载时手动处理初始化
onMounted(() => {
  if (props.stepParams) {
    // 
    initRequestConfig(props.stepParams);
  }
});


// 初始化请求配置
const initRequestConfig = (caseStep: CaseStep) => {
  // 
  
  // 🔥 设置初始化标志，防止初始化期间的emit事件
  isInitializing.value = true;
  
  // 🔥 关键修复：兼容处理id和step_id字段，确保正确获取步骤ID
  const actualStepId = caseStep.step_id || (caseStep as any).id || 0;
  // 
  
  // 🔥 优先设置stepParams的基础信息，特别是step_id
  stepParams.value = { 
    ...caseStep,
    step_id: actualStepId  // 🔥 确保step_id字段正确设置
  };
  
  // 
  
  // CaseStep 对象包含 params 字段，它是 ApiStepParams 类型
  if (caseStep.params) {
    // 

    // 🔥 修复：确保step_id正确设置（冗余但确保安全）
    stepParams.value.step_id = actualStepId;
    // 

    // 处理请求头 - 从ExtendedHeaderParam[]转换为Record<string, string>格式
    if (caseStep.params.header_source && Array.isArray(caseStep.params.header_source)) {
      const headersObj: Record<string, string> = {};
      caseStep.params.header_source.forEach(header => {
        if (header.name && header.name.trim() !== '') {
          headersObj[header.name] = header.value || '';
        }
      });
      requestHeaders.value = headersObj;
      // 
    } else {

      requestHeaders.value = {};
    }
    
    // 处理查询参数 - 从ExtendedQueryParam[]转换为Record<string, string>格式
    if (caseStep.params.query_source && Array.isArray(caseStep.params.query_source)) {
      const queryObj: Record<string, string> = {};
      caseStep.params.query_source.forEach(query => {
        if (query.name && query.name.trim() !== '') {
          queryObj[query.name] = query.value || '';
        }
      });
      requestQuery.value = queryObj;
      // 
    } else {

      requestQuery.value = {};
    }
    
    // 处理请求体 - 直接使用body_source
    if (caseStep.params.body_source !== undefined) {
      requestBody.value = caseStep.params.body_source;
      // 
    } else {

      requestBody.value = {};
    }
  } else {
    // console.warn('步骤参数中没有找到params字段:', caseStep);
    // 设置默认值
    requestHeaders.value = {};
    requestQuery.value = {};
    requestBody.value = {};
  }

  // 处理断言
  if (caseStep.assertions && Array.isArray(caseStep.assertions)) {
    assertions.value = caseStep.assertions;
    // 
  } else {

    assertions.value = [];
  }
  
  // 🔥 关键：延迟重置初始化标志，确保所有子组件都完成了初始化
  // 对于新步骤（负数ID），给更多时间确保完全初始化
  const delay = actualStepId < 0 ? 200 : 100;
  setTimeout(() => {
    isInitializing.value = false;
    // 
  }, delay);
};



// 更新请求头
const updateHeaders = (headers: Record<string, string>) => {
  if (isInitializing.value) {
    // 
    return;
  }
  
  if (!stepParams.value.params) {
    stepParams.value.params = {} as ApiStepParams;
  }
  
  // 转换为API需要的ExtendedHeaderParam[]格式
  stepParams.value.params.header_source = Object.entries(headers)
    .filter(([name, value]) => name.trim() !== '') // 过滤空的键名
    .map(([name, value]) => ({
      name: name.trim(),
      value: value || '',
      type: { type: 'string' }
    }));
  
  // 同步更新本地状态，确保双向绑定
  requestHeaders.value = { ...headers };
  
  // 
  
  // 通知父组件
  emit('newstep', stepParams.value);
};

// 更新查询参数
const updateQuerys = (querys: Record<string, string>) => {
  if (isInitializing.value) {
    // 
    return;
  }
  
  if (!stepParams.value.params) {
    stepParams.value.params = {} as ApiStepParams;
  }
  
  // 转换为API需要的ExtendedQueryParam[]格式
  stepParams.value.params.query_source = Object.entries(querys)
    .filter(([name, value]) => name.trim() !== '') // 过滤空的键名
    .map(([name, value]) => ({
      name: name.trim(),
      value: value || '',
      type: { type: 'string' }
    }));
  
  // 同步更新本地状态，确保双向绑定
  requestQuery.value = { ...querys };
  
  // 
  
  // 通知父组件
  emit('newstep', stepParams.value);
};

// 更新请求体
const updateBody = (body: any) => {
  if (isInitializing.value) {

    return;
  }
  
  if (!stepParams.value.params) {
    stepParams.value.params = {} as ApiStepParams;
  }
  
  // 直接保存body数据
  stepParams.value.params.body_source = body;
  
  // 同步更新本地状态，确保双向绑定
  requestBody.value = body;
  
  // 
  
  // 通知父组件
  emit('newstep', stepParams.value);
};

// 更新Content-Type（Body组件可能需要）
const updateContentType = (contentType: string) => {
  if (isInitializing.value) {
    // 
    return;
  }
  
  if (!stepParams.value.params) {
    stepParams.value.params = {} as ApiStepParams;
  }
  
  // 更新Content-Type到header_source中
  if (!stepParams.value.params.header_source) {
    stepParams.value.params.header_source = [];
  }
  
  // 查找是否已存在Content-Type
  const existingIndex = stepParams.value.params.header_source.findIndex(
    header => header.name.toLowerCase() === 'content-type'
  );
  
  if (existingIndex >= 0) {
    // 更新现有的Content-Type
    stepParams.value.params.header_source[existingIndex].value = contentType;
  } else {
    // 添加新的Content-Type
    stepParams.value.params.header_source.push({
      name: 'Content-Type',
      value: contentType,
      type: { type: 'string' }
    });
  }
  
  // 同步更新requestHeaders
  requestHeaders.value = {
    ...requestHeaders.value,
    'Content-Type': contentType
  };
  
  // 
  
  // 通知父组件
  emit('newstep', stepParams.value);
};

// 更新断言
const updateAssert = (assertRules: any[]) => {
  if (isInitializing.value) {
    // 
    return;
  }
  
  if (!stepParams.value) {
    stepParams.value = {} as CaseStep;
  }
  
  // 处理断言数据：区分现有断言和新增断言
  const processedAssertions = assertRules.map((rule, index) => {
    const now = new Date().toISOString();
    
    // 如果是新增的断言（没有id或id为负数/0）
    if (!rule.id || rule.id <= 0) {
      // 🔥 关键修复：新增断言不包含id字段，让服务器分配

      const newAssertion = {
        // ❌ 不设置id字段，让服务器分配
        type: rule.type || 'jsonpath',
        expression: rule.expression,
        operator: rule.operator,
        expected_value: rule.expected_value,
        created: now,
        updated: now,
        enabled: rule.enabled !== undefined ? rule.enabled : true,
        step: props.stepParams?.step_id || stepParams.value.step_id || 0,
        display_text: `${rule.expression} ${rule.operator} ${rule.expected_value}`
      };
      return newAssertion;
    } else {
      // 现有断言，保持原有结构，只更新修改时间

      return {
        ...rule,
        updated: now,
        step: props.stepParams?.step_id || stepParams.value.step_id || 0
      } as Rule;
    }
  });
  
  stepParams.value.assertions = processedAssertions as any; // 类型断言：新增断言没有id字段
  
  // 同步更新本地状态，确保双向绑定
  assertions.value = [...processedAssertions] as any; // 类型断言：新增断言没有id字段
  

  
  // 通知父组件
  emit('newstep', stepParams.value);
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
