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
        :stepId="props.stepParams?.id"
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

import type { HeaderSourceItem, QuerySourceItem, CaseStep, Rule, ApiStepParams } from '@/api/case/caseStep/types';

// 定义接收的props
const props = defineProps<{
  stepParams?: CaseStep;
}>(); 

// 定义事件
const emit = defineEmits(['newstep']);
const requestBody = ref<any>({}) // 默认请求体
const requestHeaders = ref<Record<string, string>>({}) // 默认请求头
const requestQuery = ref<Record<string, string>>({}) // 默认请求查询参数
const assertions = ref<Rule[]>([]) // 断言规则列表

// 监听步骤参数变化
watch(() => props.stepParams, (newParams) => {
  if (newParams) {
    console.log('ParamCard接收到新的步骤参数:', newParams);
    initRequestConfig(newParams);
  }
}, { deep: true });

// 请求配置数据
const stepParams = ref<CaseStep>({
  id: 0,
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

// 组件挂载时初始化
onMounted(() => {
  if (props.stepParams) {
    console.log('paramCard组件挂载时初始化stepParams:', props.stepParams);
    initRequestConfig(props.stepParams);
  }
});


// 初始化请求配置
const initRequestConfig = (caseStep: CaseStep) => {
  console.log('paramCard初始化请求配置，接收到的步骤数据:', caseStep);
  
  // 先将完整的CaseStep对象保存到本地状态
  stepParams.value = { ...caseStep };
  
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
    } else {
      console.log('没有query_source数据或格式不正确');
      // 设置为空对象，确保有默认值
      requestQuery.value = {};
    }
    
    // 处理请求体
    if (caseStep.params.body_source) {
      requestBody.value = caseStep.params.body_source;
      console.log('设置body:', caseStep.params.body_source);
    } else {
      console.log('没有body_source数据');
      requestBody.value = {};
    }
  } else {
    console.warn('步骤参数中没有找到params字段:', caseStep);
  }

  // 处理断言
  if (caseStep.assertions && Array.isArray(caseStep.assertions)) {
    assertions.value = caseStep.assertions;
    console.log('设置assertions.value:', assertions.value);
  } else {
    console.log('没有断言数据或格式不正确');
    assertions.value = [];
  }
};



// 更新请求头
const updateHeaders = (headers: Record<string, string>) => {
  if (!stepParams.value.params) {
    stepParams.value.params = {} as ApiStepParams;
  }
  
  // 转换为API需要的格式
  stepParams.value.params.header_source = Object.entries(headers).map(([name, value], index) => ({
    id: Date.now() + index,
    name,
    value,
    type: { type: 'string', auto: true }
  }));
  
  // 通知父组件
  emit('newstep', stepParams.value);
};

// 更新查询参数
const updateQuerys = (querys: Record<string, string>) => {
  if (!stepParams.value.params) {
    stepParams.value.params = {} as ApiStepParams;
  }
  
  // 转换为API需要的格式
  stepParams.value.params.query_source = Object.entries(querys).map(([name, value], index) => ({
    id: Date.now() + index,
    name,
    value,
    type: { type: 'string', auto: false }
  }));
  
  // 通知父组件
  emit('newstep', stepParams.value);
};

// 更新请求体
const updateBody = (body: any) => {
  if (!stepParams.value.params) {
    stepParams.value.params = {} as ApiStepParams;
  }
  
  stepParams.value.params.body_source = body;
  
  // 通知父组件
  emit('newstep', stepParams.value);
};

// 更新断言
const updateAssert = (assertRules: Rule[]) => {
  if (!stepParams.value) {
    stepParams.value = {} as CaseStep;
  }
  
  stepParams.value.assertions = assertRules;
  
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
