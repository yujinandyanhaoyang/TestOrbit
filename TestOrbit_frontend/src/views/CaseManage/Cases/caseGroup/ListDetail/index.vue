<template>
  <div class="case-steps" v-loading="loading">
    
    <div class="steps-container">
      <draggable 
        v-model="steps" 
        item-key="step_id"
        handle=".drag-handle"
        ghost-class="ghost"
        @end="onDragEnd"
      >
        <template #item="{ element, index }">
          <div class="step-item">
            <el-collapse v-model="activeNames" @change="handleChange">
              <el-collapse-item :name="(element.step_id || (element as any).id || index).toString()">
                <template #title>
                  <div class="step-header">
                    <el-icon class="drag-handle"><Rank /></el-icon>
                    <span class="step-number">步骤{{ index + 1 }}</span>
                    <span class="step-title">{{ element.step_name }}</span>
                  </div>
                </template>
                <StepDetail 
                  :key="`step-${element.step_id || (element as any).id || index}`"
                  :step-id="element.step_id || (element as any).id" 
                  :step-name="element.step_name"
                  :stepParams="element"
                  @update:step-name="updateStepName(element.step_id || (element as any).id, $event)"
                  @step-saved="handleStepSaved"
                />
                <div class="step-actions">
                  <el-button size="small" type="danger" @click.stop="removeStep(element.step_id || (element as any).id)">删除步骤</el-button>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </template>
      </draggable>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, defineExpose, watch } from 'vue'
import StepDetail from './stepDetail.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Rank, Upload } from '@element-plus/icons-vue'
import type { CollapseModelValue } from 'element-plus'
// 引入draggable组件
import draggable from 'vuedraggable'
import type { CaseGroupDetailResponse, CaseGroupDetail as CaseGroupDetailType } from '@/api/case/caseGroup/types'
import type { CaseStep, ApiStepParams } from '@/api/case/caseStep/types'

// 定义组件props
const props = defineProps<{
  case_id?: number
  stepsData?: CaseStep[]
}>()


// 步骤数据
const steps = ref<CaseStep[]>([]);

// 当前激活的步骤
const activeNames = ref<string[]>(['1']);

// 用例组详情数据
const caseGroupData = ref<CaseGroupDetailType | null>(null);
// 加载状态
const loading = ref(false);

// 组件挂载时获取用例组详情（如果有groupId），默认不展开任何步骤
onMounted(async () => {
  // 默认不展开任何步骤
  activeNames.value = [];

  // 如果有case_id，则获取用例组详情
  if (props.case_id) {
    await fetchCaseGroupDetail(props.case_id);
  }
});

// 监听case_id变化，重新获取用例组详情
watch(() => props.case_id, async (newCaseId) => {
  if (newCaseId) {
    await fetchCaseGroupDetail(newCaseId);
  }
});

