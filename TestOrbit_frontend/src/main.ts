import { createApp } from 'vue'
import { createPinia } from 'pinia'

//引入自己安装的依赖库
//element组件库
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 引入element图标库
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 引入Element Plus 中文语言包
import zhCn from 'element-plus/es/locale/lang/zh-cn'
//引入自定义全局组件
import Header from '@/component/head.vue'

// 引入样式重置
import './assets/style/reset.scss'


import App from './App.vue'
import router from './router'
import useUserStore from '@/store/user'
// 提前导入路由权限控制
import '@/utils/permission'

const app = createApp(App)

app.use(createPinia())
app.use(router)

// 创建一个函数在应用挂载后清除用户状态
const resetUserState = () => {
  try {
    const userStore = useUserStore()
    // 只清除 localStorage，而不设置 store 状态为 null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  } catch (error) {
    console.error('重置用户状态时出错：', error)
  }
}

// 在应用挂载前清空本地存储
resetUserState()

//挂载自己添加的组件
app.use(ElementPlus, {
  locale: zhCn,
})

// 注册 Element Plus 图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}
app.component('Header', Header)

app.mount('#app')
