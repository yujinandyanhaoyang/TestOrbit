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
import type { CaseStep, AddCaseStepRequest, HttpMethod} from '@/api/case/caseStep/types'

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
  (e: 'step-saved', id: number, data: any): void; // 修改为kebab-case，与模板中的@step-saved匹配
}>();

// 基本信息 - 使用props的值或默认值
const stepName = ref<string>(props.stepName || '新建步骤')

// 添加标志位来防止循环更新
const isUpdatingFromProps = ref(false);

// 监听stepName变化，实时通知父组件
watch(stepName, (newStepName, oldStepName) => {
  // 如果正在从props更新，跳过emit
  if (isUpdatingFromProps.value) {
    console.log('跳过props更新触发的emit');
    return;
  }
  
  // 确保有有效的步骤ID才发送更新事件
  const currentStepId = props.stepId || step.value?.step_id || props.stepParams?.step_id;
  
  console.log('stepName变化调试信息:', {
    newStepName,
    oldStepName,
    'props.stepId': props.stepId,
    'step.value?.step_id': step.value?.step_id,
    'props.stepParams?.step_id': props.stepParams?.step_id,
    'currentStepId': currentStepId
  });
  
  if (currentStepId && newStepName !== oldStepName) {
    // console.log(`步骤 ${currentStepId} 的名称从 "${oldStepName}" 更新为: "${newStepName}"`);
    // 实时通知父组件步骤名称变化，并传递正确的stepId
    emit('update:stepName', newStepName);
  }
}, { immediate: false });

// 监听props变化，更新内部状态
watch(
  () => props.stepName,
  (newStepName) => {
    // console.log('props.stepName变化调试信息:', {
    //   newStepName,
    //   // 'stepName.value': stepName.value,
    //   'props.stepId': props.stepId,
    //   // 'props.stepParams?.step_id': props.stepParams?.step_id,
    //   // 'stepParams.value.step_order':  props.stepParams?.step_order
    //   'stepParams.value.params':  props.stepParams?.params.host
    // });
    
    // 只有当props传入的stepName确实发生变化，且与当前值不同时才更新
    if (newStepName && newStepName !== stepName.value) {
      // console.log(`从props接收到新的步骤名称: ${newStepName}, 当前值: ${stepName.value}, 步骤ID: ${props.stepId}`);
      
      // 设置标志位，防止触发emit
      isUpdatingFromProps.value = true;
      stepName.value = newStepName;
      
      // 下一个tick后清除标志位
      setTimeout(() => {
        isUpdatingFromProps.value = false;
      }, 0);
    }
  },
  { immediate: true }
);

// 定义步骤参数，基于props或默认值
const address = ref<string>('') // 默认路径
const UrlInput = ref<string>('') // 默认主机名
const method = ref<HttpMethod>() // 默认HTTP方法
const step = ref<CaseStep>() // 步骤参数

