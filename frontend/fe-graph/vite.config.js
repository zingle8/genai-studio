import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import qiankun from 'vite-plugin-qiankun'

// 子应用：知识图谱（对应后端 py-genai-graph），端口 38206
export default defineConfig({
  plugins: [vue(), qiankun('fe-graph', { useDevMode: true })],
  server: {
    port: 38206,
    // 允许 qiankun 基座跨域加载
    cors: true,
    origin: '//localhost:38206',
    proxy: {
      // 本体知识服务（py-genai-ontology 38105）
      '/api/onto': 'http://localhost:38105',
      '/api/graph': 'http://localhost:38117'
    }
  }
})
