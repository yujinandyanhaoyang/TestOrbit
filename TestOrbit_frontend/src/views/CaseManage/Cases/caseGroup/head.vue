
<template>
    <div class="case-group-head">
        <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px" inline>
          <el-form-item label="用例组名称" prop="name" required>
            <el-input
              v-model="formData.name"
              style="width: 240px"
              placeholder="请输入用例组名称"
              clearable
            />
          </el-form-item>
          <!-- 使用新的模块选择组件 -->
          <ModulePath 
            v-model:moduleValue="formData.module" 
            :moduleId="props.moduleId" 
            @moduleChange="handleModuleChangeEvent" 
          /> 
        </el-form>
        <div class="action-buttons">
          <el-button type="primary" @click="openDialog('global')">全局变量</el-button>
          <el-button type="primary" @click="openDialog('region')">场景变量</el-button>
          <el-button type="primary">一键运行</el-button>
          <el-button type="primary" @click="handleSave">保存</el-button>
          <el-button type="primary" @click="handleAddStep">添加步骤</el-button>
        </div>
    </div>

  <el-dialog v-model="showGlobalVarDialog"  fullscreen @close="closeDialog">
    <GlobalVar />
  </el-dialog>

  <el-dialog v-model="showRegionVarDialog" title="场景变量配置" fullscreen @close="closeDialog">
    <RegionVar />
  </el-dialog>


</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage } from 'element-plus';
import { addCaseGroup } from '@/api/case/caseGroup';

// 定义组件可以发射的事件
const emit = defineEmits(['add-step', 'save-order', 'get-steps-data', 'case-saved']);

// 定义组件接收的属性，包括ListDetail组件的引用

const props = defineProps<{
  caseId?: number          // 可选，更新时需要
  caseName: string        // 用例组名称
  moduleId?: string        // 模块ID
  listDetailRef?: any      // ListDetail组件引用
}>()

// 引入自定义组件
import RegionVar from './env/region_var.vue';
import GlobalVar from './env/global_var.vue';
import ModulePath from './modulePath.vue';


// 表单引用
const formRef = ref<FormInstance>();
// 环境id，暂时写为固定值1

// 表单数据
const formData = reactive({
  id: props.caseId,
  name: props.caseName || '',
  module_id: props.moduleId || '',
  module: [] as string[],  // 由ModulePath组件控制，期望是字符串数组
});

// 监听props变化，更新表单数据
watch(() => props.caseName, (newValue) => {
  if (newValue) {
    // console.log('用例组名称更新为formData.name:', newValue);
    formData.name = newValue;
  }
}, { immediate: true });


// 处理模块选择变更事件
const handleModuleChangeEvent = (data: { path: string[], moduleId: string, moduleInfo: any }) => {
  // 更新formData中的module_id
  formData.module_id = data.moduleId;
  // console.log('模块选择已更新:', data);
};

// 使用两个独立的布尔变量来控制对话框显示
const showGlobalVarDialog = ref(false);
const showRegionVarDialog = ref(false);

// 保留这个变量用于记录当前打开的对话框类型
const dialogVisibleType = ref<'global' | 'region' | null>(null);


onMounted(() => {
  // 初始化时的操作，如果有需要
  // console.log('head组件已挂载');
});

/**
 * 打开指定类型的对话框
 * @param type 对话框类型：'global' 或 'region'
 */
const openDialog = (type: 'global' | 'region') => {
  dialogVisibleType.value = type;
  if (type === 'global') {
    showGlobalVarDialog.value = true;
  } else if (type === 'region') {
    showRegionVarDialog.value = true;
  }
};

/**
 * 关闭当前打开的对话框
 */
const closeDialog = () => {
  if (dialogVisibleType.value === 'global') {
    showGlobalVarDialog.value = false;
  } else if (dialogVisibleType.value === 'region') {
    showRegionVarDialog.value = false;
  }
  dialogVisibleType.value = null;
};

/**
 * 保存对话框内容并关闭对话框
 */
const saveDialog = () => {
  // 这里可以添加保存逻辑
  console.log('保存', dialogVisibleType.value, '变量配置');
  
  // 保存完成后关闭对话框
  closeDialog();
};

// 表单校验规则
const rules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入用例组名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度应为2到50个字符', trigger: 'blur' }
  ],
  module: [
    { required: true, message: '请选择所属模块', trigger: 'change' }
  ]
});



