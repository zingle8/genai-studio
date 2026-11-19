<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">使用日志</div>
        <div class="page-subtitle">调用明细检索（jv-genai-logs · 网关接入 SDK 上报汇聚）· 点击行查看调用详情</div>
      </div>
    </div>

    <div class="stat-grid mb-16">
      <div class="stat-card"><div><div class="stat-label">今日请求</div><div class="stat-value">{{ num(summary.requests) }}</div></div></div>
      <div class="stat-card"><div><div class="stat-label">成功率</div><div class="stat-value">{{ summary.successRate != null ? summary.successRate + '%' : '-' }}</div></div></div>
      <div class="stat-card"><div><div class="stat-label">今日 Token</div><div class="stat-value">{{ fmtNum(summary.tokens) }}</div></div></div>
      <div class="stat-card"><div><div class="stat-label">今日消费</div><div class="stat-value">¥{{ num(summary.cost) }}</div></div></div>
    </div>

    <div class="filter-bar">
      <input class="form-input" type="date" v-model="q.startDate" style="width:150px;" />
      <span class="muted">至</span>
      <input class="form-input" type="date" v-model="q.endDate" style="width:150px;" />
      <select class="form-select" v-model="q.model" style="width:170px;">
        <option value="">全部模型</option>
        <option v-for="m in models" :key="m" :value="m">{{ m }}</option>
      </select>
      <select class="form-select" v-model="q.apiKeyId" style="width:200px;">
        <option value="">全部 API Key</option>
        <option v-for="k in apiKeys" :key="k.id" :value="k.id">{{ k.name }}（{{ k.count }} 次）</option>
      </select>
      <select class="form-select" v-model="q.status" style="width:120px;">
        <option value="">全部状态</option>
        <option value="success">成功</option>
        <option value="fail">失败</option>
      </select>
      <input class="form-input" v-model="q.keyword" placeholder="Key / 链路ID / IP" style="width:180px;" @keyup.enter="search" />
      <button class="btn btn-primary" @click="search">查询</button>
    </div>

    <div class="card">
      <div class="card-body no-pad">
        <div class="table-wrap">
          <table>
            <thead>
              <tr><th>时间</th><th>链路 ID</th><th>API Key</th><th>模型</th><th>来源服务</th>
                  <th>Prompt</th><th>Completion</th><th>Token</th><th>消费</th><th>耗时</th><th>状态</th></tr>
            </thead>
            <tbody>
              <tr v-for="l in list" :key="l.id" class="log-row" @click="openDetail(l)">
                <td class="muted mono text-sm">{{ fmtTime(l.createdAt) }}</td>
                <td class="mono text-sm">{{ l.traceId }}</td>
                <td>{{ l.apiKeyName }} <span class="muted text-sm">{{ l.apiKeyId }}</span></td>
                <td><span class="tag">{{ l.model }}</span></td>
                <td class="muted text-sm">{{ l.serviceId }}</td>
                <td class="mono">{{ l.promptTokens }}</td>
                <td class="mono">{{ l.completionTokens }}</td>
                <td class="mono"><b>{{ l.totalTokens }}</b></td>
                <td class="mono">¥{{ l.cost }}</td>
                <td class="muted">{{ l.durationMs }} ms</td>
                <td>
                  <span class="tag" :class="l.status === 'success' ? 'tag-success' : 'tag-danger'">
                    {{ l.status === 'success' ? '成功' : '失败' }}
                  </span>
                </td>
              </tr>
              <tr v-if="!list.length"><td colspan="11"><div class="empty" style="padding:48px 0;">暂无数据</div></td></tr>
            </tbody>
          </table>
        </div>
        <div class="card-footer">
          <div class="text-sm muted">共 {{ total }} 条</div>
          <div class="pager">
            <select class="form-select page-size-select" v-model.number="size" @change="search">
              <option :value="10">10 个/页</option>
              <option :value="20">20 个/页</option>
              <option :value="50">50 个/页</option>
              <option :value="100">100 个/页</option>
            </select>
            <span class="text-sm muted">第 {{ page }} / {{ totalPages }} 页</span>
            <button class="page-btn" :disabled="page <= 1" @click="go(page - 1)">‹ 上一页</button>
            <button class="page-btn" :disabled="page >= totalPages" @click="go(page + 1)">下一页 ›</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 调用详情抽屉 -->
    <div class="drawer-mask" :class="{ show: detailOpen }" @click.self="detailOpen = false">
      <div class="log-drawer">
        <div class="drawer-head">
          <div>
            <div class="drawer-title">
              {{ detail?.model || row?.model || '-' }}
              <span class="tag" :class="detail?.statusCode === 200 ? 'tag-success' : 'tag-danger'" style="margin-left:8px;">{{ detail?.statusCode || '-' }}</span>
              <span class="tag" :class="isStream ? 'tag-accent' : 'tag-muted'" style="margin-left:6px;">{{ isStream ? '流式 stream' : '非流式' }}</span>
            </div>
            <div class="text-xs muted mono" style="margin-top:4px;">{{ detail?.traceId }}</div>
          </div>
          <button class="modal-close" @click="detailOpen = false">×</button>
        </div>
        <div class="drawer-body">
          <div class="drawer-meta">
            <div class="meta-item"><span class="meta-label">接口路径</span><code class="mini-code">{{ detail?.method }} {{ detail?.path }}</code></div>
            <div class="meta-item"><span class="meta-label">调用时间</span><span class="text-sm">{{ fmtTime(detail?.createdAt) }}</span></div>
            <div class="meta-item"><span class="meta-label">API Key</span><span class="text-sm">{{ row?.apiKeyName }}</span></div>
            <div class="meta-item"><span class="meta-label">耗时</span><span class="text-sm mono">{{ row?.durationMs }} ms</span></div>
            <div class="meta-item"><span class="meta-label">Token</span><span class="text-sm mono">{{ row?.promptTokens }} + {{ row?.completionTokens }} = {{ row?.totalTokens }}</span></div>
            <div class="meta-item"><span class="meta-label">消费</span><span class="text-sm mono">¥{{ row?.cost }}</span></div>
          </div>
          <div v-if="detail?.errorMsg" class="err-line">⚠ {{ detail.errorMsg }}</div>

          <div class="sec-title">用户输入（当前问题）</div>
          <div class="user-question">{{ curQuestion || '（未能从请求体解析出用户消息）' }}</div>

          <div class="sec-title">请求 JSON</div>
          <pre class="json-box">{{ prettyReq || '（无请求体记录）' }}</pre>

          <div class="sec-title">返回 JSON</div>
          <pre class="json-box">{{ prettyResp || '（无响应体记录）' }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

const size = ref(10)
const summary = ref({})
const list = ref([])
const total = ref(0)
const page = ref(1)
const q = ref({ startDate: '', endDate: '', model: '', status: '', apiKeyId: '', keyword: '' })
const models = ['DeepSeek-V3.2', 'DeepSeek-R1', 'GLM-4.7', 'GLM-4.6', 'GLM-4.5-Air', 'GLM-Embedding-3']
const apiKeys = ref([])

/* 详情抽屉状态 */
const detailOpen = ref(false)
const detail = ref(null)   // relay_log 详情（请求/响应 body）
const row = ref(null)      // 当前列表行（tokens/cost 等）
const curQuestion = ref('')
const prettyReq = ref('')
const prettyResp = ref('')
const isStream = ref(false)

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / size.value)))

