<template>
  <div class="page-header">
    <div><div class="page-title">OCR 管理</div><div class="page-subtitle">图片识别 / 引擎探测 / 任务历史（py-genai-ocr）</div></div>
    <div class="page-actions">
      <span class="tag" v-for="v in visionModels" :key="v" style="margin-right:6px;">视觉引擎 {{ v }}</span>
      <button class="btn btn-primary" @click="fileInput?.click()">＋ 上传图片识别</button>
      <input ref="fileInput" type="file" accept="image/*" style="display:none;" @change="onFilePicked" />
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

  <div class="modal-mask" v-if="promptOpen" @click.self="promptOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">识别提示词（OCR Prompt）</div><button class="modal-close" @click="promptOpen = false">×</button></div>
      <div class="modal-body">
        <div class="text-xs muted" style="margin-bottom:6px;">图片：{{ pendingFile?.name }}，提交后按此提示词调用视觉模型</div>
        <textarea class="form-input" v-model="ocrPrompt" rows="4"></textarea>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="promptOpen = false">取消</button><button class="btn btn-primary" @click="startRecognize">开始识别</button></div>
    </div>
  </div>

  <div class="modal-mask" v-if="detail" @click.self="detail = null">
    <div class="modal modal-lg">
      <div class="modal-header"><div class="modal-title">{{ detail.name }} — 任务详情</div><button class="modal-close" @click="detail = null">×</button></div>
      <div class="modal-body">
        <div class="ocr-detail-grid">
          <div>
            <img v-if="detail.id" :src="withBase('/api/ocr/tasks/' + detail.id + '/image')" class="ocr-img" @error="e => e.target.style.display = 'none'" />
            <div class="text-xs muted" style="margin-top:6px;">原图</div>
          </div>
          <div class="ocr-params">
            <div class="param-row"><span class="param-label">引擎</span><span class="tag">{{ detail.engine }}</span></div>
            <div class="param-row"><span class="param-label">状态</span><span class="tag" :class="detail.status === 'done' ? 'tag-success' : 'tag-danger'">{{ detail.status }}</span></div>
            <div class="param-row"><span class="param-label">耗时</span><b>{{ detail.cost_ms ? detail.cost_ms + ' ms' : '—' }}</b></div>
            <div class="param-row"><span class="param-label">文件大小</span>{{ detail.size ? (detail.size / 1024).toFixed(1) + ' KB' : '—' }}</div>
            <div class="param-row"><span class="param-label">创建时间</span>{{ detail.created_at }}</div>
            <div class="param-row" style="align-items:flex-start;"><span class="param-label">提示词</span><div class="prompt-box">{{ detail.prompt || '（默认）' }}</div></div>
          </div>
        </div>
        <b class="text-sm" style="display:block; margin:12px 0 6px;">识别回复</b>
        <div class="hit-text" style="background:var(--bg-soft); border:1px solid var(--border-light); border-radius:8px; padding:10px; max-height:30vh; overflow:auto;">{{ detail.text || detail.error || '（空）' }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api, withBase } from '../api'
const fileInput = ref(null)
const preview = ref(''); const busy = ref(false); const ocrText = ref('')
const lastEngine = ref(''); const lastCost = ref(0)
const promptOpen = ref(false); const pendingFile = ref(null); const ocrPrompt = ref('识别图片中的全部文字，按原样输出，不要解释。')
const tasks = ref([]); const detail = ref(null); const visionModels = ref([])
onMounted(async () => { loadTasks(); const r = await api('/api/ocr/engines'); if (r.code === 0) visionModels.value = r.data['ollama-vision'] })

async function loadTasks() { const r = await api('/api/ocr/tasks'); if (r.code === 0) tasks.value = r.data }

function onFilePicked(e) {
  const f = e.target.files[0]
  if (!f) return
  pendingFile.value = f
  promptOpen.value = true
  e.target.value = ''
}
async function startRecognize() {
  const f = pendingFile.value
  if (!f) return
  promptOpen.value = false
  preview.value = URL.createObjectURL(f)
  busy.value = true; ocrText.value = ''; lastEngine.value = ''; lastCost.value = 0
  try {
    const fd = new FormData()
    fd.append('file', f)
    fd.append('prompt', ocrPrompt.value || '识别图片中的全部文字，按原样输出，不要解释。')
    const res = await fetch(withBase('/api/ocr/recognize'), { method: 'POST', body: fd })
    const r = await res.json()
    if (r.code === 0) { ocrText.value = r.data.text; lastEngine.value = r.data.engine; lastCost.value = r.data.costMs }
    else alert(r.detail || '识别失败')
    loadTasks()
  } finally {
    busy.value = false
    pendingFile.value = null
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
.ocr-detail-grid { display: flex; gap: 14px; }
.ocr-detail-grid > div:first-child { width: 260px; flex-shrink: 0; }
.ocr-params { flex: 1; display: flex; flex-direction: column; gap: 7px; }
.param-row { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.param-label { width: 62px; color: var(--text-secondary); font-size: 12px; flex-shrink: 0; }
.prompt-box { flex: 1; background: var(--bg-soft); border: 1px solid var(--border-light); border-radius: 6px; padding: 6px 9px; font-size: 12.5px; line-height: 1.5; }
</style>
