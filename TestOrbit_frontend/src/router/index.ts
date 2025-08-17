import component from 'element-plus/es/components/tree-select/src/tree-select-option.mjs'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    //重定向
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login/Login.vue')
    },
    {
      path: '/home',
      name: 'HomePage',
      component: () => import('@/views/Home/HomePage.vue'),
      children: [
        // 子路由将在HomePage的router-view中显示
        //子路由重定向
        {
          path: '/home',
          redirect: '/ProjectManage'
        },
        {
          path: '/ProjectManage',
          component: () => import('@/views/ProjectManage/index.vue')
        },
        {
          path: '/UserManage',
          component: () => import('@/views/UserManage/index.vue'),
        },
        {
          path: '/PressureTest',
          component: () => import('@/views/PressureTest/index.vue')
        },
      ]
    },
    {
      path:'/Case',
      component: () => import('@/views/CaseManage/index.vue'),
      children:[
        
      ]
    }
  ],
})

export default router
