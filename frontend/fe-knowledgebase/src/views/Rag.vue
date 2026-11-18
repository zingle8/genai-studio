<template>
  <div class="page-header">
    <div><div class="page-title">RAG 管理</div><div class="page-subtitle">检索管道配置 / RAG 查询（多源） / RAG 评估（py-genai-rag-systemone）</div></div>
    <div class="page-actions" v-if="tab === 'pipe'"><button class="btn btn-primary" @click="openCreate">＋ 新建管道</button></div>
  </div>

  <div class="mode-tabs" style="margin-bottom:12px;">
    <button class="mode-tab" :class="{active: tab === 'pipe'}" @click="tab = 'pipe'">管道配置</button>
    <button class="mode-tab" :class="{active: tab === 'query'}" @click="switchTab('query')">RAG 查询</button>
    <button class="mode-tab" :class="{active: tab === 'eval'}" @click="switchTab('eval')">RAG 评估</button>
  </div>

  <!-- ===== Tab 1: 管道配置 ===== -->
  <div v-if="tab === 'pipe'">
    <div class="card" style="margin-bottom:12px;"><div class="card-body">
      <b style="display:block; margin-bottom:10px;">索引统计与依赖健康</b>
      <div class="stat-row">
        <div class="stat-box"><div class="stat-num">{{ stats.totalChunks ?? '—' }}</div><div class="stat-label">索引分块总数</div></div>
        <div class="stat-box" v-for="(ok, name) in stats.services || {}" :key="name">
          <div class="stat-num"><span class="dot" :class="ok ? 'green' : 'red'"></span></div>
          <div class="stat-label">{{ name }}</div>
        </div>
      </div>
      <div class="text-xs muted" style="margin-top:8px;" v-if="stats.kbs?.length">可绑定知识库：{{ stats.kbs.map(k => k.name + '(' + k.chunkCount + '块)').join('、') }}</div>
    </div></div>

    <div class="card"><div class="card-body">
      <b style="display:block; margin-bottom:10px;">检索管道</b>
      <div class="table-wrap"><table>
        <thead><tr><th>管道</th><th>知识库</th><th>策略</th><th>重排</th><th>Top-K</th><th class="text-right">操作</th></tr></thead>
        <tbody>
          <tr v-for="p in pipes" :key="p.id">
            <td><b>{{ p.name }}</b></td>
            <td>{{ p.kb_name || '—' }}</td>
            <td><span class="tag" :class="p.strategy === 'hybrid' ? 'tag-accent' : ''">{{ p.strategy }}</span></td>
            <td><span class="tag" :class="p.rerank_on ? 'tag-success' : ''">{{ p.rerank_on ? '开' : '关' }}</span></td>
            <td>{{ p.top_k }}</td>
            <td class="text-right">
              <button class="btn btn-ghost btn-sm" @click="openEdit(p)">编辑</button>
              <button class="btn btn-ghost btn-sm" @click="testOpen(p)">检索测试</button>
              <button class="btn btn-ghost btn-sm" @click="delPipe(p)">删除</button>
            </td>
          </tr>
          <tr v-if="!pipes.length"><td colspan="6" class="text-center muted">暂无管道，点右上角新建</td></tr>
        </tbody>
      </table></div>
    </div></div>
  </div>

  <!-- ===== Tab 2: RAG 查询（多源） ===== -->
  <div v-if="tab === 'query'">
    <div class="card"><div class="card-body">
      <b style="display:block; margin-bottom:10px;">RAG 查询 — 知识库 / 知识图谱 / 本体图谱</b>
      <div class="row-head" style="gap:8px; flex-wrap:wrap;">
        <select class="form-input" v-model="qSrcType" style="width:130px;" @change="qSource = ''">
          <option value="kb">知识库</option>
          <option value="graph">知识图谱</option>
          <option value="onto">本体图谱</option>
        </select>
        <select class="form-input" v-model="qSource" style="width:200px;">
          <option value="">— 选择实例 —</option>
          <option v-for="s in (sources[qSrcType] || [])" :key="s.id" :value="s.id">{{ s.name }}（{{ s.chunkCount }}）</option>
        </select>
        <input class="form-input" v-model="qText" placeholder="查询问题，如：如何计费 / 研发部" @keyup.enter="doQuery" style="flex:1; min-width:200px;" />
        <input class="form-input" type="number" v-model.number="qTopK" min="1" max="20" title="Top-K" style="width:70px;" />
        <button class="btn btn-primary" @click="doQuery" :disabled="!qSource || qLoading">{{ qLoading ? '查询中…' : '查询' }}</button>
      </div>
      <div v-if="qResult" style="margin-top:12px;">
        <div class="text-xs muted">后端 {{ qResult.backend }} · 命中 {{ qResult.hits.length }} 条</div>
        <div class="hit" v-for="(h, i) in qResult.hits" :key="i">
          <span class="tag">{{ h.title }}</span> <span class="text-xs muted">{{ h.meta }} · score {{ h.score }}</span>
          <div class="hit-text">{{ h.content }}</div>
        </div>
        <div v-if="!qResult.hits.length" class="text-sm muted">无命中</div>
      </div>
    </div></div>
  </div>

  <!-- ===== Tab 3: RAG 评估 ===== -->
  <div v-if="tab === 'eval'">
    <div class="card" style="margin-bottom:12px;"><div class="card-body">
      <b style="display:block; margin-bottom:10px;">RAG 评估 — 检索质量测试集（hit@k / MRR / 时延）</b>
      <div class="row-head" style="gap:8px; flex-wrap:wrap; margin-bottom:10px;">
        <select class="form-input" v-model="evKb" style="width:200px;">
          <option value="">— 选择知识库 —</option>
          <option v-for="s in (sources.kb || [])" :key="s.id" :value="s.id">{{ s.name }}（{{ s.chunkCount }} 块）</option>
        </select>
        <input class="form-input" type="number" v-model.number="evTopK" min="1" max="10" title="Top-K" style="width:70px;" />
        <button class="btn btn-primary" @click="doEval" :disabled="!evKb || evLoading || !evText.trim()">{{ evLoading ? '评估中…' : '执行评估' }}</button>
      </div>
      <textarea class="form-input" v-model="evText" rows="5"
        placeholder="每行一个用例：问题||期望关键词（期望可省略）&#10;如：如何计费||token&#10;　　　OCR 支持什么格式||图片"></textarea>
      <div class="text-xs muted" style="margin-top:6px;">期望关键词命中判定：出现在检索结果的标题或内容中即命中；rank 用于 MRR 计算。</div>
      <div v-if="evSummary" style="margin-top:12px;">
        <div class="stat-row">
          <div class="stat-box"><div class="stat-num">{{ evSummary.cases }}</div><div class="stat-label">用例数</div></div>
          <div class="stat-box"><div class="stat-num">{{ (evSummary.hitRate * 100).toFixed(1) }}%</div><div class="stat-label">Hit@{{ evTopK }} 命中率</div></div>
          <div class="stat-box"><div class="stat-num">{{ evSummary.mrr }}</div><div class="stat-label">MRR</div></div>
          <div class="stat-box"><div class="stat-num">{{ evSummary.avgScore }}</div><div class="stat-label">平均检索分</div></div>
          <div class="stat-box"><div class="stat-num">{{ evSummary.avgLatencyMs }}ms</div><div class="stat-label">平均时延</div></div>
        </div>
        <div class="table-wrap" style="margin-top:10px;"><table>
          <thead><tr><th>问题</th><th>期望</th><th>命中</th><th>Rank</th><th>分数</th><th>时延</th><th>Top 内容</th></tr></thead>
          <tbody>
            <tr v-for="(d, i) in evDetails" :key="i">
              <td>{{ d.q }}</td><td>{{ d.expect || '—' }}</td>
              <td><span class="tag" :class="d.hit ? 'tag-success' : ''">{{ d.hit ? '✓' : '✗' }}</span></td>
              <td>{{ d.rank || '—' }}</td><td>{{ d.score }}</td><td>{{ d.latencyMs }}ms</td>
              <td class="text-xs muted" style="max-width:260px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{{ d.topContent }}</td>
            </tr>
          </tbody>
        </table></div>
      </div>
    </div></div>

    <div class="card"><div class="card-body">
      <b style="display:block; margin-bottom:10px;">评估历史</b>
      <div class="table-wrap"><table>
        <thead><tr><th>Run</th><th>源</th><th>用例</th><th>命中率</th><th>MRR</th><th>平均时延</th><th>时间</th></tr></thead>
        <tbody>
          <tr v-for="g in evalRuns" :key="g.runId">
            <td><b>{{ g.runId }}</b></td>
            <td>{{ g.sourceName || (g.sourceType + '#' + g.sourceId) }}</td>
            <td>{{ g.cases }}</td>
            <td>{{ (g.hitRate * 100).toFixed(1) }}%</td>
            <td>{{ g.mrr }}</td>
            <td>{{ g.avgLatencyMs }}ms</td>
            <td class="text-xs muted">{{ g.createdAt }}</td>
          </tr>
          <tr v-if="!evalRuns.length"><td colspan="7" class="text-center muted">暂无评估记录</td></tr>
        </tbody>
      </table></div>
    </div></div>
  </div>

  <!-- 管道编辑 -->
  <div class="modal-mask" v-if="open" @click.self="open = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">{{ editId ? '编辑管道' : '新建管道' }}</div><button class="modal-close" @click="open = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">管道名</label><input class="form-input" v-model="form.name" /></div>
        <div class="form-row"><label class="form-label">绑定知识库</label>
          <select class="form-input" v-model="form.kbSel">
            <option value="">— 不绑定 —</option>
            <option v-for="k in kbs" :key="k.id" :value="k.id">{{ k.name }}（{{ k.chunkCount }} 块）</option>
          </select>
        </div>
        <div class="form-row"><label class="form-label">检索策略</label>
          <select class="form-input" v-model="form.strategy">
            <option value="keyword">keyword（关键词）</option>
            <option value="vector">vector（向量，需 embedding 服务）</option>
            <option value="hybrid">hybrid（混合）</option>
          </select>
        </div>
        <div class="form-row"><label class="form-label">Top-K</label><input class="form-input" type="number" v-model.number="form.top_k" min="1" max="20" /></div>
        <div class="form-row"><label class="form-label"><input type="checkbox" v-model="form.rerank_on" /> 启用重排（bge-reranker-v2-m3，服务在线时生效）</label></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="open = false">取消</button><button class="btn btn-primary" @click="savePipe">保存</button></div>
    </div>
  </div>

  <!-- 检索测试 -->
  <div class="modal-mask" v-if="testing" @click.self="testing = false">
    <div class="modal modal-lg">
      <div class="modal-header"><div class="modal-title">检索测试 — {{ testPipe?.name }}</div><button class="modal-close" @click="testing = false">×</button></div>
      <div class="modal-body">
        <div class="row-head" style="gap:8px;">
          <input class="form-input" v-model="testQ" placeholder="测试查询" @keyup.enter="doTest" style="flex:1;" />
          <button class="btn btn-primary" @click="doTest">执行</button>
        </div>
        <div v-if="testRes" style="margin-top:10px;">
          <div class="text-xs muted">策略 {{ testRes.strategy }} · Top-K {{ testRes.topK }} · {{ testRes.costMs }}ms · {{ testRes.note }}</div>
          <div class="hit" v-for="h in testRes.hits" :key="h.chunkId">
            <span class="tag">{{ h.doc }} #{{ h.idx }}</span> <span class="text-xs muted">score {{ h.score }}</span>
            <div class="hit-text">{{ h.content }}</div>
          </div>
          <div v-if="!testRes.hits?.length" class="text-sm muted">无命中</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