// 监听stepsData变化，更新本地steps数据（优化版）
watch(() => props.stepsData, (newStepsData, oldStepsData) => {
  console.log('👀 stepsData变化监听触发:', { 
    newStepsDataLength: newStepsData?.length || 0, 
    currentStepsLength: steps.value.length,
    oldStepsDataLength: oldStepsData?.length || 0
  });
  
  // 🔥 关键优化：只在真正的外部数据变化时才更新
  // 避免因内部handleStepSaved引起的循环更新
  if (newStepsData && newStepsData.length > 0) {
    // 检查是否是真正的外部数据变化（比如来自API的新数据）
    const isExternalChange = !oldStepsData || 
                           oldStepsData.length !== newStepsData.length ||
                           steps.value.length === 0; // 初始化时
    
    console.log('📊 数据变化分析:', {
      isExternalChange,
      isInitialization: steps.value.length === 0,
      lengthChanged: oldStepsData && oldStepsData.length !== newStepsData.length
    });
    
    if (isExternalChange) {
      // 处理步骤数据，确保每个步骤的step_name字段存在且不为空
      const processedSteps = newStepsData.map((step: CaseStep) => {
        const processedStep = { ...step };
        
        // 修复：确保step_name字段存在且有值
        if (!processedStep.step_name || processedStep.step_name === '') {
          // 如果步骤名称为空，尝试保留现有步骤的名称或使用默认值
          const existingStep = steps.value.find(s => 
            s.step_id === step.step_id || 
            (s as any).id === (step as any).id
          );
          
          if (existingStep && existingStep.step_name) {
            processedStep.step_name = existingStep.step_name;
            console.log(`🔄 保留现有步骤名称: "${existingStep.step_name}" (ID: ${step.step_id})`);
          } else {
            processedStep.step_name = `步骤${step.step_order || ''}`;
            console.log(`⚠️ 步骤名称为空，设置默认名称: "${processedStep.step_name}" (ID: ${step.step_id})`);
          }
        }
        
        return processedStep;
      });
      
      console.log('📝 外部数据变化，更新steps数据');
      steps.value = processedSteps;
      activeNames.value = [];
    } else {
      console.log('⏭️ 内部数据变化，跳过更新以避免循环');
    }
  }
}, { immediate: true });


// 步骤拖拽结束事件处理
const onDragEnd = async () => {
  // 首先更新本地steps数组中的顺序
  const updatedSteps = steps.value.map((step, index) => ({
    ...step,
    step_order: index + 1  // 从1开始编号
  }));
  
  // 更新本地状态
  steps.value = updatedSteps;

  // 同步更新 caseGroupData 中的步骤数据（如果存在）
  if (caseGroupData.value && caseGroupData.value.steps) {
    caseGroupData.value.steps = updatedSteps;
  }
  
  // 触发每个步骤的更新以确保子组件同步
  for (const step of updatedSteps) {
    await handleStepSaved(step.step_id || (step as any).id, step);
  }
  
  ElMessage.success('步骤顺序已更新');
};

// 添加新步骤
const addNewStep = () => {
  console.log('🔥 addNewStep被调用，当前步骤数量:', steps.value.length);
  
  // 计算新步骤的顺序号（基于当前步骤数量）
  const newOrder = steps.value.length + 1;
  
  // 创建临时本地ID（用于前端管理，保存时会被服务器分配的真实ID替换）
  const tempId = Date.now(); // 使用时间戳作为临时ID
  
  // 创建初始的空白步骤
  const newStepTitle = `新步骤${newOrder}`;
  
  console.log('🆕 准备创建新步骤:', { tempId: -tempId, stepName: newStepTitle, order: newOrder });
  
  // 创建新步骤对象并添加到步骤列表
  const newStep: CaseStep = {
    // 使用负数作为临时ID，避免与服务器分配的正数ID冲突
    step_id: -tempId, // 临时ID，保存后会被服务器分配的真实ID替换
    step_name: newStepTitle,
    step_order: newOrder,
    type: 'api',
    status: 0,
    controller_data: null,
    retried_times: null,
    enabled: true,
    results: {
      message: null,
      request_log: {
        url: '',
        body: {},
        header: {},
        method: 'GET',
        results: null,
        response: null,
        res_header: {},
        spend_time: 0
      }
    },
    params: {
      host: '',
      path: '/',
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
  };
  
  // 添加新步骤到数组
  steps.value.push(newStep);
  console.log('✅ 步骤已添加到steps数组，当前步骤总数:', steps.value.length);
  
  // 自动展开新添加的步骤（使用步骤的step_id）
  activeNames.value = [newStep.step_id.toString()];
  
  // ❌ 移除重复的数据同步 - 不要同时维护两个数据源
  // 因为 props.stepsData 来自 caseGroupData.steps，会导致数据重复
  // if (caseGroupData.value && caseGroupData.value.steps) {
  //   caseGroupData.value.steps.push(newStep);
  //   console.log('✅ 步骤已同步到caseGroupData，caseGroupData.steps长度:', caseGroupData.value.steps.length);
  // }
  
  console.log('🎯 addNewStep完成，最终steps数组:', steps.value.map(s => ({ id: s.step_id, name: s.step_name })));
  
  ElMessage.success('已添加新步骤');
};

// 删除步骤
const removeStep = (id: number) => {
  ElMessageBox.confirm(
    '确定要删除此步骤吗？此操作不可撤销。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(() => {
      steps.value = steps.value.filter(step => step.step_id !== id);
      ElMessage.success('步骤已删除');
    })
    .catch(() => {
      // 用户取消删除操作
    });
};