// 创建默认step对象的函数
const createDefaultStep = (): CaseStep => {
  // 优先使用props中的真实ID
  const realStepId = props.stepId || props.stepParams?.step_id || 0;
  
  return {
    step_id: realStepId,  // 使用真实的step_id
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

// 监听props.stepId变化，确保step_id保持正确
watch(() => props.stepId, (newStepId) => {
  if (newStepId && step.value && step.value.step_id !== newStepId) {
    // console.log(`更新step_id从 ${step.value.step_id} 到 ${newStepId}`);
    step.value.step_id = newStepId;
  }
}, { immediate: true });

// 请求参数配置
const requestConfig = ref<AddCaseStepRequest>({
  case_id: 0, // 初始化为不存在数据
  env_id: 0, // 初始化为不存在数据
  steps: []
})


// 监听stepParams变化，更新参数（优化版，避免重复更新）
const lastProcessedParamsData = ref<string>('');

watch(() => props.stepParams, (newParams) => {
  // console.group('props.stepParams:', newParams);
  // console.group('props.stepParams.params:', newParams?.params);
  // console.group('props.stepParams.assertions:', newParams?.assertions);
  
  if (newParams) {
    // 🔥 优化：检测数据是否真正变化，避免重复更新界面
    const currentParamsFingerprint = JSON.stringify({
      stepId: newParams.step_id || (newParams as any).id,
      host: newParams.params?.host,
      path: newParams.params?.path,
      method: newParams.params?.method,
      stepName: newParams.step_name
    });
    
    if (lastProcessedParamsData.value !== currentParamsFingerprint) {
      console.log('📝 stepDetail检测到params数据变化，更新界面');
      lastProcessedParamsData.value = currentParamsFingerprint;
      
      // 通过.params访问ApiStepParams的属性
      if (newParams.params) {
        // 🔥 优化：只在数据真正变化时才更新界面输入框
        if (UrlInput.value !== (newParams.params.host || '')) {
          UrlInput.value = newParams.params.host || '';
        }
        
        if (address.value !== (newParams.params.path || '')) {
          address.value = newParams.params.path || '';
        }
        
        if (method.value !== newParams.params.method) {
          method.value = newParams.params.method as HttpMethod;
        }

        // 更新步骤参数，确保使用正确的ID字段，优先使用props.stepId
        const correctStepId = props.stepId || newParams.step_id || (newParams as any).id || 0;
        
        step.value = {
          ...newParams,
          step_id: correctStepId  // 确保使用正确的ID
        };
        
        // console.log(`✅ stepParams更新完成，step_id: ${correctStepId}`);
        
      } else {
        console.warn('CaseStep对象中没有params属性！');
      }
    } else {
      // console.log('⏭️ stepDetail跳过重复的params更新');
    }
  } else {
    console.log('没有接收到stepParams参数');
  }
}, { deep: true, immediate: true });

// 防止过度同步的标志位
const isSyncingToParent = ref(false);

// 安全重置同步标志的辅助函数
const resetSyncFlag = () => {
  setTimeout(() => {
    isSyncingToParent.value = false;
    console.log('🔄 重置isSyncingToParent标志');
  }, 100);
};

// 监听页面输入框变化，实时同步到step对象（优化频率）
watch([stepName, UrlInput, address, method], () => {
  if (step.value && step.value.params && !isSyncingToParent.value) {
    // 实时同步页面输入框的值到step对象
    step.value.step_name = stepName.value.trim();
    step.value.params.host = UrlInput.value.trim();
    step.value.params.path = address.value.trim() || '/';
    if (method.value) {
      step.value.params.method = method.value;
    }
    
    // 更新请求配置中的steps（保持同步）
    requestConfig.value.steps = [step.value];
    
    // 🔥 优化：延迟同步，减少频繁触发
    if (step.value.step_id) {
      // 确保step_name字段不为空
      if (!step.value.step_name || step.value.step_name === '') {
        step.value.step_name = props.stepName || stepName.value || `步骤${step.value.step_order || ''}`;
      }
      
      // 设置防护标志并延迟同步
      if (syncTimeoutId.value) {
        clearTimeout(syncTimeoutId.value);
      }
      syncTimeoutId.value = setTimeout(() => {
        if (step.value && step.value.step_id) {
          console.log('🔄 延迟同步基础输入框数据到父组件');
          emit('step-saved', step.value.step_id, step.value);
          resetSyncFlag(); // 确保同步标志被重置
        }
      }, 300); // 300ms防抖
    }
  }
});

// 防抖定时器ID
const syncTimeoutId = ref<number | null>(null);

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
  console.log('stepDetail收到子组件paramCard更新的配置:', {
    stepId: config.step_id,
    hasAssertions: config.assertions?.length > 0,
    assertionsCount: config.assertions?.length || 0
  });

  // 🔥 关键修复：增加防护，只有当子组件传递了有效的step_id时才进行合并
  // 这可以防止子组件在自身初始化期间（此时step_id可能为0）发出的事件污染父组件状态
  const configStepId = config.step_id || (config as any).id || 0;
  if (configStepId === 0) {
    console.warn('⚠️ 拦截到来自子组件的无效更新（stepId为0），已跳过');
    return;
  }
  
  // 防止在同步过程中触发额外的同步
  isSyncingToParent.value = true;
  
  try {
    // 深度合并配置，确保不丢失任何数据
    if (step.value) {
      // 🔥 关键修复：完整保存原始数据，特别是assertions
      const originalAssertions = step.value.assertions || [];
      const newAssertions = config.assertions || [];
      
      // 如果step已存在，深度合并新配置
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
        },
        // 🔥 关键修复：智能合并assertions，保持数据完整性
        assertions: newAssertions.length > 0 ? newAssertions : originalAssertions
      };
      
      console.log('合并assertions:', {
        original: originalAssertions.length,
        new: newAssertions.length, 
        final: step.value.assertions?.length || 0
      });
      
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
        },
        // 🔥 确保assertions字段被正确设置
        assertions: config.assertions || []
      };
      
      // 删除可能存在的多余id字段
      delete (step.value as any).id;
    }
    
    // 更新请求配置中的steps（保持同步）
    requestConfig.value.steps = [step.value];
    
    // 🔥 关键修复：参数更新后立即同步到父组件，但要确保数据完整性
    if (step.value && step.value.step_id) {
      // 确保同步时step_name字段不为空
      if (!step.value.step_name || step.value.step_name === '') {
        // 如果step_name为空，使用props中的stepName或当前的stepName.value
        step.value.step_name = props.stepName || stepName.value || `步骤${step.value.step_order || ''}`;
        console.log(`⚠️ 同步前发现step_name为空，已修正为: "${step.value.step_name}"`);
      }
      
      console.log('🔄 参数更新后同步到父组件:', {
        stepId: step.value.step_id,
        stepName: step.value.step_name,
        hasBodySource: !!step.value.params?.body_source,
        hasQuerySource: step.value.params?.query_source?.length > 0,
        hasHeaderSource: step.value.params?.header_source?.length > 0,
        assertionsCount: step.value.assertions?.length || 0
      });
      
      // 修复：将驼峰式命名 'stepSaved' 改为 kebab-case 'step-saved'，与父组件中的监听名称一致
      emit('step-saved', step.value.step_id, step.value);
    }
  } finally {
    // 重置防护标志
    resetSyncFlag();
  }
  
  console.log('更新后的完整step对象assertions长度:', step.value?.assertions?.length || 0);
}

