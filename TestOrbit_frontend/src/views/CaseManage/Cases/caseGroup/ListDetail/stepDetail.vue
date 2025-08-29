
<template>
    <div class="container" title="步骤名称">
        <!--顶部操作框(请求方式，请求地址，请求路径，运行按钮)-->
        <div class="top">
          <h2>步骤名称</h2>
              <el-input
                v-model="stepName"
                style="width: 240px"
                placeholder="请输入步骤名称"
                clearable
              />
          <h2>请求方式</h2>
            <el-select v-model="method" placeholder="Select" style="width: 240px">
                <el-option
                v-for="item in methodOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
                />
            </el-select>
            <h2>域名</h2>
              <el-input
                v-model="UrlInput"
                style="width: 240px"
                placeholder="Please input"
                clearable
              />
            <h2>路径</h2>
              <el-input
                v-model="address"
                style="width: 240px"
                placeholder="Please input"
                clearable
              />
            <el-button type="primary" @click="handleSave">保存</el-button>
            <el-button type="primary" @click="handleRun">运行</el-button>
        </div>
        <!--请求参数配置卡片(Headers, Query Params, Body（目前规定仅支持json）, 前置脚本，后置脚本)-->
        <div class="center">
          <ParamCard 
            :step-params="props.stepParams" 
            @update:requestConfig="updateRequestConfig" 
          />
        </div>
        <!--结果卡片（运行结果、控制台打印详情、请求详情、参数提取详情）-->
        <div class="bottom">
          <ResponseCard :apiResponse="apiResponse" />
        </div>

    </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import ParamCard from './paramCard.vue'
import ResponseCard from './responseCard.vue'
import { addCaseStep, runCaseStep } from '@/api/case/caseStep'
import type { CaseStep, AddCaseStepRequest, HttpMethod, ApiStepParams, HeaderSourceItem, QuerySourceItem } from '@/api/case/caseStep/types'

// 定义接收的props
const props = defineProps<{
  stepId?: number;
  stepName?: string;
  stepParams?: CaseStep;  // 改回 CaseStep，因为现在传递的是完整的 element 对象
}>();

// 定义emit事件
const emit = defineEmits<{
  (e: 'update:stepName', value: string): void;
  (e: 'stepSaved', id: number, data: any): void;
}>();

// 基本信息 - 使用props的值或默认值
const stepName = ref<string>(props.stepName || '新建步骤')

// 监听props变化，更新内部状态
watch(
  () => props.stepName,
  (newStepName) => {
    if (newStepName && newStepName !== stepName.value) {
      stepName.value = newStepName;
    }
  }
);

// 定义步骤参数，基于props或默认值
const address = ref<string>('') // 默认路径
const UrlInput = ref<string>('') // 默认主机名
const method = ref<HttpMethod>() // 默认HTTP方法
const requestBody = ref<any>({}) // 默认请求体
const requestHeaders = ref<any>({}) // 默认请求头
const requestQuery = ref<any>({}) // 默认请求查询参数

// 请求参数配置
const requestConfig = ref<{
  headers: HeaderSourceItem[];
  querys: QuerySourceItem[];
  body: any;
  contentType: string;
  beforeScript: string;
  afterScript: string;
}>({
  headers: [],
  querys: [],
  body: {},
  contentType: 'application/json',
  beforeScript: '',
  afterScript: ''
});

// 如果有传入的步骤参数，则初始化
if (props.stepParams) {
  // console.log('StepDetail接收到的参数-params:', props.stepParams.params);
  
  // 现在stepParams是完整的CaseStep对象，通过.params访问ApiStepParams
  if (props.stepParams.params) {
    // console.log('开始初始化参数...');
    
    // 更新主机地址
    if (props.stepParams.params.host) {
      UrlInput.value = props.stepParams.params.host;
    }
    
    // 更新路径
    if (props.stepParams.params.path) {
      address.value = props.stepParams.params.path;
    }
    
    // 更新请求方法
    if (props.stepParams.params.method) {
      method.value = props.stepParams.params.method;
    }

  } else {
    console.warn('CaseStep对象中没有params属性！');
  }
}

