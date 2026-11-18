<template>
  <div class="page-header">
    <div><div class="page-title">知识库</div><div class="page-subtitle">知识空间 / 库配置（ES·PG·内置）/ 文档切分 / 检索测试</div></div>
    <div class="page-actions">
      <button class="btn btn-ghost" @click="spaceOpen = true">＋ 新建空间</button>
      <button class="btn btn-primary" @click="openNewKb">＋ 新建知识库</button>
    </div>
  </div>
  <div class="kb-layout">
    <!-- 左：空间 -->
    <div class="card kb-side"><div class="card-body no-pad">
      <div style="padding:10px 14px; border-bottom:1px solid var(--border-light);"><b class="text-sm">知识空间</b></div>
      <div class="kb-item" :class="{ active: curSpace === 0 }" @click="curSpace = 0; loadKbs()">
        <div><b>全部</b></div>
      </div>
      <div class="kb-item" v-for="s in spaces" :key="s.id" :class="{ active: curSpace === s.id }" @click="curSpace = s.id; loadKbs()">
        <div><b>{{ s.name }}</b></div>
        <div class="text-xs muted">{{ s.kbCount }} 个库 · {{ s.description || '—' }}</div>
      </div>
      <div v-if="!spaces.length" class="side-empty text-sm muted">暂无空间，点右上角新建</div>
    </div></div>
    <!-- 中：知识库列表 -->
    <div class="card kb-side2"><div class="card-body no-pad">
      <div style="padding:10px 14px; border-bottom:1px solid var(--border-light);"><b class="text-sm">知识库</b></div>
      <div class="kb-item" v-for="k in kbs" :key="k.id" :class="{ active: curKb?.id === k.id }" @click="pickKb(k)">
        <div style="display:flex; align-items:center; gap:6px;">
          <b>{{ k.name }}</b>
          <span class="tag" style="font-size:11px;" :class="k.kb_type === 'golden_answer' ? 'tag-accent' : ''">{{ typeLabel(k.kb_type) }}</span>
        </div>
        <div class="text-xs muted">{{ k.docCount }} 文档 · {{ storeLabel(k.db_type) }} <span v-if="k.db_type !== 'sqlite'" class="dot-mini" :class="k.dbOk ? 'green' : 'red'"></span></div>
        <div class="text-xs muted" v-if="k.embedding_model">emb: {{ k.embedding_model }} <template v-if="k.reranker_model && k.reranker_model !== '（无）'">· rerank: {{ k.reranker_model }}</template></div>
      </div>
      <div v-if="!kbs.length" class="side-empty text-sm muted">当前范围暂无知识库</div>
    </div></div>
    <!-- 右：文档 + 检索 -->
    <div style="flex:1; min-width:0; display:flex; flex-direction:column; gap:12px;">
      <template v-if="curKb">
        <div class="card"><div class="card-body">
          <div class="row-head">
            <b>{{ curKb.name }}</b>
            <span class="tag">{{ typeLabel(curKb.kb_type) }}</span>
            <span class="tag">{{ storeLabel(curKb.db_type) }}</span>
            <span class="text-xs muted">{{ curKb.description || '—' }}</span>
            <span style="flex:1"></span>
            <button class="btn btn-ghost btn-sm" @click="editKb(curKb)">配置</button>
            <button class="btn btn-ghost btn-sm" @click="delKb(curKb)">删除库</button>
          </div>
          <div class="text-xs muted" style="margin-top:6px;">切分：{{ modeLabel(curKb.chunk_mode) }} / {{ curKb.chunk_len }} 字</div>
        </div></div>

        <div class="card"><div class="card-body">
          <div class="row-head" style="margin-bottom:10px;">
            <b>文档列表</b><span style="flex:1"></span>
            <button class="btn btn-primary btn-sm" @click="docOpen = true">＋ 上传文档</button>
          </div>
          <div class="table-wrap"><table>
            <thead><tr><th>文档名</th><th>分块</th><th>大小</th><th>状态</th><th>时间</th><th class="text-right">操作</th></tr></thead>
            <tbody>
              <tr v-for="d in docs" :key="d.id">
                <td>{{ d.name }}</td><td>{{ d.chunks }}</td><td>{{ fmtSize(d.size) }}</td>
                <td><span class="tag tag-success">{{ d.status }}</span></td>
                <td class="text-xs muted">{{ d.created_at }}</td>
                <td class="text-right"><button class="btn btn-ghost btn-sm" @click="viewChunks(d)">分块</button> <button class="btn btn-ghost btn-sm" @click="delDoc(d)">删除</button></td>
              </tr>
              <tr v-if="!docs.length"><td colspan="6" class="text-center muted">暂无文档</td></tr>
            </tbody>
          </table></div>
        </div></div>

        <div class="card"><div class="card-body">
          <b style="display:block; margin-bottom:8px;">检索测试 <span class="text-xs muted" v-if="lastBackend">（{{ storeLabel(lastBackend) }}）</span></b>
          <div class="row-head" style="gap:8px;">
            <input class="form-input" v-model="query" placeholder="输入查询" @keyup.enter="search" style="flex:1;" />
            <button class="btn btn-primary" @click="search">检索</button>
          </div>
          <div v-if="searched" class="search-res">
            <div class="text-xs muted" style="margin:8px 0;">命中 {{ hits.length }} 条</div>
            <div class="hit" v-for="h in hits" :key="h.chunkId + '-' + h.idx">
              <span class="tag">{{ h.doc || '文档#' + h.docId }} #{{ h.idx }}</span> <span class="text-xs muted">score {{ h.score }}</span>
              <div class="hit-text">{{ h.content }}</div>
            </div>
            <div v-if="!hits.length" class="text-sm muted">无命中</div>
          </div>
        </div></div>
      </template>
      <div v-else class="card"><div class="card-body text-center muted" style="padding:40px 0;">从左侧选择知识库，或新建一个</div></div>
    </div>
  </div>

  <!-- 新建空间 -->
  <div class="modal-mask" v-if="spaceOpen" @click.self="spaceOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">新建知识空间</div><button class="modal-close" @click="spaceOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">空间名</label><input class="form-input" v-model="spaceForm.name" /></div>
        <div class="form-row"><label class="form-label">描述</label><input class="form-input" v-model="spaceForm.description" /></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="spaceOpen = false">取消</button><button class="btn btn-primary" @click="saveSpace">创建</button></div>
    </div>
  </div>

  <!-- 新建/配置知识库 -->
  <div class="modal-mask" v-if="kbOpen" @click.self="kbOpen = false">
    <div class="modal modal-lg">
      <div class="modal-header"><div class="modal-title">{{ kbForm.id ? '知识库配置' : '新建知识库' }}</div><button class="modal-close" @click="kbOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">知识空间</label>
          <select class="form-input" v-model="kbForm.space_id">
            <option :value="0">— 不归属空间 —</option>
            <option v-for="s in spaces" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select></div>
        <div class="form-row"><label class="form-label">知识库名</label><input class="form-input" v-model="kbForm.name" /></div>
        <div class="form-row"><label class="form-label">描述</label><input class="form-input" v-model="kbForm.description" /></div>
        <div class="text-xs muted" style="margin:0 0 8px 118px;">模型/切分默认值来自平台配置（kb.*），可在「平台配置」统一维护</div>
        <div class="form-row"><label class="form-label">存储数据库</label>
          <div style="display:flex; gap:8px; flex:1;">
            <select class="form-input" v-model="kbForm.db_type" style="flex:1;" @change="connCfg = cfgFor(kbForm.db_type, kbForm.db_config || '')">
              <option v-for="t in opts.dbTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
            <button v-if="kbForm.db_type !== 'sqlite'" class="btn btn-ghost" @click="pingDb">测试连接</button>
          </div>
        </div>
        <div class="form-row" v-if="kbForm.db_type !== 'sqlite'">
          <label class="form-label">{{ kbForm.db_type === 'es' ? 'ES 配置' : 'PG 配置' }}</label>
          <div style="flex:1; display:flex; flex-direction:column; gap:6px;">
            <div class="row-head" style="gap:6px;">
              <input class="form-input" v-model="connCfg.url" placeholder="http://localhost:9200" v-if="kbForm.db_type === 'es'" />
              <template v-if="kbForm.db_type === 'pg'">
                <input class="form-input" v-model="connCfg.host" placeholder="host" style="flex:1;" />
                <input class="form-input" v-model="connCfg.port" placeholder="端口" style="width:80px;" />
              </template>
            </div>
            <div class="row-head" style="gap:6px;" v-if="kbForm.db_type === 'pg'">
              <input class="form-input" v-model="connCfg.dbname" placeholder="数据库名" style="flex:1;" />
            </div>
            <div class="row-head" style="gap:6px;">
              <input class="form-input" v-model="connCfg.user" placeholder="用户" style="flex:1;" />
              <input class="form-input" type="password" v-model="connCfg.password" placeholder="密码" style="flex:1;" />
            </div>
            <div class="text-xs" :class="pingMsg.includes('成功') ? 'ok-text' : 'muted'" v-if="pingMsg">{{ pingMsg }}</div>
          </div>
        </div>
        <div class="form-row"><label class="form-label">知识库类型</label>
          <select class="form-input" v-model="kbForm.kb_type">
            <option v-for="t in opts.kbTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
          </select></div>
        <div class="form-row"><label class="form-label">切分方式</label>
          <div style="display:flex; gap:8px; flex:1; align-items:center;">
            <select class="form-input" v-model="kbForm.chunk_mode" style="flex:1;">
              <option v-for="m in opts.chunkModes" :key="m.value" :value="m.value">{{ m.label }}</option>
            </select>
            <input class="form-input" type="number" v-model.number="kbForm.chunk_len" min="100" max="2000" style="width:110px;" />
            <span class="text-xs muted">字/块</span>
          </div></div>
        <div class="form-row"><label class="form-label">Embedding 模型</label>
          <select class="form-input" v-model="kbForm.embedding_model">
            <option value="">— 暂不启用向量 —</option>
            <option v-for="m in opts.embeddingModels" :key="m" :value="m">{{ m }}</option>
          </select></div>
        <div class="form-row"><label class="form-label">Reranker 模型</label>
          <select class="form-input" v-model="kbForm.reranker_model">
            <option value="">（无）</option>
            <option v-for="m in opts.rerankerModels" :key="m" :value="m">{{ m }}</option>
          </select></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="kbOpen = false">取消</button><button class="btn btn-primary" @click="saveKb">保存</button></div>
    </div>
  </div>

  <!-- 上传文档 -->
  <div class="modal-mask" v-if="docOpen" @click.self="docOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">上传文档 → {{ curKb.name }}</div><button class="modal-close" @click="docOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">选择文件（txt / md）</label><input class="form-input" type="file" accept=".txt,.md,.json,.csv" @change="e => docFile = e.target.files[0]" /></div>
        <div class="form-row"><label class="form-label">或直接粘贴文本</label><textarea class="form-input" v-model="docText" rows="6"></textarea></div>
        <div class="form-row"><label class="form-label">文档名（粘贴文本时必填）</label><input class="form-input" v-model="docName" /></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="docOpen = false">取消</button><button class="btn btn-primary" @click="saveDoc">提交并切分</button></div>
    </div>
  </div>

  <!-- 分块预览 -->
  <div class="modal-mask" v-if="chunkOpen" @click.self="chunkOpen = false">
    <div class="modal modal-lg">
      <div class="modal-header"><div class="modal-title">分块预览 — {{ chunkDoc?.name }}</div><button class="modal-close" @click="chunkOpen = false">×</button></div>
      <div class="modal-body">
        <div class="hit" v-for="(c, i) in chunks" :key="i"><span class="tag">#{{ c.idx }}</span><div class="hit-text">{{ c.content }}</div></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
