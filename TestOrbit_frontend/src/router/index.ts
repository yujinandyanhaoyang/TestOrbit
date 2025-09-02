import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    //重定向到首页
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login/Login.vue')
    },
    {
      path: '/home',
      name: 'HomePage',
      component: () => import('@/views/Home/HomePage.vue')
    },
    {
      path: '/ProjectManage',
      name: 'ProjectManage',
      component: () => import('@/views/ProjectManage/index.vue')
    },
    {
      path: '/UserManage',
      name: 'UserManage',
      component: () => import('@/views/UserManage/index.vue')
    },
    {
      path: '/PressureTest',
      name: 'PressureTest',
      component: () => import('@/views/PressureTest/index.vue')
    },
    {
      path: '/Case',
      name: 'CaseManage',
      component: () => import('@/views/CaseManage/index.vue')
    }
  ],
})

export default router
