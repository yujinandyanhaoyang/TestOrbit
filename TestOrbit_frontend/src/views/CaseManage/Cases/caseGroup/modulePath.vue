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
      style="width: 240px"
      :show-all-levels="true" 
      clearable
      :loading="isLoading"
      :placeholder="modulePlaceholder"
      @focus="handleFocus"
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
import { ref, reactive, onMounted, watch, computed } from 'vue';
import { getCaseFolderTree, getTestModuleDetail } from '@/api/case/module';
import type { TestModuleNode } from '@/api/case/module/types';
import { useCaseModuleStore } from '@/store/caseModule';

// 定义组件的输入属性
const props = defineProps({
  moduleId: {
    type: String,
    default: ''
  }
});

// 定义组件事件
const emit = defineEmits(['update:moduleValue', 'moduleChange']);

// 使用 Pinia store 获取当前选中的项目ID
const caseModuleStore = useCaseModuleStore();

// 级联选择器的当前值
const moduleValue = ref<string[]>([]);

// 模块名称（用于显示在placeholder中）
const moduleName = ref<string>('');

// 模块选择器的placeholder
const modulePlaceholder = computed(() => {
  return moduleName.value ? `${moduleName.value}` : '请选择所属模块';
});

// 监听moduleValue的变化，向父组件发送更新事件
watch(moduleValue, (newValue, oldValue) => {
  // console.log(`🔄 moduleValue变化: ${JSON.stringify(oldValue)} -> ${JSON.stringify(newValue)}`);
  emit('update:moduleValue', newValue);
  
  // 当有值时，发送最后一级模块ID
  if (newValue && newValue.length > 0) {
    const selectedModuleId = newValue[newValue.length - 1];
    // console.log(`📍 选中的模块ID: ${selectedModuleId}`);
    
    const moduleInfo = findModuleByPath(newValue);
    
    // 只有在找到模块信息时才更新模块名称，避免覆盖已有的正确名称
    if (moduleInfo) {
      const newModuleName = moduleInfo.label;
      if (moduleName.value !== newModuleName) {
        moduleName.value = newModuleName;
        // console.log(`📝 更新模块名称: ${newModuleName}`);
      }
    } else {
      // console.log(`⚠️ 未在模块树中找到模块信息，保持当前名称: "${moduleName.value}"`);
    }
    
    emit('moduleChange', {
      path: newValue,
      moduleId: selectedModuleId,
      moduleInfo
    });
  } else {
    // 当清空选择时才清空名称
    // console.log('🗑️ 清空模块选择');
    if (moduleName.value !== '') {
      moduleName.value = '';
      // console.log('📝 重置模块名称为空');
    }
    emit('moduleChange', {
      path: [],
      moduleId: '',
      moduleInfo: null
    });
  }
}, { deep: true });

// 监听props.moduleId，当外部传入moduleId变化时获取名称并更新选择器
watch(() => props.moduleId, async (newValue) => {
  // console.log(`moduleId变化: ${oldValue} -> ${newValue}`);
  if (newValue) {
    await loadModuleNameById(newValue);
  } else {
    // 如果moduleId被清空，也要清空选择和名称
    moduleValue.value = [];
    moduleName.value = '';
  }
}, { immediate: true });

// 监听项目ID变化，重新加载对应项目的模块树
watch(() => caseModuleStore.selectedProjectId, async (newProjectId, oldProjectId) => {
  if (newProjectId !== oldProjectId && newProjectId) {
    console.log(`🔄 项目ID变化: ${oldProjectId} -> ${newProjectId}，重新加载模块树`);
    // 清空当前已加载的标志，强制重新加载
    hasLoadedModuleTree.value = false;
    // 重新加载模块树
    await fetchCaseFolderTree();
    hasLoadedModuleTree.value = true;
  }
}, { immediate: false });

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

// 是否已加载模块树
const hasLoadedModuleTree = ref(false);

onMounted(async () => {
  // 如果有初始moduleId，立即获取模块名称
  if (props.moduleId) {
    await loadModuleNameById(props.moduleId);
  }
});

/**
 * 根据模块ID加载模块名称
 */
