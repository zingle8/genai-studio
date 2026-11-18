<template>
  <div class="app">
    <!-- qiankun 基座内运行时隐藏自带导航，避免与基座菜单重复 -->
    <header v-if="!inQiankun" class="brand-bar">
      <span class="logo-brand">GenAI Studio</span>
      <span class="logo-badge">运营分析</span>
    </header>
    <div class="main-wrap">
      <aside v-if="!inQiankun" class="side-nav">
        <router-link to="/costs" class="side-item" active-class="active">成本统计</router-link>
        <router-link to="/usage-logs" class="side-item" active-class="active">使用日志</router-link>
      </aside>
      <main class="main">
        <div class="content"><router-view /></div>
      </main>
    </div>
  </div>
</template>

<script setup>
// qiankun 基座内：标记挂在 window.proxy 上（动态 import 的模块运行在主文档，裸 window 上没有）
const inQiankun = !!window.__GENAI_IN_BASE__
</script>

<style>
.brand-bar { display: flex; align-items: center; gap: 8px; padding: 12px 24px; border-bottom: 1px solid var(--border-light); background: #fff; }
.logo-brand { font-size: 17px; font-weight: 700; }
.logo-badge { font-size: 10px; color: #fff; background: var(--text-primary); padding: 2px 6px; border-radius: 4px; }
.main-wrap { display: flex; min-height: calc(100vh - 53px); }
.side-nav { width: 180px; flex-shrink: 0; border-right: 1px solid var(--border-light); background: #fff; padding: 12px 8px; }
.side-item { display: block; padding: 10px 14px; border-radius: 8px; font-size: 13.5px; color: var(--text-secondary); text-decoration: none; }
.side-item:hover { background: var(--bg-soft); color: var(--text-primary); }
.side-item.active { background: var(--accent-soft); color: var(--accent); font-weight: 500; }
.main { flex: 1; min-width: 0; }
</style>

<style>
/* ===== 侧边栏响应式：窄屏变为顶部横向滚动导航 ===== */
@media (max-width: 960px) {
  .main-wrap { flex-direction: column; }
  .side-nav { display: flex; flex-direction: row; overflow-x: auto; width: 100%; border-right: none; border-bottom: 1px solid var(--border-light); padding: 6px 10px; gap: 4px; }
  .side-nav .side-item { white-space: nowrap; }
}
</style>
