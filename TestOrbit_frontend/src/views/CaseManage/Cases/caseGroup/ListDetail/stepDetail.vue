
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

      // 更新步骤参数
      step.value = newParams;
      
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
  console.log('stepDetail收到子组件paramCard更新的配置:', config);
  // 更新本地步骤数据
  step.value = config;
  
  // 更新请求配置中的steps
  requestConfig.value.steps = [config];
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

    // 设置请求参数
    if (step.value) {
      requestConfig.value.case_id = 23 // 暂时固定
      requestConfig.value.env_id = 1 // 暂时固定
      requestConfig.value.steps = [step.value]
      console.log('保存步骤请求参数:', requestConfig.value)
    } else {
      ElMessage.warning('步骤数据不完整，无法保存')
      return
    }

    // // 发送保存请求
    // const res = await addCaseStep(requestConfig.value)
    
    // if (res?.code === 200) {
    //   ElMessage.success('保存成功')
    //   console.log('保存步骤响应:', res)
      
    //   // 通知父组件步骤名称已更新
    //   emit('update:stepName', stepName.value);
      
    //   // 通知父组件步骤已保存，并传递完整的步骤数据
    // } else {
    //   ElMessage.error(`保存失败: ${res?.message || '未知错误'}`)
    // }
  } catch (error) {
    console.error('保存步骤错误:', error)
    ElMessage.error(`保存步骤错误: ${(error as Error).message || '未知错误'}`)
  }
}

// 运行测试
const handleRun = async () => {
  try {
    // 检查步骤是否存在
    if (!step.value || !step.value.id) {
      ElMessage.warning('没有有效的步骤ID，请先保存步骤')
      return
    }

    // 发送运行请求
    const res = await runCaseStep(step.value.id)
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