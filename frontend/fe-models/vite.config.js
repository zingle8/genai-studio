import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

// 子应用：模型管理（对应后端 jv-genai-models），端口 38204
export default defineConfig({
  plugins: [vue(), qiankun('fe-models', { useDevMode: true })],
  server: {
    proxy: {
      '/api/models': 'http://localhost:38086'
    },
    port: 38204,
    // 允许 qiankun 基座跨域加载
    cors: true,
    origin: '//localhost:38204'
  }
})