// 更新步骤名称
const updateStepName = (stepId: number, newName: string) => {
  // 尝试多种方式查找步骤
  let stepIndex = steps.value.findIndex(step => step.step_id === stepId);
  if (stepIndex === -1) {
    // 如果通过step_id找不到，尝试通过id字段查找
    stepIndex = steps.value.findIndex(step => (step as any).id === stepId);
  }
  
  if (stepIndex !== -1) {
    steps.value[stepIndex].step_name = newName;
  }
  
  // 同时更新 caseGroupData 中的步骤名称（如果存在）
  if (caseGroupData.value && caseGroupData.value.steps) {
    let caseStepIndex = caseGroupData.value.steps.findIndex(step => 
      step.step_id === stepId
    );
    if (caseStepIndex === -1) {
      caseStepIndex = caseGroupData.value.steps.findIndex(step => 
        (step as any).id === stepId
      );
    }
    if (caseStepIndex !== -1) {
      caseGroupData.value.steps[caseStepIndex].step_name = newName;
    }
  }
};

// 处理步骤保存事件
const handleStepSaved = (stepId: number, stepData: any) => {
  console.log('🔄 handleStepSaved被调用:', { 
    stepId, 
    stepName: stepData.step_name,
    assertionsCount: stepData.assertions?.length || 0,
    currentStepsIds: steps.value.map(s => ({ id: s.step_id, name: s.step_name }))
  });
  
  // 首先尝试通过step_id查找步骤
  let stepIndex = steps.value.findIndex(step => step.step_id === stepId);
  console.log('📍 通过step_id查找结果:', stepIndex);
  
  // 如果找不到，再尝试通过id字段查找
  if (stepIndex === -1) {
    stepIndex = steps.value.findIndex(step => (step as any).id === stepId);
    console.log('📍 通过id字段查找结果:', stepIndex);
  }
  
  if (stepIndex !== -1) {
    console.log('✅ 找到步骤，更新索引:', stepIndex);
    // 合并数据，确保保留原始数据的结构
    const originalStep = steps.value[stepIndex];
    
    // 修复：确保stepData.step_name不为空，如果为空则保留原始步骤名称
    if (!stepData.step_name || stepData.step_name === '') {
      if (originalStep.step_name) {
        // 如果原步骤有名称，则保留原名称
        console.log(`⚠️ 发现stepData.step_name为空，保留原步骤名称: "${originalStep.step_name}"`);
        stepData.step_name = originalStep.step_name;
      } else {
        // 如果原步骤也没有名称，则设置默认名称
        stepData.step_name = `步骤${originalStep.step_order || stepIndex + 1}`;
        console.log(`⚠️ 发现步骤名称缺失，设置默认名称: "${stepData.step_name}"`);
      }
    }
    
    // 🔥 关键修复：智能保留assertions数据
    const originalAssertions = originalStep.assertions || [];
    const newAssertions = stepData.assertions || [];
    
    // 如果新数据的assertions为空，但原数据有assertions，则保留原数据
    const finalAssertions = newAssertions.length > 0 ? newAssertions : originalAssertions;
    
    console.log('assertions数据处理:', {
      original: originalAssertions.length,
      new: newAssertions.length,
      final: finalAssertions.length
    });
    
    const updatedStep = {
      ...originalStep,            // 保持原有数据
      ...stepData,                // 覆盖更新的数据
      step_id: stepId,           // 确保step_id不被修改
      step_order: originalStep.step_order, // 保留原始顺序
      assertions: finalAssertions // 🔥 使用智能合并的assertions
    };
    
    console.log('📝 步骤数据对比:', {
      before: { name: originalStep.step_name, assertions: originalStep.assertions?.length || 0 },
      after: { name: updatedStep.step_name, assertions: updatedStep.assertions?.length || 0 }
    });
    
    steps.value[stepIndex] = updatedStep;
  } else {
    // 如果找不到匹配的步骤，添加一个新步骤
    console.log(`找不到ID为${stepId}的步骤，添加新步骤`);
    stepData.step_id = stepId;
    stepData.step_order = steps.value.length + 1;
    steps.value.push(stepData);
  }
  
  // ❌ 移除对caseGroupData的同步更新，避免循环触发
  // 因为caseGroupData.steps会触发props.stepsData变化，导致循环
  // 让用例组保存时统一更新caseGroupData
  console.log('🎯 跳过caseGroupData同步，避免循环触发');
};

