<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">模型广场</div>
        <div class="page-subtitle">可用模型一览（模型的上架 / 注册请在「模型管理」操作）</div>
      </div>
    </div>
    <div class="filter-bar">
      <input class="form-input" v-model="keyword" placeholder="模型名 / 提供方" style="width:220px;" @keyup.enter="load" />
      <button class="btn btn-primary" @click="load">查询</button>
      <div class="spacer"></div><span class="text-sm muted">当前 {{ filteredList.length }} / 共 {{ total }} 个模型</span>
    </div>
    <!-- 按模型类型的 tab 页签筛选 -->
    <div class="type-tabs">
      <button
        v-for="t in TABS"
        :key="t.key"
        class="type-tab"
        :class="{ active: tab === t.key }"
        @click="tab = t.key"
      >{{ t.label }}<span class="tab-count">{{ countOf(t) }}</span></button>
    </div>
    <div class="model-grid">
      <div v-for="m in filteredList" :key="m.id" class="model-card" @click="showDetail(m)">
        <div class="model-card-head">
          <b class="model-card-name">{{ m.name }}</b>
          <span class="tag" :class="isLocal(m) ? 'tag-success' : 'tag-accent'">{{ isLocal(m) ? '本地' : '云端' }}</span>
          <span class="tag" :class="m.status === 1 ? 'tag-success' : ''">{{ m.status === 1 ? '已上架' : '已下架' }}</span>
        </div>
        <div class="model-card-real" v-if="m.realName && m.realName !== m.name">
          真实模型：<code>{{ m.realName }}</code>
        </div>
        <div class="model-card-tags">
          <span class="tag" :class="tagCls(m.category)">{{ m.category || '文本生成' }}</span>
          <span class="tag">{{ isLocal(m) ? (m.vendor || m.provider) : (m.vendor || m.provider) }}</span>
          <span class="tag tag-muted">{{ m.apiFormat || 'openai' }} 格式</span>
        </div>
        <div class="model-card-desc">{{ m.description || '暂无描述' }}</div>
        <div class="model-card-foot">
          <span class="text-xs muted">上下文 {{ m.contextLen ? m.contextLen.toLocaleString() : '-' }}</span>
          <span class="link">查看详情 ›</span>
        </div>
      </div>
      <div v-if="!filteredList.length" class="empty" style="grid-column:1/-1; padding:48px 0;">该类型暂无模型</div>
    </div>

    <div class="modal-mask" :class="{ show: detailOpen }" @click.self="detailOpen = false">
      <div class="modal" style="max-width:640px;">
        <div class="modal-header"><div class="modal-title">{{ cur?.name }}<span v-if="cur?.realName && cur.realName !== cur.name" class="real-name-hint">（真实模型：{{ cur.realName }}）</span></div><button class="modal-close" @click="detailOpen = false">×</button></div>
        <div class="modal-body">
          <div class="detail-tags">
            <span class="tag" :class="tagCls(cur?.category)">{{ cur?.category || '文本生成' }}</span>
            <span class="tag" :class="isLocal(cur) ? 'tag-success' : 'tag-accent'">{{ isLocal(cur) ? '本地模型' : '外部云端模型' }}</span>
            <span class="tag">{{ cur?.vendor || cur?.provider }}</span>
            <span class="tag tag-muted">{{ cur?.apiFormat || 'openai' }} 格式</span>
            <span class="tag tag-muted">上下文 {{ cur?.contextLen ? cur.contextLen.toLocaleString() : '-' }}</span>
          </div>

          <!-- 模型详细描述 -->
          <div class="detail-sec-title">模型详细描述</div>
          <div class="detail-desc">{{ cur?.description || '暂无描述' }}</div>
          <div class="detail-body">{{ cur?.detail || '该模型暂无详细说明。' }}</div>

          <!-- 模型使用 -->
          <div class="detail-sec-title" style="margin-top:16px;">模型使用</div>
          <div class="usage-grid">
            <div class="usage-item"><span class="usage-label">接口格式</span><span class="tag" :class="fmtCls(cur?.apiFormat)">{{ cur?.apiFormat || 'openai' }}</span></div>
            <div class="usage-item"><span class="usage-label">计费等级</span><span class="tag" :class="cur?.tier === '旗舰' ? 'tag-danger' : cur?.tier === '免费' ? 'tag-success' : ''">{{ cur?.tier || '标准' }}</span></div>
            <div class="usage-item"><span class="usage-label">上下文长度</span><span class="mono text-xs">{{ cur?.contextLen ? cur.contextLen.toLocaleString() : '-' }}</span></div>
            <div class="usage-item"><span class="usage-label">API Key</span><span class="mono text-xs">{{ cur?.apiKey ? '已配置（' + cur.apiKey + '）' : '平台统一鉴权' }}</span></div>
          </div>
          <div class="usage-row" v-if="cur?.baseUrl">
            <span class="usage-label">Base URL</span>
            <code class="usage-code">{{ cur.baseUrl }}</code>
          </div>
          <div class="usage-row">
            <span class="usage-label">支持接口</span>
            <div class="usage-paths">
              <div v-for="(p, i) in curPaths" :key="i" class="usage-path">
                <code class="usage-code">{{ p.path }}</code>
                <span class="tag tag-muted">{{ p.format }}</span>
              </div>
              <span v-if="!curPaths.length" class="text-xs muted">默认 /chat/completions（openai）</span>
            </div>
          </div>
          <div class="usage-note">调用方式：向 <code>http://localhost:38100{{ curPaths[0]?.path || '/chat/completions' }}</code> 发起 POST 请求，请求头携带 <code>Authorization: Bearer sk-...</code>（体验中心「API Key」面板可获取），请求体为 OpenAI 兼容的 messages 格式。</div>
        </div>
        <div class="modal-footer"><button class="btn btn-primary" @click="detailOpen = false">关闭</button></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
