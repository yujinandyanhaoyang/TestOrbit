<template>
  <el-form-item label="所属模块" prop="module" required>
    <el-cascader 
      v-model="moduleValue"
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
</template>

<script setup lang="ts">
import { ref, reactive, onMounted,  watch } from 'vue';
import { getCaseFolderTree } from '@/api/case/module';
import type { TestModuleNode } from '@/api/case/module/types';

// 定义组件的输入属性
const props = defineProps({
  moduleId: {
    type: String,
    default: ''
  }
});

// 定义组件事件
const emit = defineEmits(['update:moduleValue', 'moduleChange']);

// 级联选择器的当前值
const moduleValue = ref<string[]>([]);

// 监听moduleValue的变化，向父组件发送更新事件
watch(moduleValue, (newValue) => {
  emit('update:moduleValue', newValue);
  
  // 当有值时，发送最后一级模块ID
  if (newValue && newValue.length > 0) {
    const selectedModuleId = newValue[newValue.length - 1];
    const moduleInfo = findModuleByPath(newValue);
    emit('moduleChange', {
      path: newValue,
      moduleId: selectedModuleId,
      moduleInfo
    });
  } else {
    // 当清空选择时
    emit('moduleChange', {
      path: [],
      moduleId: '',
      moduleInfo: null
    });
  }
}, { deep: true });

// 监听props.moduleId，当外部传入moduleId变化时更新选择器
watch(() => props.moduleId, async (newValue) => {
  if (newValue && options.value.length > 0) {
    await findAndSetModulePath(newValue);
  }
}, { immediate: true });

// 定义级联选择器需要的选项类型
interface CascaderOption {
  value: string;
  label: string;
  children?: CascaderOption[];
}

// 用例组所属模块 - 使用我们定义的CascaderOption类型
const options = ref<CascaderOption[]>([]);

// 加载状态
const isLoading = ref(false);

onMounted(() => {
  // 初始化时获取用例组所属模块数据
  // console.log('模块选择组件已挂载，正在获取模块数据...');
  fetchCaseFolderTree();
});

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
    }
    
    return option;
  });
}

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
        
        // 如果有初始moduleId，尝试设置级联路径
        if (props.moduleId) {
          await findAndSetModulePath(props.moduleId);
        }
      } else {
        console.warn('模块数据为空');
        options.value = [];
      }
    } else {
      console.error('获取模块数据失败:', response.msg);
    }
  } catch (error) {
    console.error('获取用例组所属模块数据失败:', error);
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
 * 根据模块ID查找级联选择器路径
 * @param moduleId 要查找的模块ID
 * @returns 查找到的模块路径(数组形式)
 */
const findModulePath = (moduleId: string, currentOptions: CascaderOption[] = options.value, currentPath: string[] = []): string[] | null => {
  if (!moduleId || !currentOptions || currentOptions.length === 0) return null;
  
  for (const option of currentOptions) {
    // 检查当前选项是否匹配
    if (option.value === moduleId) {
      return [...currentPath, option.value];
    }
    
    // 如果有子项，递归查找
    if (option.children && option.children.length > 0) {
      const result = findModulePath(moduleId, option.children, [...currentPath, option.value]);
      if (result) {
        return result;
      }
    }
  }
  
  return null;
};

/**
 * 查找并设置模块路径
 * 这个函数会尝试根据moduleId找到级联选择器的路径并设置选择器的值
 */
const findAndSetModulePath = async (moduleId: string) => {
  // 确保选项已加载
  if (options.value.length === 0) {
    await fetchCaseFolderTree();
  }
  
  // 查找模块路径
  const path = findModulePath(moduleId);
  if (path) {
    moduleValue.value = path;
    // console.log('已设置模块路径:', path);
  } else {
    console.warn(`未找到模块ID为 ${moduleId} 的路径`);
    // 如果只有moduleId但找不到路径，可以设置单值
    if (moduleId) {
      moduleValue.value = [moduleId];
    }
  }
};
</script>

<style scoped lang="scss">
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
