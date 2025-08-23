
<template>
    <div class="case-group-head">
        <el-form :model="formData" :rules="rules" ref="formRef" label-width="100px" inline>
          <el-form-item label="用例组名称" prop="groupName" required>
            <el-input
              v-model="formData.groupName"
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
          <el-button type="success" @click="handleSaveOrder">保存顺序</el-button>
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
import { ref, reactive, onMounted,watch } from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
import { addCaseGroup } from '@/api/case/caseGroup';

// 定义组件可以发射的事件
const emit = defineEmits(['add-step', 'save-order', 'get-steps-data']);

// 定义组件接收的属性，包括ListDetail组件的引用
const props = defineProps({
  caseName: {
    type: String,
    default: ''
  },
  moduleId: {
    type: String,
    default: ''
  },
  listDetailRef: {
    type: Object,
    default: null
  }
});

// 引入自定义组件
import RegionVar from './env/region_var.vue';
import GlobalVar from './env/global_var.vue';
import ModulePath from './modulePath.vue';


// 表单引用
const formRef = ref<FormInstance>();


// 表单数据
const formData = reactive({
  id: props.moduleId || '',
  groupName: props.caseName || '',
  module_id: props.moduleId || '',
  module: []  // 由ModulePath组件控制
});

// 监听props变化，更新表单数据
watch(() => props.caseName, (newValue) => {
  if (newValue) {
    formData.groupName = newValue;
  }
}, { immediate: true });

// 处理模块选择变更事件
const handleModuleChangeEvent = (data: { path: string[], moduleId: string, moduleInfo: any }) => {
  // 更新formData中的module_id
  formData.module_id = data.moduleId;
  console.log('模块选择已更新:', data);
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
  groupName: [
    { required: true, message: '请输入用例组名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度应为2到50个字符', trigger: 'blur' }
  ],
  module: [
    { required: true, message: '请选择所属模块', trigger: 'change' }
  ]
});



const handleSave = async () => {
  // 使用formData中的数据
  const name = formData.groupName;
  
  // 获取选择的模块ID，现在由ModulePath组件通过handleModuleChangeEvent更新
  const module_id = formData.module_id || props.moduleId;
  const module_related = module_id ? [module_id] : [];
  
  // 从ListDetail组件获取步骤数据
  let steps = [];
  
  if (props.listDetailRef && typeof props.listDetailRef.getStepsData === 'function') {
    steps = props.listDetailRef.getStepsData();
    console.log('从ListDetail获取到的步骤数据:');
    console.log('- 步骤数量:', steps.length);
    console.log('- 完整数据:', steps);
    
    // 验证每个步骤的数据完整性
    steps.forEach((step: any, index: number) => {
      console.log(`步骤 ${index + 1} (ID: ${step.id}):`, {
        step_name: step.step_name,
        type: step.type,
        params: step.params ? '有参数' : '无参数',
        params_detail: step.params
      });
    });
  } else {
    console.warn('无法获取ListDetail组件引用或getStepsData方法');
    console.log('props.listDetailRef:', props.listDetailRef);
    if (props.listDetailRef) {
      console.log('listDetailRef的方法:', Object.keys(props.listDetailRef));
    }
    // 使用空数组作为后备方案
    steps = [];
  }
  
  // 组装请求体数据
  const requestData = {
    name,
    module_id,
    module_related,
    // 如果是编辑模式，需要提供id
    id: props.moduleId ? 11 : undefined, // 这里可以根据实际情况修改或通过props传入
    steps // 使用ListDetail组件提供的步骤数据
  };
  
  console.log('准备保存的数据:', requestData);
  
  // 使用addCaseGroup提交
  try {
    const response = await addCaseGroup(requestData);
    if (response.code === 200 && response.success) {
      console.log('保存成功:', response.results);
      // 可以添加提示或其他操作
    } else {
      console.error('保存失败:', response.msg);
    }
  } catch (error) {
    console.error('保存请求失败:', error);
  }
}

// 添加步骤按钮处理函数
const handleAddStep = () => {
  // 触发添加步骤事件，ListDetail组件会监听此事件
  emit('add-step');
}

// 保存顺序按钮处理函数
const handleSaveOrder = () => {
  // 触发保存顺序事件，ListDetail组件会监听此事件
  emit('save-order');
}

// 处理步骤更新事件
const handleStepsUpdated = (updatedSteps: any[]) => {
  console.log('步骤列表已更新:', updatedSteps);
  // 这里可以添加其他处理逻辑，比如保存到状态管理器等
};

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