const spaces = ref([]); const curSpace = ref(0)
const kbs = ref([]); const curKb = ref(null); const docs = ref([])
const opts = ref({ dbTypes: [], kbTypes: [], chunkModes: [], embeddingModels: [], rerankerModels: [] })
const spaceOpen = ref(false); const spaceForm = ref({ name: '', description: '' })
const kbOpen = ref(false); const kbForm = ref({}); const connCfg = ref({}); const pingMsg = ref('')
const docOpen = ref(false); const docFile = ref(null); const docText = ref(''); const docName = ref('')
const chunkOpen = ref(false); const chunkDoc = ref(null); const chunks = ref([])
const query = ref(''); const hits = ref([]); const searched = ref(false); const lastBackend = ref('')

const pub = ref({})
async function loadPub() {
  try {
    const res = await fetch('/api/configs?size=100').catch(() => fetch('http://localhost:38087/api/configs?size=100'))
    const r = await res.json()
    if (r.code === 0) { const m = {}; for (const it of (r.data.list || r.data || [])) m[it.configKey] = it.configValue; pub.value = m }
  } catch {}
}
onMounted(async () => { loadPub(); loadSpaces(); loadKbs(); const r = await api('/api/kb/options'); if (r.code === 0) opts.value = r.data })

async function loadSpaces() { const r = await api('/api/kb/spaces'); if (r.code === 0) spaces.value = r.data }
async function loadKbs() { const r = await api('/api/kb/list' + (curSpace.value ? '?space_id=' + curSpace.value : '')); if (r.code === 0) kbs.value = r.data }
function pickKb(k) { curKb.value = k; loadDocs() }
async function loadDocs() { const r = await api(`/api/kb/${curKb.value.id}/docs`); if (r.code === 0) docs.value = r.data }

