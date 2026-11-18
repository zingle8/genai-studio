import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

// 子应用：运营分析（成本统计 / 使用日志），端口 38201
export default defineConfig({
  plugins: [vue(), qiankun('fe-dashboard', { useDevMode: true })],
  server: {
    port: 38201,
    cors: true,
    origin: '//localhost:38201',
    proxy: {
      // 成本核算服务 jv-genai-costs
      '/api/costs': 'http://localhost:38093',
      // 日志服务 jv-genai-logs
      '/api/logs': 'http://localhost:38094'
    }
  }
})