const list = ref([]); const total = ref(0); const keyword = ref('')
const detailOpen = ref(false); const cur = ref(null)

/* 按模型类型的 tab 页签；match 为 category 关键词（大小写不敏感） */
const TABS = [
  { key: 'all',        label: '全部',            match: null },
  { key: 'text',       label: '纯文本',          match: ['文本'] },
  { key: 'multimodal', label: '多模态',          match: ['多模态'] },
  { key: 'voice',      label: '语音',            match: ['语音', 'TTS', 'ASR'] },
  { key: 'video',      label: '视频',            match: ['视频'] },
  { key: 'image',      label: '图片',            match: ['图片', '图像'] },
  { key: 'embedding',  label: '向量 Embedding',  match: ['向量', 'embedding'] },
  { key: 'reranker',   label: '排序 Reranker',   match: ['排序', 'rerank'] },
  { key: 'judge',      label: '判断 Judge',      match: ['判断', 'judge'] },
  { key: 'ocr',        label: 'OCR',             match: ['OCR', '文字识别'] }
]
const tab = ref('all')

function matchTab(m, t) {
  if (!t.match) return true
  const c = (m.category || '文本生成').toLowerCase()
  return t.match.some(k => c.includes(k.toLowerCase()))
}
function countOf(t) { return list.value.filter(m => matchTab(m, t)).length }

/* tab + 关键词双过滤（keyword 已由后端过滤，这里做 tab 维度） */
const filteredList = computed(() => list.value.filter(m => matchTab(m, TABS.find(t => t.key === tab.value))))

onMounted(load)
async function load() {
  const res = await api('/api/models?keyword=' + encodeURIComponent(keyword.value) + '&size=50')
  if (res.code === 0) { list.value = res.data.list || []; total.value = res.data.total || 0 }
}
function showDetail(m) { cur.value = m; detailOpen.value = true }
/** 当前详情模型的接口路径列表（urlPaths JSON 解析，含默认兜底） */
const curPaths = computed(() => {
  try {
    const arr = JSON.parse(cur.value?.urlPaths || '[]')
    if (Array.isArray(arr) && arr.length) return arr.filter(p => p.path).map(p => ({ path: p.path, format: p.format || 'openai' }))
  } catch (e) { /* 非法 JSON 走默认 */ }
  return [{ path: '/chat/completions', format: 'openai' }]
})
/** 是否本地部署模型（provider 含"本地"，如 本地/本地 Ollama） */
function isLocal(m) { return !m ? false : /本地/.test(m.provider || '') }
function fmtCls(f) { return f === 'claude' ? 'tag-warning' : f === 'gemini' ? 'tag-accent' : f === 'other' ? 'tag-muted' : 'tag-success' }
function tagCls(c) {
  if (!c) return ''
  if (c.includes('向量') || c.toLowerCase().includes('embedding')) return 'tag-accent'
  if (c.includes('多模态') || c.includes('语音') || c.includes('OCR') || c.includes('视频') || c.includes('图片')) return 'tag-warning'
  if (c.includes('排序') || c.toLowerCase().includes('rerank')) return 'tag-danger'
  if (c.includes('判断') || c.toLowerCase().includes('judge')) return 'tag-accent'
  return ''
}
</script>

