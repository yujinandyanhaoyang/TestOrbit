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
// 导入路由权限控制
import '@/utils/permission'

const app = createApp(App)

app.use(createPinia())
app.use(router)

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
