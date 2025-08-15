import router from '@/router';
import useUserStore from '@/store/user';
import { ElMessage } from 'element-plus';

// 不需要登录就可以访问的白名单路径
const whiteList = ['/login'];

// 路由前置守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore();
  
  // 判断用户是否已登录（是否有token）
  if (userStore.isLoggedIn) {
    // 已登录状态下访问登录页，则重定向到首页
    if (to.path === '/login') {
      next({ path: '/home' });
    } else {
      // 已登录状态下，正常访问其他页面
      next();
    }
  } else {
    // 未登录状态下，判断是否在白名单内
    if (whiteList.includes(to.path)) {
      // 白名单内的路径允许访问
      next();
    } else {
      // 非白名单路径，重定向到登录页
      ElMessage.warning('请先登录');
      next(`/login?redirect=${to.path}`);
    }
  }
});

// 路由后置守卫
router.afterEach(() => {
  // 可以在这里处理加载状态结束等操作
});
