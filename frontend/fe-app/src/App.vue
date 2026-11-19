<template>
  <!-- 登录页独立全屏渲染 -->
  <router-view v-if="$route.path === '/login'" />
  <div v-else class="app">
    <!-- 顶部公告条（内容在 平台配置 announce.* 配置），置于平台顶栏上方 -->
    <div v-if="announce.show" class="announce-bar">
      <span class="announce-text">
        {{ announce.content }}
        <a v-if="announce.link" class="announce-link" :href="'#' + announce.link" @click.prevent="go(announce.link)">点击查看详情 ›</a>
      </span>
      <button class="announce-close" aria-label="关闭公告" @click="closeAnnounce">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg>
      </button>
    </div>
    <header class="brand-bar">
      <button class="hamburger" @click.stop="sideOpen = !sideOpen" aria-label="菜单">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <span class="logo-brand">GenAI Studio</span>
      <span class="logo-badge">微服务v0.1</span>
      <div class="spacer"></div>
      <template v-if="user">
        <span class="text-sm muted">{{ user.name || user.username }}</span>
      </template>
      <router-link v-else class="btn btn-primary btn-sm" to="/login">登录</router-link>
    </header>
    <div class="main-wrap">
      <!-- 左侧导航（参考 AI Studio 侧边栏） -->
      <aside class="app-side" :class="{ open: sideOpen }">
        <nav>
          <template v-for="(item, i) in visibleMenus" :key="i">
            <div v-if="item.group" class="side-group">{{ item.group }}</div>
            <component
              :is="item.disabled ? 'div' : 'router-link'"
              v-else
              :to="item.disabled ? undefined : item.to"
              class="side-item"
              :class="{ active: isActive(item), disabled: item.disabled }"
            >
              <span class="side-icon" v-html="icons[item.icon]"></span>
              <span class="side-label">{{ item.label }}</span>
              <span v-if="item.disabled" class="side-tag">未开放</span>
              <!-- 悬停状态气泡：运行中(绿) / 建设中(灰) -->
              <span v-else class="menu-tip" :class="item.building ? 'gray' : 'green'">{{ item.building ? '建设中' : '运行中' }}</span>
            </component>
          </template>
        </nav>
        <!-- 侧边栏底部用户菜单（复刻 demo sidebar-user） -->
        <div v-if="user" class="sidebar-user" :class="{ open: userMenuOpen }">
          <button class="user-chip" @click.stop="userMenuOpen = !userMenuOpen">
            <span class="user-avatar">{{ avatarChar }}</span>
            <span class="user-meta">
              <span class="user-name">{{ user.name || user.username }}</span>
              <span class="user-role">{{ user.role || '用户' }}</span>
            </span>
            <svg class="user-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
          </button>
          <div class="user-dropdown" @click.stop>
            <div class="ud-head">
              <span class="user-avatar lg">{{ avatarChar }}</span>
              <span class="ud-info">
                <span class="ud-name">{{ user.name || user.username }}</span>
                <span class="ud-mail">{{ user.email || ((user.username || 'user') + '@genai-studio.cn') }}</span>
              </span>
            </div>
            <div class="ud-tags">
              <span class="tag tag-success">已登录</span>
              <span class="tag tag-accent">免费版</span>
            </div>
            <div class="ud-sep"></div>
            <a class="ud-item" href="javascript:void(0)" @click="go('/fe-admin/billing')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6M9 13h8M9 17h8"/></svg>
              我的账单
            </a>
            <a class="ud-item" href="javascript:void(0)" @click="go('/fe-docs/help')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
              帮助与反馈
            </a>
            <div class="ud-sep"></div>
            <button class="ud-item danger" @click="onLogout">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
              退出登录
            </button>
          </div>
        </div>
      </aside>
      <main class="main">
        <!-- 基座自有页面（首页等）：带 .content 内边距 -->
        <div v-if="!isSubApp" class="content">
          <router-view />
        </div>
        <!-- qiankun 子应用挂载容器：放在 .content 外层，避免与子应用自身的 .content
             内边距叠加（子应用页面与首页保持同一间距） -->
        <div id="subapp-container"></div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getUser, logout } from './api'

