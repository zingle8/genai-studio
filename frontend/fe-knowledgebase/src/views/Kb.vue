<template>
  <div class="page-header">
    <div><div class="page-title">知识库</div><div class="page-subtitle">空间管理 / 知识库管理 / 文档管理 / 检索测试</div></div>
    <div class="page-actions">
      <button v-if="tab === 'spaces'" class="btn btn-primary" @click="spaceOpen = true">＋ 新建空间</button>
      <button v-if="tab === 'kbs'" class="btn btn-primary" @click="openNewKb">＋ 新建知识库</button>
      <button v-if="tab === 'docs' && curKb" class="btn btn-primary" @click="docOpen = true">＋ 上传文档</button>
    </div>
  </div>

  <div class="mode-tabs">
    <button class="mode-tab" :class="{ active: tab === 'spaces' }" @click="tab = 'spaces'">空间管理</button>
    <button class="mode-tab" :class="{ active: tab === 'kbs' }" @click="tab = 'kbs'">知识库管理</button>
    <button class="mode-tab" :class="{ active: tab === 'docs' }" @click="tab = 'docs'">文档管理</button>
    <button class="mode-tab" :class="{ active: tab === 'search' }" @click="tab = 'search'">检索测试</button>
  </div>

  <!-- 面包屑 -->
  <div class="kb-crumbs" v-if="crumbs.length">
    <template v-for="(c, i) in crumbs" :key="i">
      <span class="crumb-link" v-if="c.go" @click="c.go()">{{ c.label }}</span>
      <span class="crumb-cur" v-else>{{ c.label }}</span>
      <span class="crumb-sep" v-if="i < crumbs.length - 1">/</span>
    </template>
  </div>

  <!-- ═══ Tab 1: 空间管理 ═══ -->
  <div class="card" v-if="tab === 'spaces'"><div class="card-body">
    <div class="table-wrap"><table>
      <thead><tr><th>空间名称</th><th>描述</th><th>知识库数</th><th>创建时间</th><th class="text-right">操作</th></tr></thead>
      <tbody>
        <tr v-for="s in spaces" :key="s.id">
          <td><b>{{ s.name }}</b></td>
          <td class="text-xs muted">{{ s.description || '—' }}</td>
          <td><span class="tag">{{ s.kbCount }}</span></td>
          <td class="text-xs muted">{{ s.created_at }}</td>
          <td class="text-right">
            <button class="btn btn-ghost btn-sm" @click="gotoSpaceKbs(s)">查看知识库</button>
            <button class="btn btn-ghost btn-sm" @click="delSpace(s)">删除</button>
          </td>
        </tr>
        <tr v-if="!spaces.length"><td colspan="5" class="text-center muted">暂无空间，点右上角新建</td></tr>
      </tbody>
    </table></div>
  </div></div>

  <!-- ═══ Tab 2: 知识库管理 ═══ -->
  <div class="card" v-if="tab === 'kbs'"><div class="card-body">
    <div class="row-head" style="margin-bottom:10px;">
      <span class="text-sm muted">空间过滤</span>
      <select class="form-input" v-model="curSpace" style="width:180px;" @change="loadKbs()">
        <option :value="0">全部空间</option>
        <option v-for="s in spaces" :key="s.id" :value="s.id">{{ s.name }}</option>
      </select>
      <span style="flex:1"></span>
      <span class="text-xs muted" v-if="curKb">当前选中：<b>{{ curKb.name }}</b></span>
    </div>
    <div class="table-wrap"><table>
      <thead><tr><th>所属空间</th><th>知识库</th><th>类型</th><th>存储</th><th>文档</th><th>模型</th><th class="text-right">操作</th></tr></thead>
      <tbody>
        <tr v-for="k in kbs" :key="k.id" :class="{ 'row-active': curKb?.id === k.id }">
          <td class="text-xs">{{ spaceName(k.space_id) }}</td>
          <td><b>{{ k.name }}</b><div class="text-xs muted">{{ k.description || '' }}</div></td>
          <td><span class="tag" :class="k.kb_type === 'golden_answer' ? 'tag-accent' : ''">{{ typeLabel(k.kb_type) }}</span></td>
          <td>{{ storeLabel(k.db_type) }} <span v-if="k.db_type !== 'sqlite'" class="dot-mini" :class="k.dbOk ? 'green' : 'red'"></span></td>
          <td>{{ k.docCount }}</td>
          <td class="text-xs muted">{{ k.embedding_model || '—' }}</td>
          <td class="text-right">
            <button class="btn btn-ghost btn-sm" @click="gotoDocs(k)">文档</button>
            <button class="btn btn-ghost btn-sm" @click="gotoSearch(k)">检索</button>
            <button class="btn btn-ghost btn-sm" @click="editKb(k)">配置</button>
            <button class="btn btn-ghost btn-sm" @click="delKb(k)">删除</button>
          </td>
        </tr>
        <tr v-if="!kbs.length"><td colspan="7" class="text-center muted">当前范围暂无知识库</td></tr>
      </tbody>
    </table></div>
  </div></div>

  <!-- ═══ Tab 3: 文档管理 ═══ -->
  <div class="card" v-if="tab === 'docs'"><div class="card-body">
    <div class="row-head" style="margin-bottom:10px;">
      <span class="text-sm muted">知识库</span>
      <select class="form-input" style="width:220px;" :value="curKb?.id || ''" @change="pickKbById(Number($event.target.value))">
        <option value="">— 请选择知识库 —</option>
        <option v-for="k in allKbs" :key="k.id" :value="k.id">{{ spaceName(k.space_id) }} / {{ k.name }}</option>
      </select>
      <span style="flex:1"></span>
      <button class="btn btn-primary btn-sm" v-if="curKb" @click="docOpen = true">＋ 上传文档</button>
    </div>
    <template v-if="curKb">
      <div class="text-xs muted" style="margin-bottom:8px;">切分：{{ modeLabel(curKb.chunk_mode) }} / {{ curKb.chunk_len }} 字 · 类型 {{ typeLabel(curKb.kb_type) }} · 存储 {{ storeLabel(curKb.db_type) }}</div>
      <div class="table-wrap"><table>
        <thead><tr><th>文档名</th><th>分块</th><th>大小</th><th>状态</th><th>时间</th><th class="text-right">操作</th></tr></thead>
        <tbody>
          <tr v-for="d in docs" :key="d.id">
            <td><b>{{ d.name }}</b></td><td>{{ d.chunks }}</td><td>{{ fmtSize(d.size) }}</td>
            <td><span class="tag tag-success">{{ d.status }}</span></td>
            <td class="text-xs muted">{{ d.created_at }}</td>
            <td class="text-right">
              <button class="btn btn-ghost btn-sm" @click="viewChunks(d)">分块</button>
              <button class="btn btn-ghost btn-sm" @click="delDoc(d)">删除</button>
            </td>
          </tr>
          <tr v-if="!docs.length"><td colspan="6" class="text-center muted">该库暂无文档</td></tr>
        </tbody>
      </table></div>
    </template>
    <div v-else class="text-center muted" style="padding:36px 0;">先在上方选择一个知识库</div>
  </div></div>

  <!-- ═══ Tab 4: 检索测试 ═══ -->
  <div class="card" v-if="tab === 'search'"><div class="card-body">
    <div class="row-head" style="margin-bottom:10px;">
      <span class="text-sm muted">知识库</span>
      <select class="form-input" style="width:220px;" :value="curKb?.id || ''" @change="pickKbById(Number($event.target.value))">
        <option value="">— 请选择知识库 —</option>
        <option v-for="k in allKbs" :key="k.id" :value="k.id">{{ spaceName(k.space_id) }} / {{ k.name }}</option>
      </select>
    </div>
    <div class="row-head" style="gap:8px;">
      <input class="form-input" v-model="query" placeholder="输入查询" @keyup.enter="search" style="flex:1;" />
      <button class="btn btn-primary" @click="search" :disabled="!curKb">检索</button>
    </div>
    <div v-if="searched" class="search-res">
      <div class="text-xs muted" style="margin:8px 0;">命中 {{ hits.length }} 条 <template v-if="lastBackend">（{{ storeLabel(lastBackend) }}）</template></div>
      <div class="hit" v-for="h in hits" :key="h.chunkId + '-' + h.idx">
        <span class="tag">{{ h.doc || '文档#' + h.docId }} #{{ h.idx }}</span> <span class="text-xs muted">score {{ h.score }}</span>
        <div class="hit-text">{{ h.content }}</div>
      </div>
      <div v-if="!hits.length" class="text-sm muted">无命中</div>
    </div>
  </div></div>

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
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
const tab = ref('spaces')
const spaces = ref([]); const curSpace = ref(0)
const kbs = ref([]); const allKbs = ref([]); const curKb = ref(null); const docs = ref([])
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
onMounted(async () => { loadPub(); loadSpaces(); loadKbs(true); const r = await api('/api/kb/options'); if (r.code === 0) opts.value = r.data })

