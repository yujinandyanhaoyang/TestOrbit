
<template>
    <div class="assertion-editor">
        <!-- 断言类型选择区 -->
        <div class="assertion-type-selector">
            <span class="type-label">断言类型：</span>
            <el-radio-group v-model="assertionType" @change="changeAssertionType">
                <el-radio-button label="jsonpath">JSONPath</el-radio-button>
                <el-radio-button label="regex">正则表达式</el-radio-button>
                <el-radio-button label="xpath">XPath</el-radio-button>
                <el-radio-button label="status_code">状态码</el-radio-button>
            </el-radio-group>
        </div>
        
        <!-- 断言表格 -->
        <el-table :data="assertionItems" border style="width: 100%; margin-top: 15px;">
            <!-- 启用/禁用列 -->
            <el-table-column width="50">
                <template #default="scope">
                    <el-checkbox v-model="scope.row.enabled" @change="updateAssertions" />
                </template>
            </el-table-column>
            
            <!-- 提取表达式列 -->
            <el-table-column label="提取表达式" width="220">
                <template #default="scope">
                    <el-input 
                        v-model="scope.row.expression" 
                        :placeholder="getExpressionPlaceholder(assertionType)" 
                        @change="updateAssertions"
                        :disabled="!scope.row.enabled" 
                    />
                </template>
            </el-table-column>
            
            <!-- 断言条件列 -->
            <el-table-column label="条件" width="150">
                <template #default="scope">
                    <el-select 
                        v-model="scope.row.operator" 
                        placeholder="选择操作符"
                        @change="updateAssertions"
                        :disabled="!scope.row.enabled"
                        style="width: 100%"
                    >
                        <el-option label="等于 (==)" value="==" />
                        <el-option label="不等于 (!=)" value="!=" />
                        <el-option label="大于 (>)" value=">" />
                        <el-option label="小于 (<)" value="<" />
                        <el-option label="大于等于 (>=)" value=">=" />
                        <el-option label="小于等于 (<=)" value="<=" />
                        <el-option label="包含" value="contains" />
                        <el-option label="不包含" value="not_contains" />
                        <el-option label="匹配正则" value="matches" />
                    </el-select>
                </template>
            </el-table-column>
            
            <!-- 预期结果列 -->
            <el-table-column label="预期结果">
                <template #default="scope">
                    <el-input 
                        v-model="scope.row.expected_value" 
                        placeholder="输入预期结果值" 
                        @change="updateAssertions"
                        :disabled="!scope.row.enabled" 
                    />
                </template>
            </el-table-column>
            
            <!-- 操作列 -->
            <el-table-column width="70">
                <template #default="scope">
                    <el-button 
                        type="danger" 
                        icon="Delete" 
                        circle 
                        size="small"
                        @click="deleteRow(scope.$index)" 
                    />
                </template>
            </el-table-column>
        </el-table>
        
        <!-- 底部操作区 -->
        <div class="action-bar">
            <el-button type="primary" @click="addRow" size="small">
                <el-icon><Plus /></el-icon> 添加断言
            </el-button>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, watch, computed } from 'vue';
import { Delete, Plus } from '@element-plus/icons-vue';
import type { Rule } from '@/api/case/caseStep/types';

// 定义断言项类型
interface AssertionItem {
    id: number;
    expression: string;
    operator: string;
    expected_value: string;
    enabled: boolean;
    created: string;
    updated: string;
}

// 定义接收的props
const props = defineProps<{
    stepId?: number;
    initialAssertions?: Rule[];
}>();

// 定义事件
const emit = defineEmits(['update:assert']);

// 断言类型（当前选中的断言类型）
const assertionType = ref<string>('jsonpath');

// 断言项列表
const assertionItems = ref<AssertionItem[]>([]);

// 所有断言规则（根据类型分组）
const allAssertions = ref<Record<string, Rule[]>>({
    'jsonpath': [],
    'regex': [],
    'xpath': [],
    'status_code': []
});


