import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  //配置跨域代理
    server: {
    proxy: {
        '/api': {

        //本地测试地址
        target: 'http://localhost:8000',
        //参考服务器地址
        // target: 'http://121.43.43.59:8006',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      },
    }
    }
})
