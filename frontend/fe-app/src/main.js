import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { registerMicroApps, start } from 'qiankun'
import App from './App.vue'
import './assets/style.css'

const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    { path: '/login', component: () => import('./views/Login.vue') },
    { path: '/', redirect: '/home' },
    { path: '/home', component: () => import('./views/Home.vue') }
  ]
})

// 登录守卫：未登录（无 token）一律回登录页
router.beforeEach((to) => {
  const token = localStorage.getItem('genai_token')
  if (to.path !== '/login' && !token) {
    return { path: '/login' }
  }
})

// 微前端子应用注册（按后端模块划分）
// 含「管理」的菜单仅 ADMIN 可访问：非管理员直接输入 URL 时重定向首页
const adminOnlyPaths = ['/fe-models/model-admin', '/fe-prompt/prompts', '/fe-knowledgebase/rag',
  '/fe-knowledgebase/ocr', '/fe-admin/mcp', '/fe-admin/agent', '/fe-admin/perms', '/fe-admin/users']
router.beforeEach((to) => {
  if (adminOnlyPaths.includes(to.path)) {
    const role = String((JSON.parse(localStorage.getItem('genai_user') || 'null') || {}).role || '').toUpperCase()
    if (role !== 'ADMIN') return '/home'
  }
})

registerMicroApps([
  { name: 'fe-dashboard', entry: '//localhost:38201', container: '#subapp-container', activeRule: '/fe-dashboard' },
  { name: 'fe-chats', entry: '//localhost:38202', container: '#subapp-container', activeRule: '/fe-chats' },
  { name: 'fe-prompt', entry: '//localhost:38203', container: '#subapp-container', activeRule: '/fe-prompt' },
  { name: 'fe-models', entry: '//localhost:38204', container: '#subapp-container', activeRule: '/fe-models' },
  { name: 'fe-knowledgebase', entry: '//localhost:38205', container: '#subapp-container', activeRule: '/fe-knowledgebase' },
  { name: 'fe-graph', entry: '//localhost:38206', container: '#subapp-container', activeRule: '/fe-graph' },
  { name: 'fe-market', entry: '//localhost:38207', container: '#subapp-container', activeRule: '/fe-market' },
  { name: 'fe-docs', entry: '//localhost:38208', container: '#subapp-container', activeRule: '/fe-docs' },
  { name: 'fe-admin', entry: '//localhost:38209', container: '#subapp-container', activeRule: '/fe-admin' }
])

createApp(App).use(router).mount('#app')
start({ prefetch: false })