// 准备步骤数据并同步到父组件
const handleSave = () => {
  try {
    // 检验必要数据
    if (!stepName.value.trim()) {
      ElMessage.warning('请输入步骤名称')
      return false
    }
    
    if (!method.value) {
      ElMessage.warning('请选择请求方法')
      return false
    }
    
    if (!UrlInput.value.trim()) {
      ElMessage.warning('请输入域名')
      return false
    }

    // 检查step对象和params的完整性
    if (!step.value || !step.value.params) {
      ElMessage.warning('步骤信息不完整，请检查参数配置')
      console.error('step.value 或 step.value.params 不存在:', step.value)
      return false
    }

    // 更新步骤基本信息（从页面输入框获取）
    step.value.step_name = stepName.value.trim();
    step.value.params.host = UrlInput.value.trim();
    step.value.params.path = address.value.trim() || '/';
    step.value.params.method = method.value;
    
    // 确保step_name字段不为空
    if (!step.value.step_name || step.value.step_name === '') {
      step.value.step_name = stepName.value || `步骤${step.value.step_order || ''}`;
      console.log(`⚠️ 保存前发现step_name为空，已修正为: "${step.value.step_name}"`);
    }
    
    // 通知父组件步骤数据已准备好 - 使用kebab-case格式的事件名
    emit('step-saved', step.value.step_id, step.value);
    
    return true
  } catch (error) {
    console.error('准备步骤数据错误:', error)
    ElMessage.error(`准备步骤数据错误: ${(error as Error).message || '未知错误'}`)
    return false
  }
}

// 运行测试
const handleRun = async () => {
  try {
    // 首先确保步骤数据已同步到父组件
    const saveResult = handleSave();
    if (!saveResult) {
      ElMessage.warning('步骤数据准备不完整，无法运行');
      return;
    }
    
    // 检查步骤是否存在
    if (!step.value || !step.value.step_id) {
      console.log('当前step_id:', step.value?.step_id);
      ElMessage.warning('没有有效的步骤ID，请先保存用例组');
      return;
    }

    // 提示用户运行前需要整体保存
    ElMessage({
      message: '数据已准备好，即将运行测试',
      type: 'info',
      duration: 2000
    });

    // 发送运行请求
    const res = await runCaseStep(step.value.step_id);
    if (res?.code === 200) {
      ElMessage.success('运行成功');
      
      // 直接将API响应结果赋值给apiResponse
      apiResponse.value = res;
    } else {
      ElMessage.error(`运行失败: ${res?.message || '未知错误'}`);
    }
  } catch (error) {
    console.error('运行步骤错误:', error);
    ElMessage.error(`运行步骤错误: ${(error as Error).message || '未知错误'}`);
  }
}

// 向父组件暴露方法
defineExpose({
  handleSave,
  getStepData: () => step.value  // 添加获取当前步骤数据的方法
});

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