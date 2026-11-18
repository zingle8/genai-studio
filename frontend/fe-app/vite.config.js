import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 基座应用（门户 + 登录），端口 38200
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 38200,
        proxy: {
      '/api/onto': 'http://localhost:38105',
      // 知识库 py-genai-knowledgebase
      '/api/kb': 'http://localhost:38116',
      // 知识图谱 py-genai-graph
      '/api/graph': 'http://localhost:38117',
      // OCR py-genai-ocr
      '/api/ocr': 'http://localhost:38118',
      // RAG 管理 py-genai-rag-systemone
      '/api/rag': 'http://localhost:38119',

      // 认证服务 jv-genai-auth
      '/api/auth': 'http://localhost:38081',
      // 模型广场 jv-genai-models
      '/api/models': 'http://localhost:38086',
      // 提示词 jv-genai-prompt
      '/api/prompts': 'http://localhost:38089',
      // 会话/体验中心 jv-genai-chats
      '/api/chats': 'http://localhost:38090',
      // MCP 管理 jv-genai-mcpgateway
      '/api/mcp': 'http://localhost:38084',
      // Skill/Agent jv-genai-agentgateway
      '/api/agents': 'http://localhost:38085',
      // 平台配置 jv-genai-config
      '/api/configs': 'http://localhost:38087',
      // 运维中心 jv-genai-dashboard
      '/api/ops': 'http://localhost:38082',
      // 用户/权限（jv-genai-user 代理网关）
      '/api/users': 'http://localhost:38088',
      '/api/perms': 'http://localhost:38088',
      // 接口文档 jv-genai-docs
      '/api/docs': 'http://localhost:38096',
      // API Key 可用列表（jv-genai-apikey，体验中心子应用经基座访问时需要）
      '/api/apikeys': 'http://localhost:38091',
      // 模型路由直连（jv-genai-router，体验中心子应用经基座访问时需要）
      '/v1': 'http://localhost:38100',
      // 开发者中心（fe-admin 相关后端）
      '/api/apikeys': 'http://localhost:38091',
      '/api/billing': 'http://localhost:38092',
      '/api/costs': 'http://localhost:38093',
      '/api/logs': 'http://localhost:38094'
    }
  }
})