// 监听initialAssertions参数变化
watch(() => props.initialAssertions, (currentAssertions) => {
  if (currentAssertions && currentAssertions.length > 0) {
    console.log('initialAssertions接收到新的步骤参数:', currentAssertions);
    console.log('初始断言规则:', currentAssertions[0].type);
    
    // 清空旧的断言分组数据
    allAssertions.value = {
        'jsonpath': [],
        'regex': [],
        'xpath': [],
        'status_code': []
    };
    
    // 设置当前断言类型为第一个断言的类型
    assertionType.value = currentAssertions[0].type;
    
    // 将断言按类型分组
    currentAssertions.forEach(assertion => {
        if (!allAssertions.value[assertion.type]) {
            allAssertions.value[assertion.type] = [];
        }
        allAssertions.value[assertion.type].push(assertion);
    });
    // console.log('分组后的结果:', allAssertions.value);
    
    // 加载当前类型的断言到表格中
    loadAssertionItems();
  }
}, { deep: true, immediate: true });


// 根据当前选中的断言类型加载断言项
const loadAssertionItems = () => {
    const typeAssertions = allAssertions.value[assertionType.value] || [];
    
    assertionItems.value = typeAssertions.map(assertion => ({
        id: assertion.id,
        expression: assertion.expression,
        operator: assertion.operator,
        expected_value: assertion.expected_value,
        enabled: assertion.enabled,
        created: assertion.created,
        updated: assertion.updated
    }));
    
    // 如果没有断言项，添加一个空的
    if (assertionItems.value.length === 0) {
        addRow();
    }
};

// 更改断言类型
const changeAssertionType = (type: string) => {
    // 保存当前类型的断言
    saveCurrentAssertions();
    
    // 更新当前类型
    assertionType.value = type;
    
    // 加载新类型的断言
    loadAssertionItems();
};

// 保存当前类型的断言
const saveCurrentAssertions = () => {
    // 将当前表格中的断言项保存到对应类型的断言列表中
    allAssertions.value[assertionType.value] = assertionItems.value.map(item => ({
        id: item.id,
        type: assertionType.value,
        expression: item.expression,
        operator: item.operator,
        expected_value: item.expected_value,
        created: item.created,
        updated: item.updated,
        enabled: item.enabled,
        step: props.stepId || 0,
        display_text: generateDisplayText(item)
    }));
};

// 添加一行
const addRow = () => {
    assertionItems.value.push({
        id: generateTempId(),
        expression: '',
        operator: '==',
        expected_value: '',
        enabled: true,
        created: new Date().toISOString(),
        updated: new Date().toISOString()
    });
    
    updateAssertions();
};

// 删除一行
const deleteRow = (index: number) => {
    assertionItems.value.splice(index, 1);
    
    // 如果删除后没有断言项，添加一个空的
    if (assertionItems.value.length === 0) {
        addRow();
    } else {
        updateAssertions();
    }
};

// 更新断言，向父组件发送更新后的数据
const updateAssertions = () => {
    // 保存当前类型的断言
    saveCurrentAssertions();
    
    // 将所有类型的断言合并为一个数组
    const allAssertionsList = Object.values(allAssertions.value).flat();
    
    // 只发送有效的断言（表达式和操作符不为空）
    const validAssertions = allAssertionsList.filter(
        assertion => assertion.expression && assertion.expression.trim() !== '' && assertion.enabled
    );
    
    // 发送给父组件
    emit('update:assert', validAssertions);
};

// 生成临时ID (负数，避免与后端生成的正数ID冲突)
const generateTempId = (): number => {
    return -Math.floor(Math.random() * 1000000);
};

// 生成断言的显示文本
const generateDisplayText = (assertion: AssertionItem): string => {
    if (!assertion.expression || !assertion.operator) {
        return '未完成的断言规则';
    }
    
    return `${assertion.expression} ${assertion.operator} ${assertion.expected_value}`;
};

// 根据断言类型获取表达式输入提示
const getExpressionPlaceholder = (type: string): string => {
    switch (type) {
        case 'jsonpath':
            return '例如: $.status 或 $.data.items[0].id';
        case 'regex':
            return '例如: .*success.*';
        case 'xpath':
            return '例如: //div[@class="result"]/text()';
        case 'status_code':
            return '直接输入状态码，如: 200';
        default:
            return '请输入提取表达式';
    }
};
</script>

<style scoped>
.assertion-editor {
    padding: 10px;
}

.assertion-type-selector {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
}

.type-label {
    margin-right: 10px;
    font-weight: 500;
}

.action-bar {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    margin-top: 15px;
}

:deep(.el-table__header) {
    background-color: #f5f7fa;
}

:deep(.el-table__row) {
    height: 50px;
}

:deep(.el-input.is-disabled .el-input__inner) {
    color: #909399;
    background-color: #f5f7fa;
}
</style>