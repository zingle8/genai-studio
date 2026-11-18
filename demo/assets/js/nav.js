/* 侧边栏导航菜单数据 */
const NAV_GROUPS = [
  {
    title: '',
    items: [
      { href: 'index.html', label: '首页', key: 'dashboard', icon: 'home' }
    ]
  },
  {
    title: '开发者中心',
    items: [
      { href: 'pages/developer.html', label: 'API Key', key: 'developer', icon: 'key' },
      { href: 'pages/workbench.html', label: '工作台', key: 'workbench', icon: 'terminal' },
      { href: 'pages/user-center.html', label: '用户中心', key: 'user-center', icon: 'user' },
      { href: 'pages/orders.html', label: '账单', key: 'orders', icon: 'bill' },
      { href: 'pages/topup.html', label: '充值', key: 'topup', icon: 'wallet' },
      { href: 'pages/cost-statistics.html', label: '成本统计', key: 'cost-statistics', icon: 'chart' },
      { href: 'pages/usage-logs.html', label: '使用日志', key: 'usage-logs', icon: 'log' }
    ]
  },
  {
    title: '模型与能力',
    items: [
      { href: 'pages/model-config.html', label: '模型广场', key: 'model-config', icon: 'cpu' },
      { href: 'pages/chat-workbench.html', label: '体验中心', key: 'chat', icon: 'chat' },
      { href: 'pages/prompt-management.html', label: '提示词管理', key: 'prompt', icon: 'edit' },
      { href: 'pages/rag-management.html', label: 'RAG 管理', key: 'rag', icon: 'search' },
      { href: 'pages/knowledge-base.html', label: '知识库', key: 'knowledge-base', icon: 'book' },
      { href: 'pages/ocr-management.html', label: 'OCR 管理', key: 'ocr-management', icon: 'scan' },
      { href: 'pages/knowledge-graph.html', label: '知识图谱Graph', key: 'knowledge-graph', icon: 'graph' },
      { href: 'pages/ontology.html', label: '本体图谱Onto', key: 'ontology', icon: 'ontology' },
      { href: 'pages/mcp-management.html', label: 'MCP 管理', key: 'mcp', icon: 'plug' },
      { href: 'pages/agent-management.html', label: 'Skill / Agent', key: 'agent', icon: 'bot' }
    ]
  },
  {
    title: '系统管理',
    items: [
      { href: 'pages/platform-config.html', label: '平台配置', key: 'platform-config', icon: 'settings' },
      { href: 'pages/permission-management.html', label: '权限管理', key: 'permission', icon: 'shield' },
      { href: 'pages/user-management.html', label: '用户管理', key: 'user-management', icon: 'users' },
      { href: 'pages/ops-center.html', label: '运维中心', key: 'ops', icon: 'server' }
    ]
  }
];

const BOTTOM_LINKS = [
  { label: '接口文档', icon: 'doc', href: 'pages/api-docs.html', key: 'api-docs' },
  { label: '帮助与反馈', icon: 'help', href: 'pages/help-feedback.html', key: 'help' },
  { label: '产品定价', icon: 'tag', href: 'pages/pricing.html', key: 'pricing' },
  { label: '网页版免费对话', icon: 'globe', href: 'pages/web-chat.html', key: 'web-chat' }
];

const ICONS = {
  home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2h-4v-7h-6v7H5a2 2 0 0 1-2-2V9z"/>',
  key: '<circle cx="7.5" cy="15.5" r="4.5"/><path d="M10.7 12.3L21 2M18 5l3 3M15 8l2 2"/>',
  user: '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',
  bill: '<path d="M4 2h16v20l-3-2-2 2-3-2-3 2-2-2-3 2V2z"/><line x1="9" y1="8" x2="15" y2="8"/><line x1="9" y1="12" x2="15" y2="12"/>',
  wallet: '<path d="M20 12V8H6a2 2 0 0 1 0-4h12v4"/><path d="M4 6v12a2 2 0 0 0 2 2h14v-4"/><path d="M18 12a2 2 0 0 0 0 4h4v-4z"/>',
  chart: '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
  log: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="13" y2="17"/>',
  cpu: '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="2" x2="9" y2="4"/><line x1="15" y1="2" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="22"/><line x1="15" y1="20" x2="15" y2="22"/><line x1="20" y1="9" x2="22" y2="9"/><line x1="20" y1="15" x2="22" y2="15"/><line x1="2" y1="9" x2="4" y2="9"/><line x1="2" y1="15" x2="4" y2="15"/>',
  edit: '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
  search: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
  book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
  scan: '<path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><line x1="7" y1="9" x2="17" y2="9"/><line x1="7" y1="13" x2="17" y2="13"/><line x1="7" y1="17" x2="13" y2="17"/>',
  graph: '<circle cx="6" cy="6" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="18" r="3"/><line x1="9" y1="6" x2="15" y2="6"/><line x1="6" y1="9" x2="6" y2="15"/><line x1="18" y1="9" x2="18" y2="15"/><line x1="9" y1="18" x2="15" y2="18"/>',
  space: '<path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>',
  ontology: '<rect x="9" y="2" width="6" height="5" rx="1"/><rect x="2" y="17" width="6" height="5" rx="1"/><rect x="16" y="17" width="6" height="5" rx="1"/><path d="M12 7v7M5 14v3M19 14v3"/><path d="M5 14h14"/>',
  plug: '<path d="M9 2v6M15 2v6M5 8h14v3a6 6 0 0 1-6 6h-2a6 6 0 0 1-6-6V8zM12 17v5"/>',
  bot: '<rect x="4" y="8" width="16" height="12" rx="3"/><circle cx="12" cy="4" r="2"/><path d="M12 6v2"/><circle cx="9" cy="14" r="1"/><circle cx="15" cy="14" r="1"/>',
  chat: '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
  settings: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
  users: '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
  server: '<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>',
  doc: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>',
  help: '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
  tag: '<path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/>',
  globe: '<circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>',
  terminal: '<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>'
};

