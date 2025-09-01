
<template>
    <div class="container" v-loading="loading" element-loading-text="正在加载用例组详情...">
        <!--顶部操作框-->
        <div class="top">
            <Head 
                :caseId="props.caseId"
                :case-name="caseGroupData?.name" 
                :module-id="caseGroupData?.module_id" 
                :list-detail-ref="listDetailRef"
                @add-step="handleAddStep" 
                @save-order="handleSaveOrder" 
            />
        </div>
        <!----用例组展示框-->
        <div class="case-group">
            <ListDetail 
                ref="listDetailRef" 
                :caseId="props.caseId"
                :steps-data="caseGroupData?.steps" 
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Head from './head.vue';
import ListDetail from './ListDetail/index.vue';
import { getCaseGroupDetail } from '@/api/case/caseGroup'
import { ElMessage } from 'element-plus'

// 定义组件接收的props
const props = defineProps<{
  caseId?: number
}>()

// 引用ListDetail组件实例
const listDetailRef = ref<any>(null);
// 用于存储用例组详情数据
const caseGroupData = ref<any>(null);
// 加载状态
const loading = ref(false);

// 获取用例组详情的通用方法
const fetchCaseGroupData = async (case_id: number) => {
    if (!case_id) return;
    
    loading.value = true;
    try {
        // console.log('(caseGroup/index)正在获取用例组详情，ID:', case_id);
        // 获取用例组详情，使用await等待异步操作完成
        const response = await getCaseGroupDetail(case_id);
        
        if (response.code === 200) {
            // 保存用例组详情数据
            caseGroupData.value = response.results;
            // console.log('用例组详情加载成功:', response.results);
            
            // 调用ListDetail组件的setCaseGroupDetail方法
            if (listDetailRef.value) {
              console.log('调用ListDetail组件的setCaseGroupDetail方法');
              listDetailRef.value.setCaseGroupDetail(response);
            } else {
              console.warn('listDetailRef.value没有setCaseGroupDetail方法');
            }
            ElMessage.success(`成功加载用例组: ${response.results.name}`);
        } else {
            ElMessage.error(response.msg || `加载用例组 #${case_id} 详情失败`);
        }
    } catch (error) {
        console.error("获取用例组详情失败:", error);
        ElMessage.error("获取用例组详情时发生错误，请稍后重试");
    } finally {
        loading.value = false;
    }
};

onMounted(async () => {
    // 使用props中的caseId获取数据
    if (props.caseId) {
        await fetchCaseGroupData(props.caseId);
    }
});

// 监听caseId的变化，当从外部传入新的caseId时重新获取数据
watch(() => props.caseId, async (newCaseId) => {
    if (newCaseId) {
        console.log('检测到caseId变化，重新加载数据:', newCaseId);
        await fetchCaseGroupData(newCaseId);
    }
});

// 处理添加步骤事件
const handleAddStep = () => {
    // 调用ListDetail组件的addNewStep方法
    if (listDetailRef.value) {
        listDetailRef.value.addNewStep();
    }
};

// 处理保存顺序事件
const handleSaveOrder = () => {
    // 调用ListDetail组件的saveStepOrder方法
    if (listDetailRef.value) {
        listDetailRef.value.saveStepOrder();
    }
};
</script>