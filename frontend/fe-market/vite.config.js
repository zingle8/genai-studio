import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

// 子应用：市场（对应后端 jv-genai-market），端口 38207
export default defineConfig({
  plugins: [vue(), qiankun('fe-market', { useDevMode: true })],
  server: {
    port: 38207,
    // 允许 qiankun 基座跨域加载
    cors: true,
    origin: '//localhost:38207'
  }
})
