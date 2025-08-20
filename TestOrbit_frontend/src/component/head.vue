
<template>
    <div class="top">
      <h1>这里是头部</h1>
      <!--用户信息和退出登录-->
      <div class="user-info">
        <span style="padding: 5px;font-weight: bold;">
          <el-avatar
            class="avatar-icon"
            :size="50"
            src="https://cube.elemecdn.com/0/88/03b0d39583f48206768a7534e55bcpng.png"
          />
          {{ userStore.userInfo?.username || '未登录' }}
        </span>
        <el-button 
          v-if="userStore.isLoggedIn"
          type="danger" 
          size="small" 
          @click="handleLogout"
          class="logout-btn">
          退出登录
        </el-button>
      </div>
    </div>
</template>

<script setup lang="ts">
import useUserStore from '@/store/user'
import { useRouter } from 'vue-router';
import { ElMessageBox } from 'element-plus';

const userStore = useUserStore();
const router = useRouter();

// 退出登录处理
const handleLogout = () => {
  ElMessageBox.confirm(
    '确定要退出登录吗?',
    '提示',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    userStore.logout();
    router.push('/login');
  }).catch(() => {
    // 取消操作，不做任何事
  });
};
</script>

<style lang="scss">
.top {
  background-color: skyblue;
  padding: 20px;
  text-align: center;
  display: flex;
  justify-content: space-between;
  align-items: center;

  .user-info {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .avatar-icon {
    cursor: pointer;
    transition: all 0.3s;
    &:hover {
      transform: scale(1.1);
      box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
  }

  .logout-btn {
    margin-left: 10px;
  }
}

</style>