import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
// qiankun 生命周期注册（等价 vite-plugin-qiankun helper，包内 ESM 未导出该方法故内联）
const qk = window.proxy || window
function renderWithQiankun(lifecycles) {
  if (qk && qk.__POWERED_BY_QIANKUN__ && qk.qiankunName) {
    window.moudleQiankunAppLifeCycles = window.moudleQiankunAppLifeCycles || {}
    window.moudleQiankunAppLifeCycles[qk.qiankunName] = lifecycles
  }
}

let instance = null

const router = createRouter({
  history: createWebHistory(location.pathname.startsWith('/fe-market/') ? '/fe-market/' : '/'),
  routes: [
    { path: '/', redirect: '/mcp-market' },
    { path: '/mcp-market', component: () => import('./views/Placeholder.vue'), meta: { title: 'MCP 广场', desc: '发现与订阅 MCP 服务（对应后端 jv-genai-market）' } },
    { path: '/agent-market', component: () => import('./views/Placeholder.vue'), meta: { title: 'Agent 市场', desc: '发现与订阅智能体应用（对应后端 jv-genai-market）' } },
    { path: '/skill-market', component: () => import('./views/Placeholder.vue'), meta: { title: 'Skill & Agent 市场', desc: '技能与智能体市场（对应后端 jv-genai-market）' } }
  ]
})

// qiankun 生命周期
function renderApp(props = {}) {
  instance = createApp(App)
  instance.use(router)
  const el = props.container ? props.container.querySelector('#app') : '#app'
  instance.mount(el)
}

renderWithQiankun({
  bootstrap() {},
  mount(props) { renderApp(props) },
  unmount() { if (instance) { instance.unmount(); instance = null } },
  update() {}
})

if (!window.proxy) { renderApp() }
