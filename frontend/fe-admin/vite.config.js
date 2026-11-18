import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

// 子应用：开发者控制台（API Key / 账单），端口 38209
export default defineConfig({
  plugins: [vue(), qiankun('fe-admin', { useDevMode: true })],
  server: {
    port: 38209,
    cors: true,
    origin: '//localhost:38209',
    proxy: {
      // API Key 服务 jv-genai-apikey
      '/api/apikeys': 'http://localhost:38091',
      // 计费服务 jv-genai-billing
      '/api/billing': 'http://localhost:38092',
      '/api/mcp': 'http://localhost:38084',
      '/api/agents': 'http://localhost:38085',
      '/api/configs': 'http://localhost:38087',
      '/api/ops': 'http://localhost:38082',
      '/api/users': 'http://localhost:38088',
      '/api/perms': 'http://localhost:38088'
    }
  }
})