const handleSave = async () => {

  // 从ListDetail组件获取步骤数据
  let steps = [];
  
  if (props.listDetailRef && typeof props.listDetailRef.getStepsData === 'function') {
    // 获取最新的步骤数据
    steps = props.listDetailRef.getStepsData();
    
    // 处理步骤数据的字段一致性问题：
    // 1. 新步骤（临时负数ID）：移除step_id，让服务器分配新ID
    // 2. 已有步骤（正数ID）：保留step_id用于更新
    steps = steps.map((step: any) => {
      const processedStep = { ...step }; // 创建副本避免修改原对象
      
      // 修复：确保step_name字段存在且有值
      if (!processedStep.step_name || processedStep.step_name === '') {
        // 如果步骤名称为空，设置一个默认名称
        processedStep.step_name = `步骤${processedStep.step_order || ''}`;
        console.log(`⚠️ 步骤名称为空，设置默认名称: "${processedStep.step_name}"`);
      }
      
      // 检查是否是新步骤（我们用负数作为临时ID）
      if (step.step_id && step.step_id < 0) {
        // 新步骤：移除step_id让服务器分配新ID
        delete processedStep.step_id;
        console.log(`🆕 新步骤 "${processedStep.step_name}" 移除临时ID，等待服务器分配真实ID`);
      } else if (step.step_id && step.step_id > 0) {
        // 已有步骤：保留step_id用于更新
        console.log(`✏️ 已有步骤 "${processedStep.step_name}" (ID: ${step.step_id}) 保持ID用于更新`);
      } else if (step.id && !step.step_id) {
        // 兼容性处理：如果有id但没有step_id，则添加step_id = id
        processedStep.step_id = step.id;
        console.log(`🔄 步骤 "${processedStep.step_name}" 字段转换: id -> step_id`);
      }
      
      // 确保所有必要的字段都存在
      if (!processedStep.params) {
        console.warn(`步骤 ${processedStep.step_name || '未命名'} 缺少params字段，使用默认值`);
        processedStep.params = {}; // 确保params字段存在
      }
      
      return processedStep;
    });
    
    // 检查是否有步骤数据
    if (steps.length === 0) {
      console.warn('没有找到任何步骤数据');
    } else {
      console.log(`获取到 ${steps.length} 个步骤的最新数据`);
    }
  } else {
    console.warn('无法获取ListDetail组件引用或getStepsData方法');
    if (props.listDetailRef) {
      console.log('listDetailRef可用的方法:', Object.keys(props.listDetailRef));
    }
    // 使用空数组作为后备方案
    steps = [];
  }
  
  // 组装请求体数据 - 根据 AddCaseGroupRequest 接口定义
  const requestData = {
    name: formData.name,            // 用例组名称
    module_id: formData.module_id,  // 模块ID
    env_id: 1,                      // 环境ID，暂时写死为1
    case_id: props.caseId,          // 用例组ID，更新时需要
    steps                           // 测试步骤列表
  };
  
  // console.log('🚀 准备保存的数据:', requestData);
  // console.log('📋 步骤详情:', steps.map((s: any) => ({
  //   name: s.step_name,
  //   hasStepId: !!s.step_id,
  //   stepId: s.step_id,
  //   isNew: !s.step_id ? '新步骤(无ID)' : s.step_id < 0 ? '临时步骤(负ID)' : '已有步骤(正ID)'
  // })));
  
  // 使用addCaseGroup提交
  try {
    const response = await addCaseGroup(requestData);
    if (response.code === 200) {
      ElMessage.success('用例组保存成功');
      console.log('保存成功:', response.results);
      
      // 如果是新建（没有case_id），可以使用返回的ID更新当前ID
      if (!props.caseId && response.results.id) {
        // 这里可以通过emit通知父组件ID已更新
        emit('case-saved', response.results.id);
      }
    } else {
      ElMessage.error(response.msg || '保存失败，请重试');
      console.error('保存失败:', response.msg);
    }
  } catch (error) {
    ElMessage.error('保存请求发生错误，请重试');
    console.error('保存请求失败:', error);
  }
}
 
// 添加步骤按钮处理函数
const handleAddStep = () => {
  // 触发添加步骤事件，ListDetail组件会监听此事件
  emit('add-step');
}


</script>


<style scoped lang="scss">
.case-group-head {
  padding: 15px;
  border-bottom: 1px solid #eee;
  
  .el-form {
    margin-bottom: 15px;
  }
  
  .action-buttons {
    display: flex;
    gap: 10px;
    margin-top: 15px;
  }
}

/* 级联选择器样式已移至modulePath.vue */
</style>