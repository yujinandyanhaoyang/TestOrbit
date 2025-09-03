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
                    <el-tooltip content="拖拽排序" placement="top" :show-after="500">
                      <el-icon class="drag-handle"><Rank /></el-icon>
                    </el-tooltip>
                    <span class="step-number">步骤{{ index + 1 }}</span>
                    <span class="step-title">{{ element.step_name || '未命名步骤' }}</span>
                    <div class="step-badges">
                      <el-tag size="small" :type="getStepStatusType(element.status)" v-if="element.status" class="status-badge">
                        {{ getStepStatusText(element.status) }}
                      </el-tag>
                      <el-tag size="small" type="info" v-if="element.assertions && element.assertions.length > 0" class="count-badge">
                        断言: {{ element.assertions.length }}
                      </el-tag>
                    </div>
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
                  <el-button size="small" type="danger" @click.stop="removeStep(element.step_id || (element as any).id)" class="delete-btn">
                    <el-icon><Delete /></el-icon>
                    删除步骤
                  </el-button>
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
import { ref, onMounted, defineExpose, watch, computed } from 'vue'
import StepDetail from './stepDetail.vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Rank, Delete } from '@element-plus/icons-vue'
import type { CollapseModelValue } from 'element-plus'
// 引入draggable组件
import draggable from 'vuedraggable'
// 引入Pinia store
import { useCaseGroupStore } from '@/store/caseGroupStore'

// 定义组件props
const props = defineProps<{
  caseId: number,
  isNew?: boolean
}>()

// 使用Pinia store
const caseGroupStore = useCaseGroupStore()

// 从store获取步骤数据
const steps = computed({
  get: () => caseGroupStore.steps,
  set: (value) => {
    // 这里处理拖拽排序时的步骤更新
    if (caseGroupStore.caseGroupDetail) {
      caseGroupStore.caseGroupDetail.steps = value
    }
  }
})

// 当前激活的步骤
const activeNames = ref<string[]>([]);

// 加载状态直接从store获取
const loading = computed(() => caseGroupStore.loading)

// 组件挂载时不需要获取数据，因为父组件会通过store管理数据
onMounted(async () => {
  // 默认不展开任何步骤
  activeNames.value = [];
});

// 步骤拖拽结束事件处理
const onDragEnd = async () => {
  // 拖拽排序后，steps的computed setter会自动更新store中的数据
  // 这里只需要更新每个步骤的order并保存
  const updatedSteps = steps.value.map((step, index) => ({
    ...step,
    step_order: index + 1  // 从1开始编号
  }));
  
  // 触发每个步骤的更新以确保子组件同步
  for (const step of updatedSteps) {
    await caseGroupStore.updateStep(step.step_id || (step as any).id, step);
  }
  
  ElMessage.success('步骤顺序已更新');
};

// 添加新步骤
const addNewStep = async () => {
  console.log('🔥 addNewStep被调用，当前步骤数量:', steps.value.length);
  
  try {
    // 直接调用 Pinia store 的 addNewStep 方法
    await caseGroupStore.addNewStep();
    
    // 自动展开新添加的步骤（获取最后一个步骤）
    const newStep = caseGroupStore.steps[caseGroupStore.steps.length - 1];
    if (newStep) {
      activeNames.value = [newStep.step_id.toString()];
    }
    
    console.log('🎯 addNewStep完成，最终steps数组:', steps.value.map(s => ({ id: s.step_id, name: s.step_name })));
    ElMessage.success('已添加新步骤');
  } catch (error) {
    console.error('❌ 添加新步骤失败:', error);
    ElMessage.error('添加新步骤失败，请稍后重试');
  }
};

// 删除步骤
const removeStep = async (id: number) => {
  ElMessageBox.confirm(
    '确定要删除此步骤吗？此操作不可撤销。',
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  )
    .then(async () => {
      try {
        await caseGroupStore.removeStep(id);
        ElMessage.success('步骤已删除');
      } catch (error) {
        console.error('❌ 删除步骤失败:', error);
        ElMessage.error('删除步骤失败，请稍后重试');
      }
    })
    .catch(() => {
      ElMessage.info('已取消删除');
    });
};

