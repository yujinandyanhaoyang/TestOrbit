
<template>
  <div class="container">
    <Header />
    <div class="content">
      <router-view />
    </div>
  </div>
</template>

<script setup lang="ts">
// App.vue 作为应用的根组件，只需要渲染路由内容

import Header from '@/component/head.vue'
</script>

<style lang="scss">
.container {
  display: flex;
  flex-direction: column;
  min-height: 100vh; // 确保容器至少占满整个视口高度
  
}
</style>