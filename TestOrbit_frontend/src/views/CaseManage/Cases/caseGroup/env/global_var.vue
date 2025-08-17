
<template>
  <div class="container">
    <div class="top">
      <h1>全局变量配置</h1>
        <h2>当前选中全局变量：</h2>
          <el-select
            v-model="GlobalVarValue"
            clearable
            placeholder="请选择全局变量"
            style="width: 240px"
          >
            <el-option
              v-for="item in GlobalVaroptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
      <el-button type="primary" @click="handleAdd">新增全局变量</el-button>
    </div>
    <div class="content">
    <!--全局变量列表-->
    <el-table :data="tableData" stripe style="width: 100%">
    <el-table-column type="index" label="序号" width="80" align="center" />
    <el-table-column prop="name" label="环境名称" width="180" />
    <el-table-column prop="name" label="URL(待后端改造，暂时用name占位)" width="180" />
    <el-table-column prop="created" label="创建时间" />
    <el-table-column prop="remark" label="描述" />
    <el-table-column
        label="操作"
        align="center"
        fixed="right">
        <template #default="{ row }">
            <el-button size="small" type="primary" @click="handleEdit(row.id)">修改</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
    </el-table-column>
  </el-table>
  </div>
  </div>

  <!-- 添加/编辑全局变量对话框 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
    <el-form 
      ref="formRef" 
      :model="currentVar" 
      label-width="100px" 
      :rules="rules"
    >
      <el-form-item label="环境名称" prop="name">
        <el-input v-model="currentVar.name" placeholder="请输入环境名称" />
      </el-form-item>
      <el-form-item label="环境地址" prop="envir_1_host">
        <el-input v-model="currentVar.envir_1_host" placeholder="请输入环境地址，例如: http://example.com" />
      </el-form-item>
      <el-form-item label="描述" prop="remark">
        <el-input 
          v-model="currentVar.remark" 
          type="textarea" 
          rows="3" 
          placeholder="请输入环境描述" 
        />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm">确认</el-button>
      </span>
    </template>
  </el-dialog>
</template>


<script lang="ts" setup>
import { onMounted, ref, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { getGlobalVariables,addGlobalVariables,updateGlobalVariables,deleteGlobalVariables } from '@/api/case';
import type { GlobalVarInfo,CreateGlobalVarRequest } from '@/api/case/types';
import type { FormRules, FormInstance } from 'element-plus';

// 定义下拉选项的接口
interface OptionItem {
  value: string | number;
  label: string;
}

const tableData = ref<GlobalVarInfo[]>([]);
// 选中的全局变量ID，可以是字符串或数字，也可以是null（未选择）
const GlobalVarValue = ref<string | number | null>('');
// 全局变量选项列表
const GlobalVaroptions = ref<OptionItem[]>([]);



// 组件挂载后初始化数据
onMounted(() => {
    fetchGlobalVariables();
});

const fetchGlobalVariables = async () => {
    try {
        const res = await getGlobalVariables();
        // console.log('获取全局变量列表:', res);
        
        if (res.code === 200 && res.results?.data) {
            // 更新表格数据
            tableData.value = res.results.data;
            
            // 更新下拉选项
            GlobalVaroptions.value = res.results.data.map(item => ({
                value: item.id,
                label: item.name
            }));
            
            // 如果有数据但没有选中值，可以默认选中第一项
            if (GlobalVaroptions.value.length > 0 && !GlobalVarValue.value) {
                GlobalVarValue.value = GlobalVaroptions.value[0].value;
            }
        } else {
            ElMessage.error(`获取全局变量列表失败: ${res.msg || '未知错误'}`);
        }
    } catch (error) {
        console.error('获取全局变量异常:', error);
        ElMessage.error('获取全局变量列表发生异常');
    }
};


// 控制添加/编辑对话框显示
const dialogVisible = ref(false);
// 当前编辑的变量 - 合并了GlobalVarInfo和CreateGlobalVarRequest
const currentVar = ref<Partial<GlobalVarInfo & CreateGlobalVarRequest>>({});
// 对话框标题
const dialogTitle = ref('新增全局变量');
// 表单引用
const formRef = ref<FormInstance>();

// 表单验证规则
const rules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入环境名称', trigger: 'blur' },
    { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
  ],
  envir_1_host: [
    { required: true, message: '请输入环境地址', trigger: 'blur' },
    { 
      pattern: /^(http|https):\/\/[^ "]+$/,
      message: '请输入有效的URL地址，以http://或https://开头', 
      trigger: 'blur' 
    }
  ],
  remark: [
    { max: 200, message: '长度不能超过200个字符', trigger: 'blur' }
  ]
});

/**
 * 打开新增全局变量对话框
 */
const handleAdd = () => {
    dialogTitle.value = '新增全局变量';
    // 重置表单
    currentVar.value = {
        name: '',
        remark: '',
        envir_1_host: ''
    };
    dialogVisible.value = true;
};

/**
 * 打开编辑全局变量对话框
 * @param id 全局变量ID
 */
const handleEdit = (id: number) => {
    dialogTitle.value = '编辑全局变量';
    // 查找当前编辑的变量
    const varInfo = tableData.value.find(item => item.id === id);
    if (varInfo) {
        // 创建一个新对象避免直接修改原始数据
        currentVar.value = { ...varInfo };
        dialogVisible.value = true;
    } else {
        ElMessage.error('未找到要编辑的变量');
    }
};

/**
 * 删除全局变量
 * @param id 全局变量ID
 */
const handleDelete = (id: number) => {
    // 使用确认对话框
    ElMessageBox.confirm(
        '确定要删除该全局变量吗？此操作不可恢复',
        '删除确认',
        {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning',
        }
    )
      .then(() => {
          // 这里应该调用删除API
          deleteGlobalVariables(id).then(res => {
              if (res.code === 200) {
                  ElMessage.success('删除成功');
                  // 从列表中移除
                  tableData.value = tableData.value.filter(item => item.id !== id);
              } else {
                  ElMessage.error('删除失败');
              }
          });
      })
};

/**
 * 提交表单
 */
const submitForm = async () => {
  if (!formRef.value) return;

  try {
    // 表单验证
    await formRef.value.validate();
    
    // 判断是新增还是编辑
    if (currentVar.value.id) {
      // 编辑逻辑 - 这里应该调用后端API
      const response = await updateGlobalVariables(currentVar.value);
      if (response.code === 200) {
        ElMessage.success('更新成功');
        fetchGlobalVariables();
      } else {
        ElMessage.error('更新失败');
      }
    } else {
      // 新增场景变量逻辑 - 这里应该调用后端API
      const res = await addGlobalVariables(currentVar.value);
      if (res.code === 200) {
        ElMessage.success('添加成功');
        fetchGlobalVariables();
      } else {
        ElMessage.error('添加失败');
      }
    }
    // 关闭对话框
    dialogVisible.value = false;
  } catch (error) {
    console.error('表单验证失败:', error);
  }
};


</script>