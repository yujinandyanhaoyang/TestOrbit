<template>
  <div class="case-steps" v-loading="loading">
    
    <div class="steps-container">
      <draggable 
        v-model="steps" 
        item-key="id"
        handle=".drag-handle"
        ghost-class="ghost"
        @end="onDragEnd"
      >
        <template #item="{ element, index }">
          <div class="step-item">
            <el-collapse v-model="activeNames" @change="handleChange">
              <el-collapse-item :name="element.id.toString()">
                <template #title>
                  <div class="step-header">
                    <el-icon class="drag-handle"><Rank /></el-icon>
                    <span class="step-number">步骤{{ index + 1 }}</span>
                    <span class="step-title">{{ element.title }}</span>
                  </div>
                </template>
                <StepDetail 
                  :step-id="element.id" 
                  :step-name="element.title"
                  :step-params="getStepParams(element.id)"
                  @update:step-name="updateStepName(element.id, $event)"
                  @step-saved="handleStepSaved"
                />
                <div class="step-actions">
                  <el-button size="small" type="danger" @click.stop="removeStep(element.id)">删除步骤</el-button>
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
import { Rank } from '@element-plus/icons-vue'
import type { CollapseModelValue } from 'element-plus'
// 引入draggable组件
import draggable from 'vuedraggable'
import type { CaseGroupDetailResponse, CaseGroupDetail as CaseGroupDetailType } from '@/api/case/caseGroup/types'
import type { CaseStep, ApiStepParams } from '@/api/case/caseStep/types'
import { getStepDetail } from '@/api/case/caseStep'

// 定义组件props
const props = defineProps<{
  groupId?: number
  stepsData?: CaseStep[]
}>()

// 测试步骤数据
interface Step {
  id: number;
  title: string;
  description: string;
  api_id?: number; // 添加API ID字段
}

// 使用props中的stepsData初始化steps数据，如果没有则使用默认值
const steps = ref<Step[]>([]);

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
  
  // 如果有groupId，则获取用例组详情
  if (props.groupId) {
    await fetchCaseGroupDetail(props.groupId);
  }
});

// 监听groupId变化，重新获取用例组详情
watch(() => props.groupId, async (newGroupId) => {
  if (newGroupId) {
    await fetchCaseGroupDetail(newGroupId);
  }
});

// 监听stepsData变化，更新本地steps数据
watch(() => props.stepsData, (newStepsData) => {
  if (newStepsData && newStepsData.length > 0) {
    console.log('接收到新的步骤数据:', newStepsData);
    
    // 将API返回的步骤格式转换为组件使用的步骤格式
    steps.value = newStepsData.map(apiStep => {
      // 检查是否有params和params.api_id
      const api_id = apiStep.params?.api_id;
      console.log(`步骤 ${apiStep.id} 的API ID:`, api_id);
      
      return {
        id: apiStep.id,
        title: apiStep.step_name,
        description: apiStep.type || '',
        api_id: api_id // 保存API ID
      };
    });
    
    // 默认不展开任何步骤
    activeNames.value = [];
  }
}, { immediate: true });


// 步骤拖拽结束事件处理
const onDragEnd = () => {
  console.log('步骤顺序已更新:', steps.value);
  ElMessage.success('步骤顺序已更新，请点击"保存顺序"按钮保存');
};

// 保存步骤顺序
const saveStepOrder = () => {
  // 这里可以添加API调用来保存步骤顺序到后端
  console.log('保存步骤顺序:', steps.value.map(step => step.id));
  ElMessage.success('步骤顺序已保存');
};

// 添加新步骤
const addNewStep = () => {
  const newId = Math.max(...steps.value.map(step => step.id), 0) + 1;
  
  // 创建初始的空白步骤
  const newStepTitle = `新步骤${newId}`;
  
  // 添加新步骤
  steps.value.push({
    id: newId,
    title: newStepTitle,
    description: '' // 不再需要描述，因为使用StepDetail组件
  });
  
  // 新增步骤后，可以选择是否自动展开
  // 如果需要自动展开新添加的步骤，保留下面这行
  activeNames.value = [newId.toString()];
  // 如果不需要自动展开，则使用：
  // activeNames.value = [];
  
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
      steps.value = steps.value.filter(step => step.id !== id);
      ElMessage.success('步骤已删除');
    })
    .catch(() => {
      // 用户取消删除操作
    });
};