const user = ref(getUser())
const router = useRouter()
const route = useRoute()
// 子应用路由（/fe-xxx 前缀）由 qiankun 渲染，基座不再额外包 .content 内边距
const isSubApp = computed(() => route.path.startsWith('/fe-'))

// 登录/登出会切换路由并改写 localStorage，路由变化时重新读取用户信息
watch(() => route.path, () => {
  user.value = getUser()
  userMenuOpen.value = false
  sideOpen.value = false
})

const userMenuOpen = ref(false)
const sideOpen = ref(false)

// 顶部公告：从平台配置（genai_config.announce.*）读取；关闭后按内容指纹记忆，内容变更会重新弹出
const announce = ref({ show: false, content: '', link: '' })
async function loadAnnounce() {
  try {
    const r = await fetch('/api/configs/announcement').then(res => res.json())
    const d = r?.data || {}
    if (d.enabled && d.content) {
      let hash = 0
      for (const ch of String(d.content)) { hash = (hash * 31 + ch.charCodeAt(0)) | 0 }
      const closed = localStorage.getItem('announce_closed') === String(hash)
      announce.value = { show: !closed, content: d.content, link: d.link || '' }
    }
  } catch (e) { /* 公告拉取失败不影响主界面 */ }
}
function closeAnnounce() {
  let hash = 0
  for (const ch of announce.value.content) { hash = (hash * 31 + ch.charCodeAt(0)) | 0 }
  localStorage.setItem('announce_closed', String(hash))
  announce.value.show = false
}
loadAnnounce()
const avatarChar = computed(() => (user.value?.name || user.value?.username || 'A').charAt(0).toUpperCase())
function go(path) { router.push(path) }

// 菜单：参考 AI Studio 侧边栏结构；disabled=本期不开发，building=建设中（第二波交付）
// 含「管理」的菜单仅管理员（role=ADMIN）可见；分组下无可见项时整组隐藏
const isAdmin = computed(() => String(user.value?.role || '').toUpperCase() === 'ADMIN')
function filterAdminMenus(list) {
  const visible = list.filter(it => it.group || !(it.label || '').includes('管理') || isAdmin.value)
  const res = []
  for (let i = 0; i < visible.length; i++) {
    const it = visible[i]
    if (it.group) {
      let has = false
      for (let j = i + 1; j < visible.length && !visible[j].group; j++) { if (visible[j].label) { has = true; break } }
      if (!has) continue
    }
    res.push(it)
  }
  return res
}
const visibleMenus = computed(() => filterAdminMenus(menus))

const menus = [
  { label: '首页', icon: 'home', to: '/home' },
  { group: '开发者中心' },
  { label: 'API Key', icon: 'key', to: '/fe-admin/apikey' },
  { label: '账单', icon: 'doc', to: '/fe-admin/billing' },
  { label: '成本统计', icon: 'chart', to: '/fe-dashboard/costs' },
  { label: '使用日志', icon: 'file', to: '/fe-dashboard/usage-logs' },
  { group: '模型与能力' },
  { label: '模型广场', icon: 'models', to: '/fe-models/models' },
  { label: '模型管理', icon: 'models', to: '/fe-models/model-admin' },
  { label: '体验中心', icon: 'chat', to: '/fe-chats/playground' },
  { label: '提示词广场', icon: 'pen', to: '/fe-prompt/square' },
  { label: '提示词管理', icon: 'pen', to: '/fe-prompt/prompts' },
  { label: '知识库kb', icon: 'book', to: '/fe-knowledgebase/kb', },
  { label: '知识图谱Graph', icon: 'graph', to: '/fe-graph/graph', },
  { label: '本体图谱Onto', icon: 'onto', to: '/fe-graph/onto' },
  { label: 'RAG 管理', icon: 'search', to: '/fe-knowledgebase/rag', },
  { label: 'OCR 管理', icon: 'scan', to: '/fe-knowledgebase/ocr', },
  { label: 'MCP 管理', icon: 'plug', to: '/fe-admin/mcp', building: true },
  { label: 'MCP 广场', icon: 'store', to: '/fe-market/mcp-market', building: true },
  { label: 'Agent 管理', icon: 'robot', to: '/fe-admin/agent', building: true },
  { label: 'Agent 市场', icon: 'market', to: '/fe-market/agent-market', building: true },
  { label: 'Skill & Agent 市场', icon: 'skills', to: '/fe-market/skill-market', building: true },
  { group: '系统管理' },
  { label: '平台配置', icon: 'gear', to: '/fe-admin/config' },
  { label: '权限管理', icon: 'shield', to: '/fe-admin/perms' },
  { label: '用户管理', icon: 'users', to: '/fe-admin/users' },
  { label: '运维中心', icon: 'server', to: '/fe-admin/ops' },
  { group: '帮助中心' },
  { label: '接口文档', icon: 'bookdoc', to: '/fe-docs/api-docs' },
  { label: '帮助与反馈', icon: 'help', to: '/fe-docs/help' }
]

