<template>
  <div class="page-header">
    <div><div class="page-title">OCR 管理</div><div class="page-subtitle">图片识别 / 引擎探测 / 任务历史（py-genai-ocr）</div></div>
    <div class="page-actions">
      <span class="tag" v-for="v in visionModels" :key="v" style="margin-right:6px;">视觉引擎 {{ v }}</span>
      <button class="btn btn-primary" @click="fileInput?.click()">＋ 上传图片识别</button>
      <input ref="fileInput" type="file" accept="image/*" style="display:none;" @change="onFile" />
    </div>
  </div>

  <div class="ocr-layout">
    <div class="card ocr-preview-card"><div class="card-body">
      <b style="display:block; margin-bottom:10px;">识别预览</b>
      <div v-if="!preview" class="text-center muted" style="padding:60px 0;">上传图片后开始识别</div>
      <template v-else>
        <img :src="preview" class="ocr-img" />
        <div style="margin-top:10px;" class="row-head">
          <span class="text-xs muted" v-if="busy"><span class="spinner"></span> 识别中…</span>
          <span class="text-xs muted" v-else-if="lastEngine">引擎 {{ lastEngine }} · {{ lastCost }}ms</span>
          <span style="flex:1"></span>
          <button class="btn btn-ghost btn-sm" v-if="ocrText" @click="copyText">复制文本</button>
        </div>
        <textarea class="form-input ocr-result" v-model="ocrText" rows="10" placeholder="识别结果"></textarea>
      </template>
    </div></div>

    <div class="card" style="flex:1; min-width:0;"><div class="card-body no-pad">
      <div style="padding:12px 14px; border-bottom:1px solid var(--border-light);"><b>任务历史</b></div>
      <div class="table-wrap"><table>
        <thead><tr><th>文件</th><th>引擎</th><th>状态</th><th>耗时</th><th class="text-right">操作</th></tr></thead>
        <tbody>
          <tr v-for="t in tasks" :key="t.id">
            <td class="text-sm">{{ t.name }}</td>
            <td class="text-xs">{{ t.engine }}</td>
            <td><span class="tag" :class="t.status === 'done' ? 'tag-success' : (t.status === 'failed' ? 'tag-danger' : '')">{{ t.status }}</span></td>
            <td class="text-xs">{{ t.cost_ms ? t.cost_ms + 'ms' : '—' }}</td>
            <td class="text-right">
              <button class="btn btn-ghost btn-sm" @click="viewTask(t)">查看</button>
              <button class="btn btn-ghost btn-sm" @click="delTask(t)">删除</button>
            </td>
          </tr>
          <tr v-if="!tasks.length"><td colspan="5" class="text-center muted">暂无任务</td></tr>
        </tbody>
      </table></div>
    </div></div>
  </div>

  <div class="modal-mask" v-if="detail" @click.self="detail = null">
    <div class="modal modal-lg">
      <div class="modal-header"><div class="modal-title">{{ detail.name }} — 识别结果</div><button class="modal-close" @click="detail = null">×</button></div>
      <div class="modal-body"><div class="hit-text" style="max-height:50vh; overflow:auto;">{{ detail.text || detail.error || '（空）' }}</div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api, withBase } from '../api'
const fileInput = ref(null)
const preview = ref(''); const busy = ref(false); const ocrText = ref('')
const lastEngine = ref(''); const lastCost = ref(0)
const tasks = ref([]); const detail = ref(null); const visionModels = ref([])
onMounted(async () => { loadTasks(); const r = await api('/api/ocr/engines'); if (r.code === 0) visionModels.value = r.data['ollama-vision'] })

async function loadTasks() { const r = await api('/api/ocr/tasks'); if (r.code === 0) tasks.value = r.data }

async function onFile(e) {
  const f = e.target.files[0]
  if (!f) return
  preview.value = URL.createObjectURL(f)
  busy.value = true; ocrText.value = ''; lastEngine.value = ''; lastCost.value = 0
  try {
    const fd = new FormData()
    fd.append('file', f)
    const res = await fetch(withBase('/api/ocr/recognize'), { method: 'POST', body: fd })
    const r = await res.json()
    if (r.code === 0) { ocrText.value = r.data.text; lastEngine.value = r.data.engine; lastCost.value = r.data.costMs }
    else alert(r.detail || '识别失败')
    loadTasks()
  } finally {
    busy.value = false
    e.target.value = ''
  }
}
async function viewTask(t) { const r = await api('/api/ocr/tasks/' + t.id); if (r.code === 0) detail.value = r.data }
async function delTask(t) { if (!confirm('删除该任务？')) return; await api('/api/ocr/tasks/' + t.id, { method: 'DELETE' }); loadTasks() }
function copyText() { navigator.clipboard?.writeText(ocrText.value); alert('已复制') }
</script>

<style>
.ocr-layout { display: flex; gap: 12px; flex: 1; min-height: 0; align-items: flex-start; }
.ocr-preview-card { width: 380px; flex-shrink: 0; }
.ocr-img { max-width: 100%; max-height: 260px; border-radius: 8px; border: 1px solid var(--border-light); }
.ocr-result { width: 100%; margin-top: 10px; resize: vertical; font-size: 13px; }
.row-head { display: flex; align-items: center; gap: 10px; }
.hit-text { font-size: 13px; line-height: 1.7; white-space: pre-wrap; }
.tag-danger { color: #ef4444; background: #fef2f2; border-color: #fecaca; }
</style>
