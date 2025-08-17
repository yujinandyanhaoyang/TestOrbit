
<template>
    <div class="container" title="步骤名称">
        <!--顶部操作框(请求方式，请求地址，请求路径，运行按钮)-->
        <div class="top">
          <h2>步骤名称</h2>
              <el-input
                v-model="stepName"
                style="width: 240px"
                placeholder="请输入步骤名称"
                clearable
              />
          <h2>请求方式</h2>
            <el-select v-model="method" placeholder="Select" style="width: 240px">
                <el-option
                v-for="item in methodOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
                />
            </el-select>
            <h2>域名</h2>
              <el-input
                v-model="UrlInput"
                style="width: 240px"
                placeholder="Please input"
                clearable
              />
            <h2>路径</h2>
              <el-input
                v-model="address"
                style="width: 240px"
                placeholder="Please input"
                clearable
              />
            <el-button type="primary" @click="handleSave">保存</el-button>
            <el-button type="primary" @click="runTest">运行</el-button>
        </div>
        <!--请求参数配置卡片(Headers, Query Params, Body（目前规定仅支持json）, 前置脚本，后置脚本)-->
        <div class="center">
          <ParamCard @update:requestConfig="updateRequestConfig" />
        </div>
        <!--结果卡片（运行结果、控制台打印详情、请求详情、参数提取详情）-->
        <div class="bottom">
          <ResponseCard />
        </div>

    </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import ParamCard from './paramCard.vue'
import ResponseCard from './responseCard.vue'
import { addCaseStep } from '@/api/case'
import type { AddCaseStepRequest, HttpMethod } from '@/api/case/types'

// 基本信息
const stepName = ref<string>('新建步骤')
const address = ref<string>('/path')
const UrlInput = ref<string>('https://ai.m.taobao.com/')
const method = ref<HttpMethod>('GET')

// 请求参数配置
const requestConfig = ref({
  headers: [],
  querys: [],
  body: {},
  contentType: 'application/json',
  beforeScript: '',
  afterScript: ''
})

// 项目ID，实际应该从路由或者父组件传入
const projectId = ref<number>(4)

const methodOptions = [
  {
    value: 'POST',
    label: 'POST',
  },
  {
    value: 'GET',
    label: 'GET',
  },
  {
    value: 'DELETE',
    label: 'DELETE',
  },
  {
    value: 'PUT',
    label: 'PUT',
  },
  {
    value: 'PATCH',
    label: 'PATCH',
  },
]

// 更新请求配置
const updateRequestConfig = (config: any) => {
  requestConfig.value = config
}

// 保存步骤
const handleSave = async () => {
  try {
    // 检验必要数据
    if (!stepName.value.trim()) {
      ElMessage.warning('请输入步骤名称')
      return
    }
    
    if (!method.value) {
      ElMessage.warning('请选择请求方法')
      return
    }
    
    if (!UrlInput.value.trim()) {
      ElMessage.warning('请输入域名')
      return
    }
    
    // 构建请求参数
    const requestData: AddCaseStepRequest = {
      step_name: stepName.value,
      name: stepName.value,
      project_id: projectId.value,
      method: method.value,
      host: UrlInput.value.trim(),
      host_type: 1, // 默认值，根据实际情况调整
      path: address.value,
      ban_redirects: false, // 默认允许重定向
      header_mode: 1, // 默认值，根据实际情况调整
      header_source: requestConfig.value.headers,
      query_mode: 1, // 默认值，根据实际情况调整
      query_source: requestConfig.value.querys,
      body_mode: 2, // JSON格式
      body_source: {
        name: "请求体",
        id: 2
      },
      expect_mode: 1, // 默认值
      expect_source: [],
      output_mode: 1, // 默认值
      output_source: [],
      is_case: true // 是测试用例步骤
    }
    
    console.log('保存步骤请求参数:', requestData)
    
    // 发送保存请求
    const res = await addCaseStep(requestData)
    
    if (res?.code === 200) {
      ElMessage.success('保存成功')
      console.log('保存步骤响应:', res)
    } else {
      ElMessage.error(`保存失败: ${res?.message || '未知错误'}`)
    }
  } catch (error) {
    console.error('保存步骤错误:', error)
    ElMessage.error(`保存步骤错误: ${(error as Error).message || '未知错误'}`)
  }
}

// 运行测试
const runTest = async () => {
  ElMessage.info('运行测试功能暂未实现')
}


</script>

<style scoped lang="scss">
.container {
    display: flex;
    flex-direction: column;
    flex: 1;
    min-height: 600px;
    background-color: #f5f7fa;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    
    .top {
        display: flex;
        align-items: center;
        padding: 15px;
        background-color: #fff;
        border-bottom: 1px solid #ebeef5;
        flex-wrap: wrap;
        gap: 10px;
        
        h2 {
            font-size: 14px;
            color: #606266;
            margin: 0 5px 0 15px;
        }
        
        .el-button {
            margin-left: auto;
        }
        
        .el-button + .el-button {
            margin-left: 10px;
        }
    }
    
    .center {
        flex: 1;
        padding: 15px;
        background-color: #fff;
        margin: 15px;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04);
    }
    
    .bottom {
        flex: 1;
        padding: 15px;
        background-color: #fff;
        margin: 0 15px 15px;
        border-radius: 4px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.12), 0 0 6px rgba(0, 0, 0, 0.04);
    }
}
</style>