onMounted(() => { loadSummary(); loadApiKeys(); load() })

async function loadApiKeys() {
  const res = await api('/api/logs/apikeys')
  if (res.code === 0) apiKeys.value = res.data || []
}

async function loadSummary() {
  const res = await api('/api/logs/summary')
  if (res.code === 0) summary.value = res.data || {}
}

async function load() {
  const p = new URLSearchParams({
    startDate: q.value.startDate, endDate: q.value.endDate,
    model: q.value.model, status: q.value.status,
    apiKeyId: q.value.apiKeyId,
    keyword: q.value.keyword, page: page.value, size: size.value
  })
  const res = await api('/api/logs?' + p.toString())
  if (res.code === 0) {
    list.value = res.data.list || []; total.value = res.data.total || 0
    if (!list.value.length && page.value > 1) { page.value--; return load() }
  }
}

function search() { page.value = 1; load() }
function go(p) { if (p < 1 || p > totalPages.value) return; page.value = p; load() }

/** 点击行：拉取转发内容日志（完整请求/响应） */
async function openDetail(l) {
  row.value = l; detail.value = null
  curQuestion.value = ''; prettyReq.value = ''; prettyResp.value = ''; isStream.value = false
  detailOpen.value = true
  const res = await api('/api/logs/relay/' + encodeURIComponent(l.traceId))
  if (res.code === 0 && res.data) {
    detail.value = res.data
    // 请求体：stream 标志 + 最后一条用户消息（当前问题）
    let req = null
    try { req = JSON.parse(res.data.requestBody || 'null') } catch (e) { /* 非 JSON 原样展示 */ }
    // 后端 relay_log 已单独落 question / is_stream 列，缺失时回退从 requestBody 解析
    isStream.value = detail.value.isStream != null ? !!detail.value.isStream : !!req?.stream
    curQuestion.value = detail.value.question || ''
    if (req && typeof req === 'object') {
      prettyReq.value = JSON.stringify(req, null, 2)
      if (!curQuestion.value) {
        const msgs = Array.isArray(req.messages) ? req.messages : []
        const lastUser = [...msgs].reverse().find(m => m.role === 'user')
        curQuestion.value = lastUser?.content || ''
      }
    } else if (res.data.requestBody) {
      prettyReq.value = res.data.requestBody
    }
    // 响应体：JSON 美化；SSE 文本流原样展示
    try {
      const resp = JSON.parse(res.data.responseBody || 'null')
      prettyResp.value = resp ? JSON.stringify(resp, null, 2) : (res.data.responseBody || '')
    } catch (e) {
      prettyResp.value = res.data.responseBody || ''
    }
  }
}

