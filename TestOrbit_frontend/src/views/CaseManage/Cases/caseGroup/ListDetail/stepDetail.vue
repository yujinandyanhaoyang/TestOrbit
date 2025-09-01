
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
            :stepParams="props.stepParams" 
            @newstep="updateRequestConfig" 
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
import type { CaseStep, AddCaseStepRequest, HttpMethod, HeaderSourceItem, QuerySourceItem, Rule } from '@/api/case/caseStep/types'

// 定义接收的props
const props = defineProps<{
  stepId?: number;
  stepName?: string;
  stepParams?: CaseStep;  // 改回 CaseStep，因为现在传递的是完整的 element 对象
  newstepParams?: CaseStep; // paramsCard提供的更新后的参数信息
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
const step = ref<CaseStep>() // 步骤参数

// 创建默认step对象的函数
const createDefaultStep = (): CaseStep => {
  return {
    step_id: 0,  // 使用step_id而不是id
    step_name: stepName.value || '新建步骤',
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
      host: UrlInput.value || '',
      path: address.value || '/',
      method: method.value || 'GET',
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
  };
}

// 初始化step对象（确保在组件创建时就有完整的step对象）
if (!step.value) {
  step.value = createDefaultStep();
}

// 请求参数配置
const requestConfig = ref<AddCaseStepRequest>({
  case_id: 0, // 初始化为不存在数据
  env_id: 0, // 初始化为不存在数据
  steps: []
})


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

      // 更新步骤参数，确保使用正确的ID字段
      step.value = {
        ...newParams,
        step_id: newParams.step_id || (newParams as any).id || 0
      };
      
      // 删除可能存在的多余id字段
      delete (step.value as any).id;
      
    } else {
      console.warn('CaseStep对象中没有params属性！');
    }
  } else {
    console.log('没有接收到stepParams参数');
  }
}, { deep: true, immediate: true });

// 监听页面输入框变化，实时同步到step对象
watch([stepName, UrlInput, address, method], () => {
  if (step.value && step.value.params) {
    // 实时同步页面输入框的值到step对象
    step.value.step_name = stepName.value.trim();
    step.value.params.host = UrlInput.value.trim();
    step.value.params.path = address.value.trim() || '/';
    if (method.value) {
      step.value.params.method = method.value;
    }
    
    // 更新请求配置中的steps（保持同步）
    requestConfig.value.steps = [step.value];
  }
});

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
const updateRequestConfig = (config: CaseStep) => {
  // console.log('stepDetail收到子组件paramCard更新的配置:', config);
  
  // 深度合并配置，确保不丢失任何数据
  if (step.value) {
    // 如果step已存在，合并新配置
    step.value = {
      ...step.value,
      ...config,
      // 确保使用正确的ID字段
      step_id: step.value.step_id || config.step_id || (config as any).id || 0,
      // 确保params正确合并
      params: {
        ...step.value.params,
        ...config.params,
        // 保持界面输入框的值优先级更高
        host: UrlInput.value.trim() || config.params?.host || step.value.params?.host || '',
        path: address.value.trim() || config.params?.path || step.value.params?.path || '/',
        method: method.value || config.params?.method || step.value.params?.method || 'GET'
      }
    };
    
    // 删除可能存在的多余id字段
    delete (step.value as any).id;
  } else {
    // 如果step不存在，直接使用配置并补充界面数据
    step.value = {
      ...config,
      // 确保使用正确的ID字段
      step_id: config.step_id || (config as any).id || 0,
      params: {
        ...config.params,
        host: UrlInput.value.trim() || config.params?.host || '',
        path: address.value.trim() || config.params?.path || '/',
        method: method.value || config.params?.method || 'GET'
      }
    };
    
    // 删除可能存在的多余id字段
    delete (step.value as any).id;
  }
  
  // 更新请求配置中的steps（保持同步）
  requestConfig.value.steps = [step.value];
  
  // console.log('更新后的完整step对象:', step.value);
  // console.log('更新后的请求配置:', requestConfig.value);
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

    // 检查step对象和params的完整性
    if (!step.value || !step.value.params) {
      ElMessage.warning('步骤信息不完整，请检查参数配置')
      console.error('step.value 或 step.value.params 不存在:', step.value)
      return
    }

    // 更新步骤基本信息（从页面输入框获取）
    step.value.step_name = stepName.value.trim();
    step.value.params.host = UrlInput.value.trim();
    step.value.params.path = address.value.trim() || '/';
    step.value.params.method = method.value;

    // console.log('保存前的完整step对象:', JSON.stringify(step.value, null, 2));

    // 设置请求参数
    requestConfig.value.case_id = 23 // 暂时固定
    requestConfig.value.env_id = 1 // 暂时固定
    requestConfig.value.steps = [step.value]
    
    console.log('保存步骤请求参数:', JSON.stringify(requestConfig.value, null, 2))

    // 发送保存请求
    const res = await addCaseStep(requestConfig.value)
    
    if (res?.code === 200) {
      ElMessage.success('保存成功')
      console.log('保存步骤响应:', res)
      
      // 通知父组件步骤名称已更新
      emit('update:stepName', stepName.value);
      
      // 如果返回了步骤ID，更新本地step对象
      if (res.data && res.data.step_id) {
        step.value.step_id = res.data.step_id;
        console.log('更新step ID为:', step.value.step_id);
      }
      
      // 通知父组件步骤已保存，并传递完整的步骤数据
      emit('stepSaved', step.value.step_id, step.value);
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
    // 检查步骤是否存在
    if (!step.value || !step.value.step_id) {
      console.log('当前step_id:', step.value?.step_id);
      ElMessage.warning('没有有效的步骤ID，请先保存步骤')
      return
    }

    // 发送运行请求
    const res = await runCaseStep(step.value.step_id)
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