// 监听stepParams变化，更新参数
watch(() => props.stepParams, (newParams) => {
  // console.log('StepDetail接收到新的stepParams:', newParams);
  
  if (newParams) {
    
    // 通过.params访问ApiStepParams的属性
    if (newParams.params) {
      // 更新主机
      UrlInput.value = newParams.params.host || '';
      
      // 更新路径
      address.value = newParams.params.path || '';
      
      // 更新请求方法  
      method.value = newParams.params.method as HttpMethod;
      
    } else {
      console.warn('CaseStep对象中没有params属性！');
    }
  } else {
    console.log('没有接收到stepParams参数');
  }
}, { deep: true, immediate: true });

// API 响应数据
const apiResponse = ref({
  code: 0,
  msg: null,
  results: {
    request_log: {
      url: '',
      method: '',
      response: null,
      res_header: {},
      header: {},
      body: {},
      spend_time: 0,
      results: null
    }
  },
  success: false
})

// 项目ID，可以从步骤参数中获取或使用默认值
const projectId = ref<number>(6) // 默认值，代表本地项目

const methodOptions = [
  {
    value: 'POST',
    label: 'POST',
  },
  {
    value: 'GET',
    label: 'GET',
  },
  {
    value: 'DELETE',
    label: 'DELETE',
  },
  {
    value: 'PUT',
    label: 'PUT',
  },
  {
    value: 'PATCH',
    label: 'PATCH',
  },
]

// 更新请求配置
const updateRequestConfig = (config: any) => {
  requestConfig.value = config
}

