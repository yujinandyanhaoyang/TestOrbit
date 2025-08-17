
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
          <el-form-item label="所属模块" prop="module" required>
            <el-cascader 
              v-model="formData.module"
              :options="options" 
              :show-all-levels="false" 
              clearable
              placeholder="请选择所属模块"
            />
          </el-form-item>
        </el-form>
        <div class="action-buttons">
          <el-button type="primary" @click="openDialog('global')">全局变量</el-button>
          <el-button type="primary" @click="openDialog('region')">场景变量</el-button>
          <el-button type="primary">新增用例</el-button>
          <el-button type="primary">一键运行</el-button>
          <el-button type="primary">保存</el-button>
        </div>
    </div>

  <el-dialog v-model="showGlobalVarDialog" title="全局变量配置" fullscreen @close="closeDialog">
    
    <GlobalVar />
  </el-dialog>

  <el-dialog v-model="showRegionVarDialog" title="场景变量配置" fullscreen @close="closeDialog">
    <RegionVar />
  </el-dialog>



</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
// 引入自定义组件
import RegionVar from './env/region_var.vue';
import GlobalVar from './env/global_var.vue';

// 表单引用
const formRef = ref<FormInstance>();

// 表单数据
const formData = reactive({
  groupName: '用例组001',
  module: []
});

// 使用两个独立的布尔变量来控制对话框显示
const showGlobalVarDialog = ref(false);
const showRegionVarDialog = ref(false);

// 保留这个变量用于记录当前打开的对话框类型
const dialogVisibleType = ref<'global' | 'region' | null>(null);





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

// 用例组所属模块
const options = [
  {
    value: 'guide',
    label: 'Guide',
    children: [
      {
        value: 'disciplines',
        label: 'Disciplines',
        children: [
          {
            value: 'consistency',
            label: 'Consistency',
          },
          {
            value: 'feedback',
            label: 'Feedback',
          },
          {
            value: 'efficiency',
            label: 'Efficiency',
          },
          {
            value: 'controllability',
            label: 'Controllability',
          },
        ],
      },
    ],
  },
]

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
</style>