// 折叠面板变更事件 - 简化版，只负责展示面板
const handleChange = (val: CollapseModelValue) => {
  // 获取当前打开的步骤ID
  const currentStepId = Array.isArray(val) ? val[0] : val;

  // 如果没有步骤ID，或者步骤ID不是数字，不做任何操作
  if (!currentStepId || isNaN(Number(currentStepId))) {
    return;
  }
  
};


// 获取用例组详情数据（备用方法，主要数据通过props传递）
const fetchCaseGroupDetail = async (groupId: number) => {
  // 通过子组件传递数据
};

// 提供给父组件的方法，用于设置用例组详情
const setCaseGroupDetail = (response: CaseGroupDetailResponse) => {
  if (response.code === 200) {
    caseGroupData.value = response.results;
    
    // 更新步骤数据
    if (caseGroupData.value?.steps && caseGroupData.value.steps.length > 0) {
      // 处理API返回的步骤数据，确保step_name字段存在且不为空
      const processedSteps = caseGroupData.value.steps.map(step => {
        // 创建副本避免修改原对象
        const processedStep = { ...step };
        
        // 修复：确保step_name字段存在且不为空
        if (!processedStep.step_name || processedStep.step_name === '') {
          // 如果缺少step_name，尝试从其他字段获取或使用默认名称
          processedStep.step_name = step.step_name || `步骤${step.step_order || '未知'}`;
          console.log(`🔧 修复步骤名称: ID=${step.step_id}, 设置name=${processedStep.step_name}`);
        }
        
        return processedStep;
      });
      
      // console.log('📊 处理后的步骤数据:', processedSteps.map(s => ({
      //   id: s.step_id, 
      //   name: s.step_name, 
      //   order: s.step_order
      // })));
      
      // 使用处理后的步骤数据
      steps.value = processedSteps;
      
      // 默认不展开任何步骤
      activeNames.value = [];
    }
  }
};

// 获取当前的步骤数据
const getStepsData = () => {
  // 确保返回最新的步骤数据，包含所有更新
  // steps.value 中包含了通过handleStepSaved方法更新的数据
  
  // 1. 确保所有步骤数据的完整性
  const currentSteps = steps.value.map((step, index) => {
    const processedStep = { ...step }; // 创建副本避免修改原对象
    
    // 处理ID字段统一性
    if (!processedStep.step_id && (step as any).id) {
      processedStep.step_id = (step as any).id;
    }
    
    // 确保step_order字段正确（基于当前索引）
    processedStep.step_order = index + 1;
    
    // 确保必要的字段存在
    if (!processedStep.params) {
      console.warn(`步骤 ${step.step_name || '未命名'} 缺少params字段`);
      // 使用默认的空params结构
      processedStep.params = step.params || {
        host: '',
        path: '/',
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
      } as any;
    }
    
    // 删除可能存在的多余id字段，统一使用step_id
    delete (processedStep as any).id;
    
    // 🎯 重要：这里不处理临时ID的移除逻辑
    // 让head.vue中的保存逻辑来处理新步骤的ID移除
    // 这样保持职责分离：getStepsData只负责获取数据，不负责数据转换
    
    return processedStep;
  });
  
  console.log(`🔍 getStepsData: 准备提交 ${currentSteps.length} 个步骤数据`, 
    currentSteps.map(s => ({ 
      name: s.step_name, 
      id: s.step_id, 
      isNew: s.step_id && s.step_id < 0 ? '新步骤' : '已有步骤' 
    }))
  );
  
  return currentSteps;
};

