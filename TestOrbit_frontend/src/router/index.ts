import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    //重定向
    {
      path: '/',
      redirect: '/ProjectManage'
    },
    {
      path: '/ProjectManage',
      component: () => import('@/views/ProjectManage/index.vue')
    },
    {
      path: '/CaseManage',
      component: () => import('@/views/CaseManage/Cases/index.vue')
    },
    {
      path: '/CombineCases',
      component: () => import('@/views/CaseManage/CombineCases/index.vue')
    },
    {
      path: '/UserManage',
      component: () => import('@/views/UserManage/index.vue')
    },
    {
      path: '/PressureTest',
      component: () => import('@/views/PressureTest/index.vue')
    },
  ],
})

export default router