function blankKb() {
  const p = pub.value
  return { id: null, name: '', description: '', space_id: curSpace.value || 0, db_type: 'sqlite',
           kb_type: 'doc', chunk_mode: p['kb.chunk.mode'] || 'paragraph', chunk_len: Number(p['kb.chunk.len']) || 500,
           embedding_model: p['kb.embedding.model'] || '', reranker_model: p['kb.reranker.model'] || '' }
}
function editKb(k) {
  kbForm.value = { ...k }
  connCfg.value = cfgFor(k.db_type, k.db_config)
  pingMsg.value = ''
  kbOpen.value = true
}
function cfgFor(dbType, raw) {
  if (raw) { try { const c = JSON.parse(raw); if (Object.keys(c).length) return c } catch {} }
  const p = pub.value
  if (dbType === 'es') return { url: p['kb.es.url'] || 'http://localhost:9200', user: p['kb.es.user'] || '', password: p['kb.es.password'] || '' }
  if (dbType === 'pg') return { host: p['kb.pg.host'] || 'localhost', port: Number(p['kb.pg.port']) || 5432, user: p['kb.pg.user'] || 'postgres', password: p['kb.pg.password'] || '', dbname: p['kb.pg.dbname'] || 'postgres' }
  return {}
}
function saveSpace() {
  api('/api/kb/spaces', { method: 'POST', body: JSON.stringify(spaceForm.value) }).then(r => {
    if (r.code === 0) { spaceOpen.value = false; spaceForm.value = { name: '', description: '' }; loadSpaces() } else alert(r.detail || '失败')
  })
}
async function pingDb() {
  syncConfig()
  const r = await api('/api/kb/ping', { method: 'POST', body: JSON.stringify({ db_type: kbForm.value.db_type, db_config: JSON.stringify(connCfg.value) }) })
  pingMsg.value = r.message || (r.data?.ok ? '连接成功' : '连接失败')
}
function syncConfig() {
  if (kbForm.value.db_type !== 'sqlite') connCfg.value = cfgFor(kbForm.value.db_type, null)
}
function openNewKb() { kbForm.value = blankKb(); connCfg.value = {}; pingMsg.value = ''; kbOpen.value = true }
async function saveKb() {
  syncConfig()
  const body = { ...kbForm.value, db_config: kbForm.value.db_type === 'sqlite' ? '' : JSON.stringify(connCfg.value) }
  const r = kbForm.value.id
    ? await api('/api/kb/' + kbForm.value.id, { method: 'PUT', body: JSON.stringify(body) })
    : await api('/api/kb', { method: 'POST', body: JSON.stringify(body) })
  if (r.code === 0) { kbOpen.value = false; loadKbs(); if (kbForm.value.id) loadDocs() } else alert(r.detail || '失败')
}
async function delKb(k) {
  if (!confirm(`删除知识库「${k.name}」及其全部文档${k.db_type === 'es' ? '（含 ES 索引）' : ''}？`)) return
  await api(`/api/kb/${k.id}`, { method: 'DELETE' })
  if (curKb.value?.id === k.id) { curKb.value = null; docs.value = [] }
  loadKbs()
}
async function saveDoc() {
  if (!docFile.value && !docText.value.trim()) { alert('请选择文件或粘贴文本'); return }
  const fd = new FormData()
  if (docFile.value) { fd.append('file', docFile.value) } else { fd.append('name', docName.value || '未命名'); fd.append('text', docText.value) }
  const res = await fetch(`/api/kb/${curKb.value.id}/docs`.replace(/^\/api\/kb/, 'http://localhost:38126/api/kb'), { method: 'POST', body: fd })
  const r = await res.json()
  if (r.code === 0) { docOpen.value = false; docText.value = ''; docName.value = ''; docFile.value = null; loadDocs() } else alert(r.detail || '失败')
}
async function delDoc(d) {
  if (!confirm(`删除文档「${d.name}」？`)) return
  await api(`/api/kb/${curKb.value.id}/docs/${d.id}`, { method: 'DELETE' })
  loadDocs()
}
async function viewChunks(d) {
  chunkDoc.value = d
  const r = await api(`/api/kb/${curKb.value.id}/docs/${d.id}/chunks`)
  if (r.code === 0) { chunks.value = r.data; chunkOpen.value = true }
}
async function search() {
  if (!query.value.trim()) return
  searched.value = true
  const r = await api(`/api/kb/${curKb.value.id}/search?q=` + encodeURIComponent(query.value))
  if (r.code === 0) { hits.value = r.data; lastBackend.value = r.backend }
}
function fmtSize(n) { return n > 1024 ? (n / 1024).toFixed(1) + ' KB' : n + ' B' }
function typeLabel(t) { return ({ golden_answer: '标准答案', qa: 'QA', doc: '文档', faq: 'FAQ' })[t] || t }
function storeLabel(t) { return ({ sqlite: '内置', es: 'ES', pg: 'PG' })[t] || t }
function modeLabel(m) { return ({ paragraph: '段落', sentence: '句子', fixed: '固定长度' })[m] || m }
</script>

<style>
.kb-layout { display: flex; gap: 12px; flex: 1; min-height: 0; }
.kb-side { width: 190px; flex-shrink: 0; overflow-y: auto; }
.kb-side2 { width: 240px; flex-shrink: 0; overflow-y: auto; }
.kb-item { padding: 10px 14px; border-bottom: 1px solid var(--border-light); cursor: pointer; transition: background .15s; }
.kb-item:hover { background: var(--bg-soft); }
.kb-item.active { background: var(--bg-soft); border-left: 3px solid var(--accent, #4d6bfe); }
.side-empty { padding: 20px; text-align: center; }
.row-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.hit { background: var(--bg-soft); border: 1px solid var(--border-light); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; }
.hit-text { font-size: 13px; margin-top: 6px; line-height: 1.6; white-space: pre-wrap; }
.dot-mini { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-left: 4px; }
.dot-mini.green { background: #22c55e; }
.dot-mini.red { background: #ef4444; }
.ok-text { color: #16a34a; }
.modal { min-width: 440px; }
.modal-lg { min-width: 560px; }
</style>
