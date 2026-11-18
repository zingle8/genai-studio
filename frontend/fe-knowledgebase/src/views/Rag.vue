<template>
  <div class="page-header">
    <div><div class="page-title">RAG 管理</div><div class="page-subtitle">检索管道配置 / 索引统计 / 检索测试（py-genai-rag-systemone）</div></div>
    <div class="page-actions"><button class="btn btn-primary" @click="openCreate">＋ 新建管道</button></div>
  </div>

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
const pipes = ref([]); const stats = ref({}); const kbs = ref([])
const open = ref(false); const editId = ref(null)
const form = ref({})
const testing = ref(false); const testPipe = ref(null); const testQ = ref(''); const testRes = ref(null)
onMounted(load)

async function load() {
  const [a, s, k] = await Promise.all([api('/api/rag/pipelines'), api('/api/rag/stats'), api('/api/rag/kbs')])
  if (a.code === 0) pipes.value = a.data
  if (s.code === 0) stats.value = s.data
  if (k.code === 0) kbs.value = k.data
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
</style>