const loadModuleNameById = async (moduleId: string) => {
  isLoading.value = true;
  try {
    // console.log(`🔍 正在获取模块详情，ID: ${moduleId}`);
    const response = await getTestModuleDetail(moduleId);
    
    if (response.code === 200 && response.success) {
      moduleName.value = response.results.data.name;
      // console.log(`✅ 获取到模块名称: ${moduleName.value}`);

      // 如果没有预选模块路径，则直接使用模块ID
      if (!moduleValue.value || moduleValue.value.length === 0) {
        moduleValue.value = [moduleId];
        // console.log(`🎯 设置默认模块路径: [${moduleId}]`);
      }
    } else {
      console.warn(`⚠️ 获取模块详情失败: ${response.msg}`);
      moduleName.value = `模块ID: ${moduleId}`;  // 显示备用信息
    }
  } catch (error) {
    console.error('❌ 获取模块详情失败:', error);
    moduleName.value = `模块ID: ${moduleId}`;  // 显示备用信息
  } finally {
    isLoading.value = false;
  }
};

/**
 * 处理级联选择器获得焦点事件
 * 只有在第一次点击时加载模块树数据，避免不必要的请求
 */
const handleFocus = async () => {
  // 检查是否有选中的项目ID
  if (!caseModuleStore.selectedProjectId) {
    console.warn('⚠️ 未选择项目，无法加载模块树');
    return;
  }
  
  if (!hasLoadedModuleTree.value) {
    console.log('🎯 首次点击，加载模块树数据');
    await fetchCaseFolderTree();
    hasLoadedModuleTree.value = true;
  }
};

/**
 * 将API返回的模块树转换为级联选择器所需的格式
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

/**
 * 获取用例组所属模块数据
 * 根据当前选中的项目ID获取对应的模块树
 */
const fetchCaseFolderTree = async () => {
  // 设置加载状态
  isLoading.value = true;
  
  try {
    // 获取当前选中的项目ID
    const currentProjectId = caseModuleStore.selectedProjectId;
    console.log(`🌲 获取项目 ${currentProjectId} 的模块树`);
    
    // 调用API，传入项目ID参数
    const response = await getCaseFolderTree(currentProjectId || undefined);
    
    if (response && response.code === 200) {
      if (response.results && response.results.length > 0) {
        // 转换为级联选择器需要的格式
        const cascaderOptions = transformToCascaderOptions(response.results);
        options.value = cascaderOptions;
        console.log(`📋 加载了 ${cascaderOptions.length} 个模块选项`);
        
        // 如果有moduleId，尝试在新加载的树中找到完整路径
        if (props.moduleId) {
          const path = findModulePath(props.moduleId);
          if (path) {
            console.log(`🎯 在模块树中找到路径: ${path.join(' -> ')}，模块ID: ${props.moduleId}`);
            moduleValue.value = path;
            
            // 同时更新模块名称显示
            const moduleInfo = findModuleByPath(path);
            if (moduleInfo) {
              moduleName.value = moduleInfo.label;
              console.log(`📝 设置模块名称: ${moduleName.value}`);
            }
          } else {
            console.warn(`⚠️ 在项目 ${currentProjectId} 的模块树中未找到模块 ${props.moduleId}`);
            // 如果在树中找不到指定模块，保持现有的模块名称但清空路径
            moduleValue.value = [];
          }
        }
      } else {
        console.warn(`📭 项目 ${currentProjectId} 暂无模块数据`);
        options.value = [];
      }
    } else {
      console.error('获取模块数据失败:', response.msg);
      options.value = [];
    }
  } catch (error) {
    console.error('获取用例组所属模块数据失败:', error);
    options.value = [];
  } finally {
    // 无论成功还是失败，都需要关闭加载状态
    isLoading.value = false;
  }
}

/**
 * 根据路径查找模块信息
 */
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
 * 根据模块ID查找级联选择器路径
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
</script>

<style scoped lang="scss">
/* 级联选择器中的加载和空数据样式 */
.loading-text, .empty-text {
  padding: 10px;
  color: #18191a;
  text-align: center;
}
</style>