// 保存步骤
const handleSave = async () => {
  try {
    // 检验必要数据
    if (!stepName.value.trim()) {
      ElMessage.warning('请输入步骤名称')
      return
    }
    
    if (!method.value) {
      ElMessage.warning('请选择请求方法')
      return
    }
    
    if (!UrlInput.value.trim()) {
      ElMessage.warning('请输入域名')
      return
    }
    
    // 构建请求参数
    const requestData: AddCaseStepRequest = {
      step_name: stepName.value,
      name: stepName.value,
      env_id: projectId.value,
      method: method.value,
      host: UrlInput.value.trim(),
      host_type: 1, // 默认值，根据实际情况调整
      path: address.value,
      ban_redirects: false, // 默认允许重定向
      header_mode: 1, // 默认值，根据实际情况调整
      header_source: requestConfig.value.headers,
      query_mode: 1, // 默认值，根据实际情况调整
      query_source: requestConfig.value.querys,
      body_mode: 2, // JSON格式
      body_source: {
        name: "请求体",
        id: 2
      },
      expect_mode: 1, // 默认值
      expect_source: [],
      output_mode: 1, // 默认值
      output_source: [],
      is_case: true, // 是测试用例步骤
      // 添加id字段：如果有stepId且不是新建步骤，则包含id字段（表示更新操作）
      ...(props.stepId && props.stepId > 0 ? { id: props.stepId } : {})
    }
    
    console.log('保存步骤请求参数:', requestData)
    
    // 发送保存请求
    const res = await addCaseStep(requestData)
    
    if (res?.code === 200) {
      ElMessage.success('保存成功')
      console.log('保存步骤响应:', res)
      
      // 获取返回的api_id，这将作为步骤的新ID
      const newStepId = res.results?.api_id || props.stepId;
      const isNewStep = !props.stepId || props.stepId <= 0;
      
      console.log(`步骤保存成功 - ${isNewStep ? '新建' : '更新'} - API ID: ${newStepId}`);
      
      // 构建步骤数据
      const stepData = {
        id: newStepId, // 使用返回的api_id作为步骤ID
        params: {
          host: UrlInput.value,
          name: stepName.value,
          path: address.value,
          api_id: newStepId, // 同时设置params中的api_id
          method: method.value,
          body_mode: requestData.body_mode,
          host_type: requestData.host_type,
          query_mode: requestData.query_mode,
          body_source: requestConfig.value.body || {},
          expect_mode: requestData.expect_mode,
          header_mode: requestData.header_mode,
          output_mode: requestData.output_mode,
          query_source: requestConfig.value.querys,
          ban_redirects: requestData.ban_redirects,
          expect_source: requestData.expect_source,
          header_source: requestConfig.value.headers,
          output_source: requestData.output_source
        },
        step_name: stepName.value,
        type: "api",
        status: 4,
        enabled: true,
        controller_data: null,
        retried_times: 0,
        results: null
      };
      
      // 通知父组件步骤名称已更新
      emit('update:stepName', stepName.value);
      
      // 通知父组件步骤已保存，并传递完整的步骤数据
      // 使用新的步骤ID（api_id）
      emit('stepSaved', newStepId, stepData);
    } else {
      ElMessage.error(`保存失败: ${res?.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('保存步骤错误:', error)
    ElMessage.error(`保存步骤错误: ${(error as Error).message || '未知错误'}`)
  }
}

// 运行测试
const handleRun = async () => {
  try {
    // 检验必要数据
    if (!stepName.value.trim()) {
      ElMessage.warning('请输入步骤名称')
      return
    }
    
    if (!method.value) {
      ElMessage.warning('请选择请求方法')
      return
    }
    
    if (!UrlInput.value.trim()) {
      ElMessage.warning('请输入域名')
      return
    }
    
    // 构建请求参数 - 严格按照后端API格式调整
    const paramsData = {
      step_name: stepName.value,
      name: stepName.value,
      env_id: projectId.value,
      method: method.value,
      timeout: null, // 根据示例添加
      host: UrlInput.value.trim(),
      host_type: 1,
      path: address.value,
      ban_redirects: false,
      header_mode: 1,
      header_source: requestConfig.value.headers,
      query_mode: 1,
      query_source: requestConfig.value.querys,
      body_mode: 2,
      // 根据示例，body_source是一个对象，而不是接口定义中的BodySourceItem
      body_source: requestConfig.value.body && Object.keys(requestConfig.value.body).length > 0 
        ? requestConfig.value.body 
        : requestBody.value,
      expect_mode: 1,
      expect_source: [],
      output_mode: 1,
      output_source: []
      // 注意：移除了is_case，因为示例中没有这个字段
    }
    
    // 构建最终请求结构 - 包含params和外层step_name
    const requestData = {
      params: paramsData,
      step_name: stepName.value
    }
    
    // 发送运行请求
    const res = await runCaseStep(requestData)
    
    if (res?.code === 200) {
      ElMessage.success('运行成功')
      // console.log('运行步骤响应:', res)
      
      // 直接将API响应结果赋值给apiResponse
      apiResponse.value = res;
    } else {
      ElMessage.error(`运行失败: ${res?.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('运行步骤错误:', error)
    ElMessage.error(`运行步骤错误: ${(error as Error).message || '未知错误'}`)
  }
}


</script>

<style scoped lang="scss">
.container {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 600px;
    background-color: #f5f7fa;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    
    .top {
        display: flex;
        align-items: center;
        padding: 15px;
        background-color: #fff;
        border-bottom: 1px solid #ebeef5;
        flex-wrap: wrap;
        gap: 10px;
        
        h2 {
            font-size: 14px;
            color: #606266;
            margin: 0 5px 0 15px;
        }
        
        .el-button {
            margin-left: auto;
        }
        
        .el-button + .el-button {
            margin-left: 10px;
        }
    }
    
    .center {
        flex: 1;
        padding: 15px;
        background-color: #fff;
        margin: 15px;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04);
    }
    
    .bottom {
        flex: 1;
        padding: 15px;
        background-color: #fff;
        margin: 0 15px 15px;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04);
    }
}
</style>