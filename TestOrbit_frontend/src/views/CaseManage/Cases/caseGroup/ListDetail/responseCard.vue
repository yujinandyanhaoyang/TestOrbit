<template>
  <el-tabs type="border-card" class="demo-tabs">
    <el-tab-pane label="响应结果">
        <Response :responseData="responseData"/>
    </el-tab-pane>
    <el-tab-pane label="请求详情">
      <RequestMessage />
    </el-tab-pane>
    <el-tab-pane label="控制台详情">
      <ConsoleDetail />
    </el-tab-pane>
    <el-tab-pane label="参数提取结果">
      <ParamExtract />
    </el-tab-pane>
  </el-tabs>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
// 引入自定义组件
import Response from './responseComponent/response.vue';
import RequestMessage from './responseComponent/requestMessage.vue';
import ConsoleDetail from './responseComponent/consoleDetail.vue';
import ParamExtract from './responseComponent/paramExtract.vue';

// 假设这是从API请求获取的响应数据
const responseData = ref({
  status: 200,
  time: 253, // 毫秒
  size: 1548, // 字节
  body: '{"code":0,"message":"成功","data":{"id":123,"name":"测试项目"}}',
  headers: {
    'Content-Type': 'application/json',
    'Date': 'Sun, 17 Aug 2025 10:23:45 GMT'
  }
});

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