const icons = {
  home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/></svg>',
  key: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="8" cy="15" r="4"/><path d="M11 12 21 2m-4 4 3 3m-6 0 2 2"/></svg>',
  terminal: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>',
  user: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>',
  doc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6"/></svg>',
  wallet: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="6" width="20" height="14" rx="2"/><path d="M2 10h20"/><path d="M6 15h4"/></svg>',
  chart: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M7 15l4-6 4 3 5-8"/></svg>',
  file: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2h9l5 5v15H6z"/><path d="M9 13h8M9 17h8M9 9h2"/></svg>',
  models: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 2v2m6-2v2M9 20v2m6-2v2M2 9h2m-2 6h2m16-6h2m-2 6h2"/></svg>',
  chat: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-8 8H4l2-3a8 8 0 1 1 15-5z"/></svg>',
  pen: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4z"/></svg>',
  search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="7"/><path d="m21 21-4-4"/></svg>',
  book: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V2H6.5A2.5 2.5 0 0 0 4 4.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/></svg>',
  scan: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7V5a2 2 0 0 1 2-2h2m10 0h2a2 2 0 0 1 2 2v2m0 10v2a2 2 0 0 1-2 2h-2M7 22H5a2 2 0 0 1-2-2v-2"/><line x1="3" y1="12" x2="21" y2="12"/></svg>',
  graph: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="12" cy="18" r="3"/><path d="M8.5 8 11 15.5m4.5-7.5L13 15.5M9 6h6"/></svg>',
  onto: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="2" width="6" height="5" rx="1"/><rect x="2" y="17" width="6" height="5" rx="1"/><rect x="16" y="17" width="6" height="5" rx="1"/><path d="M12 7v5m0 0-7 5m7-5 7 5"/></svg>',
  plug: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 2v6m6-6v6M6 8h12v4a6 6 0 0 1-12 0z"/><path d="M12 18v4"/></svg>',
  robot: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="8" width="16" height="12" rx="2"/><path d="M12 8V4m-2 0h4"/><circle cx="9" cy="14" r="1"/><circle cx="15" cy="14" r="1"/></svg>',
  store: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l1.5-5h15L21 9"/><path d="M3 9a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/><path d="M4 12v9h16v-9"/><path d="M9 21v-6h6v6"/></svg>',
  market: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 6h15l-1.5 8H8z"/><circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M6 6L5 3H2"/></svg>',
  skills: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l2.4 4.9 5.4.8-3.9 3.8.9 5.4-4.8-2.5-4.8 2.5.9-5.4L4.2 7.7l5.4-.8z"/><path d="M5 20h14"/></svg>',
  gear: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3m-3.6-6.4-2.1 2.1m-8.6 8.6-2.1 2.1m0-12.8 2.1 2.1m8.6 8.6 2.1 2.1"/></svg>',
  shield: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
  users: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="9" cy="8" r="4"/><path d="M2 21c0-4 3.5-6 7-6s7 2 7 6"/><path d="M16 4a4 4 0 0 1 0 8m5 9c0-3-1.5-5-4-5.7"/></svg>',
  server: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="7" rx="2"/><rect x="2" y="14" width="20" height="7" rx="2"/><line x1="6" y1="6.5" x2="6.01" y2="6.5"/><line x1="6" y1="17.5" x2="6.01" y2="17.5"/></svg>',
  bookdoc: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 2h9l5 5v15H6z"/><path d="M14 2v6h6M9 13h8M9 17h8"/></svg>',
  help: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>'
}

