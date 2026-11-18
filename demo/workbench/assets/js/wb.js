/* ============================================================
   AI Workbench · 共享脚本（顶栏导航 / 图标 / Toast / 文件树数据）
   ============================================================ */

const WB_ICONS = {
  home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2h-4v-7h-6v7H5a2 2 0 0 1-2-2V9z"/>',
  folder: '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
  book: '<path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>',
  terminal: '<polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/>',
  activity: '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
  chart: '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 5-6"/>',
  caret: '<polyline points="9 18 15 12 9 6"/>',
  file: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>',
  plus: '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
  play: '<polygon points="6 4 20 12 6 20 6 4"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="1"/>',
  refresh: '<polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.13-9.36L23 10"/>',
  up: '<line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/>',
  down: '<line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/>',
  trash: '<polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  code: '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
  edit: '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>',
  cpu: '<rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="2" x2="9" y2="4"/><line x1="15" y1="2" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="22"/><line x1="15" y1="20" x2="15" y2="22"/><line x1="20" y1="9" x2="22" y2="9"/><line x1="20" y1="15" x2="22" y2="15"/><line x1="2" y1="9" x2="4" y2="9"/><line x1="2" y1="15" x2="4" y2="15"/>',
  upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
  search: '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
  arrowLeft: '<line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/>',
  ext: '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>',
  check: '<polyline points="20 6 9 17 4 12"/>',
  x: '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>',
  info: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/>',
  gpu: '<rect x="2" y="6" width="20" height="12" rx="2"/><circle cx="8" cy="12" r="2.5"/><circle cx="16" cy="12" r="2.5"/>',
  clock: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
  server: '<rect x="2" y="2" width="20" height="8" rx="2"/><rect x="2" y="14" width="20" height="8" rx="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>'
};

function wbIcon(name, size) {
  return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"' +
    (size ? ' style="width:' + size + 'px;height:' + size + 'px"' : '') + '>' + (WB_ICONS[name] || '') + '</svg>';
}

/* 顶部导航 */
const WB_NAV = [
  { id: 'home', href: 'index.html', label: '控制台', icon: 'home' },
  { id: 'files', href: 'files.html', label: '文件', icon: 'folder' },
  { id: 'notebook', href: 'notebook.html', label: 'Notebook', icon: 'book' },
  { id: 'terminals', href: 'terminals.html', label: '终端', icon: 'terminal' },
  { id: 'sessions', href: 'sessions.html', label: '运行中的会话', icon: 'activity' },
  { id: 'resources', href: 'resources.html', label: '资源监控', icon: 'chart' }
];

window.initWb = function (activeId) {
  var root = document.getElementById('wb-header-root');
  if (!root) return;

  /* 内嵌模式：iframe 中或带 ?embed=1 → 隐藏"返回 AI Studio"，内部跳转保留参数 */
  var embedded = (window.self !== window.top) || /embed=1/.test(window.location.search);

  var links = WB_NAV.map(function (n) {
    var href = n.href + (embedded ? '?embed=1' : '');
    return '<a href="' + href + '" class="' + (n.id === activeId ? 'active' : '') + '">' +
      wbIcon(n.icon) + '<span>' + n.label + '</span></a>';
  }).join('');

  root.innerHTML = '<header class="wb-header"><div class="wb-header-inner">' +
    '<a class="wb-logo" href="index.html' + (embedded ? '?embed=1' : '') + '">' +
      '<span class="wb-logo-mark">λ</span>' +
      '<span class="wb-logo-name">AI Workbench</span>' +
      '<span class="wb-logo-sub">v1.0 Beta</span>' +
    '</a>' +
    '<nav class="wb-nav">' + links + '</nav>' +
    '<div class="wb-header-right">' +
      '<span class="wb-server-chip" title="服务器状态"><i></i>服务器运行中</span>' +
      (embedded ? '' :
        '<a class="wb-back-link" href="../index.html">' + wbIcon('arrowLeft', 13) + '返回 AI Studio</a>') +
      '<span class="wb-avatar" title="Admin（演示账号）">A</span>' +
    '</div>' +
    '</div></header>';

  if (!document.querySelector('.wb-toast-wrap')) {
    var tw = document.createElement('div');
    tw.className = 'wb-toast-wrap';
    document.body.appendChild(tw);
  }
};

/* Toast 提示 */
window.wbToast = function (msg, type) {
  var wrap = document.querySelector('.wb-toast-wrap');
  if (!wrap) return;
  var icon = type === 'err' ? 'x' : (type === 'ok' ? 'check' : 'info');
  var t = document.createElement('div');
  t.className = 'wb-toast ' + (type || '');
  t.innerHTML = wbIcon(icon) + '<span>' + msg + '</span>';
  wrap.appendChild(t);
  setTimeout(function () {
    t.classList.add('out');
    setTimeout(function () { t.remove(); }, 300);
  }, 2600);
};

/* 下拉菜单开关（点击切换，点击外部关闭） */
window.wbToggleMenu = function (el, e) {
  if (e) e.stopPropagation();
  document.querySelectorAll('.wb-dropdown.open').forEach(function (d) {
    if (d !== el.closest('.wb-dropdown')) d.classList.remove('open');
  });
  var dd = el.closest('.wb-dropdown');
  if (dd) dd.classList.toggle('open');
};
document.addEventListener('click', function () {
  document.querySelectorAll('.wb-dropdown.open').forEach(function (d) { d.classList.remove('open'); });
});

/* ==================== 共享文件系统数据（演示） ==================== */
const WB_FS = {
  name: '~', children: [
    { name: 'notebooks', dir: true, children: [
      { name: '01-数据探索.ipynb', type: 'nb', size: '24 KB', mtime: '今天 14:32', running: true },
      { name: '02-模型训练.ipynb', type: 'nb', size: '156 KB', mtime: '今天 11:08', running: true },
      { name: '03-模型评估.ipynb', type: 'nb', size: '88 KB', mtime: '昨天 19:21' },
      { name: 'EDA-销售数据.ipynb', type: 'nb', size: '42 KB', mtime: '3 天前' }
    ]},
    { name: 'data', dir: true, children: [
      { name: 'sales_2026.csv', type: 'csv', size: '12.4 MB', mtime: '昨天 09:12' },
      { name: 'sales_2025.csv', type: 'csv', size: '11.8 MB', mtime: '上周' },
      { name: 'products.parquet', type: 'txt', size: '38.2 MB', mtime: '上周' }
    ]},
    { name: 'models', dir: true, children: [
      { name: 'xgb_v3.pkl', type: 'txt', size: '8.6 MB', mtime: '今天 12:40' },
      { name: 'lstm_v1.pkl', type: 'txt', size: '21.3 MB', mtime: '上周' }
    ]},
    { name: 'train.py', type: 'py', size: '6 KB', mtime: '今天 10:02' },
    { name: 'eval.py', type: 'py', size: '4 KB', mtime: '昨天' },
    { name: 'requirements.txt', type: 'txt', size: '1 KB', mtime: '上周' },
    { name: 'README.md', type: 'md', size: '2 KB', mtime: '上周' }
  ]
};

/* 文件类型 → 图标/标签 */
window.wbFileIcon = function (f) {
  if (f.dir) return '<span class="f-icon dir">' + wbIcon('folder', 14) + '</span>';
  var map = { nb: ['nb', 'IPYNB'], py: ['py', 'PY'], csv: ['csv', 'CSV'], md: ['md', 'MD'], txt: ['txt', 'TXT'] };
  var m = map[f.type] || ['txt', 'TXT'];
  return '<span class="f-icon ' + m[0] + '">' + m[1] + '</span>';
};