/* ==================== 登录态（演示环境，存 localStorage） ==================== */
const AUTH_KEY = 'ai_studio_user';
const AUTH_LOGOUT_FLAG = 'ai_studio_logged_out';

/* 默认演示账号：admin / admin123，登录页已预填，点击即登录 */
const DEMO_ADMIN = {
  username: 'admin',
  password: 'admin123',
  name: 'Admin',
  role: '超级管理员',
  email: 'admin@ai-studio.cn',
  plan: '免费版',
  avatar: 'A'
};

const Auth = {
  getUser() {
    try { return JSON.parse(localStorage.getItem(AUTH_KEY) || 'null'); } catch (e) { return null; }
  },
  isLogin() { return !!Auth.getUser(); },
  /* 首次访问自动注入演示账号，保证各页面都有完整用户上下文 */
  ensure() {
    if (Auth.getUser()) return Auth.getUser();
    if (localStorage.getItem(AUTH_LOGOUT_FLAG)) return null;
    return Auth.login(DEMO_ADMIN.username, DEMO_ADMIN.password);
  },
  login(username, password) {
    const isDefault = username === DEMO_ADMIN.username;
    const u = {
      username: username,
      name: isDefault ? DEMO_ADMIN.name : username,
      role: isDefault ? DEMO_ADMIN.role : '普通用户',
      email: isDefault ? DEMO_ADMIN.email : username + '@ai-studio.cn',
      plan: DEMO_ADMIN.plan,
      avatar: (isDefault ? 'A' : String(username).charAt(0)).toUpperCase(),
      loginAt: Date.now()
    };
    localStorage.setItem(AUTH_KEY, JSON.stringify(u));
    localStorage.removeItem(AUTH_LOGOUT_FLAG);
    return u;
  },
  /* 退出登录并跳转登录页 */
  logout(toLogin) {
    localStorage.removeItem(AUTH_KEY);
    localStorage.setItem(AUTH_LOGOUT_FLAG, '1');
    if (toLogin !== false) {
      window.location.href = ASSET_BASE + 'pages/login.html?logout=1';
    }
  },
  /* 登录页地址（带来源回跳） */
  loginUrl(redirect) {
    const to = redirect || (window.location.pathname + window.location.search);
    return ASSET_BASE + 'pages/login.html?redirect=' + encodeURIComponent(to);
  }
};
window.Auth = Auth;

/* 顶部蓝色公告条 */
function renderAnnounceBar() {
  return `<div class="announce-bar">
    <span class="announce-text">AI Studio V4.1 发布，文本与 Agent 能力再升级，兼具多模态视觉理解能力，能力更强、速度更快、成本更低 —— 欢迎测试与反馈，<b>点击查看详情 ›</b></span>
    <button class="announce-close" onclick="closeAnnounceBar(this)">×</button>
  </div>`;
}

/* 关闭公告条：同步调整侧边栏高度，避免底部被裁切 */
window.closeAnnounceBar = function (btn) {
  if (btn && btn.parentElement) btn.parentElement.style.display = 'none';
  document.documentElement.style.setProperty('--announce-h', '0px');
};

/* 站点根路径：由 nav.js 自身地址（assets/js/nav.js）反推，与当前页面 URL 无关
   例如 http://host/demo/assets/js/nav.js?v=2 → http://host/demo/  */
