import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

// 子应用：开发者文档（对应后端 jv-genai-docs），端口 38208
export default defineConfig({
  plugins: [vue(), qiankun('fe-docs', { useDevMode: true })],
  server: {
    proxy: {
      '/api/docs': 'http://localhost:38096'
    },
    port: 38208,
    // 允许 qiankun 基座跨域加载
    cors: true,
    origin: '//localhost:38208'
  }
})
