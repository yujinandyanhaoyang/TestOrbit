import { createApp } from 'vue'
import { createPinia } from 'pinia'

//引入自己安装的依赖库
//element组件库
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// 引入Element Plus 中文语言包
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'


// 引入样式重置
import './assets/style/reset.scss'


import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

//挂载自己添加的组件
app.use(ElementPlus, {
  locale: zhCn
})

app.mount('#app')
