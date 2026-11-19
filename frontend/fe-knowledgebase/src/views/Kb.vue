<template>
  <div class="page-header">
    <div><div class="page-title">知识库</div><div class="page-subtitle">空间 / 知识库 / 文档 / 检索 — 左树右面板工作台</div></div>
    <div class="page-actions">
      <button v-if="!selKb" class="btn btn-ghost" @click="spaceOpen = true">＋ 新建空间</button>
      <button class="btn btn-primary" @click="openNewKb">＋ 新建知识库</button>
      <button v-if="selKb" class="btn btn-primary" @click="docOpen = true">＋ 上传文档</button>
    </div>
  </div>

  <div class="kb-layout">
    <!-- ═══ 左栏：空间 → 知识库 两级树 ═══ -->
    <div class="kb-tree">
      <input class="form-input tree-filter" v-model="treeFilter" placeholder="过滤空间 / 知识库…" />
      <div class="kb-tree-item" :class="{ active: !selSpace && !selKb }" @click="selAll">
        <span class="tree-ico">🗂️</span><b>全部</b><span class="kb-badge">{{ allKbs.length }} 库</span>
      </div>
      <div class="acc-group" v-for="g in tree" :key="g.id"
           :class="{ open: g.open, forced: !!treeFilter.trim() }">
        <div class="acc-head" :class="{ active: selSpace === g.id && !selKb }" @click="toggleGroup(g)"
             :title="g.description || ''">
          <span class="acc-arrow">▶</span>
          <span class="tree-ico">📁</span>
          <span class="tree-name" :title="g.name">{{ g.name }}</span>
          <span class="kb-badge">{{ g.children.length }} 库</span>
          <span class="tree-del" @click.stop="delSpace(g)" title="删除空间">×</span>
        </div>
        <div class="acc-body"><div class="acc-body-inner">
          <div class="kb-tree-item kb-tree-leaf" v-for="k in g.children" :key="k.id"
               :class="{ active: selKb?.id === k.id }" @click="pickKb(k)" :title="k.description || ''">
            <span class="type-dot" :class="k.kb_type"></span>
            <span class="tree-name" :title="k.name">{{ k.name }}</span>
            <span class="kb-badge">{{ k.docCount }} 文档</span>
          </div>
          <div v-if="!g.children.length" class="tree-empty text-xs muted">（无知识库）</div>
        </div></div>
      </div>
      <div v-if="treeFilter && !tree.length" class="tree-empty text-sm muted">无匹配结果</div>
    </div>

    <!-- ═══ 右栏：内容面板 ═══ -->
    <div class="kb-main">
      <!-- 面板 A：空间概览（全部/某空间） -->
      <template v-if="!selKb">
        <div class="panel-head">
          <div>
            <b style="font-size:15px;">{{ selSpace ? spaceName(selSpace) : '全部知识库' }}</b>
            <div class="text-xs muted" v-if="selSpace">{{ curSpaceObj?.description || '—' }}</div>
          </div>
          <div class="row-head" style="gap:6px;">
            <span class="text-xs muted">{{ panelKbs.length }} 个库 · {{ panelKbs.reduce((s, k) => s + (k.docCount || 0), 0) }} 文档 · {{ panelKbs.reduce((s, k) => s + (k.chunkCount || 0), 0) }} 分块</span>
          </div>
        </div>
        <div class="kb-cards">
          <div class="kb-card" v-for="k in panelKbs" :key="k.id" @click="pickKb(k)">
            <div class="row-head" style="justify-content:space-between;">
              <b class="kb-card-name" :title="k.name">{{ k.name }}</b>
              <span class="tag" :class="k.kb_type === 'golden_answer' ? 'tag-accent' : ''">{{ typeLabel(k.kb_type) }}</span>
            </div>
            <div class="text-xs muted" style="margin:6px 0 10px; min-height:16px;">{{ k.description || '—' }}</div>
            <div class="kb-card-meta">
              <span><b>{{ k.docCount }}</b> 文档</span>
              <span><b>{{ k.chunkCount }}</b> 分块</span>
              <span>{{ storeLabel(k.db_type) }} <i class="dot-mini" :class="k.db_type === 'sqlite' || k.dbOk ? 'green' : 'red'"></i></span>
            </div>
            <div class="kb-card-acts" @click.stop>
              <button class="btn btn-ghost btn-sm" @click="editKb(k)">配置</button>
              <button class="btn btn-ghost btn-sm" @click="delKb(k)">删除</button>
            </div>
          </div>
          <div v-if="!panelKbs.length" class="kb-empty">
            <div class="text-sm muted" style="margin-bottom:12px;">{{ selSpace ? '该空间暂无知识库' : '暂无知识库' }}</div>
            <button class="btn btn-primary" @click="openNewKb">＋ 新建知识库</button>
          </div>
        </div>
      </template>

      <!-- 面板 B：知识库详情（文档 | 检索测试 内嵌切换） -->
      <template v-else>
        <div class="panel-head">
          <div>
            <div class="row-head" style="gap:8px;">
              <span class="crumb-link" @click="backToSpace">📁 {{ spaceName(selKb.space_id) }}</span>
              <span class="muted">/</span>
              <b style="font-size:15px;">{{ selKb.name }}</b>
              <span class="tag" :class="selKb.kb_type === 'golden_answer' ? 'tag-accent' : ''">{{ typeLabel(selKb.kb_type) }}</span>
            </div>
            <div class="text-xs muted" style="margin-top:4px;">
              切分：{{ modeLabel(selKb.chunk_mode) }} / {{ selKb.chunk_len }} 字 · 存储 {{ storeLabel(selKb.db_type) }}<i class="dot-mini" :class="selKb.db_type === 'sqlite' || selKb.dbOk ? 'green' : 'red'"></i>
              · Embedding {{ selKb.embedding_model || '未启用' }} · Reranker {{ selKb.reranker_model || '（无）' }}
            </div>
          </div>
          <div class="row-head" style="gap:6px;">
            <button class="btn btn-ghost btn-sm" @click="editKb(selKb)">配置</button>
            <button class="btn btn-primary btn-sm" @click="docOpen = true">＋ 上传文档</button>
          </div>
        </div>

        <div class="sub-tabs">
          <button class="sub-tab" :class="{ active: subTab === 'docs' }" @click="subTab = 'docs'">文档（{{ docs.length }}）</button>
          <button class="sub-tab" :class="{ active: subTab === 'search' }" @click="subTab = 'search'">检索测试</button>
        </div>

        <!-- 文档 -->
        <div v-if="subTab === 'docs'" class="table-wrap panel-body"><table>
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
            <tr v-if="!docs.length"><td colspan="6" class="text-center muted">该库暂无文档，点右上角上传</td></tr>
          </tbody>
        </table></div>

        <!-- 检索测试 -->
        <div v-else class="panel-body">
          <div class="row-head" style="gap:8px; flex-wrap:nowrap;">
            <div class="search-mode-seg">
              <button class="seg-btn" :class="{ active: searchMode === 'keyword' }" @click="searchMode = 'keyword'">关键词检索</button>
              <button class="seg-btn" :class="{ active: searchMode === 'semantic' }" @click="searchMode = 'semantic'">语义检索</button>
            </div>
            <input class="form-input" v-model="query" :placeholder="searchMode === 'semantic' ? '语义检索：支持同义/近义表述，如「费用怎么算」' : '关键词检索：按字面分词匹配'" @keyup.enter="search" style="flex:1; min-width:180px;" />
            <button class="btn btn-primary" style="flex-shrink:0;" @click="search" :disabled="!query.trim() || searching">{{ searching ? '检索中…' : '检索' }}</button>
          </div>
          <div class="text-xs muted" style="margin-top:6px;" v-if="searchMode === 'semantic'">
            语义检索调用向量服务（{{ semModel || 'bge-m3' }}）对查询与全部分块编码后按余弦相似度排序，chunk 较多时首次稍慢。
          </div>
          <div v-if="searched" class="search-res">
            <div class="text-xs muted" style="margin:10px 0;">
              命中 {{ hits.length }} 条 <template v-if="lastBackend">（{{ backendLabel(lastBackend) }}）</template>
            </div>
            <div class="hit" v-for="h in hits" :key="h.chunkId + '-' + h.idx">
              <span class="tag">{{ h.doc || '文档#' + h.docId }} #{{ h.idx }}</span> <span class="text-xs muted">score {{ h.score }}</span>
              <div class="hit-text">{{ h.content }}</div>
            </div>
            <div v-if="!hits.length" class="text-sm muted">无命中</div>
          </div>
        </div>
      </template>
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
        <div class="form-row"><label class="form-label">知识空间 <span style="color:#ef4444;">*</span></label>
          <select class="form-input" v-model="kbForm.space_id">
            <option :value="0" disabled>— 请选择知识空间（必选）—</option>
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
      <div class="modal-header"><div class="modal-title">上传文档 → {{ selKb.name }}</div><button class="modal-close" @click="docOpen = false">×</button></div>
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
import { ref, computed, reactive, onMounted } from 'vue'
import { api } from '../api'
const selSpace = ref(0); const selKb = ref(null); const subTab = ref('docs')
const treeFilter = ref('')
const spaces = ref([])
const allKbs = ref([]); const docs = ref([])
const opts = ref({ dbTypes: [], kbTypes: [], chunkModes: [], embeddingModels: [], rerankerModels: [] })
const spaceOpen = ref(false); const spaceForm = ref({ name: '', description: '' })
const kbOpen = ref(false); const kbForm = ref({}); const connCfg = ref({}); const pingMsg = ref('')
const docOpen = ref(false); const docFile = ref(null); const docText = ref(''); const docName = ref('')
const chunkOpen = ref(false); const chunkDoc = ref(null); const chunks = ref([])
const query = ref(''); const hits = ref([]); const searched = ref(false); const lastBackend = ref('')
const searchMode = ref('keyword'); const searching = ref(false); const semModel = ref('')

