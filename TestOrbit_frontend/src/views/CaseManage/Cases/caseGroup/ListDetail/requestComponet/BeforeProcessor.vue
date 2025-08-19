<template>
  <div class="processor-editor">
    <el-alert
      title="前置处理器"
      type="info"
      description="前置处理器在请求发送前执行，可以用来设置变量、处理请求参数等。"
      :closable="false"
      show-icon
    />
    
    <div class="script-editor">
      <el-input
        v-model="processorScript"
        type="textarea"
        :rows="10"
        placeholder="// 输入前置处理脚本
// 示例:
// pm.variables.set('timestamp', Date.now());
// pm.variables.set('randomId', Math.floor(Math.random() * 1000));"
        @change="updateProcessor"
      />
    </div>
    
    <div class="help-section">
      <h4>可用的API:</h4>
      <ul>
        <li><code>pm.variables.set(key, value)</code> - 设置变量</li>
        <li><code>pm.variables.get(key)</code> - 获取变量</li>
        <li><code>pm.request.headers.add(name, value)</code> - 添加请求头</li>
        <li><code>pm.request.headers.remove(name)</code> - 删除请求头</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

// 定义事件
const emit = defineEmits(['update:beforeScript']);

// 前置处理器脚本内容
const processorScript = ref('');

// 更新脚本内容
const updateProcessor = () => {
  emit('update:beforeScript', processorScript.value);
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
