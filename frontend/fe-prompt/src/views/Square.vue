<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">提示词广场</div>
        <div class="page-subtitle">精选提示词模板一览（新增 / 编辑请在「提示词管理」操作）</div>
      </div>
      <div class="page-actions"><span class="link text-sm" style="cursor:pointer;" @click="goAdmin">前往提示词管理 ›</span></div>
    </div>
    <div class="filter-bar">
      <input class="form-input" v-model="keyword" placeholder="模板名 / 标签 / 内容" style="width:220px;" @keyup.enter="load" />
      <button class="btn btn-primary" @click="load">查询</button>
      <div class="spacer"></div><span class="text-sm muted">当前 {{ filteredList.length }} / 共 {{ total }} 个模板</span>
    </div>
    <div class="type-tabs">
      <button v-for="t in tabs" :key="t.key" class="type-tab" :class="{ active: tab === t.key }" @click="tab = t.key">
        {{ t.label }}<span class="tab-count">{{ countOf(t) }}</span>
      </button>
    </div>
    <div class="model-grid">
      <div v-for="p in filteredList" :key="p.id" class="model-card" @click="showDetail(p)">
        <div class="model-card-head">
          <b class="model-card-name">{{ p.name }}</b>
          <span class="tag" :class="p.status === 1 ? 'tag-success' : ''">{{ p.status === 1 ? '已启用' : '已停用' }}</span>
        </div>
        <div class="model-card-tags">
          <span class="tag" v-for="t in tagList(p)" :key="t">{{ t }}</span>
        </div>
        <div class="model-card-desc">{{ p.content }}</div>
        <div class="model-card-foot">
          <span class="text-xs muted">{{ varList(p).length ? varList(p).length + ' 个变量' : '无变量' }} · {{ (p.createdAt || '').slice(0, 10) }}</span>
          <span class="link">查看详情 ›</span>
        </div>
      </div>
      <div v-if="!filteredList.length" class="empty" style="grid-column:1/-1; padding:48px 0;">该分类暂无提示词</div>
    </div>

    <div class="modal-mask" :class="{ show: detailOpen }" @click.self="detailOpen = false">
      <div class="modal" style="max-width:640px;">
        <div class="modal-header"><div class="modal-title">{{ cur?.name }}</div><button class="modal-close" @click="detailOpen = false">×</button></div>
        <div class="modal-body">
          <div class="detail-tags">
            <span class="tag" v-for="t in tagList(cur)" :key="t">{{ t }}</span>
            <span class="tag" :class="cur?.status === 1 ? 'tag-success' : 'tag-muted'">{{ cur?.status === 1 ? '已启用' : '已停用' }}</span>
          </div>
          <div class="detail-sec-title">提示词内容</div>
          <div class="detail-body">{{ cur?.content }}</div>
          <div class="detail-sec-title" style="margin-top:16px;">变量</div>
          <div class="usage-row" v-if="varList(cur).length">
            <div class="prompt-vars">
              <code class="usage-code" v-for="v in varList(cur)" :key="v">{{ wrapVar(v) }}</code>
            </div>
          </div>
          <div v-else class="text-xs muted">该模板无变量，可直接复制使用</div>
          <div class="usage-note">使用方式：复制提示词内容，将 <code>{{ varHint }}</code> 替换为实际内容后发给模型；或在「体验中心」粘贴后直接对话。</div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-ghost" @click="copyPrompt">{{ copied ? '✓ 已复制' : '复制提示词' }}</button>
          <button class="btn btn-primary" @click="detailOpen = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import { useRouter } from 'vue-router'
const router = useRouter()
const list = ref([]); const total = ref(0); const keyword = ref('')
const detailOpen = ref(false); const cur = ref(null); const copied = ref(false)

/* 分类 tab：静态常用分类 + 动态合并数据里出现过的标签 */
const STATIC_TABS = [
  { key: 'all', label: '全部', match: null },
  { key: 'c通用', label: '通用', match: ['通用'] },
  { key: 'c编程', label: '编程', match: ['编程', '代码', 'SQL'] },
  { key: 'c办公', label: '办公', match: ['办公', '周报', '总结'] },
  { key: 'cRAG', label: 'RAG 问答', match: ['RAG', '问答'] },
  { key: 'c翻译', label: '翻译', match: ['翻译'] },
  { key: 'c教育', label: '教育', match: ['教育', '科普', '面试'] }
]
const tabs = computed(() => {
  const seen = new Set(STATIC_TABS.flatMap(t => t.match || []))
  const extra = []
  for (const p of list.value) {
    for (const t of tagList(p)) {
      if (!seen.has(t) && !extra.some(x => x.label === t)) extra.push({ key: 'x' + t, label: t, match: [t] })
    }
  }
  return [...STATIC_TABS, ...extra]
})
const tab = ref('all')

