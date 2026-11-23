<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">模型管理</div>
        <div class="page-subtitle">模型注册（厂商 / 接口格式 / Base URL / API Key）/ 上下架 / 删除（仅管理员可见）</div>
      </div>
      <div class="page-actions"><button class="btn btn-primary" @click="openCreate">＋ 注册模型</button></div>
    </div>
    <div class="filter-bar">
      <input class="form-input" v-model="keyword" placeholder="模型名 / 提供方 / 厂商 / 真实名" style="width:200px;" @keyup.enter="resetAndLoad" />
      <select class="form-input filter-select" v-model="fProvider" @change="resetAndLoad"><option value="">提供方：全部</option><option v-for="o in providerOptions" :key="o" :value="o">{{ o }}</option></select>
      <select class="form-input filter-select" v-model="fVendor" @change="resetAndLoad"><option value="">厂商：全部</option><option v-for="o in vendorOptions" :key="o" :value="o">{{ o }}</option></select>
      <select class="form-input filter-select" v-model="fCategory" @change="resetAndLoad"><option value="">类型：全部</option><option v-for="o in categoryOptions" :key="o" :value="o">{{ o }}</option></select>
      <select class="form-input filter-select" v-model="fTier" @change="resetAndLoad"><option value="">等级：全部</option><option v-for="o in TIERS" :key="o" :value="o">{{ o }}</option></select>
      <select class="form-input filter-select" v-model="fStatus" @change="resetAndLoad"><option value="">状态：全部</option><option :value="1">已上架</option><option :value="0">已下架</option></select>
      <button class="btn btn-primary" @click="resetAndLoad">查询</button>
      <button v-if="hasFilter" class="btn btn-secondary" @click="clearFilters">清空筛选</button>
      <div class="spacer"></div><span class="text-sm muted">共 {{ total }} 个模型</span>
    </div>
    <div class="card"><div class="card-body no-pad"><div class="table-wrap">
      <table>
        <thead><tr><th>模型</th><th>厂商</th><th>格式</th><th>Base URL</th><th>URL Paths</th><th>API Key</th><th>类型</th><th>等级</th><th>上下文</th><th>状态</th><th class="text-right">操作</th></tr></thead>
        <tbody>
          <tr v-for="m in list" :key="m.id">
            <td><b>{{ m.name }}</b><div class="text-xs muted">{{ m.provider }}<template v-if="m.realName && m.realName !== m.name"> · 真实: {{ m.realName }}</template></div></td>
            <td class="muted">{{ m.vendor || '-' }}</td>
            <td><span class="tag" :class="fmtCls(m.apiFormat)">{{ m.apiFormat || 'openai' }}</span></td>
            <td class="mono text-xs" :title="m.baseUrl">{{ shortUrl(m.baseUrl) }}</td>
            <td class="text-xs" :title="m.urlPaths">{{ pathsSummary(m.urlPaths) }}</td>
            <td class="mono text-xs muted">{{ m.apiKey || '-' }}</td>
            <td><span class="tag" :class="tagCls(m.category)">{{ m.category }}</span></td>
            <td><span class="tag" :class="tierCls(m.tier)">{{ m.tier || '标准' }}</span></td>
            <td class="mono">{{ m.contextLen ? m.contextLen.toLocaleString() : '-' }}</td>
            <td><span class="tag" :class="m.status === 1 ? 'tag-success' : ''">{{ m.status === 1 ? '已上架' : '已下架' }}</span></td>
            <td class="text-right" style="white-space:nowrap;">
              <span class="link" style="cursor:pointer;" @click="openEdit(m)">编辑</span> |
              <span class="link" style="cursor:pointer;" @click="toggle(m)">{{ m.status === 1 ? '下架' : '上架' }}</span> |
              <span class="link" style="color:var(--danger); cursor:pointer;" @click="remove(m)">删除</span>
            </td>
          </tr>
          <tr v-if="!list.length"><td colspan="11"><div class="empty" style="padding:48px 0;">暂无数据</div></td></tr>
        </tbody>
      </table>
    </div></div></div>

    <div class="pagination-bar">
      <span class="text-sm muted">共 {{ total }} 条</span>
      <span class="page-size-wrap">
        <select class="form-input page-size" v-model.number="pageSize" @change="resetAndLoad">
          <option :value="10">10 个/页</option>
          <option :value="20">20 个/页</option>
          <option :value="50">50 个/页</option>
          <option :value="100">100 个/页</option>
        </select>
      </span>
      <button class="page-btn" :disabled="page <= 1" @click="goPage(page - 1)">‹ 上一页</button>
      <span class="page-info">第 <b>{{ page }}</b> / {{ totalPages }} 页</span>
      <button class="page-btn" :disabled="page >= totalPages" @click="goPage(page + 1)">下一页 ›</button>
    </div>

    <div class="modal-mask" :class="{ show: open }" @click.self="open = false">
      <div class="modal modal-reg">
        <div class="modal-header"><div class="modal-title">{{ editId ? '编辑模型' : '注册模型' }}</div><button class="modal-close" @click="open = false">×</button></div>
        <div class="modal-body reg-form">
          <div class="form-field">
            <div class="field-desc">平台对外名称，即 /v1/models 暴露的 ID。调用方在请求体中填写的 model 就是这个名字。</div>
            <div class="field-line">
              <label class="form-label" title="平台对外名称，即 /v1/models 暴露的 ID">模型名称 <span class="required">*</span></label>
              <input class="form-input" v-model="form.name" placeholder="如 GLM-4.7" />
            </div>
          </div>
          <div class="form-field" v-if="editId">
            <div class="field-line"><label class="form-label">当前编辑</label><div class="editing-name"><b>{{ form.name }}</b></div></div>
          </div>
          <div class="form-field">
            <div class="field-desc">上游厂商的真实模型 ID，转发请求时由网关自动替换。留空则与模型名称相同。</div>
            <div class="field-line">
              <label class="form-label" title="上游厂商的真实模型 ID，留空则与模型名称相同">真实模型名称</label>
              <input class="form-input" v-model="form.realName" placeholder="如 gpt-5.2-2026-08-07" />
            </div>
          </div>
          <div class="form-field">
            <div class="field-desc">可下拉选择已有值，或直接输入新值。</div>
            <div class="field-line">
              <label class="form-label" title="可下拉选择或直接输入">提供方</label>
              <ComboInput v-model="form.provider" :options="providerOptions" placeholder="如 智谱 AI / DeepSeek / 本地" />
            </div>
          </div>
          <div class="form-field">
            <div class="field-desc">可下拉选择已有值，或直接输入新值。</div>
            <div class="field-line">
              <label class="form-label" title="可下拉选择或直接输入新增">模型厂商</label>
              <ComboInput v-model="form.vendor" :options="vendorOptions" placeholder="如 智谱 AI / xAI" />
            </div>
          </div>
          <div class="form-field">
            <div class="field-desc">外接转发使用的接口协议，可下拉选择或输入新增（openai / claude / gemini）。</div>
            <div class="field-line">
              <label class="form-label" title="外接转发的接口协议">模型格式</label>
              <ComboInput v-model="form.apiFormat" :options="formatOptions" placeholder="如 openai / ollama" />
            </div>
          </div>
          <div class="form-field">
            <div class="field-line"><label class="form-label">Base URL</label><input class="form-input" v-model="form.baseUrl" placeholder="如 https://open.bigmodel.cn/api/paas/v4" /></div>
          </div>
          <div class="form-field">
            <div class="field-desc">外接模型转发用的上游密钥{{ editId ? '；留空保持原值' : '' }}。调用方无需填写此项。</div>
            <div class="field-line">
              <label class="form-label" title="外接模型转发用，调用方无需填写">API Key</label>
              <input class="form-input" type="password" v-model="form.apiKey" :placeholder="editId ? '留空则不修改' : 'sk-...'" autocomplete="new-password" />
            </div>
          </div>
          <div class="form-field">
            <div class="field-desc">支持的接口路径及各自的请求格式。如 GPT 配 /chat/completions、/v1/responses；Claude 可同时配 /v1/messages（claude 格式）与 /chat/completions（openai 格式）。已上架模型默认出现在 /v1/models 列表。</div>
            <div class="field-line field-line-top">
              <label class="form-label" title="支持的接口路径及各自的请求格式">URL Paths</label>
              <div class="url-paths">
                <div v-for="(p, i) in urlPaths" :key="i" class="url-path-row">
                  <input class="form-input" v-model="p.path" placeholder="如 /v1/chat/completions" />
                  <input class="form-input" v-model="p.format" list="format-options" placeholder="格式" style="width:140px;" autocomplete="off" />
                  <button type="button" class="btn btn-secondary btn-sm" @click="urlPaths.splice(i, 1)" :disabled="urlPaths.length <= 1">删除</button>
                </div>
                <button type="button" class="btn btn-secondary btn-sm" @click="urlPaths.push({ path: '', format: form.apiFormat })">＋ 添加路径</button>
              </div>
            </div>
          </div>
          <div class="form-field">
            <div class="field-desc">可下拉选择已有值，或直接输入新值。</div>
            <div class="field-line">
              <label class="form-label" title="可下拉选择或输入新增">模型类型</label>
              <ComboInput v-model="form.category" :options="categoryOptions" placeholder="如 文本生成 / 多模态 / 向量 Embedding" />
            </div>
          </div>
          <div class="form-field">
            <div class="field-desc">关联计费单价：旗舰 / 标准 / 免费，转发按 token 用量实时扣费。</div>
            <div class="field-line">
              <label class="form-label" title="关联计费单价">模型等级</label>
              <select class="form-input" v-model="form.tier"><option>旗舰</option><option>标准</option><option>免费</option></select>
            </div>
          </div>
          <div class="form-field">
            <div class="field-line"><label class="form-label">上下文长度</label><input class="form-input" type="number" v-model="form.contextLen" placeholder="如 128000" /></div>
          </div>
          <div class="form-field">
            <div class="field-desc">模型广场列表 / 卡片摘要，一句话介绍。</div>
            <div class="field-line">
              <label class="form-label" title="模型广场列表摘要">模型描述</label>
              <input class="form-input" v-model="form.description" placeholder="如 旗舰文本生成模型，兼具多模态视觉理解" />
            </div>
          </div>
          <div class="form-field">
            <div class="field-desc">模型广场「查看详情」展示的完整介绍：能力、适用场景、限制与计费说明。</div>
            <div class="field-line field-line-top">
              <label class="form-label" title="模型广场查看详情的完整介绍">模型详情</label>
              <textarea class="form-input" v-model="form.detail" rows="5" placeholder="详细能力说明、适用场景、限制与计费说明等"></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="open = false">取消</button>
          <button class="btn btn-primary" @click="submit">{{ editId ? '保存' : '注册' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import ComboInput from '../components/ComboInput.vue'
const list = ref([]); const total = ref(0); const keyword = ref(''); const open = ref(false); const editId = ref(null)
/* 下拉筛选 */
const fProvider = ref(''); const fVendor = ref(''); const fCategory = ref(''); const fTier = ref(''); const fStatus = ref('')
/* 分页 */
const page = ref(1); const pageSize = ref(10)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const hasFilter = computed(() => !!(keyword.value || fProvider.value || fVendor.value || fCategory.value || fTier.value || fStatus.value !== ''))
const providers = ['智谱 AI', 'DeepSeek', 'OpenAI', 'Anthropic', 'Google', '阿里云', '月之暗面', 'MiniMax', '本地']
const vendors = ['智谱 AI', 'DeepSeek', 'OpenAI', 'Anthropic', 'Google', '阿里云', '月之暗面', 'MiniMax', 'xAI Grok', '本地', '其他']
const BASE_FORMATS = ['openai', 'claude', 'gemini', 'other']
const CATEGORIES = ['文本生成', '多模态', '向量 Embedding', '排序 Reranker', '判断 Judge', '语音', '视频', '图片', 'OCR', '代码', '其他']
const TIERS = ['旗舰', '标准', '免费']

/* 动态合并：预设选项 + 模型列表里已使用的值（用户历史新增自动进入下拉） */
const providerOptions = computed(() => [...new Set([...providers, ...list.value.map(m => m.provider).filter(Boolean)])])
const vendorOptions = computed(() => [...new Set([...vendors, ...list.value.map(m => m.vendor).filter(Boolean)])])
const categoryOptions = computed(() => [...new Set([...CATEGORIES, ...list.value.map(m => m.category).filter(Boolean)])])
const formatOptions = computed(() => {
  const used = []
  for (const m of list.value) {
    if (m.apiFormat) used.push(m.apiFormat)
    try { for (const p of JSON.parse(m.urlPaths || '[]')) if (p.format) used.push(p.format) } catch (e) { /* 忽略 */ }
  }
  return [...new Set([...BASE_FORMATS, ...used])]
})
const emptyForm = () => ({ name: '', realName: '', provider: '', vendor: '智谱 AI', apiFormat: 'openai', baseUrl: '', apiKey: '', category: '文本生成', tier: '标准', contextLen: '', description: '', detail: '' })
const form = ref(emptyForm())
const urlPaths = ref([{ path: '/chat/completions', format: 'openai' }])

function parseUrlPaths(json) {
  try {
    const arr = JSON.parse(json || '[]')
    if (Array.isArray(arr) && arr.length) return arr.map(p => ({ path: p.path || '', format: p.format || 'openai' }))
  } catch (e) { /* 非法 JSON 走默认 */ }
  return [{ path: '/chat/completions', format: 'openai' }]
}

onMounted(load)
async function load() {
  const p = new URLSearchParams()
  if (keyword.value) p.set('keyword', keyword.value)
  if (fProvider.value) p.set('provider', fProvider.value)
  if (fVendor.value) p.set('vendor', fVendor.value)
  if (fCategory.value) p.set('category', fCategory.value)
  if (fTier.value) p.set('tier', fTier.value)
  if (fStatus.value !== '') p.set('status', fStatus.value)
  p.set('page', page.value); p.set('size', pageSize.value)
  const res = await api('/api/models?' + p.toString())
  if (res.code === 0) {
    list.value = res.data.list || []; total.value = res.data.total || 0
    // 数据被删导致当前页超界时回退一页
    if (!list.value.length && page.value > 1) { page.value--; return load() }
  }
}
/** 下拉/查询/页大小变化：回到第 1 页再加载 */
function resetAndLoad() { page.value = 1; load() }
function goPage(p) { if (p < 1 || p > totalPages.value) return; page.value = p; load() }
function clearFilters() {
  keyword.value = ''; fProvider.value = ''; fVendor.value = ''; fCategory.value = ''; fTier.value = ''; fStatus.value = ''
  resetAndLoad()
}
function openCreate() {
  editId.value = null; form.value = emptyForm()
  urlPaths.value = [{ path: '/chat/completions', format: 'openai' }]
  open.value = true
}
function openEdit(m) {
  editId.value = m.id
  form.value = { name: m.name || '', realName: m.realName || '', provider: m.provider || '', vendor: m.vendor || '其他', apiFormat: m.apiFormat || 'openai', baseUrl: m.baseUrl || '', apiKey: '', category: m.category || '文本生成', tier: m.tier || '标准', contextLen: m.contextLen || '', description: m.description || '', detail: m.detail || '' }
  urlPaths.value = parseUrlPaths(m.urlPaths)
  open.value = true
}
async function submit() {
  if (!form.value.name) { alert('模型名称不能为空'); return }
  // URL Paths 过滤空行后序列化；全空则传空数组（后端按默认路径兜底）
  const paths = urlPaths.value.filter(p => p.path && p.path.trim())
  const body = {
    ...form.value,
    realName: (form.value.realName || '').trim() || form.value.name, // 真实模型名留空时与模型名称一致
    urlPaths: JSON.stringify(paths.map(p => ({ path: p.path.trim(), format: p.format }))),
    contextLen: form.value.contextLen || null
  }
  const res = editId.value
    ? await api('/api/models/' + editId.value, { method: 'PUT', body: JSON.stringify(body) })
    : await api('/api/models', { method: 'POST', body: JSON.stringify(body) })
  if (res.code === 0) { open.value = false; editId.value = null; load() } else alert(res.message || '保存失败')
}
async function toggle(m) {
  await api('/api/models/' + m.id, { method: 'PUT', body: JSON.stringify({ status: m.status === 1 ? 0 : 1 }) })
  load()
}
async function remove(m) {
  if (!confirm('确认删除模型「' + m.name + '」？')) return
  await api('/api/models/' + m.id, { method: 'DELETE' }); load()
}
function tagCls(c) {
  if (!c) return ''
  if (c.includes('向量') || c.toLowerCase().includes('embedding')) return 'tag-accent'
  if (c.includes('多模态') || c.includes('语音') || c.includes('OCR')) return 'tag-warning'
  if (c.includes('排序') || c.toLowerCase().includes('rerank')) return 'tag-danger'
  if (c.includes('判断') || c.toLowerCase().includes('judge')) return 'tag-accent'
  return ''
}
function tierCls(t) { return t === '旗舰' ? 'tag-danger' : t === '免费' ? 'tag-success' : '' }
function fmtCls(f) { return f === 'claude' ? 'tag-warning' : f === 'gemini' ? 'tag-accent' : f === 'other' ? '' : 'tag-success' }
function shortUrl(u) { if (!u) return '-'; return u.length > 34 ? u.slice(0, 34) + '…' : u }
function pathsSummary(json) {
  try {
    const arr = JSON.parse(json || '[]')
    if (!Array.isArray(arr) || !arr.length) return '-'
    return arr.map(p => p.path).join('  ')
  } catch (e) { return '-' }
}
</script>

<style>
/* URL Paths 动态行 */
.url-paths { flex: 1; display: flex; flex-direction: column; gap: 8px; }
.url-path-row { display: flex; gap: 8px; align-items: center; }
.url-path-row .form-input { flex: 1; }
/* 当前编辑模型名展示 */
.editing-name { padding: 8px 12px; background: var(--bg-soft); border-radius: 8px; font-size: 14px; }
/* 筛选下拉 */
.filter-select { width: 130px; flex-shrink: 0; }
/* 分页条 */
.pagination-bar {
  display: flex; align-items: center; gap: 14px; margin-top: 12px;
  justify-content: flex-end;
}
.pagination-bar .page-size { width: 92px; padding: 4px 8px; font-size: 13px; }
.page-btn {
  height: 28px; padding: 0 12px; border: 1px solid var(--border); border-radius: 6px;
  background: #fff; font-size: 13px; color: var(--text-secondary); cursor: pointer; transition: all .15s;
}
.page-btn:hover:not(:disabled) { border-color: var(--accent); color: var(--accent); }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-info { font-size: 13px; color: var(--text-secondary); }
.page-info b { color: var(--accent); }
</style>

<style scoped>
/* 注册 / 编辑模型弹窗：说明独占上行，名称 + 输入框在下行 */
.modal-reg { max-width: 680px; }
.reg-form .form-field { margin-bottom: 16px; }
.reg-form .form-field:last-child { margin-bottom: 0; }
.reg-form .field-desc {
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-tertiary);
  margin-bottom: 7px;
  padding-left: 2px;
}
.reg-form .field-line { display: flex; align-items: center; gap: 14px; }
.reg-form .field-line-top { align-items: flex-start; }
.reg-form .field-line .form-label {
  width: 104px;
  flex-shrink: 0;
  margin-bottom: 0;
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
  cursor: help;
}
.reg-form .field-line > .form-input,
.reg-form .field-line > .url-paths,
.reg-form .field-line > .combo { flex: 1; min-width: 0; }
.reg-form .field-line-top .form-label { padding-top: 9px; }
.reg-form .url-paths { flex: 1; }
.reg-form textarea.form-input { min-height: 108px; }
</style>
