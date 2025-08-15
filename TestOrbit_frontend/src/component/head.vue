
<template>
    <div class="top">
      <h1>这里是头部</h1>
      <!--用户头像-->
        <span style="padding: 5px;font-weight: bold;">
          <el-avatar
          class="avatar-icon"
          :size="50"
          src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
        />
          {{userStore.userInfo.name}}</span>
    </div>
</template>

<script setup lang="ts">
import useUserStore from '@/store/user'
const userStore = useUserStore();
</script>

<style lang="css">
.top {
  background-color: skyblue;
  padding: 20px;
  text-align: center;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .avatar-icon {
    cursor: pointer;
    transition: all 0.3s;
    &:hover {
      transform: scale(1.1);
      box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
  }
}

</style>