// 更新步骤名称
const updateStepName = (stepId: number, newName: string) => {
  const stepIndex = steps.value.findIndex(step => step.id === stepId);
  if (stepIndex !== -1) {
    steps.value[stepIndex].title = newName;
  }
};

// 获取步骤参数
const getStepParams = (stepId: number): ApiStepParams | undefined => {
  // 先尝试从API返回的数据中获取
  if (caseGroupData.value?.steps) {
    // console.log('尝试从caseGroupData中查找步骤', stepId, caseGroupData.value.steps);
    const apiStep = caseGroupData.value.steps.find(step => step.id === stepId);
    if (apiStep) {
      // console.log('找到步骤参数:', apiStep.params);
      return apiStep.params;
    }
  }
  
  // 如果API数据中找不到，则尝试从props中获取
  if (props.stepsData) {
    const propStep = props.stepsData.find(step => step.id === stepId);
    if (propStep) {
      // console.log('在props中找到步骤参数:', propStep.params);
      return propStep.params;
    }
  }
  
  console.log('找不到步骤参数', stepId);
  return undefined;
};

// 处理步骤保存事件
const handleStepSaved = (stepId: number, data: any) => {
  console.log(`步骤 ${stepId} 已保存:`, data);
  // 可以在这里添加其他逻辑，比如更新步骤列表、向后端发送数据等
};

// 折叠面板变更事件
const handleChange = async (val: CollapseModelValue) => {
  
  // 获取当前打开的步骤ID
  const currentStepId = Array.isArray(val) ? val[0] : val;

  // 如果没有步骤ID，或者步骤ID不是数字，不做任何操作
  if (!currentStepId || isNaN(Number(currentStepId))) {
    return;
  }
  
  try {
    // 获取步骤详情
    const stepId = Number(currentStepId);
    console.log('开始处理步骤详情, 步骤ID:', stepId);
    
    // 查找当前步骤
    const currentStep = steps.value.find(s => s.id === stepId);
    if (!currentStep) {
      console.warn(`找不到ID为${stepId}的步骤`);
      return;
    }
    
    console.log('找到当前步骤:', currentStep);
    
    // 检查是否可以从caseGroupData中获取完整的步骤参数
    if (caseGroupData.value && caseGroupData.value.steps) {
      const apiStep = caseGroupData.value.steps.find(s => s.id === stepId);
      if (apiStep && apiStep.params) {
        console.log('从用例组数据中找到步骤参数:', apiStep.params);
        
        // 检查步骤是否有API ID，如果没有但步骤参数中有，则更新步骤的API ID
        if (!currentStep.api_id && apiStep.params.api_id) {
          currentStep.api_id = apiStep.params.api_id;
          console.log(`更新步骤${stepId}的API ID为:`, currentStep.api_id);
        }
        
        // 检查是否需要从API获取额外信息
        if (currentStep.api_id && (!apiStep.params.path || !apiStep.params.method)) {
          // 从API获取步骤详情，使用API ID
          loading.value = true;
          console.log(`步骤参数缺少path或method，使用API ID ${currentStep.api_id}获取步骤详情`);
          const response = await getStepDetail(currentStep.api_id);
          loading.value = false;
          
          if (response && response.code === 200) {
            console.log('获取步骤详情成功:', response.results);
            
            // 使用类型断言处理返回的数据
            const apiDetails = response.results as any;
            
            // 更新参数
            if ('path' in apiDetails && !apiStep.params.path) {
              apiStep.params.path = apiDetails.path;
            }
            if ('method' in apiDetails && !apiStep.params.method) {
              apiStep.params.method = apiDetails.method;
            }
            if ('host' in apiDetails && !apiStep.params.host) {
              apiStep.params.host = apiDetails.host;
            }
            console.log('更新后的步骤参数:', apiStep.params);
          }
        }
        
        // 强制触发组件更新
        steps.value = [...steps.value]; // 创建数组的新副本触发响应式更新
            
        // 手动触发activeNames的变更来强制组件重新渲染
        activeNames.value = [];
        setTimeout(() => {
          activeNames.value = [stepId.toString()];
        }, 10);
        
        ElMessage.success('步骤详情已加载');
      } else {
        console.warn(`在用例组数据中找不到步骤${stepId}的参数`);
        
        // 如果步骤有API ID，但在用例组数据中找不到参数，则从API获取详情
        if (currentStep.api_id) {
          await loadStepDetailFromApi(stepId, currentStep.api_id);
        } else {
          ElMessage.warning('此步骤没有足够的参数信息');
        }
      }
    } else {
      console.warn('用例组数据不完整，无法获取步骤参数');
      
      // 如果步骤有API ID，从API获取详情
      if (currentStep.api_id) {
        await loadStepDetailFromApi(stepId, currentStep.api_id);
      } else {
        ElMessage.warning('此步骤没有关联的API，无法获取详情');
      }
    }
  } catch (error) {
    loading.value = false;
    console.error('处理步骤详情出错:', error);
    ElMessage.error('处理步骤详情出错');
  }
};

