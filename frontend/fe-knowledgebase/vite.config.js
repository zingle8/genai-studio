import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

// 子应用：知识库管理（对应后端 py-genai-knowledgebase），端口 38205
export default defineConfig({
  plugins: [vue(), qiankun('fe-knowledgebase', { useDevMode: true })],
  server: {
    port: 38205,
    // 允许 qiankun 基座跨域加载
    cors: true,
    origin: '//localhost:38205',
    proxy: {
      '/api/kb': 'http://localhost:38116',
      '/api/rag': 'http://localhost:38119',
      '/api/ocr': 'http://localhost:38118'
    }
  }
})