function isActive(item) {
  if (!item.to) return false
  return route.path === item.to || route.path.startsWith(item.to + '/')
}

function onLogout() {
  logout()
  user.value = null
  router.push('/login')
}
</script>

<style>
.brand-bar {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 24px; border-bottom: 1px solid var(--border-light); background: #fff;
}
.logo-brand { font-size: 17px; font-weight: 700; letter-spacing: -0.4px; }
.logo-badge { font-size: 10px; color: #fff; background: var(--text-primary); padding: 2px 6px; border-radius: 4px; }
.brand-bar .spacer { flex: 1; }
/* 顶部公告条（平台配置 announce.* 驱动） */
.announce-bar {
  display: flex; align-items: center; justify-content: center; gap: 12px;
  padding: 7px 44px 7px 16px;
  background: linear-gradient(90deg, #4D6BFE, #6E5BFF);
  color: #fff; font-size: 12.5px;
  position: relative; flex-shrink: 0;
}
.announce-text { text-align: center; line-height: 1.5; }
.announce-link { color: #fff; font-weight: 600; text-decoration: underline; text-underline-offset: 2px; margin-left: 4px; }
.announce-link:hover { opacity: 0.85; }
.announce-close {
  position: absolute; right: 10px; top: 50%; transform: translateY(-50%);
  width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;
  background: none; border: none; color: #fff; cursor: pointer; opacity: 0.85; border-radius: 6px;
}
.announce-close:hover { opacity: 1; background: rgba(255,255,255,0.15); }
.announce-close svg { width: 14px; height: 14px; }
/* 基座布局用 .app 前缀提升优先级，避免被子应用泄漏的全局同名类覆盖 */
.app { height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
.app .main-wrap { display: flex; flex: 1; min-height: 0; }
.app .app-side {
  width: 236px; flex-shrink: 0; border-right: 1px solid var(--border-light);
  background: #fff; padding: 12px 14px 14px;
  display: flex; flex-direction: column;
  height: 100%; overflow: hidden;
}
.app .app-side nav { display: flex; flex-direction: column; gap: 2px; flex: 1; overflow-y: auto; min-height: 0; }
.app .app-side .side-group {
  font-size: 11px; color: var(--text-tertiary); letter-spacing: 1px;
  padding: 14px 12px 6px;
}
.app .app-side .side-item {
  display: flex; align-items: center; gap: 14px;
  padding: 9px 14px; border-radius: 8px; cursor: pointer;
  font-size: 13.5px; color: var(--text-secondary); text-decoration: none;
  white-space: nowrap;
  transition: background .15s, color .15s;
}
.app .app-side .side-item:hover { background: var(--bg-soft); color: var(--text-primary); }
.app .app-side .side-item.active { background: var(--accent-soft); color: var(--accent); font-weight: 500; }
.app .app-side .side-item.disabled { color: var(--text-tertiary); cursor: not-allowed; }
.app .app-side .side-item.disabled:hover { background: transparent; color: var(--text-tertiary); }
.app .app-side .side-icon { width: 16px; height: 16px; flex-shrink: 0; display: inline-flex; }
.app .app-side .side-icon svg { width: 100%; height: 100%; }
.app .app-side .side-label { flex: 1; }
.app .app-side /* 菜单悬停状态气泡（运行中=绿 / 建设中=灰） */
.side-item { position: relative; }
.menu-tip {
  position: absolute; right: 8px; top: 50%; transform: translateY(-50%) scale(.9);
  padding: 3px 10px; border-radius: 6px; font-size: 11.5px; white-space: nowrap;
  background: #1f2430; opacity: 0; pointer-events: none;
  transition: opacity .15s, transform .15s; z-index: 60; box-shadow: 0 4px 14px rgba(0,0,0,0.18);
  font-weight: 600;
}
.menu-tip::before {
  content: ''; position: absolute; left: -4px; top: 50%; margin-top: -4px;
  border: 4px solid transparent; border-right-color: #1f2430;
}
/* 气泡悬浮时标签淡出，避免遮挡 */
.side-item:hover .side-label { opacity: .45; }
.side-item:hover .menu-tip { opacity: 1; transform: translateY(-50%) scale(1); }
.menu-tip.green { color: #22c55e; }
.menu-tip.gray { color: #9ca3af; }
.side-tag {
  font-size: 10px; color: var(--text-tertiary);
  border: 1px solid var(--border); border-radius: 4px; padding: 0 4px; line-height: 16px;
}
.app .main { flex: 1; min-width: 0; height: 100%; overflow-y: auto; }

/* ===== 侧边栏底部用户菜单（复刻 demo） ===== */
.hamburger { display: none; background: none; border: none; padding: 6px; margin-right: 4px; cursor: pointer; color: var(--text-secondary); }
.hamburger svg { width: 20px; height: 20px; display: block; }

.app .app-side .sidebar-user { position: relative; margin-top: auto; padding: 9px 10px 10px; border-top: 1px solid var(--border-light); flex-shrink: 0; }
.user-chip { display: flex; align-items: center; gap: 9px; width: 100%; padding: 7px 10px; border-radius: var(--radius); text-align: left; background: none; border: none; cursor: pointer; transition: background 0.14s; }
.user-chip:hover { background: var(--sidebar-hover); }
.sidebar-user.open .user-chip { background: var(--sidebar-hover); }
.user-avatar { width: 28px; height: 28px; border-radius: 50%; background: linear-gradient(135deg, #4D6BFE, #7B5CFF); color: #fff; font-size: 12px; font-weight: 600; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.user-avatar.lg { width: 34px; height: 34px; font-size: 13px; }
.user-chip .user-meta { flex: 1; min-width: 0; display: flex; flex-direction: column; text-align: left; }
.user-name { font-size: 13px; font-weight: 500; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { font-size: 11px; color: var(--text-tertiary); margin-top: 1px; }
.user-caret { width: 14px; height: 14px; color: var(--text-tertiary); transition: transform 0.18s; flex-shrink: 0; }
.sidebar-user.open .user-caret { transform: rotate(180deg); }
.user-dropdown { position: absolute; left: 10px; right: 10px; bottom: calc(100% + 6px); background: #fff; border: 1px solid var(--border); border-radius: 12px; box-shadow: var(--shadow-lg); padding: 6px; opacity: 0; visibility: hidden; transform: translateY(6px); transition: opacity 0.16s, transform 0.16s, visibility 0.16s; z-index: 60; }
.sidebar-user.open .user-dropdown { opacity: 1; visibility: visible; transform: translateY(0); }
.ud-head { display: flex; align-items: center; gap: 9px; padding: 7px 8px 5px; }
.ud-info { min-width: 0; display: flex; flex-direction: column; }
.ud-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.ud-mail { font-size: 11.5px; color: var(--text-tertiary); margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.ud-tags { display: flex; gap: 6px; padding: 0 8px 8px; }
.ud-sep { height: 1px; background: var(--border-light); margin: 5px 4px; }
.ud-item { display: flex; align-items: center; gap: 9px; width: 100%; padding: 8px 9px; border-radius: 8px; font-size: 13px; color: var(--text-secondary); background: none; border: none; cursor: pointer; transition: background 0.13s, color 0.13s; }
.ud-item:hover { background: var(--bg-soft); color: var(--text-primary); }
.ud-item svg { width: 15px; height: 15px; flex-shrink: 0; }
.ud-item.danger { color: var(--danger); }
.ud-item.danger:hover { background: var(--danger-soft); color: var(--danger); }

/* ===== 基座响应式 ===== */
@media (max-width: 960px) {
  .hamburger { display: block; }
  .app .main-wrap { display: block; position: relative; }
  .app .app-side { position: fixed; left: 0; top: var(--header-h, 48px); bottom: 0; width: 240px; z-index: 70; transform: translateX(-100%); transition: transform 0.2s; box-shadow: none; height: auto; }
  .app .app-side.open { transform: none; box-shadow: var(--shadow-lg); }
  .app .app-side .sidebar-user { display: block; }
  .app .main { height: calc(100vh - var(--header-h, 48px)); }
}
@media (max-width: 640px) {
  .brand-bar { padding: 0 10px; }
  .logo-badge { display: none; }
}
</style>