// 从API加载步骤详情
const loadStepDetailFromApi = async (stepId: number, apiId: number) => {
  loading.value = true;
  try {
    console.log(`正在使用API ID ${apiId}获取步骤详情`);
    const response = await getStepDetail(apiId);
    
    if (response && response.code === 200) {
      console.log('获取步骤详情成功:', response.results);
      
      // 检查响应数据结构
      if (response.results && typeof response.results === 'object') {
        const apiDetails = response.results as any;
        
        // 构建更新的参数对象
        const updatedParams: any = {
          api_id: apiId
        };
        
        // 添加需要的字段
        if ('name' in apiDetails) updatedParams.name = apiDetails.name;
        if ('load_name' in apiDetails) updatedParams.load_name = apiDetails.load_name;
        if ('path' in apiDetails) updatedParams.path = apiDetails.path;
        if ('method' in apiDetails) updatedParams.method = apiDetails.method;
        if ('host' in apiDetails) updatedParams.host = apiDetails.host;
        
        // 确保caseGroupData结构完整
        if (!caseGroupData.value) {
          caseGroupData.value = { 
            id: 0, 
            name: '', 
            remark: null,
            steps: [], 
            module_id: '', 
            latest_run_time: '', 
            updated: '',
            module_related: [],
            only_show: false
          };
        }
        
        // 安全地访问steps属性
        const caseSteps = caseGroupData.value?.steps || [];
        
        // 查找步骤索引
        const stepIndex = caseSteps.findIndex(s => s.id === stepId);
        
        if (stepIndex !== -1) {
          // 更新现有步骤
          if (!caseSteps[stepIndex].params) {
            caseSteps[stepIndex].params = updatedParams;
          } else {
            caseSteps[stepIndex].params = {
              ...caseSteps[stepIndex].params,
              ...updatedParams
            };
          }
        } else {
          // 添加新步骤
          caseSteps.push({
            id: stepId,
            step_name: updatedParams.name || `步骤${stepId}`,
            params: updatedParams,
            type: 'api',
            status: 0,
            enabled: true,
            controller_data: null,
            retried_times: 0,
            results: null
          });
        }
        
        // 如果caseGroupData存在，更新其steps属性
        if (caseGroupData.value) {
          caseGroupData.value.steps = [...caseSteps];
        }
        
        console.log('更新后的步骤参数:', caseSteps.find(s => s.id === stepId)?.params);
        
        // 强制触发更新
        steps.value = [...steps.value];
        
        // 手动触发重新渲染
        activeNames.value = [];
        setTimeout(() => {
          activeNames.value = [stepId.toString()];
        }, 10);
        
        ElMessage.success('步骤详情已更新');
      }
    } else {
      ElMessage.error('获取步骤详情失败');
    }
  } catch (error) {
    console.error('从API获取步骤详情出错:', error);
    ElMessage.error('获取步骤详情出错');
  } finally {
    loading.value = false;
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
      console.log('用例组详情中的步骤数据:', caseGroupData.value.steps);

      // 将API返回的步骤格式转换为组件使用的步骤格式
      steps.value = caseGroupData.value.steps.map(apiStep => {
        // 检查是否有params和params.api_id
        const api_id = apiStep.params?.api_id;
        console.log(`步骤 ${apiStep.id} 的API ID:`, api_id);
        
        return {
          id: apiStep.id,
          title: apiStep.step_name,
          description: apiStep.type || '',
          api_id: api_id // 保存API ID
        };
      });
      
      // 默认不展开任何步骤
      activeNames.value = [];
    } else {
      console.log('setCaseGroupDetail: 没有步骤数据');
    }
  } else {
    console.warn('setCaseGroupDetail: 响应码不是200', response.code);
  }
};

// 公开方法给父组件调用
defineExpose({
  addNewStep,
  saveStepOrder,
  setCaseGroupDetail
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