function tagList(p) { return (p?.tags || '').split(',').map(s => s.trim()).filter(Boolean) }
function varList(p) { return (p?.variables || '').split(',').map(s => s.trim()).filter(Boolean) }
function matchTab(p, t) {
  if (!t.match) return true
  const tags = (p?.tags || '').toLowerCase()
  const content = (p?.content || '').toLowerCase()
  return t.match.some(k => tags.includes(k.toLowerCase()) || content.includes(k.toLowerCase()))
}
function countOf(t) { return list.value.filter(p => matchTab(p, t)).length }
const filteredList = computed(() => list.value.filter(p => matchTab(p, tabs.value.find(t => t.key === tab.value))))

onMounted(load)
async function load() {
  const res = await api('/api/prompts?keyword=' + encodeURIComponent(keyword.value) + '&size=100')
  if (res.code === 0) { list.value = res.data.list || []; total.value = res.data.total || 0 }
}
function showDetail(p) { cur.value = p; copied.value = false; detailOpen.value = true }
const varHint = '{{变量}}'
function wrapVar(v) { return '{{' + v + '}}' }
async function copyPrompt() {
  try {
    await navigator.clipboard.writeText(cur.value?.content || '')
    copied.value = true
    setTimeout(() => { copied.value = false }, 1500)
  } catch { alert('复制失败，请手动选择文本复制') }
}
function goAdmin() { router.push('/fe-prompt/prompts') }
</script>

<style>
/* 复用模型广场卡片体系（model-grid / model-card / type-tab 等与 fe-models 同款） */
.detail-sec-title {
  font-size: 12px; font-weight: 600; color: var(--text-muted, #6b7280);
  margin-bottom: 8px; padding-left: 8px;
  border-left: 3px solid var(--primary, #4d6bfe); line-height: 1.4;
}
.detail-body {
  font-size: 13.5px; line-height: 1.7; color: var(--text-muted, #4b5563);
  white-space: pre-wrap; background: var(--bg-soft, #f7f8fa);
  border-radius: 10px; padding: 12px 14px; min-height: 80px;
}
.detail-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.prompt-vars { display: flex; flex-wrap: wrap; gap: 6px; }
.usage-code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px;
  background: var(--bg-soft, #f7f8fa); border: 1px solid var(--border-light, #e5e8ef);
  border-radius: 6px; padding: 3px 8px; color: var(--text, #1f2430); word-break: break-all;
}
.usage-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 8px; }
.usage-note {
  font-size: 12px; line-height: 1.7; color: var(--text-muted, #6b7280);
  background: var(--bg-soft, #f7f8fa); border-radius: 8px; padding: 10px 12px; margin-top: 4px;
}
.usage-note code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11.5px;
  background: #fff; border: 1px solid var(--border-light, #e5e8ef);
  border-radius: 4px; padding: 1px 5px; color: var(--primary, #4d6bfe);
}
.tag-muted { background: #f3f4f6; color: #6b7280; }
.type-tabs { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.type-tab {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 14px; font-size: 13px; cursor: pointer;
  border: 1px solid var(--border-light, #e5e8ef); border-radius: 999px;
  background: #fff; color: var(--text, #1f2430); transition: all .15s;
}
.type-tab:hover { border-color: var(--primary, #4d6bfe); color: var(--primary, #4d6bfe); }
.type-tab.active { background: var(--primary, #4d6bfe); border-color: var(--primary, #4d6bfe); color: #fff; font-weight: 600; }
.tab-count { font-size: 11px; padding: 1px 7px; border-radius: 999px; background: rgba(0,0,0,0.06); color: inherit; }
.type-tab.active .tab-count { background: rgba(255,255,255,0.25); }
.filter-bar { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
.filter-bar .spacer { flex: 1; }
</style>
