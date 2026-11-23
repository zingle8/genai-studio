<template>
  <div class="docs-page">
    <div class="page-header">
      <div>
        <div class="page-title">开发者文档中心</div>
        <div class="page-subtitle">模型调用、知识库、知识图谱、本体图谱的使用教程与接口参考</div>
      </div>
      <div class="page-actions">
        <span class="doc-version">v1.0 · 2026-11-23</span>
      </div>
    </div>

    <div class="docs-layout">
      <!-- 左栏：菜单与索引目录 -->
      <aside class="docs-nav">
        <div class="docs-search">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg>
          <input v-model="keyword" type="text" placeholder="搜索教程或接口路径..." />
          <span v-if="keyword" class="search-clear" @click="keyword = ''">×</span>
        </div>

        <div class="docs-nav-scroll">
          <div class="nav-group" v-for="mod in filteredModules" :key="mod.id">
            <div class="nav-group-head" @click="toggleModule(mod.id)">
              <span class="nav-mod-icon" :style="{ background: mod.color }">{{ mod.icon }}</span>
              <span class="nav-mod-name">{{ mod.name }}</span>
              <span class="nav-caret" :class="{ open: expanded[mod.id] }">›</span>
            </div>
            <div class="nav-items" v-show="expanded[mod.id]">
              <div
                v-for="sec in mod.sections"
                :key="sec.id"
                class="nav-item"
                :class="{ active: activeId === sec.id }"
                @click="selectDoc(sec.id)"
              >
                <span class="nav-dot" :class="sec.kind"></span>
                <span class="nav-item-text">{{ sec.title }}</span>
              </div>
            </div>
          </div>

          <div class="nav-group nav-group-extra">
            <div class="nav-group-head" @click="toggleModule('__platform')">
              <span class="nav-mod-icon" style="background:#8A8F98">#</span>
              <span class="nav-mod-name">平台接口索引</span>
              <span class="nav-caret" :class="{ open: expanded['__platform'] }">›</span>
            </div>
            <div class="nav-items" v-show="expanded['__platform']">
              <div class="nav-item" :class="{ active: activeId === '__platform' }" @click="selectDoc('__platform')">
                <span class="nav-dot"></span>
                <span class="nav-item-text">全部接口清单（jv-genai-docs）</span>
              </div>
            </div>
          </div>
        </div>

        <div class="nav-footer">文档随代码同步维护 · 接口以源码为准</div>
      </aside>

      <!-- 右栏：具体内容 -->
      <main class="docs-content">
        <!-- 教程类 -->
        <article v-if="activeDoc" class="doc-article">
          <div class="doc-breadcrumb">
            <span>{{ activeDoc.mod.name }}</span>
            <span class="crumb-sep">/</span>
            <span class="crumb-current">{{ activeDoc.sec.title }}</span>
          </div>
          <h1 class="doc-h1">{{ activeDoc.sec.title }}</h1>
          <p class="doc-lead">{{ activeDoc.sec.lead }}</p>

          <template v-if="activeDoc.sec.kind === 'tutorial'">
            <section v-for="(step, i) in activeDoc.sec.steps" :key="i" class="doc-step">
              <h3 class="doc-h3">{{ step.title }}</h3>
              <p class="doc-p">{{ step.body }}</p>
              <div v-if="step.code" class="code-block">
                <button class="copy-btn" @click="copyText(step.code)">复制</button>
                <pre><code>{{ step.code }}</code></pre>
              </div>
            </section>

            <section v-if="activeDoc.sec.table" class="doc-section">
              <h3 class="doc-h3">{{ activeDoc.sec.table.title || '说明' }}</h3>
              <div class="table-wrap doc-table-wrap">
                <table class="doc-table">
                  <thead><tr><th v-for="(h, hi) in activeDoc.sec.table.heads" :key="hi">{{ h }}</th></tr></thead>
                  <tbody>
                    <tr v-for="(row, ri) in activeDoc.sec.table.rows" :key="ri">
                      <td v-for="(cell, ci) in row" :key="ci" :class="{ 'cell-code': ci === 0 }">{{ cell }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section v-if="activeDoc.sec.notes" class="doc-section">
              <div v-for="(note, ni) in activeDoc.sec.notes" :key="ni" class="doc-note" :class="note.type">
                <span class="note-icon">{{ noteIcon(note.type) }}</span>
                <span>{{ note.text }}</span>
              </div>
            </section>
          </template>

          <template v-else>
            <section v-for="ep in activeDoc.sec.endpoints" :key="ep.id" class="endpoint-card">
              <div class="ep-head">
                <span class="tag ep-method" :class="methodCls(ep.method)">{{ ep.method }}</span>
                <code class="ep-path">{{ ep.path }}</code>
                <span class="ep-title">{{ ep.title }}</span>
              </div>
              <div class="ep-body">
                <p class="ep-desc">{{ ep.desc }}</p>
                <div class="ep-auth">
                  <span class="auth-label">鉴权</span>
                  <span>{{ ep.auth }}</span>
                </div>

                <template v-if="ep.params && ep.params.length">
                  <h4 class="ep-subtitle">请求参数</h4>
                  <div class="table-wrap doc-table-wrap">
                    <table class="doc-table param-table">
                      <thead><tr><th>参数名</th><th>位置</th><th>类型</th><th>必填</th><th>默认值</th><th>说明</th></tr></thead>
                      <tbody>
                        <tr v-for="(p, pi) in ep.params" :key="pi">
                          <td class="cell-code">{{ p.name }}</td>
                          <td><span class="where-tag">{{ p.where }}</span></td>
                          <td class="cell-type">{{ p.type }}</td>
                          <td><span v-if="p.required" class="required-mark">必填</span><span v-else class="muted">否</span></td>
                          <td class="cell-code">{{ p.default || '—' }}</td>
                          <td>{{ p.desc }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </template>
                <div v-else class="ep-no-param">无请求参数</div>

                <template v-if="ep.requestExample">
                  <h4 class="ep-subtitle">请求示例</h4>
                  <div class="code-block">
                    <button class="copy-btn" @click="copyText(ep.requestExample)">复制</button>
                    <pre><code>{{ ep.requestExample }}</code></pre>
                  </div>
                </template>

                <template v-if="ep.responseFields && ep.responseFields.length">
                  <h4 class="ep-subtitle">响应字段</h4>
                  <div class="table-wrap doc-table-wrap">
                    <table class="doc-table">
                      <thead><tr><th>字段</th><th>类型</th><th>说明</th></tr></thead>
                      <tbody>
                        <tr v-for="(f, fi) in ep.responseFields" :key="fi">
                          <td class="cell-code">{{ f.name }}</td>
                          <td class="cell-type">{{ f.type }}</td>
                          <td>{{ f.desc }}</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </template>

                <template v-if="ep.responseExample">
                  <h4 class="ep-subtitle">响应示例</h4>
                  <div class="code-block">
                    <button class="copy-btn" @click="copyText(ep.responseExample)">复制</button>
                    <pre><code>{{ ep.responseExample }}</code></pre>
                  </div>
                </template>

                <div v-for="(note, ni) in ep.notes || []" :key="ni" class="doc-note info">
                  <span class="note-icon">{{ noteIcon('info') }}</span>
                  <span>{{ noteText(note) }}</span>
                </div>
              </div>
            </section>
          </template>

          <div class="doc-source" v-if="activeDoc.mod.source">
            接口来源：<code>{{ activeDoc.mod.source }}</code>
          </div>
        </article>

        <!-- 平台接口索引 -->
        <article v-else-if="activeId === '__platform'" class="doc-article">
          <div class="doc-breadcrumb"><span>开发者文档中心</span><span class="crumb-sep">/</span><span class="crumb-current">平台接口索引</span></div>
          <h1 class="doc-h1">平台接口索引</h1>
          <p class="doc-lead">由 jv-genai-docs 聚合的全平台接口清单，包含各微服务的路径、方法与简要说明。详细参数请参考左侧各模块文档。</p>
          <div class="platform-card" v-for="(items, mod) in platformGrouped" :key="mod">
            <div class="platform-card-head"><b>{{ mod }}</b><span class="muted">{{ items.length }} 个接口</span></div>
            <div class="table-wrap">
              <table class="doc-table">
                <thead><tr><th style="width:110px">方法</th><th style="width:38%">路径</th><th>说明</th></tr></thead>
                <tbody>
                  <tr v-for="d in items" :key="d.id">
                    <td><span class="tag" :class="methodCls(d.method)">{{ d.method }}</span></td>
                    <td class="cell-code">{{ d.path }}</td>
                    <td class="muted">{{ d.description }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-if="!platformList.length" class="empty-hint">接口清单加载中或暂无数据。</div>
        </article>

        <div v-else class="empty-hint">请从左侧目录选择一篇文档。</div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { api } from '../api'
import { docModules, findDoc } from '../docsData'

const keyword = ref('')
const activeId = ref('')
const expanded = reactive({})
const platformList = ref([])

for (const mod of docModules) expanded[mod.id] = true
expanded.__platform = false

const filteredModules = computed(() => {
  const k = keyword.value.trim().toLowerCase()
  if (!k) return docModules
  return docModules.map(mod => ({
    ...mod,
    sections: mod.sections.filter(sec => {
      const hay = (mod.name + ' ' + sec.title + ' ' + (sec.lead || '')).toLowerCase()
      if (hay.includes(k)) return true
      if (sec.kind === 'api') {
        return (sec.endpoints || []).some(ep =>
          (ep.path + ' ' + ep.title + ' ' + ep.desc).toLowerCase().includes(k))
      }
      return false
    })
  })).filter(mod => mod.sections.length > 0)
})

const activeDoc = computed(() => activeId.value === '__platform' ? null : findDoc(activeId.value))

const platformGrouped = computed(() => {
  const g = {}
  for (const d of platformList.value) (g[d.module] = g[d.module] || []).push(d)
  return g
})

function selectDoc(id) {
  activeId.value = id
  if (id !== '__platform') history.replaceState(null, '', '#' + id)
  const el = document.querySelector('.docs-content')
  if (el) el.scrollTop = 0
  else window.scrollTo(0, 0)
}

function toggleModule(id) {
  expanded[id] = !expanded[id]
}

function methodCls(m) {
  if (!m) return ''
  if (m.includes('DELETE')) return 'tag-danger'
  if (m.includes('POST')) return 'tag-accent'
  if (m.includes('PUT')) return 'tag-warning'
  if (m.includes('GET')) return 'tag-success'
  return ''
}

function noteIcon(type) {
  return { info: 'i', tip: '✓', warn: '!' }[type] || 'i'
}

function noteText(note) {
  return typeof note === 'string' ? note : note.text
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    const ta = document.createElement('textarea')
    ta.value = text
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
  }
}

watch(keyword, (k) => {
  if (!k.trim()) return
  const first = filteredModules.value[0]
  if (first && first.sections.length && !filteredModules.value.some(m => m.sections.some(s => s.id === activeId.value))) {
    expanded[first.id] = true
    activeId.value = first.sections[0].id
  }
})

onMounted(async () => {
  const hash = location.hash.replace('#', '')
  activeId.value = hash && findDoc(hash) ? hash : (docModules[0]?.sections[0]?.id || '')
  try {
    const res = await api('/api/docs')
    if (res && res.code === 0) platformList.value = res.data || []
  } catch (e) {
    console.warn('加载平台接口索引失败', e)
  }
})
</script>

<style scoped>
.docs-page { max-width: 1440px; margin: 0 auto; }
.doc-version { font-size: 12.5px; color: var(--text-tertiary); background: var(--bg-soft); padding: 5px 10px; border-radius: var(--radius-sm); }

.docs-layout { display: flex; gap: 20px; align-items: flex-start; }

/* ---------- 左侧目录 ---------- */
.docs-nav {
  width: 268px;
  flex-shrink: 0;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: #fff;
  position: sticky;
  top: 16px;
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 120px);
  overflow: hidden;
}
.docs-search { display: flex; align-items: center; gap: 8px; padding: 12px 14px; border-bottom: 1px solid var(--border-light); }
.docs-search svg { width: 15px; height: 15px; color: var(--text-tertiary); }
.docs-search input { flex: 1; min-width: 0; border: none; outline: none; font-size: 13px; color: var(--text-primary); background: transparent; }
.docs-search input::placeholder { color: var(--text-quaternary); }
.search-clear { cursor: pointer; color: var(--text-tertiary); font-size: 16px; line-height: 1; }
.docs-nav-scroll { flex: 1; overflow-y: auto; padding: 8px 8px 12px; }
.docs-nav-scroll::-webkit-scrollbar { width: 4px; }
.docs-nav-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
.nav-group + .nav-group { margin-top: 4px; }
.nav-group-extra { border-top: 1px solid var(--border-light); padding-top: 8px; margin-top: 10px !important; }
.nav-group-head { display: flex; align-items: center; gap: 9px; padding: 9px 8px; border-radius: var(--radius); cursor: pointer; transition: background .14s; }
.nav-group-head:hover { background: var(--bg-soft); }
.nav-mod-icon { width: 22px; height: 22px; border-radius: 6px; color: #fff; font-size: 12px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.nav-mod-name { flex: 1; min-width: 0; font-size: 13.5px; font-weight: 600; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.nav-caret { color: var(--text-tertiary); font-size: 17px; line-height: 1; transform: rotate(90deg); transition: transform .16s; }
.nav-caret.open { transform: rotate(0deg); }
.nav-items { padding: 2px 0 6px 18px; }
.nav-item { display: flex; align-items: flex-start; gap: 8px; padding: 7px 10px; border-radius: var(--radius-sm); cursor: pointer; font-size: 12.8px; color: var(--text-secondary); line-height: 1.45; transition: background .14s, color .14s; }
.nav-item:hover { background: var(--bg-soft); color: var(--text-primary); }
.nav-item.active { background: var(--accent-soft); color: var(--accent); font-weight: 500; }
.nav-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--text-quaternary); flex-shrink: 0; margin-top: 7px; }
.nav-dot.api { background: var(--accent); }
.nav-item.active .nav-dot { background: currentColor; }
.nav-item-text { min-width: 0; }
.nav-footer { padding: 9px 14px; border-top: 1px solid var(--border-light); font-size: 11px; color: var(--text-quaternary); }

