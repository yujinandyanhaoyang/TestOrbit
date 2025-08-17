<template>
  <el-tabs type="border-card" class="demo-tabs">
    <el-tab-pane label="Header">
        <Header @update:headers="updateHeaders" />
    </el-tab-pane>
    <el-tab-pane label="Query">
      <Query @update:querys="updateQuerys" />
    </el-tab-pane>
    <el-tab-pane label="Body">
      <Body @update:body="updateBody" @update:contentType="updateContentType" />
    </el-tab-pane>
    <el-tab-pane label="前置处理器">
      <BeforeProcessor @update:beforeScript="updateBeforeScript" />
    </el-tab-pane>
    <el-tab-pane label="后置处理器">
      <AfterProcessor @update:afterScript="updateAfterScript" />
    </el-tab-pane>
  </el-tabs>
</template>

<script lang="ts" setup>
// 引入自定义组件
import { ref, defineEmits } from 'vue';
import Header from './requestComponet/Header.vue'
import Query from './requestComponet/Query.vue'
import Body from './requestComponet/Body.vue'
import BeforeProcessor from './requestComponet/BeforeProcessor.vue'
import AfterProcessor from './requestComponet/AfterProcessor.vue'
import type { HeaderSourceItem, QuerySourceItem } from '@/api/case/types';

// 定义事件
const emit = defineEmits(['update:requestConfig']);

// 请求配置数据
const requestConfig = ref({
  headers: [] as HeaderSourceItem[],
  querys: [] as QuerySourceItem[],
  body: {},
  contentType: 'application/json',
  beforeScript: '',
  afterScript: ''
});

// 更新请求头
const updateHeaders = (headers: Record<string, string>) => {
  // 转换为API需要的格式
  requestConfig.value.headers = Object.entries(headers).map(([name, value], index) => ({
    id: Date.now() + index,
    name,
    value,
    type: { type: 'string', auto: true }
  }));
  
  emitUpdate();
};

// 更新查询参数
const updateQuerys = (querys: Record<string, string>) => {
  // 转换为API需要的格式
  requestConfig.value.querys = Object.entries(querys).map(([name, value], index) => ({
    id: Date.now() + index,
    name,
    value,
    type: { type: 'string', auto: false }
  }));
  
  emitUpdate();
};

// 更新请求体
const updateBody = (body: any) => {
  requestConfig.value.body = body;
  emitUpdate();
};

// 更新内容类型
const updateContentType = (contentType: string) => {
  requestConfig.value.contentType = contentType;
  emitUpdate();
};

// 更新前置处理器脚本
const updateBeforeScript = (script: string) => {
  requestConfig.value.beforeScript = script;
  emitUpdate();
};

// 更新后置处理器脚本
const updateAfterScript = (script: string) => {
  requestConfig.value.afterScript = script;
  emitUpdate();
};

// 向父组件发送更新
const emitUpdate = () => {
  emit('update:requestConfig', { ...requestConfig.value });
};

</script>

<style>
.demo-tabs > .el-tabs__content {
  padding: 32px;
  color: #6b778c;
  font-size: 32px;
  font-weight: 600;
}
.demo-tabs .custom-tabs-label .el-icon {
  vertical-align: middle;
}
.demo-tabs .custom-tabs-label span {
  vertical-align: middle;
  margin-left: 4px;
}
</style>
