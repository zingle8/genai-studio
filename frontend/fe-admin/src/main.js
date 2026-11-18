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
import './assets/style.css'

let instance = null

const router = createRouter({
  history: createWebHistory(location.pathname.startsWith('/fe-admin/') ? '/fe-admin/' : '/'),
  routes: [
    { path: '/', redirect: '/apikey' },
    { path: '/apikey', component: () => import('./views/ApiKey.vue') },
    { path: '/billing', component: () => import('./views/Billing.vue') },
    { path: '/mcp', component: () => import('./views/Mcp.vue') },
    { path: '/agent', component: () => import('./views/Agent.vue') },
    { path: '/config', component: () => import('./views/Config.vue') },
    { path: '/perms', component: () => import('./views/Perms.vue') },
    { path: '/users', component: () => import('./views/Users.vue') },
    { path: '/ops', component: () => import('./views/Ops.vue') }
  ]
})

function renderApp(props = {}) {
  if (props.container) window.__GENAI_IN_BASE__ = true // 基座内挂载：同步打标，供 App.vue 隐藏自带导航
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
