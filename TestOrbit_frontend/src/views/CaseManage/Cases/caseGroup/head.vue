
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
              :props="{
                checkStrictly: false,
                expandTrigger: 'hover',
                value: 'value',
                label: 'label',
                children: 'children',
                multiple: false,
                emitPath: true
              }"
              :show-all-levels="true" 
              clearable
              :loading="isLoading"
              placeholder="请选择所属模块"
              @change="handleModuleChange"
            >
              <template #empty>
                <div v-if="isLoading" class="loading-text">
                  加载数据中，请稍候...
                </div>
                <div v-else class="empty-text">
                  暂无数据
                </div>
              </template>
            </el-cascader>
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

  <el-dialog v-model="showGlobalVarDialog"  fullscreen @close="closeDialog">
    <GlobalVar />
  </el-dialog>

  <el-dialog v-model="showRegionVarDialog" title="场景变量配置" fullscreen @close="closeDialog">
    <RegionVar />
  </el-dialog>



</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import type { FormInstance, FormRules } from 'element-plus';
import { getCaseFolderTree } from '@/api/case';
import type { TestModuleNode } from '@/api/case/types';

// 引入自定义组件
import RegionVar from './env/region_var.vue';
import GlobalVar from './env/global_var.vue';

// 定义级联选择器需要的选项类型
interface CascaderOption {
  value: string;
  label: string;
  children?: CascaderOption[];
}

/**
 * 将API返回的模块树转换为级联选择器所需的格式
 * @param moduleNodes 后端返回的模块节点数组
 * @param depth 当前深度，用于调试
 * @returns 适用于级联选择器的选项数组
 */
function transformToCascaderOptions(moduleNodes: TestModuleNode[], depth: number = 0): CascaderOption[] {
  return moduleNodes.map(node => {
    // 创建级联选择器选项
    const option: CascaderOption = {
      value: node.id,
      label: node.name,
    };
    
    // 递归处理子节点，支持任意深度的嵌套
    if (node.children && node.children.length > 0) {
      option.children = transformToCascaderOptions(node.children, depth + 1);
      console.log(`第${depth}级模块 "${node.name}" 有 ${option.children.length} 个子模块`);
    }
    
    return option;
  });
}

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


onMounted(() => {
  // 初始化时获取用例组所属模块数据
  console.log('组件已挂载，正在获取模块数据...');
  fetchCaseFolderTree();
});


// 用例组所属模块 - 使用我们定义的CascaderOption类型
const options = ref<CascaderOption[]>([
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
]);

// 加载状态
const isLoading = ref(false);

// 获取用例组所属模块数据
const fetchCaseFolderTree = async () => {
  // 设置加载状态
  isLoading.value = true;
  
  try {
    const response = await getCaseFolderTree();
    
    if (response && response.code === 200) {
      if (response.results && response.results.length > 0) {
        // 使用响应式API更新options
        // 转换为级联选择器需要的格式
        const cascaderOptions = transformToCascaderOptions(response.results);
        options.value = cascaderOptions;
        console.log('成功加载模块数据:', cascaderOptions);
        
        // 分析模块树的深度
        const maxDepth = analyzeTreeDepth(cascaderOptions);
        console.log(`模块树最大深度为: ${maxDepth}级`);
        
        // 如果数据很多，显示一些统计信息
        if (cascaderOptions.length > 0) {
          console.log(`顶级模块数量: ${cascaderOptions.length}`);
          cascaderOptions.forEach(option => {
            const childCount = option.children?.length || 0;
            console.log(`模块 "${option.label}" 有 ${childCount} 个子模块`);
          });
        }
      } else {
        console.warn('模块数据为空');
        // 如果没有数据，设置一个默认选项或清空选项
        options.value = [];
      }
    } else {
      console.error('获取模块数据失败:', response.msg);
      // 可以在这里添加错误提示，例如使用 Element Plus 的 Message 组件
      // ElMessage.error(response.msg || '获取用例组所属模块数据失败');
    }
  } catch (error) {
    console.error('获取用例组所属模块数据失败:', error);
    // ElMessage.error('网络错误，获取用例组所属模块数据失败');
  } finally {
    // 无论成功还是失败，都需要关闭加载状态
    isLoading.value = false;
  }
}

// 处理模块选择变更
const handleModuleChange = (value: string[]) => {
  console.log('选择的模块ID路径:', value);
  
  if (value && value.length > 0) {
    // 获取最后一级的模块ID (最具体的模块)
    const selectedModuleId = value[value.length - 1];
    console.log('最终选择的模块ID:', selectedModuleId);
    
    // 根据路径查找完整的模块信息
    const moduleInfo = findModuleByPath(value);
    console.log('选中的完整模块信息:', moduleInfo);
    
    // 这里可以添加更多的处理逻辑
    // 例如，根据所选模块获取相关数据
  } else {
    console.log('清空了模块选择');
  }
};

// 根据路径查找模块信息
const findModuleByPath = (path: string[]): CascaderOption | null => {
  if (!path || path.length === 0) return null;
  
  // 复制一份路径数组，因为我们会修改它
  const pathCopy = [...path];
  
  // 从第一级开始查找
  let currentLevel: CascaderOption[] = options.value;
  let currentModule: CascaderOption | null = null;
  
  // 逐级查找
  while (pathCopy.length > 0 && currentLevel) {
    const currentId = pathCopy.shift();
    currentModule = currentLevel.find(option => option.value === currentId) || null;
    
    // 如果找到了当前级别的模块且还有下一级要查找
    if (currentModule && pathCopy.length > 0) {
      currentLevel = currentModule.children || [];
    } else {
      break;
    }
  }
  
  return currentModule;
};

/**
 * 分析级联选择器树的最大深度
 * @param options 级联选择器选项
 * @param currentDepth 当前深度
 * @returns 树的最大深度
 */
const analyzeTreeDepth = (options: CascaderOption[], currentDepth: number = 1): number => {
  if (!options || options.length === 0) return 0;
  
  let maxDepth = currentDepth;
  
  for (const option of options) {
    if (option.children && option.children.length > 0) {
      const childDepth = analyzeTreeDepth(option.children, currentDepth + 1);
      maxDepth = Math.max(maxDepth, childDepth);
    }
  }
  
  return maxDepth;
};

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

/* 级联选择器中的加载和空数据样式 */
.loading-text {
  padding: 10px;
  color: #909399;
  text-align: center;
}

.empty-text {
  padding: 10px;
  color: #909399;
  text-align: center;
}
</style>