const pub = ref({})
async function loadPub() {
  try {
    const res = await fetch('/api/configs?size=100').catch(() => fetch('http://localhost:38087/api/configs?size=100'))
    const r = await res.json()
    if (r.code === 0) { const m = {}; for (const it of (r.data.list || r.data || [])) m[it.configKey] = it.configValue; pub.value = m }
  } catch {}
}
onMounted(async () => {
  loadPub(); loadSpaces(); loadKbs()
  const r = await api('/api/kb/options'); if (r.code === 0) opts.value = r.data
})

async function loadSpaces() {
  const r = await api('/api/kb/spaces')
  if (r.code === 0) spaces.value = r.data.map(s => reactive({ ...s, open: true }))
}
async function loadKbs() {
  const r = await api('/api/kb/list')
  if (r.code === 0) allKbs.value = r.data
}
function spaceName(id) { const s = spaces.value.find(x => x.id === id); return s ? s.name : '— 未归属 —' }
const curSpaceObj = computed(() => spaces.value.find(x => x.id === selSpace.value))

/* 左树：space_id 分组（知识库必须归属空间） */
const tree = computed(() => {
  const f = treeFilter.value.trim().toLowerCase()
  const groups = spaces.value.map(s => ({ id: s.id, name: s.name, description: s.description, open: s.open, children: [] }))
  for (const k of allKbs.value) {
    const g = groups.find(x => x.id === k.space_id)
    if (g) g.children.push(k)
  }
  const all = groups.filter(g => g.children.length || !f)
  if (!f) return all
  return all.map(g => ({ ...g, children: g.children.filter(k => (k.name || '').toLowerCase().includes(f)) }))
    .filter(g => g.children.length || g.name.toLowerCase().includes(f))
})