// 保存步骤顺序的方法
const saveStepOrder = () => {
  // 确保步骤顺序是最新的
  steps.value.forEach((step, index) => {
    step.step_order = index + 1;
  });
  
  ElMessage.success('步骤顺序已保存');
  return true;
};

// 保存所有步骤数据的方法
const saveAllSteps = async () => {
  try {
    // 获取所有展开的步骤的引用
    const stepComponents = document.querySelectorAll('.step-item .el-collapse-item__wrap');
    let allValid = true;
    
    // 如果有展开的步骤，先调用其handleSave方法
    if (stepComponents && stepComponents.length > 0) {
      console.log(`找到 ${stepComponents.length} 个可能展开的步骤组件`);
      
      // 这里我们无法直接访问Vue组件实例，而是通过emit事件的方式来同步数据
      // 实际数据已经通过handleStepSaved方法更新到steps.value中
    }
    
    if (!allValid) {
      ElMessage.warning('部分步骤数据验证失败，请检查');
      return false;
    }
    
    // 返回所有步骤数据
    return getStepsData();
  } catch (error) {
    console.error('保存所有步骤时出错:', error);
    ElMessage.error('保存步骤数据失败');
    return false;
  }
};

// 公开方法给父组件调用
defineExpose({
  addNewStep,
  setCaseGroupDetail,
  getStepsData,    // 添加获取步骤数据的方法
  saveStepOrder,   // 添加保存步骤顺序的方法
  saveAllSteps     // 添加保存所有步骤数据的方法
});
</script>

<style scoped lang="scss">
.case-steps {
  width: 100%;
  position: relative;
  min-height: 200px;
  
  .case-group-info {
    background-color: #f9fafc;
    border: 1px solid #ebeef5;
    border-radius: 4px;
    padding: 16px;
    margin-bottom: 20px;
    
    h2 {
      margin: 0 0 12px 0;
      font-size: 20px;
      color: #303133;
    }
    
    .info-row {
      margin: 6px 0;
      display: flex;
      align-items: center;
      
      .label {
        color: #606266;
        margin-right: 8px;
        font-weight: 500;
      }
      
      .value {
        color: #303133;
      }
    }
  }
  
  .steps-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h2 {
      margin: 0;
      font-size: 18px;
      color: #303133;
    }
    
    .actions {
      display: flex;
      gap: 8px;
    }
  }
  
  .steps-container {
    border: 1px solid #ebeef5;
    border-radius: 4px;
    
    .step-item {
      border-bottom: 1px solid #ebeef5;
      
      &:last-child {
        border-bottom: none;
      }
      
      .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        
        .drag-handle {
          cursor: move;
          color: #909399;
          
          &:hover {
            color: #409eff;
          }
        }
        
        .step-number {
          font-weight: bold;
          color: #606266;
        }
        
        .step-title {
          color: #303133;
        }
      }
    }
  }
}

/* 拖拽时的样式 */
.ghost {
  opacity: 0.5;
  background: #c8ebfb;
}

/* 确保el-collapse不影响拖拽功能 */
:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item) {
  border-bottom: none;
}

/* 步骤操作按钮区域 */
.step-actions {
  display: flex;
  justify-content: flex-end;
  padding: 12px 0;
  margin-top: 12px;
  border-top: 1px dashed #ebeef5;
}
</style>