<style>
/* 模型广场卡片网格 */
.model-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; }
.model-card {
  background: #fff; border: 1px solid var(--border-light); border-radius: 12px;
  padding: 16px; cursor: pointer; transition: box-shadow .15s, transform .15s;
  display: flex; flex-direction: column; gap: 10px;
}
.model-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,0.08); transform: translateY(-2px); }
.model-card-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.model-card-head .tag { white-space: nowrap; flex-shrink: 0; }
.model-card-name { font-size: 15px; }
.model-card-tags { display: flex; flex-wrap: wrap; gap: 6px; }
.model-card-desc {
  font-size: 13px; color: var(--text-muted, #6b7280); line-height: 1.55;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  min-height: 40px;
}
.model-card-real { font-size: 12px; color: var(--text-muted, #6b7280); display: flex; align-items: center; gap: 5px; margin-top: -4px; }
.model-card-real code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11.5px;
  background: var(--bg-soft, #f7f8fa); border: 1px solid var(--border-light, #e5e8ef);
  border-radius: 4px; padding: 1px 6px; color: var(--text, #1f2430);
}
.real-name-hint { font-size: 12px; font-weight: 400; color: var(--text-muted, #6b7280); margin-left: 6px; }
.model-card-foot { display: flex; align-items: center; justify-content: space-between; margin-top: auto; }
/* 详情弹窗 */
.detail-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.detail-desc { font-size: 13.5px; font-weight: 600; color: var(--text, #1f2430); margin-bottom: 10px; }
.detail-body {
  font-size: 13.5px; line-height: 1.7; color: var(--text-muted, #4b5563);
  white-space: pre-wrap; background: var(--bg-soft, #f7f8fa);
  border-radius: 10px; padding: 12px 14px; min-height: 80px;
}
.tag-muted { background: #f3f4f6; color: #6b7280; }
.tag-danger { background: #fef2f2; color: #dc2626; }

/* 详情弹框分区 */
.detail-sec-title {
  font-size: 12px; font-weight: 600; color: var(--text-muted, #6b7280);
  margin-bottom: 8px; padding-left: 8px;
  border-left: 3px solid var(--primary, #4d6bfe); line-height: 1.4;
}
/* 模型使用区块 */
.usage-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 14px; margin-bottom: 10px; }
.usage-item { display: flex; align-items: center; justify-content: space-between; gap: 8px; background: var(--bg-soft, #f7f8fa); border-radius: 8px; padding: 7px 10px; }
.usage-label { font-size: 12px; color: var(--text-muted, #6b7280); flex-shrink: 0; }
.usage-row { display: flex; align-items: flex-start; gap: 10px; margin-bottom: 8px; }
.usage-row .usage-label { padding-top: 4px; width: 64px; }
.usage-paths { display: flex; flex-direction: column; gap: 5px; flex: 1; }
.usage-path { display: flex; align-items: center; gap: 8px; }
.usage-code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px;
  background: var(--bg-soft, #f7f8fa); border: 1px solid var(--border-light, #e5e8ef);
  border-radius: 6px; padding: 3px 8px; color: var(--text, #1f2430);
  word-break: break-all;
}
.usage-note {
  font-size: 12px; line-height: 1.7; color: var(--text-muted, #6b7280);
  background: var(--bg-soft, #f7f8fa); border-radius: 8px; padding: 10px 12px; margin-top: 4px;
}
.usage-note code {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 11.5px;
  background: #fff; border: 1px solid var(--border-light, #e5e8ef);
  border-radius: 4px; padding: 1px 5px; color: var(--primary, #4d6bfe);
}

/* 模型类型 tab 页签 */
.type-tabs {
  display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 14px;
}
.type-tab {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 7px 14px; font-size: 13px; cursor: pointer;
  border: 1px solid var(--border-light, #e5e8ef); border-radius: 999px;
  background: #fff; color: var(--text, #1f2430); transition: all .15s;
}
.type-tab:hover { border-color: var(--primary, #4d6bfe); color: var(--primary, #4d6bfe); }
.type-tab.active {
  background: var(--primary, #4d6bfe); border-color: var(--primary, #4d6bfe); color: #fff; font-weight: 600;
}
.tab-count {
  font-size: 11px; padding: 1px 7px; border-radius: 999px;
  background: rgba(0,0,0,0.06); color: inherit;
}
.type-tab.active .tab-count { background: rgba(255,255,255,0.25); }
</style>
