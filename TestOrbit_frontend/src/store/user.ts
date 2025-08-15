import { defineStore } from "pinia";
import { ElMessage } from 'element-plus';
import { userLogin } from '@/api/user';

// 从本地存储中获取token
const getStoredToken = (): string => {
  return localStorage.getItem('token') || '';
};

// 从本地存储中获取用户信息
const getStoredUserInfo = () => {
  const userInfo = localStorage.getItem('userInfo');
  return userInfo ? JSON.parse(userInfo) : null;
};

const useUserStore = defineStore('user', {
  state: () => ({
    token: getStoredToken(),
    userInfo: getStoredUserInfo()
  }),

  getters: {
    // 判断用户是否已登录
    isLoggedIn: (state) => !!state.token,
    // 获取用户名
    username: (state) => state.userInfo?.username || '',
    // 获取显示名称
    displayName: (state) => state.userInfo?.name || ''
  },

  actions: {
    // 设置token
    setToken(token: string) {
      this.token = token;
      localStorage.setItem('token', token);
    },

    // 设置用户信息
    setUserInfo(userInfo: any) {
      this.userInfo = userInfo;
      localStorage.setItem('userInfo', JSON.stringify(userInfo));
    },

    // 登录操作
    async login(username: string, password: string) {
      try {
        const response = await userLogin(username, password);
        
        if (response.code === 200 && response.success) {
          // 存储token和用户信息
          this.setToken(response.results.token);
          this.setUserInfo(response.results.user_info);
          
          ElMessage.success('登录成功');
          return true;
        } else {
          ElMessage.error(response.msg || '登录失败');
          return false;
        }
      } catch (error) {
        ElMessage.error('登录请求失败');
        return false;
      }
    },

    // 退出登录
    logout() {
      this.token = '';
      this.userInfo = null;
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
      ElMessage.success('已退出登录');
    },

    // 清除用户状态
    clearUserState() {
      this.token = '';
      this.userInfo = null;
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
    }
  }
});

export default useUserStore;