/* ---------- 右侧内容 ---------- */
.docs-content { flex: 1; min-width: 0; }
.doc-article { background: #fff; border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 28px 32px 36px; min-height: 600px; }
.doc-breadcrumb { font-size: 12.5px; color: var(--text-tertiary); margin-bottom: 14px; display: flex; gap: 8px; align-items: center; }
.crumb-sep { color: var(--text-quaternary); }
.crumb-current { color: var(--text-secondary); }
.doc-h1 { font-size: 24px; font-weight: 700; letter-spacing: -.3px; margin-bottom: 14px; color: var(--text-primary); }
.doc-lead { font-size: 14px; line-height: 1.8; color: var(--text-secondary); background: var(--bg-soft); border-radius: var(--radius); padding: 14px 18px; margin-bottom: 28px; }
.doc-h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 28px 0 12px; padding-left: 10px; border-left: 3px solid var(--accent); }
.doc-p { font-size: 13.5px; line-height: 1.85; color: var(--text-secondary); }
.doc-section { margin-top: 24px; }

.code-block { position: relative; background: #1E1E24; border-radius: var(--radius); margin: 14px 0 4px; overflow: hidden; }
.code-block pre { margin: 0; padding: 18px 20px; overflow-x: auto; }
.code-block code { font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace; font-size: 12.5px; line-height: 1.7; color: #E8E8ED; white-space: pre; }
.copy-btn { position: absolute; right: 10px; top: 10px; background: rgba(255,255,255,.1); color: #C9C9D1; border-radius: var(--radius-sm); padding: 4px 10px; font-size: 11.5px; }
.copy-btn:hover { background: rgba(255,255,255,.18); color: #fff; }

.doc-note { display: flex; align-items: flex-start; gap: 10px; padding: 12px 14px; border-radius: var(--radius); font-size: 13px; line-height: 1.7; margin-bottom: 10px; }
.doc-note.info { background: var(--accent-soft); color: #3C4FA8; }
.doc-note.tip { background: var(--success-soft); color: #177856; }
.doc-note.warn { background: var(--warning-soft); color: #A8561B; }
.note-icon { width: 18px; height: 18px; border-radius: 50%; background: currentColor; color: #fff; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 700; flex-shrink: 0; margin-top: 2px; }

/* ---------- 接口卡片 ---------- */
.endpoint-card { border: 1px solid var(--border); border-radius: var(--radius-md); margin-bottom: 20px; overflow: hidden; }
.ep-head { display: flex; align-items: center; gap: 10px; padding: 14px 18px; background: var(--bg-soft); border-bottom: 1px solid var(--border-light); flex-wrap: wrap; }
.ep-method { font-family: ui-monospace, Menlo, Consolas, monospace; font-weight: 600; font-size: 11.5px; letter-spacing: .3px; flex-shrink: 0; }
.ep-path { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 13.5px; font-weight: 600; color: var(--text-primary); }
.ep-title { margin-left: auto; font-size: 13px; color: var(--text-secondary); }
.ep-body { padding: 18px 20px 20px; }
.ep-desc { font-size: 13.5px; line-height: 1.8; color: var(--text-secondary); margin-bottom: 12px; }
.ep-auth { display: flex; align-items: center; gap: 8px; font-size: 12.5px; color: var(--text-secondary); background: var(--info-soft); border-radius: var(--radius-sm); padding: 8px 12px; margin-bottom: 18px; }
.auth-label { font-size: 11px; color: var(--accent); background: #fff; border-radius: 4px; padding: 2px 6px; font-weight: 600; flex-shrink: 0; }
.ep-subtitle { font-size: 13.5px; font-weight: 600; color: var(--text-primary); margin: 20px 0 10px; }
.ep-subtitle:first-of-type { margin-top: 4px; }
.ep-no-param { font-size: 12.5px; color: var(--text-tertiary); margin: 6px 0 12px; }

.doc-table-wrap { border: 1px solid var(--border); border-radius: var(--radius); overflow-x: auto; }
.doc-table { width: 100%; font-size: 12.8px; }
.doc-table thead th { padding: 10px 14px; background: var(--bg-soft); color: var(--text-secondary); font-size: 12px; font-weight: 500; white-space: nowrap; border-bottom: 1px solid var(--border); }
.doc-table tbody td { padding: 10px 14px; border-bottom: 1px solid var(--border-light); line-height: 1.6; color: var(--text-secondary); vertical-align: top; }
.doc-table tbody tr:last-child td { border-bottom: none; }
.doc-table tbody tr:hover { background: var(--bg-soft); }
.cell-code { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12px; color: var(--text-primary); white-space: nowrap; }
.cell-type { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11.5px; color: #7B5CFF; white-space: nowrap; }
.where-tag { font-size: 11px; background: var(--bg-soft); border-radius: 4px; padding: 2px 6px; white-space: nowrap; }
.required-mark { font-size: 11px; color: var(--danger); font-weight: 600; }

.doc-source { margin-top: 28px; padding-top: 16px; border-top: 1px solid var(--border-light); font-size: 12px; color: var(--text-tertiary); }
.doc-source code { font-family: ui-monospace, Menlo, Consolas, monospace; color: var(--text-secondary); }

.platform-card { border: 1px solid var(--border); border-radius: var(--radius-md); margin-bottom: 16px; overflow: hidden; }
.platform-card-head { display: flex; align-items: center; justify-content: space-between; padding: 12px 18px; background: var(--bg-soft); border-bottom: 1px solid var(--border-light); font-size: 14px; }
.platform-card .doc-table { border: none; border-radius: 0; }
.empty-hint { text-align: center; color: var(--text-tertiary); padding: 60px 0; font-size: 13px; }

@media (max-width: 1100px) {
  .docs-nav { width: 224px; }
  .doc-article { padding: 22px 20px 28px; }
}
@media (max-width: 820px) {
  .docs-layout { flex-direction: column; }
  .docs-nav { width: 100%; position: static; max-height: 300px; }
  .ep-title { margin-left: 0; }
}
</style>