const tab = ref('pipe')
const pipes = ref([]); const stats = ref({}); const kbs = ref([])
const open = ref(false); const editId = ref(null)
const form = ref({})
const testing = ref(false); const testPipe = ref(null); const testQ = ref(''); const testRes = ref(null)
// RAG 查询
const sources = ref({ kb: [], graph: [], onto: [] })
const qSrcType = ref('kb'); const qSource = ref(''); const qText = ref(''); const qTopK = ref(5)
const qLoading = ref(false); const qResult = ref(null)
// RAG 评估
const evKb = ref(''); const evTopK = ref(3); const evText = ref('如何计费||token\n平台是否支持多模型管理||模型')
const evLoading = ref(false); const evSummary = ref(null); const evDetails = ref([]); const evalRuns = ref([])
onMounted(load)

async function switchTab(t) {
  tab.value = t
  if (t !== 'pipe') await loadSources()
  if (t === 'eval') loadEvals()
}
async function load() {
  const [a, s, k] = await Promise.all([api('/api/rag/pipelines'), api('/api/rag/stats'), api('/api/rag/kbs')])
  if (a.code === 0) pipes.value = a.data
  if (s.code === 0) stats.value = s.data
  if (k.code === 0) kbs.value = k.data
}
async function loadSources() {
  const r = await api('/api/rag/sources')
  if (r.code === 0) sources.value = r.data
}
async function doQuery() {
  if (!qSource.value || !qText.value.trim()) return
  qLoading.value = true; qResult.value = null
  try {
    const r = await api('/api/rag/query', { method: 'POST', body: JSON.stringify({
      source_type: qSrcType.value, source_id: Number(qSource.value), q: qText.value.trim(), top_k: qTopK.value }) })
    if (r.code === 0) qResult.value = r.data
    else alert(r.detail || '查询失败')
  } finally { qLoading.value = false }
}
async function doEval() {
  if (!evKb.value || !evText.value.trim()) return
  const cases = evText.value.split('\n').map(l => l.trim()).filter(Boolean).map(l => {
    const [q, expect] = l.split('||')
    return { q: (q || '').trim(), expect: (expect || '').trim() }
  }).filter(c => c.q)
  if (!cases.length) return
  evLoading.value = true
  try {
    const kbName = (sources.value.kb || []).find(s => s.id === Number(evKb.value))?.name || ''
    const r = await api('/api/rag/evaluate', { method: 'POST', body: JSON.stringify({
      source_type: 'kb', source_id: Number(evKb.value), source_name: kbName, top_k: evTopK.value, cases }) })
    if (r.code === 0) { evSummary.value = r.data.summary; evDetails.value = r.data.details; loadEvals() }
    else alert(r.detail || '评估失败')
  } finally { evLoading.value = false }
}
async function loadEvals() {
  const r = await api('/api/rag/evals?limit=50')
  if (r.code === 0) evalRuns.value = r.data
}
function blank() {
  return { name: '', kbSel: '', strategy: 'keyword', top_k: 5, rerank_on: false }
}
function openCreate() { editId.value = null; form.value = blank(); open.value = true }
function openEdit(p) {
  editId.value = p.id
  form.value = { name: p.name, kbSel: p.kb_id || '', strategy: p.strategy, top_k: p.top_k, rerank_on: !!p.rerank_on }
  open.value = true
}
async function savePipe() {
  const kb = kbs.value.find(k => k.id === Number(form.value.kbSel))
  const body = {
    name: form.value.name, kb_id: kb ? kb.id : 0, kb_name: kb ? kb.name : '',
    strategy: form.value.strategy, top_k: form.value.top_k, rerank_on: form.value.rerank_on
  }
  const r = editId.value
    ? await api('/api/rag/pipelines/' + editId.value, { method: 'PUT', body: JSON.stringify(body) })
    : await api('/api/rag/pipelines', { method: 'POST', body: JSON.stringify(body) })
  if (r.code === 0) { open.value = false; load() } else alert(r.detail || r.message || '失败')
}
async function delPipe(p) {
  if (!confirm(`删除管道「${p.name}」？`)) return
  await api('/api/rag/pipelines/' + p.id, { method: 'DELETE' })
  load()
}
function testOpen(p) { testPipe.value = p; testRes.value = null; testQ.value = ''; testing.value = true }
async function doTest() {
  if (!testQ.value.trim()) return
  const r = await api(`/api/rag/test?pid=${testPipe.value.id}&q=` + encodeURIComponent(testQ.value), { method: 'POST' })
  if (r.code === 0) testRes.value = r.data
  else alert(r.detail || '失败')
}
</script>