const ASSET_BASE = (function () {
  var src = (document.currentScript && document.currentScript.src) || '';
  var m = src.match(/^(.*?)assets\/js\/nav\.js(\?.*)?$/);
  if (m) return m[1];
  /* 兜底：按当前路径推断（位于 pages/ 子目录时回退一层） */
  var base = window.location.href.replace(/[?#].*$/, '').replace(/[^/]*$/, '');
  return /\/pages\/$/.test(base) ? base.replace(/pages\/$/, '') : base;
})();

/* 侧边栏底部用户菜单：展示登录信息，可进入用户中心 / 退出登录 */
function renderUserMenu(u) {
  return `<div class="sidebar-user" id="sidebarUser">
    <button class="user-chip" onclick="toggleUserMenu(event)">
      <span class="user-avatar">${u.avatar || 'A'}</span>
      <span class="user-meta">
        <span class="user-name">${u.name}</span>
        <span class="user-role">${u.role}</span>
      </span>
      <svg class="user-caret" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>
    </button>

    <div class="user-dropdown">
      <div class="ud-head">
        <span class="user-avatar lg">${u.avatar || 'A'}</span>
        <span class="ud-info">
          <span class="ud-name">${u.name}</span>
          <span class="ud-mail">${u.email}</span>
        </span>
      </div>
      <div class="ud-tags">
        <span class="tag tag-success">已登录</span>
        <span class="tag tag-accent">${u.plan || '免费版'}</span>
      </div>
      <a class="ud-item" href="${ASSET_BASE}pages/user-center.html">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICONS.user}</svg>用户中心
      </a>
      <a class="ud-item" href="${ASSET_BASE}pages/orders.html">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICONS.bill}</svg>我的账单
      </a>
      <a class="ud-item" href="${ASSET_BASE}pages/help-feedback.html">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${ICONS.help}</svg>帮助与反馈
      </a>
      <div class="ud-sep"></div>
      <button class="ud-item danger" onclick="Auth.logout()">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>退出登录
      </button>
    </div>
  </div>`;
}

window.toggleUserMenu = function (e) {
  if (e) e.stopPropagation();
  const el = document.getElementById('sidebarUser');
  if (el) el.classList.toggle('open');
};

document.addEventListener('click', function () {
  const el = document.getElementById('sidebarUser');
  if (el) el.classList.remove('open');
});
document.addEventListener('keydown', function (e) {
  if (e.key === 'Escape') {
    const el = document.getElementById('sidebarUser');
    if (el) el.classList.remove('open');
  }
});

/* 侧边栏（Logo + 导航 + 底部链接 + 用户菜单） */
function renderSidebar(activeKey) {
  const nav = NAV_GROUPS.map((group) => {
    const title = group.title ? `<div class="nav-section-title">${group.title}</div>` : '';
    const items = group.items.map(item => {
      const icon = ICONS[item.icon] || ICONS.home;
      const active = item.key === activeKey ? 'active' : '';
      const blank = item.blank ? ' target="_blank" rel="noopener"' : '';
      return `<a class="nav-item ${active}" href="${ASSET_BASE}${item.href}"${blank}>
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${icon}</svg>
        <span>${item.label}</span>
      </a>`;
    }).join('');
    return title + items;
  }).join('');

  const bottom = BOTTOM_LINKS.map(l => {
    const icon = ICONS[l.icon] || ICONS.doc;
    const active = l.key === activeKey ? 'active' : '';
    return `<a class="nav-item ${active}" href="${ASSET_BASE}${l.href}" title="${l.label}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${icon}</svg>
      <span>${l.label}</span>
    </a>`;
  }).join('');

  const user = Auth.ensure();

  return `<aside class="sidebar">
    <a class="sidebar-logo" href="${ASSET_BASE}index.html">
      <span class="logo-brand">AI Studio</span>
      <span class="logo-badge">微服务</span>
    </a>
    <div class="sidebar-scroll">
      <nav class="sidebar-nav">${nav}</nav>
      <div class="sidebar-bottom">${bottom}</div>
    </div>
    ${user ? renderUserMenu(user) : ''}
  </aside>`;
}

/* 通用初始化：登录校验 + 注入公告条 + 侧边栏 */
window.initLayout = function(activeKey, options) {
  const opts = options || {};

  /* 未登录（首次访问会自动注入演示账号）→ 跳转登录页并记录来源 */
  if (!Auth.ensure() && !opts.skipAuth) {
    window.location.replace(Auth.loginUrl());
    return;
  }

  const brandRoot = document.getElementById('brand-bar-root');
  if (brandRoot) brandRoot.innerHTML = renderAnnounceBar();

  const toolbarRoot = document.getElementById('toolbar-root');
  if (toolbarRoot) toolbarRoot.remove();

  const sidebarRoot = document.getElementById('sidebar-root');
  if (sidebarRoot) sidebarRoot.innerHTML = renderSidebar(activeKey);
};