// 更新步骤名称
const updateStepName = (stepId: number, newName: string) => {
  console.log(`📝 更新步骤名称: ID=${stepId}, 新名称="${newName}"`);
  
  // 由于使用了computed，直接修改store中的数据
  const step = caseGroupStore.steps.find(step => 
    step.step_id === stepId || (step as any).id === stepId
  );
  
  if (step) {
    step.step_name = newName;
    console.log('✅ 步骤名称更新成功');
  } else {
    console.warn(`⚠️ 未找到步骤 ID: ${stepId}`);
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
    // console.log('✅ 找到步骤，更新索引:', stepIndex);
    // 合并数据，确保保留原始数据的结构
    const originalStep = steps.value[stepIndex];
    
    // 修复：确保stepData.step_name不为空，如果为空则保留原始步骤名称
    if (!stepData.step_name || stepData.step_name === '') {
      if (originalStep.step_name) {
        // 如果原步骤有名称，则保留原名称
        // console.log(`⚠️ 发现stepData.step_name为空，保留原步骤名称: "${originalStep.step_name}"`);
        stepData.step_name = originalStep.step_name;
      } else {
        // 如果原步骤也没有名称，则设置默认名称
        stepData.step_name = `步骤${originalStep.step_order || stepIndex + 1}`;
        // console.log(`⚠️ 发现步骤名称缺失，设置默认名称: "${stepData.step_name}"`);
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

// 获取步骤状态类型
const getStepStatusType = (status: any): '' | 'success' | 'warning' | 'info' | 'danger' => {
  if (!status) return '';
  
  const statusNum = Number(status);
  if (isNaN(statusNum)) return '';
  
  switch (statusNum) {
    case 0: return 'info';      // 等待执行
    case 1: return 'danger';    // 执行失败
    case 2: return 'warning';   // 执行中
    case 3: return 'success';   // 执行完成
    case 4: return 'success';   // 执行成功
    case 5: return 'info';      // 跳过执行
    case 6: return 'warning';   // 手动中断
    case 7: return 'info';      // 已禁用
    case 8: return 'danger';    // 失败停止
    default: return '';
  }
};

// 获取步骤状态文本
const getStepStatusText = (status: any): string => {
  if (!status) return '';
  
  const statusNum = Number(status);
  if (isNaN(statusNum)) return '';
  
  switch (statusNum) {
    case 0: return '等待执行';
    case 1: return '执行失败';
    case 2: return '执行中';
    case 3: return '执行完成';
    case 4: return '执行成功';
    case 5: return '跳过执行';
    case 6: return '已中断';
    case 7: return '已禁用';
    case 8: return '失败停止';
    default: return '';
  }
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

// 获取当前的步骤数据
const getStepsData = () => {
  // 直接从Pinia store返回步骤数据
  return caseGroupStore.steps;
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
  padding: 8px 0;
  
  // 添加自定义滚动条
  &::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  
  &::-webkit-scrollbar-thumb {
    background-color: rgba(144, 147, 153, 0.3);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-track {
    background-color: rgba(144, 147, 153, 0.1);
    border-radius: 3px;
  }
  
  .case-group-info {
    background-color: #fff;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
    
    h2 {
      margin: 0 0 16px 0;
      font-size: 22px;
      color: #303133;
      font-weight: 600;
      position: relative;
      padding-bottom: 10px;
      
      &:after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 40px;
        height: 3px;
        background-color: #409eff;
        border-radius: 3px;
      }
    }
    
    .info-row {
      margin: 8px 0;
      display: flex;
      align-items: center;
      
      .label {
        color: #606266;
        margin-right: 10px;
        font-weight: 500;
        min-width: 80px;
      }
      
      .value {
        color: #303133;
        font-weight: 400;
      }
    }
  }
  
  .steps-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    background-color: #fff;
    padding: 16px 20px;
    border-radius: 10px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    
    h2 {
      margin: 0;
      font-size: 18px;
      color: #303133;
      font-weight: 600;
      display: flex;
      align-items: center;
      
      &:before {
        content: '';
        display: inline-block;
        width: 4px;
        height: 18px;
        background-color: #409eff;
        margin-right: 10px;
        border-radius: 2px;
      }
    }
    
    .actions {
      display: flex;
      gap: 10px;
      
      .el-button {
        border-radius: 8px;
        padding: 8px 16px;
        transition: all 0.2s ease;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
      }
    }
  }
  
  .steps-container {
    background: #f9fafc;
    border-radius: 8px;
    padding: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
    
    .step-item {
      margin-bottom: 16px;
      border-radius: 8px;
      background-color: #fff;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
      transition: all 0.3s ease;
      overflow: hidden;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
      }
      
      &:last-child {
        margin-bottom: 0;
      }
      
      .step-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 4px 8px;
        width: 100%;
        
        .drag-handle {
          cursor: move;
          color: #909399;
          background-color: #f5f7fa;
          padding: 8px;
          border-radius: 6px;
          transition: all 0.2s ease;
          
          &:hover {
            color: #409eff;
            background-color: #ecf5ff;
            transform: scale(1.1);
          }
        }
        
        .step-number {
          font-weight: 600;
          color: #409eff;
          background: rgba(64, 158, 255, 0.1);
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 14px;
          min-width: 70px;
          text-align: center;
          box-shadow: 0 2px 4px rgba(64, 158, 255, 0.1);
        }
        
        .step-title {
          color: #303133;
          font-weight: 500;
          font-size: 15px;
          flex-grow: 1;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          padding: 0 8px;
        }
        
        .step-badges {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-right: 8px;
          
          .status-badge, .count-badge {
            padding: 0 8px;
            height: 24px;
            line-height: 24px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
            
            &:hover {
              transform: scale(1.05);
            }
          }
          
          .count-badge {
            background-color: #f0f9ff;
            color: #409eff;
            border-color: #d9ecff;
          }
        }
      }
    }
  }
}

/* 拖拽时的样式 */
.ghost {
  opacity: 0.7;
  background: #e8f4fe;
  border: 2px dashed #409eff;
  border-radius: 8px;
  box-shadow: 0 0 0 4px rgba(64, 158, 255, 0.2);
  transform: scale(1.02);
}

/* 自定义el-collapse样式 */
:deep(.el-collapse) {
  border: none;
}

:deep(.el-collapse-item) {
  border-bottom: none;
  overflow: hidden;
  
  .el-collapse-item__header {
    background-color: #fff;
    padding: 12px 16px;
    border-bottom: none;
    transition: all 0.3s ease;
    
    &:hover {
      background-color: #f8fcff;
    }
    
    &.is-active {
      border-bottom-color: #ebeef5;
      background-color: #f0f9ff;
    }
    
    .el-collapse-item__arrow {
      margin-right: 8px;
      transition: transform 0.3s;
      color: #409eff;
    }
  }
  
  .el-collapse-item__wrap {
    background-color: #fff;
    
    .el-collapse-item__content {
      padding: 16px 20px;
      background-color: #fafbfc;
      border-top: 1px solid #ebeef5;
      border-bottom-left-radius: 8px;
      border-bottom-right-radius: 8px;
    }
  }
}

/* 步骤操作按钮区域 */
.step-actions {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0 4px;
  margin-top: 12px;
  border-top: 1px dashed #e0e5ee;
  
  .el-button {
    border-radius: 6px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 6px;
    
    &:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    &.delete-btn {
      background-color: #fff5f5;
      color: #f56c6c;
      border-color: #fde2e2;
      
      &:hover {
        background-color: #f56c6c;
        color: #ffffff;
        border-color: #f56c6c;
      }
    }
  }
}
</style>