async function loadSpaces() { const r = await api('/api/kb/spaces'); if (r.code === 0) spaces.value = r.data }
async function loadKbs(all = false) {
  const r = await api('/api/kb/list' + (curSpace.value ? '?space_id=' + curSpace.value : ''))
  if (r.code === 0) kbs.value = r.data
  if (all) { const ra = await api('/api/kb/list'); if (ra.code === 0) allKbs.value = ra.data }
}
function spaceName(id) { const s = spaces.value.find(x => x.id === id); return s ? s.name : '— 未归属 —' }
async function pickKbById(id) {
  const k = allKbs.value.find(x => x.id === id)
  if (k) { curKb.value = k; await loadDocs() } else { curKb.value = null; docs.value = [] }
}
async function loadDocs() { if (!curKb.value) return; const r = await api(`/api/kb/${curKb.value.id}/docs`); if (r.code === 0) docs.value = r.data }

/* 面包屑 */
const crumbs = computed(() => {
  const arr = []
  if (tab.value === 'spaces') arr.push({ label: '知识空间' })
  if (tab.value === 'kbs') {
    arr.push({ label: '知识空间', go: () => tab.value = 'spaces' })
    if (curSpace.value) arr.push({ label: spaceName(curSpace.value) })
  }
  if (tab.value === 'docs') {
    arr.push({ label: '知识空间', go: () => tab.value = 'spaces' })
    if (curKb.value) arr.push({ label: spaceName(curKb.value.space_id), go: () => { curSpace.value = curKb.value.space_id; tab.value = 'kbs' } })
    else arr.push({ label: '知识库', go: () => tab.value = 'kbs' })
    if (curKb.value) arr.push({ label: curKb.value.name })
  }
  if (tab.value === 'search') {
    arr.push({ label: '知识库', go: () => tab.value = 'kbs' })
    if (curKb.value) arr.push({ label: spaceName(curKb.value.space_id) + ' / ' + curKb.value.name })
  }
  return arr
})
function gotoSpaceKbs(s) { curSpace.value = s.id; loadKbs(); tab.value = 'kbs' }
function gotoDocs(k) { curKb.value = k; loadDocs(); tab.value = 'docs' }
function gotoSearch(k) { curKb.value = k; searched.value = false; tab.value = 'search' }

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
async function delSpace(s) {
  if (!confirm(`删除空间「${s.name}」？（库会保留为未归属）`)) return
  await api('/api/kb/spaces/' + s.id, { method: 'DELETE' })
  if (curSpace.value === s.id) curSpace.value = 0
  loadSpaces(); loadKbs(true)
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
  if (r.code === 0) { kbOpen.value = false; loadKbs(true); if (kbForm.value.id) loadDocs() } else alert(r.detail || '失败')
}
async function delKb(k) {
  if (!confirm(`删除知识库「${k.name}」及其全部文档${k.db_type === 'es' ? '（含 ES 索引）' : ''}？`)) return
  await api(`/api/kb/${k.id}`, { method: 'DELETE' })
  if (curKb.value?.id === k.id) { curKb.value = null; docs.value = [] }
  loadKbs(true)
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
  if (!query.value.trim() || !curKb.value) return
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
.mode-tabs { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
.mode-tab {
  padding: 8px 18px; font-size: 13px; cursor: pointer;
  border: 1px solid var(--border-light); border-radius: 8px;
  background: #fff; color: var(--text, #1f2430); transition: all .15s; font-weight: 500;
}
.mode-tab:hover { border-color: var(--primary, #4d6bfe); color: var(--primary, #4d6bfe); }
.mode-tab.active { background: var(--primary, #4d6bfe); border-color: var(--primary, #4d6bfe); color: #fff; font-weight: 600; }
.kb-crumbs {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
  font-size: 13px; margin-bottom: 12px; padding: 8px 14px;
  background: var(--bg-soft, #f7f8fa); border-radius: 8px;
}
.crumb-link { color: var(--primary, #4d6bfe); cursor: pointer; }
.crumb-link:hover { text-decoration: underline; }
.crumb-cur { color: var(--text, #1f2430); font-weight: 600; }
.crumb-sep { color: #b9c2d4; }
.row-active { background: var(--bg-soft, #f7f8fa); }
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
