import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

// 子应用：提示词管理（对应后端 jv-genai-prompt），端口 38203
export default defineConfig({
  plugins: [vue(), qiankun('fe-prompt', { useDevMode: true })],
  server: {
    proxy: {
      '/api/prompts': 'http://localhost:38089'
    },
    port: 38203,
    // 允许 qiankun 基座跨域加载
    cors: true,
    origin: '//localhost:38203'
  }
})