/* 面板数据源 */
const panelKbs = computed(() => selSpace.value ? allKbs.value.filter(k => k.space_id === selSpace.value) : allKbs.value)

/* 左树交互 */
function selAll() { selSpace.value = 0; selKb.value = null }
function toggleGroup(g) {
  const s = spaces.value.find(x => x.id === g.id)
  if (s) s.open = !s.open          // 状态落在 reactive 源数据上，computed 树才会响应
  selSpace.value = g.id; selKb.value = null
}
async function pickKb(k) { selKb.value = k; subTab.value = 'docs'; searched.value = false; hits.value = []; await loadDocs() }
function backToSpace() { selSpace.value = selKb.value.space_id; selKb.value = null }
async function loadDocs() { if (!selKb.value) return; const r = await api(`/api/kb/${selKb.value.id}/docs`); if (r.code === 0) docs.value = r.data }

function blankKb() {
  const p = pub.value
  // 知识库必须归属空间：默认当前空间，否则取第一个空间
  const sid = selSpace.value || (spaces.value[0]?.id ?? 0)
  return { id: null, name: '', description: '', space_id: sid, db_type: 'sqlite',
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
  if (!confirm(`删除空间「${s.name}」？（空间下需无知识库方可删除）`)) return
  await api('/api/kb/spaces/' + s.id, { method: 'DELETE' })
  if (selSpace.value === s.id) selSpace.value = 0
  loadSpaces(); loadKbs()
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
  if (!kbForm.value.space_id) { alert('知识库必须归属知识空间，请先选择空间'); return }
  syncConfig()
  const body = { ...kbForm.value, db_config: kbForm.value.db_type === 'sqlite' ? '' : JSON.stringify(connCfg.value) }
  const r = kbForm.value.id
    ? await api('/api/kb/' + kbForm.value.id, { method: 'PUT', body: JSON.stringify(body) })
    : await api('/api/kb', { method: 'POST', body: JSON.stringify(body) })
  if (r.code === 0) {
    kbOpen.value = false
    await loadKbs()
    if (kbForm.value.id && selKb.value?.id === kbForm.value.id) {
      selKb.value = allKbs.value.find(x => x.id === kbForm.value.id) || selKb.value; loadDocs()
    }
  } else alert(r.detail || '失败')
}
async function delKb(k) {
  if (!confirm(`删除知识库「${k.name}」及其全部文档${k.db_type === 'es' ? '（含 ES 索引）' : ''}？`)) return
  await api(`/api/kb/${k.id}`, { method: 'DELETE' })
  if (selKb.value?.id === k.id) { selKb.value = null; docs.value = [] }
  loadKbs()
}
async function saveDoc() {
  if (!docFile.value && !docText.value.trim()) { alert('请选择文件或粘贴文本'); return }
  const fd = new FormData()
  if (docFile.value) { fd.append('file', docFile.value) } else { fd.append('name', docName.value || '未命名'); fd.append('text', docText.value) }
  const res = await fetch(`/api/kb/${selKb.value.id}/docs`.replace(/^\/api\/kb/, 'http://localhost:38126/api/kb'), { method: 'POST', body: fd })
  const r = await res.json()
  if (r.code === 0) {
    docOpen.value = false; docText.value = ''; docName.value = ''; docFile.value = null
    await loadKbs(); loadDocs()
  } else alert(r.detail || '失败')
}
async function delDoc(d) {
  if (!confirm(`删除文档「${d.name}」？`)) return
  await api(`/api/kb/${selKb.value.id}/docs/${d.id}`, { method: 'DELETE' })
  loadDocs(); loadKbs()
}
async function viewChunks(d) {
  chunkDoc.value = d
  const r = await api(`/api/kb/${selKb.value.id}/docs/${d.id}/chunks`)
  if (r.code === 0) { chunks.value = r.data; chunkOpen.value = true }
}
async function search() {
  if (!query.value.trim() || !selKb.value) return
  searched.value = true; searching.value = true
  try {
    const path = searchMode.value === 'semantic' ? 'semantic_search' : 'search'
    const r = await api(`/api/kb/${selKb.value.id}/${path}?q=` + encodeURIComponent(query.value))
    if (r.code === 0) {
      hits.value = r.data; lastBackend.value = r.backend
      if (searchMode.value === 'semantic' && (r.backend || '').startsWith('semantic:'))
        semModel.value = r.backend.split(':')[1] || 'bge-m3'
    } else alert(r.detail || '检索失败')
  } finally { searching.value = false }
}
function backendLabel(b) {
  if ((b || '').startsWith('semantic:')) return '语义 · ' + b.split(':')[1]
  return '关键词 · ' + storeLabel(b)
}
function fmtSize(n) { return n > 1024 ? (n / 1024).toFixed(1) + ' KB' : n + ' B' }
function typeLabel(t) { return ({ golden_answer: '标准答案', qa: 'QA', doc: '文档', faq: 'FAQ' })[t] || t }
function storeLabel(t) { return ({ sqlite: '内置', es: 'ES', pg: 'PG' })[t] || t }
function modeLabel(m) { return ({ paragraph: '段落', sentence: '句子', fixed: '固定长度' })[m] || m }
</script>

<style>
.kb-layout { display: flex; gap: 14px; align-items: flex-start; }
.kb-tree {
  width: 380px; flex-shrink: 0; background: #fff;
  border: 1px solid var(--border-light, #e5e7eb); border-radius: 12px;
  padding: 10px; max-height: calc(100vh - 170px); overflow-y: auto; position: sticky; top: 12px;
}
.tree-filter { font-size: 12px; margin-bottom: 8px; }
/* 手风琴分组 */
.acc-group { border: 1px solid var(--border-light, #e9ebf0); border-radius: 10px; margin-bottom: 8px; overflow: hidden; transition: border-color .18s, box-shadow .18s; }
.acc-group:hover { border-color: #c9d3ee; }
.acc-group.open { box-shadow: 0 1px 6px rgba(77, 107, 254, .07); }
.acc-head {
  padding: 9px 12px; cursor: pointer; font-size: 13px;
  display: flex; align-items: center; gap: 8px; background: var(--bg-soft, #f8f9fb);
  user-select: none;
}
.acc-group.open .acc-head { background: #f3f5fd; }
.acc-head.active { background: rgba(77, 107, 254, .12); color: var(--primary, #4d6bfe); font-weight: 600; }
.acc-arrow { color: #9aa3b5; font-size: 9px; transition: transform .22s ease; width: 12px; text-align: center; }
.acc-group.open .acc-arrow { transform: rotate(90deg); color: var(--primary, #4d6bfe); }
.acc-body { display: grid; grid-template-rows: 0fr; opacity: 0; transition: grid-template-rows .24s ease, opacity .18s ease; }
.acc-group.open .acc-body, .acc-group.forced .acc-body { grid-template-rows: 1fr; opacity: 1; }
.acc-body-inner { overflow: hidden; min-height: 0; padding: 0 4px; }
.acc-group.open .acc-body-inner, .acc-group.forced .acc-body-inner { padding: 4px; }
.acc-body-inner > .kb-tree-item { transition: padding .18s; }
.kb-tree-item {
  padding: 8px 10px; border-radius: 8px; cursor: pointer;
  display: flex; align-items: center; gap: 7px; font-size: 13px; line-height: 1.3;
}
.kb-tree-item:hover { background: var(--bg-soft, #f5f6fa); }
.kb-tree-item.active { background: rgba(77, 107, 254, .09); color: var(--primary, #4d6bfe); font-weight: 600; }
.kb-tree-leaf { padding-left: 30px; padding-right: 10px; }
.tree-ico { font-size: 13px; }
.tree-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.kb-badge { margin-left: auto; font-size: 11px; color: var(--text-secondary, #6b7280); background: #fff; border: 1px solid var(--border-light, #e5e7eb); border-radius: 10px; padding: 1px 8px; white-space: nowrap; }
.kb-tree-item.active .kb-badge { background: #fff; border-color: rgba(77, 107, 254, .35); }
.tree-del { color: #c3cad8; font-size: 14px; padding: 0 3px; visibility: hidden; }
.acc-head:hover .tree-del, .kb-tree-item:hover .tree-del { visibility: visible; }
.tree-del:hover { color: #ef4444; }
.tree-empty { padding: 6px 12px 6px 34px; }
.kb-main { flex: 1; min-width: 0; background: #fff; border: 1px solid var(--border-light, #e5e7eb); border-radius: 12px; padding: 16px; min-height: 420px; }
.panel-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; padding-bottom: 12px; border-bottom: 1px solid var(--border-light, #eef0f4); margin-bottom: 12px; flex-wrap: wrap; }
.kb-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(215px, 1fr)); gap: 10px; }
.kb-card {
  border: 1px solid var(--border-light, #e5e7eb); border-radius: 12px; padding: 14px;
  cursor: pointer; transition: all .15s; position: relative; display: flex; flex-direction: column;
}
.kb-card:hover { border-color: var(--primary, #4d6bfe); box-shadow: 0 2px 10px rgba(77, 107, 254, .1); transform: translateY(-1px); }
.kb-card-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 140px; }
.kb-card-meta { display: flex; gap: 10px; font-size: 12px; color: var(--text-secondary, #6b7280); margin-top: auto; }
.kb-card-meta b { color: var(--text, #1f2430); }
.kb-card-acts { display: flex; gap: 4px; margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--border-light, #eef0f4); }
.kb-empty { grid-column: 1 / -1; text-align: center; padding: 48px 0; }
.sub-tabs { display: flex; gap: 2px; border-bottom: 2px solid var(--border-light, #eef0f4); margin-bottom: 12px; }
.sub-tab { border: none; background: none; padding: 8px 16px; font-size: 13px; cursor: pointer; color: var(--text-secondary, #6b7280); border-bottom: 2px solid transparent; margin-bottom: -2px; }
.sub-tab.active { color: var(--primary, #4d6bfe); border-bottom-color: var(--primary, #4d6bfe); font-weight: 600; }
.panel-body { min-height: 200px; }
.type-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.type-dot.doc { background: #4d6bfe; }
.type-dot.faq { background: #f59e0b; }
.type-dot.qa { background: #10b981; }
.type-dot.golden_answer { background: #8b5cf6; }
.search-mode-seg { display: inline-flex; background: var(--bg-soft, #f0f1f5); border: 1px solid var(--border-light, #e5e7eb); border-radius: 9px; padding: 3px; flex-shrink: 0; }
.seg-btn { border: none; background: transparent; padding: 6px 14px; border-radius: 7px; font-size: 13px; cursor: pointer; color: var(--text-secondary, #6b7280); white-space: nowrap; }
.seg-btn.active { background: #fff; color: var(--primary, #4d6bfe); font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
.row-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.hit { background: var(--bg-soft, #f7f8fa); border: 1px solid var(--border-light, #e5e7eb); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; }
.hit-text { font-size: 13px; margin-top: 6px; line-height: 1.6; white-space: pre-wrap; }
.dot-mini { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-left: 4px; }
.dot-mini.green { background: #22c55e; }
.dot-mini.red { background: #ef4444; }
.ok-text { color: #16a34a; }
.modal { min-width: 440px; }
.modal-lg { min-width: 560px; }
.crumb-link { color: var(--primary, #4d6bfe); cursor: pointer; font-size: 13px; }
.crumb-link:hover { text-decoration: underline; }
</style>