function num(v) { return v == null ? '-' : Number(v).toLocaleString('zh-CN', { maximumFractionDigits: 2 }) }
function fmtNum(n) {
  n = Number(n) || 0
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}
function fmtTime(s) { return s ? String(s).replace('T', ' ').slice(0, 19) : '' }
</script>

<style>
.log-row { cursor: pointer; }
.log-row:hover td { background: var(--bg-soft, #f7f8fa); }
.page-size-select { width: 96px; }
.pager { display: flex; align-items: center; gap: 12px; }

/* 详情抽屉 */
.drawer-mask {
  position: fixed; inset: 0; background: rgba(15,23,42,0.35); z-index: 1000;
  opacity: 0; pointer-events: none; transition: opacity .2s;
}
.drawer-mask.show { opacity: 1; pointer-events: auto; }
.log-drawer {
  position: fixed; top: 0; right: 0; bottom: 0; width: 620px; max-width: 92vw;
  background: #fff; box-shadow: -12px 0 40px rgba(0,0,0,0.18);
  transform: translateX(100%); transition: transform .25s;
  display: flex; flex-direction: column;
}
.drawer-mask.show .log-drawer { transform: translateX(0); }
.drawer-head {
  display: flex; align-items: flex-start; justify-content: space-between; gap: 10px;
  padding: 16px 20px; border-bottom: 1px solid var(--border-light, #e5e8ef);
}
.drawer-title { font-size: 16px; font-weight: 600; display: flex; align-items: center; }
.drawer-body { flex: 1; overflow-y: auto; padding: 16px 20px; }
.drawer-meta { display: grid; grid-template-columns: 1fr 1fr; gap: 8px 14px; margin-bottom: 14px; }
.meta-item { display: flex; align-items: center; justify-content: space-between; gap: 8px; background: var(--bg-soft, #f7f8fa); border-radius: 8px; padding: 7px 10px; }
.meta-label { font-size: 12px; color: var(--text-muted, #6b7280); flex-shrink: 0; }
.mini-code { font-family: ui-monospace, Menlo, monospace; font-size: 12px; background: #fff; border: 1px solid var(--border-light, #e5e8ef); border-radius: 5px; padding: 1px 6px; }
.err-line { font-size: 12.5px; color: #e5484d; background: rgba(229,72,77,0.08); border: 1px solid rgba(229,72,77,0.25); border-radius: 8px; padding: 8px 12px; margin-bottom: 12px; }
.sec-title {
  font-size: 12.5px; font-weight: 600; color: var(--text-muted, #6b7280);
  margin: 14px 0 8px; padding-left: 8px; border-left: 3px solid var(--primary, #4d6bfe); line-height: 1.4;
}
.user-question {
  font-size: 13.5px; line-height: 1.6; color: var(--text, #1f2430); white-space: pre-wrap;
  background: var(--bg-soft, #f7f8fa); border-radius: 10px; padding: 12px 14px;
}
.json-box {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12px; line-height: 1.55;
  background: #0f172a; color: #e2e8f0; border-radius: 10px; padding: 12px 14px;
  max-height: 260px; overflow: auto; white-space: pre-wrap; word-break: break-all; margin: 0;
}
</style>
