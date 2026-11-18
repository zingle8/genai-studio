import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

// 子应用：会话对话（对应后端 jv-genai-chats），端口 38202
export default defineConfig({
  plugins: [vue(), qiankun('fe-chats', { useDevMode: true })],
  server: {
    proxy: {
      '/api/chats': 'http://localhost:38090',
      // 提示词模板（jv-genai-prompt）
      '/api/prompts': 'http://localhost:38089',
      // API Key 可用列表（jv-genai-apikey）
      '/api/apikeys': 'http://localhost:38091',
      // 模型路由（jv-genai-router，体验中心三模式直连）
      '/v1': 'http://localhost:38100'
    },
    port: 38202,
    // 允许 qiankun 基座跨域加载
    cors: true,
    origin: '//localhost:38202'
  }
})
