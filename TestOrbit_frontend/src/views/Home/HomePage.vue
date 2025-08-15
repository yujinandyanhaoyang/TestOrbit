
<template>
  <div class="container">

    
    <div class="main">
      <!--左侧菜单栏-->
      <div class="left">
            <el-menu
          default-active="/ProjectManage"
          class="el-menu-vertical-demo">
          <el-menu-item index="/ProjectManage" @click="changeActive('/ProjectManage')">
            <i class="el-icon-menu"></i>
            <span slot="title">项目组管理-对应原环境管理</span>
          </el-menu-item>
          <el-menu-item index="/CaseManage" @click="changeActive('/CaseManage')">
            <i class="el-icon-menu"></i>
            <span slot="title">用例管理</span>
          </el-menu-item>
          <el-menu-item index="/Case" @click="changeActive('/Case')">
            <i class="el-icon-document"></i>
            <span slot="title">场景用例管理</span>
          </el-menu-item>
          <el-menu-item index="/UserManage" @click="changeActive('/UserManage')">
            <i class="el-icon-setting"></i>
            <span slot="title">用户管理</span>
          </el-menu-item>
          <el-menu-item index="/PressureTest" @click="changeActive('/PressureTest')">
            <i class="el-icon-setting"></i>
            <span slot="title">压测</span>
          </el-menu-item>
        </el-menu>
      </div>
      <!--内容区-->
      <div class="right">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter();


//跳转具体功能页面
const changeActive = (path: string) => {
  router.push({ path });
};

</script>


<style scoped lang="scss">
.container {
  display: flex;
  flex-direction: column;
  min-height: 100vh; // 确保容器至少占满整个视口高度


  .main {
    display: flex;
    height: 800px; // 设置主内容区的高度

    .left {
      width: 300px;
      height: 100%;
      padding: 0;
      margin: 0;
      background-color: #fff;
      
      .el-menu {
        width: 100%;
        height: 100%;
        border-right: none;
      }
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