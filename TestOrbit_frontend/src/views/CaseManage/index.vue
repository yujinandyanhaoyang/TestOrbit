<template>
  <div class="container">
    <div class="main">
      <!--左侧菜单栏-->
      <div class="left">
        <el-button type="primary" @click="$router.push('/home')">返回主页</el-button>
        <Recycle />
        <Folder />
      </div>
      <!--内容区-->
      <div class="right">
        <div class="tab-container">
          <!---顶部分页面切换-->
          <PageManage />
        </div>
      </div>
    </div>
  </div>
</template>


<script lang="ts" setup>
//引入组件
import Folder from './CombineFolder/CaseTree.vue'
import Recycle from './Cases/recyclePage.vue'
import PageManage from './Cases/pageManage.vue'

</script>

<style scoped lang="scss">
.container {
  display: flex;
  height: 100%;
  padding: 0 20px;


.main {
  display: flex;
  flex: 1;
    .left {
      width: 400px;
    }

  .right {
    flex: 1;
    width: 900px;
    padding: 0 5px;
    background-color: #fff;
    border-left: 5px solid #e6e6e6;  // 添加灰色边框线
  }
  

}
}
</style>