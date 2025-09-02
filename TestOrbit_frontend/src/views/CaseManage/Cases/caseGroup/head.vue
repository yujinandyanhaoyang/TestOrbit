
<template>
    <div class="case-group-head">
        <h2 class="page-title">{{ props.isNew ? '创建新用例组' : '编辑用例组' }}</h2>
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
          <template v-if="!props.isNew">
            <el-button type="primary" @click="openDialog('global')">全局变量</el-button>
            <el-button type="primary" @click="openDialog('region')">场景变量</el-button>
            <el-button type="primary">一键运行</el-button>
          </template>
          <el-button type="primary" @click="handleSave">{{ props.isNew ? '创建' : '保存' }}</el-button>
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
// 导入Pinia store
import { useCaseGroupStore } from '@/store/caseGroupStore';

// 定义组件可以发射的事件
const emit = defineEmits(['add-step', 'save-order', 'get-steps-data', 'case-saved']);

// 使用Pinia store
const caseGroupStore = useCaseGroupStore();

// 定义组件接收的属性，包括ListDetail组件的引用

const props = defineProps<{
  caseId?: number          // 可选，更新时需要
  caseName: string        // 用例组名称
  moduleId?: string        // 模块ID
  listDetailRef?: any      // ListDetail组件引用
  isNew?: boolean          // 新增标志
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
  // 🔥 优化：直接从Pinia store获取步骤数据，不再依赖组件引用
  let steps = [];
  
  if (caseGroupStore.caseGroupDetail && caseGroupStore.steps.length > 0) {
    // 从store获取最新的步骤数据
    steps = caseGroupStore.steps.map((step: any) => {
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
        // 已有步骤：确保step_id = step.id，用于后端识别和更新
        if (step.id) {
          processedStep.step_id = step.id;
          console.log(`✏️ 已有步骤 "${processedStep.step_name}" 设置step_id = ${step.id} (来自step.id)`);
        } else {
          processedStep.step_id = step.step_id;
          console.log(`✏️ 已有步骤 "${processedStep.step_name}" 保持step_id = ${step.step_id}`);
        }
      } else if (step.id && !step.step_id) {
        // 兼容性处理：如果有id但没有step_id，则设置step_id = id
        processedStep.step_id = step.id;
        console.log(`🔄 步骤 "${processedStep.step_name}" 设置step_id = ${step.id} (从id字段)`);
      }
      
      // 确保所有必要的字段都存在
      if (!processedStep.params) {
        console.warn(`步骤 ${processedStep.step_name || '未命名'} 缺少params字段，使用默认值`);
        processedStep.params = {}; // 确保params字段存在
      }
      
      return processedStep;
    });
    
    console.log(`从Store获取到 ${steps.length} 个步骤的最新数据`);
  } else {
    console.warn('Store中没有找到用例组详情或步骤数据');
    
    // 降级：尝试从组件引用获取数据（向后兼容）
    if (props.listDetailRef && typeof props.listDetailRef.getStepsData === 'function') {
      console.log('🔄 降级使用组件引用获取步骤数据');
      steps = props.listDetailRef.getStepsData();
    } else {
      steps = [];
    }
  }
  
  // 组装请求体数据 - 根据 AddCaseGroupRequest 接口定义
  const requestData: any = {
    name: formData.name,            // 用例组名称
    module_id: formData.module_id,  // 模块ID
    env_id: 1,                      // 环境ID，暂时写死为1
    steps                           // 测试步骤列表
  };
  
  // 如果是编辑模式而非新建模式，添加case_id参数
  if (!props.isNew && props.caseId) {
    requestData.case_id = props.caseId;
  }
  
  // 使用addCaseGroup提交
  try {
    const response = await addCaseGroup(requestData);
    if (response.code === 200) {
      // 根据模式显示不同的成功消息
      ElMessage.success(props.isNew ? '用例组创建成功' : '用例组保存成功');
      console.log(props.isNew ? '创建成功:' : '保存成功:', response.results);
      
      // 🔥 修复：获取正确的用例ID
      // 对于新建模式，使用服务器返回的新ID；对于编辑模式，使用原有ID
      const caseId = props.isNew ? response.results.case_id : props.caseId;
      if (caseId) {
        console.log(`🔄 重新获取用例组详情，caseId: ${caseId}，更新步骤ID...`);
        
        try {
          // 重新从后端获取最新的用例组详情
          await caseGroupStore.fetchCaseGroupDetail(caseId);
          
          console.log('🎉 步骤信息已更新！当前所有步骤:', 
            caseGroupStore.steps.map(s => ({ 
              name: s.step_name, 
              step_id: s.step_id,
              isRealId: s.step_id > 0 ? '真实ID' : '临时ID'
            }))
          );
          
          // 如果是新建模式，通知父组件用例已创建并返回新ID
          // 🔥 修复：使用正确的响应字段 case_id
          if (props.isNew && response.results.case_id) {
            emit('case-saved', response.results.case_id);
          }
        } catch (fetchError) {
          console.error('❌ 重新获取用例组详情失败:', fetchError);
          // 即使重新获取失败，保存操作本身是成功的
          // 对于新建模式，仍然要通知父组件创建成功
          if (props.isNew && response.results.case_id) {
            emit('case-saved', response.results.case_id);
          }
        }
      } else {
        console.warn('⚠️ 未能获取到有效的caseId');
        // 对于新建模式，即使没有caseId也要通知父组件
        if (props.isNew && response.results.case_id) {
          emit('case-saved', response.results.case_id);
        }
      }
    } else {
      ElMessage.error(response.msg || (props.isNew ? '创建失败' : '保存失败') + '，请重试');
      console.error(props.isNew ? '创建失败:' : '保存失败:', response.msg);
    }
  } catch (error) {
    ElMessage.error(props.isNew ? '创建请求发生错误' : '保存请求发生错误' + '，请重试');
    console.error(props.isNew ? '创建请求失败:' : '保存请求失败:', error);
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
  
  .page-title {
    margin: 0 0 20px 0;
    font-size: 22px;
    font-weight: 500;
    color: #303133;
  }
  
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