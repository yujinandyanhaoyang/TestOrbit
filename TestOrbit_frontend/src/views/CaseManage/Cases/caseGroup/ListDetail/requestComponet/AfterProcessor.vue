<template>
  <div class="processor-editor">
    <el-alert
      title="后置处理器"
      type="info"
      description="后置处理器在请求响应后执行，可以用来提取响应数据、设置环境变量等。"
      :closable="false"
      show-icon
    />
    
    <div class="script-editor">
      <el-input
        v-model="processorScript"
        type="textarea"
        :rows="10"
        placeholder="// 输入后置处理脚本
// 示例:
// const jsonData = pm.response.json();
// pm.variables.set('token', jsonData.token);
// pm.test('Status code is 200', () => {
//   pm.expect(pm.response.code).to.equal(200);
// });"
        @change="updateProcessor"
      />
    </div>
    
    <div class="help-section">
      <h4>可用的API:</h4>
      <ul>
        <li><code>pm.response.json()</code> - 获取JSON格式的响应</li>
        <li><code>pm.response.text()</code> - 获取文本格式的响应</li>
        <li><code>pm.variables.set(key, value)</code> - 设置变量</li>
        <li><code>pm.test(name, fn)</code> - 添加测试断言</li>
        <li><code>pm.expect(value)</code> - 断言辅助函数</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineEmits, onMounted } from 'vue';

// 定义事件
const emit = defineEmits(['update:afterScript']);

// 后置处理器脚本内容
const processorScript = ref('');

// 更新脚本内容
const updateProcessor = () => {
  emit('update:afterScript', processorScript.value);
};

// 初始化
onMounted(() => {
  updateProcessor();
});
</script>

<style scoped lang="scss">
.processor-editor {
  padding: 10px;
  
  .script-editor {
    margin-top: 15px;
    
    :deep(.el-textarea__inner) {
      font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
      font-size: 14px;
      line-height: 1.6;
      padding: 10px;
    }
  }
  
  .help-section {
    margin-top: 15px;
    padding: 10px;
    background-color: #f5f7fa;
    border-radius: 4px;
    
    h4 {
      margin-top: 0;
      margin-bottom: 10px;
      color: #409eff;
    }
    
    ul {
      margin: 0;
      padding-left: 20px;
      
      li {
        margin-bottom: 5px;
        
        code {
          background-color: #edf2fc;
          padding: 2px 4px;
          border-radius: 3px;
          color: #409eff;
        }
      }
    }
  }
}
</style>
