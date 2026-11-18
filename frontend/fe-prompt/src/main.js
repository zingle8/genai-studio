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
const base = location.pathname.startsWith('/fe-prompt/') ? '/fe-prompt/' : '/'

const router = createRouter({
  history: createWebHistory(base),
  routes: [{ path: '/', redirect: '/prompts' }, { path: '/prompts', component: () => import('./views/Prompts.vue') }]
})

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
