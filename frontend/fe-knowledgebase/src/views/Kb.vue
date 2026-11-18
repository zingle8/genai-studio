<template>
  <div class="page-header">
    <div><div class="page-title">知识库</div><div class="page-subtitle">文档上传 / 分块 / 检索测试（py-genai-knowledgebase）</div></div>
    <div class="page-actions"><button class="btn btn-primary" @click="kbOpen = true">＋ 新建知识库</button></div>
  </div>
  <div class="kb-layout">
    <!-- 左：知识库列表 -->
    <div class="card kb-side"><div class="card-body no-pad">
      <div class="kb-item" v-for="k in kbs" :key="k.id" :class="{ active: curKb?.id === k.id }" @click="pickKb(k)">
        <div><b>{{ k.name }}</b></div>
        <div class="text-xs muted">{{ k.docCount }} 文档 · {{ k.chunkCount }} 分块</div>
      </div>
      <div v-if="!kbs.length" class="side-empty text-sm muted">暂无知识库，点右上角新建</div>
    </div></div>
    <!-- 右：文档 + 检索 -->
    <div style="flex:1; min-width:0; display:flex; flex-direction:column; gap:12px;">
      <template v-if="curKb">
        <div class="card"><div class="card-body">
          <div class="row-head">
            <b>{{ curKb.name }}</b><span class="text-xs muted">{{ curKb.description || '—' }}</span>
            <span style="flex:1"></span>
            <button class="btn btn-ghost btn-sm" @click="delKb(curKb)">删除库</button>
          </div>
        </div></div>

        <div class="card"><div class="card-body">
          <div class="row-head" style="margin-bottom:10px;">
            <b>文档列表</b>
            <span style="flex:1"></span>
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
          <b style="display:block; margin-bottom:8px;">检索测试</b>
          <div class="row-head" style="gap:8px;">
            <input class="form-input" v-model="query" placeholder="输入关键词，空格分词" @keyup.enter="search" style="flex:1;" />
            <button class="btn btn-primary" @click="search">检索</button>
          </div>
          <div v-if="searched" class="search-res">
            <div class="text-xs muted" style="margin:8px 0;">命中 {{ hits.length }} 条</div>
            <div class="hit" v-for="h in hits" :key="h.chunkId">
              <span class="tag">{{ h.doc }} #{{ h.idx }}</span> <span class="text-xs muted">score {{ h.score }}</span>
              <div class="hit-text">{{ h.content }}</div>
            </div>
            <div v-if="!hits.length" class="text-sm muted">无命中</div>
          </div>
        </div></div>
      </template>
      <div v-else class="card"><div class="card-body text-center muted" style="padding:40px 0;">左侧选择知识库</div></div>
    </div>
  </div>

  <!-- 新建知识库 -->
  <div class="modal-mask" v-if="kbOpen" @click.self="kbOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">新建知识库</div><button class="modal-close" @click="kbOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">名称</label><input class="form-input" v-model="kbForm.name" /></div>
        <div class="form-row"><label class="form-label">描述</label><input class="form-input" v-model="kbForm.description" /></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="kbOpen = false">取消</button><button class="btn btn-primary" @click="saveKb">创建</button></div>
    </div>
  </div>

  <!-- 上传文档 -->
  <div class="modal-mask" v-if="docOpen" @click.self="docOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">上传文档 → {{ curKb.name }}</div><button class="modal-close" @click="docOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">选择文件（txt / md）</label><input class="form-input" type="file" accept=".txt,.md,.json,.csv" @change="e => docFile = e.target.files[0]" /></div>
        <div class="form-row"><label class="form-label">或直接粘贴文本</label><textarea class="form-input" v-model="docText" rows="6"></textarea></div>
        <div class="form-row"><label class="form-label">文档名（粘贴文本时必填）</label><input class="form-input" v-model="docName" placeholder="如 产品faq" /></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="docOpen = false">取消</button><button class="btn btn-primary" @click="saveDoc">提交并分块</button></div>
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
import { api, withBase } from '../api'
const kbs = ref([]); const curKb = ref(null); const docs = ref([])
const kbOpen = ref(false); const kbForm = ref({ name: '', description: '' })
const docOpen = ref(false); const docFile = ref(null); const docText = ref(''); const docName = ref('')
const chunkOpen = ref(false); const chunkDoc = ref(null); const chunks = ref([])
const query = ref(''); const hits = ref([]); const searched = ref(false)
onMounted(load)

async function load() { const r = await api('/api/kb/list'); if (r.code === 0) kbs.value = r.data }
function pickKb(k) { curKb.value = k; loadDocs() }
async function loadDocs() { const r = await api(`/api/kb/${curKb.value.id}/docs`); if (r.code === 0) docs.value = r.data }
async function saveKb() {
  const r = await api('/api/kb', { method: 'POST', body: JSON.stringify(kbForm.value) })
  if (r.code === 0) { kbOpen.value = false; kbForm.value = { name: '', description: '' }; load() } else alert(r.message || '失败')
}
async function delKb(k) {
  if (!confirm(`删除知识库「${k.name}」及其全部文档？`)) return
  await api(`/api/kb/${k.id}`, { method: 'DELETE' })
  if (curKb.value?.id === k.id) { curKb.value = null; docs.value = [] }
  load()
}
async function saveDoc() {
  if (!docFile.value && !docText.value.trim()) { alert('请选择文件或粘贴文本'); return }
  const fd = new FormData()
  if (docFile.value) { fd.append('file', docFile.value) } else { fd.append('name', docName.value || '未命名'); fd.append('text', docText.value) }
  const res = await fetch(withBase(`/api/kb/${curKb.value.id}/docs`), { method: 'POST', body: fd })
  const r = await res.json()
  if (r.code === 0) { docOpen.value = false; docText.value = ''; docName.value = ''; docFile.value = null; loadDocs(); load() } else alert(r.detail || '失败')
}
async function delDoc(d) {
  if (!confirm(`删除文档「${d.name}」？`)) return
  await api(`/api/kb/${curKb.value.id}/docs/${d.id}`, { method: 'DELETE' })
  loadDocs(); load()
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
  if (r.code === 0) hits.value = r.data
}
function fmtSize(n) { return n > 1024 ? (n / 1024).toFixed(1) + ' KB' : n + ' B' }
</script>

<style>
.kb-layout { display: flex; gap: 12px; flex: 1; min-height: 0; }
.kb-side { width: 240px; flex-shrink: 0; overflow-y: auto; }
.kb-item { padding: 12px 14px; border-bottom: 1px solid var(--border-light); cursor: pointer; transition: background .15s; }
.kb-item:hover { background: var(--bg-soft); }
.kb-item.active { background: var(--bg-soft); border-left: 3px solid var(--accent, #4d6bfe); }
.side-empty { padding: 24px; text-align: center; }
.row-head { display: flex; align-items: center; gap: 10px; }
.hit { background: var(--bg-soft); border: 1px solid var(--border-light); border-radius: 8px; padding: 10px 12px; margin-bottom: 8px; }
.hit-text { font-size: 13px; margin-top: 6px; line-height: 1.6; white-space: pre-wrap; }
.modal { min-width: 420px; }
</style>
