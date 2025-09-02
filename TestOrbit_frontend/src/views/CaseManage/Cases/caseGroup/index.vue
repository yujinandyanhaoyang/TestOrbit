
<template>
    <div class="container" v-loading="caseGroupStore.loading" element-loading-text="正在加载用例组详情...">
        <!--顶部操作框-->
        <div class="top">
            <Head 
                :caseId="props.caseId"
                :case-name="caseGroupStore.caseGroupName" 
                :module-id="caseGroupStore.moduleId" 
                :list-detail-ref="listDetailRef"
                @add-step="handleAddStep" 
                @save-order="handleSaveOrder" 
            />
        </div>
        <!----用例组展示框-->
        <div class="case-group">
            <ListDetail 
                v-if="props.caseId"
                ref="listDetailRef" 
                :caseId="props.caseId"
            />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import Head from './head.vue';
import ListDetail from './ListDetail/index.vue';
import { useCaseGroupStore } from '@/store/caseGroupStore'

// 定义组件接收的props
const props = defineProps<{
  caseId?: number
}>()

// 🔥 使用新的 Pinia store
const caseGroupStore = useCaseGroupStore()

// 引用ListDetail组件实例
const listDetailRef = ref<any>(null);

onMounted(async () => {
    // 使用Pinia store获取用例组详情
    if (props.caseId) {
        await caseGroupStore.fetchCaseGroupDetail(props.caseId);
    }
});

// 监听caseId的变化，当从外部传入新的caseId时重新获取数据
watch(() => props.caseId, async (newCaseId) => {
    if (newCaseId) {
        console.log('检测到caseId变化，重新加载数据:', newCaseId);
        await caseGroupStore.fetchCaseGroupDetail(newCaseId);
    }
});

// 处理添加步骤事件
const handleAddStep = () => {
    console.log('🚀 handleAddStep被调用 (caseGroup/index.vue)');
    // 调用ListDetail组件的addNewStep方法
    if (listDetailRef.value) {
        console.log('📞 准备调用ListDetail的addNewStep方法');
        listDetailRef.value.addNewStep();
    } else {
        console.warn('❌ listDetailRef.value为空，无法调用addNewStep');
    }
};

// 处理保存顺序事件
const handleSaveOrder = () => {
    // 调用ListDetail组件的saveStepOrder方法
    if (listDetailRef.value) {
        listDetailRef.value.saveStepOrder();
    }
};

// 获取最新的步骤数据（从Pinia store获取）
const getLatestStepsData = () => {
    return caseGroupStore.steps;
};
</script>