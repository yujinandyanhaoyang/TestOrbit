<template>
  <div class="login-container">
    <div class="login-box">
      <h2>TestOrbit 登录</h2>
      <el-form :model="userInfo" label-width="80px" class="login-form">
        <el-form-item label="用户名">
          <el-input v-model="userInfo.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input 
            v-model="userInfo.password" 
            type="password" 
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="Login" class="login-button">登录</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import useUserStore from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

//默认初始化登录表单
const userInfo = ref({
  username: 'admin',
  password: '123456'
});

//登录功能
const Login = async () => {
  if (!userInfo.value.username || !userInfo.value.password) {
    ElMessage.warning('用户名和密码不能为空');
    return;
  }

  try {
    const success = await userStore.login(userInfo.value.username, userInfo.value.password);
    
    if (success) {
      router.push('/home'); // 登录成功后跳转到主页
    }
    // 登录成功或失败的提示消息已经在store中处理过了
  } catch (error) {
    ElMessage.error('登录请求失败，请稍后重试');
  }
};
</script>

<style scoped lang="scss">
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-image: url('@/assets/img/black_general.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;

  .login-box {
    height: 300px;
    width: 600px;
    padding: 40px;
    background: white;  // 半透明白色背景
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);  // 增强阴影效果

    h2 {
      text-align: center;
      margin-bottom: 30px;
      color: #303133;
      font-size: 28px;
      font-weight: bold;
      text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }

    .login-form {
      .login-button {
        width: 100%;
        height: 40px;
        font-size: 16px;
        margin-top: 10px;
        border-radius: 4px;
        transition: all 0.3s;
        
        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 2px 8px rgba(64, 158, 255, 0.5);
        }
      }
    }
  }
}
</style>