<style>
.stat-row { display: flex; gap: 10px; flex-wrap: wrap; }
.stat-box { background: var(--bg-soft); border: 1px solid var(--border-light); border-radius: 10px; padding: 10px 18px; text-align: center; min-width: 110px; }
.stat-num { font-size: 18px; font-weight: 700; }
.stat-label { font-size: 12px; color: var(--text-secondary); margin-top: 3px; }
.dot { display: inline-block; width: 12px; height: 12px; border-radius: 50%; }
.dot.green { background: #22c55e; }
.dot.red { background: #ef4444; }
.row-head { display: flex; align-items: center; gap: 10px; }
.hit { background: var(--bg-soft); border: 1px solid var(--border-light); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; }
.hit-text { font-size: 13px; margin-top: 6px; line-height: 1.6; white-space: pre-wrap; }
.modal { min-width: 420px; }
.mode-tabs { display: flex; gap: 4px; background: var(--bg-soft, #f5f6fa); border: 1px solid var(--border-light, #e5e7eb); border-radius: 10px; padding: 4px; width: fit-content; }
.mode-tab { border: none; background: transparent; padding: 7px 18px; border-radius: 8px; cursor: pointer; font-size: 13px; color: var(--text-secondary, #6b7280); }
.mode-tab.active { background: #fff; color: var(--text-primary, #111827); font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,.08); }
</style>
