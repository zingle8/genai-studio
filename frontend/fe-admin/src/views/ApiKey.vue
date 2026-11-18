<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">API Key</div>
        <div class="page-subtitle">当前登录：<b>{{ owner }}</b></div>
      </div>
      <div class="page-actions">
        <button class="btn btn-primary" @click="openCreate">＋ 创建 API Key</button>
      </div>
    </div>

    <div v-if="createdNotice" class="notice" style="align-items:flex-start; background:var(--success-soft);">
      <div style="flex:1;" v-html="createdNotice"></div>
      <span class="link" style="cursor:pointer;" @click="createdNotice = ''">×</span>
    </div>

    <div class="notice" style="align-items:flex-start;">
      <div style="flex:1;">
        为保障账户安全，<b>API Key</b> 仅在创建时完整展示一次，后续无法查看或恢复。
      </div>
    </div>

    <div class="filter-bar">
      <div class="spacer"></div>
      <span class="text-sm muted">共 {{ total }} 条</span>
      <select class="form-select" v-model="filterField" style="width:150px;">
        <option value="name">按名称</option>
        <option value="key">按 API Key</option>
        <option value="owner">按创建人</option>
      </select>
      <input class="form-input" v-model="filterValue" placeholder="输入关键字" style="width:200px;" @keyup.enter="load" />
      <button class="btn btn-primary" @click="load">查询</button>
    </div>

    <div class="card">
      <div class="card-body no-pad">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>名称</th><th>API Key ID</th><th>API Key</th><th>创建时间</th>
                <th>上次使用</th><th>过期时间</th><th>可用模型</th><th>限流 R/T/C</th><th>创建人</th>
                <th class="text-right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="k in list" :key="k.id">
                <td>
                  <b>{{ k.name }}</b>
                  <div v-if="k.fields && k.fields.length" style="margin-top:4px; display:flex; gap:4px; flex-wrap:wrap;">
                    <span v-for="f in k.fields" :key="f" class="tag" style="font-size:11px;">{{ f }}</span>
                  </div>
                </td>
                <td class="mono">{{ k.keyId }}</td>
                <td class="mono">{{ k.apiKey }}</td>
                <td class="muted">{{ fmtTime(k.createdAt) }}</td>
                <td class="muted">{{ k.lastUsedAt }}</td>
                <td>
                  <span v-if="!k.expiryDate" class="muted">永久</span>
                  <span v-else-if="isExpired(k)" class="tag tag-danger">{{ k.expiryDate }} · 已过期</span>
                  <span v-else-if="isWarn(k)" class="tag tag-warning">{{ k.expiryDate }} · 即将过期</span>
                  <span v-else class="muted">{{ k.expiryDate }}</span>
                </td>
                <td>
                  <span v-if="!k.models" class="tag tag-accent">模型不限制</span>
                  <template v-else>
                    <span v-for="m in k.models.slice(0, 2)" :key="m" class="tag">{{ m }}</span>
                    <span v-if="k.models.length > 2" class="muted text-sm">+{{ k.models.length - 2 }}</span>
                  </template>
                </td>
                <td>
                  <span v-if="!k.rpm && !k.tpm && !k.cc" class="muted">不限制</span>
                  <span v-else class="mono text-sm">{{ fmtLimit(k.rpm) }} / {{ fmtLimit(k.tpm) }} / {{ k.cc == null ? '∞' : k.cc }}</span>
                </td>
                <td class="muted">{{ k.owner }}</td>
                <td class="text-right">
                  <span class="link" style="cursor:pointer;" @click="openEdit(k)">更新</span> |
                  <span class="link" style="cursor:pointer;" @click="renew(k)">延期</span> |
                  <span class="link" style="color:var(--danger); cursor:pointer;" @click="remove(k)">删除</span>
                </td>
              </tr>
              <tr v-if="!list.length"><td colspan="10"><div class="empty" style="padding:48px 0;">暂无数据</div></td></tr>
            </tbody>
          </table>
        </div>
        <div class="card-footer">
          <div class="text-sm muted">共 {{ total }} 条</div>
        </div>
      </div>
    </div>

    <!-- 创建/更新弹框 -->
    <div class="modal-mask" :class="{ show: modalOpen }" @click.self="modalOpen = false">
      <div class="modal modal-lg">
        <div class="modal-header">
          <div>
            <div class="modal-title">{{ editId ? '更新 API Key' : '创建 API Key' }}</div>
            <div class="modal-subtitle">为密钥指定可访问的模型范围，未指定的模型将无法调用。</div>
          </div>
          <button class="modal-close" @click="modalOpen = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label class="form-label">名称 <span class="required">*</span></label>
            <input class="form-input" v-model="form.name" placeholder="例如：prod-main-key" />
          </div>

          <div class="adv-divider" @click="advOpen = !advOpen">
            <div class="line"></div>
            <div class="cap">⚙ 高级配置（可选，默认已自动设置）</div>
            <div class="line"></div>
          </div>
          <div v-show="advOpen">
            <div class="form-row">
              <label class="form-label">过期时间</label>
              <div class="radio-group">
                <div class="radio-opt" :class="{ active: form.expiryType === 'never' }" @click="form.expiryType = 'never'"><span class="radio-dot"></span>永久有效</div>
                <div class="radio-opt" :class="{ active: form.expiryType === 'date' }" @click="form.expiryType = 'date'"><span class="radio-dot"></span>指定日期</div>
              </div>
              <input v-if="form.expiryType === 'date'" class="form-input" type="date" v-model="form.expiryDate" style="max-width:240px; margin-top:12px;" />
            </div>

            <div class="form-row">
              <label class="form-label">可用模型</label>
              <div class="radio-group">
                <div class="radio-opt" :class="{ active: form.modelScope === 'all' }" @click="form.modelScope = 'all'"><span class="radio-dot"></span>模型不限制</div>
                <div class="radio-opt" :class="{ active: form.modelScope === 'custom' }" @click="form.modelScope = 'custom'"><span class="radio-dot"></span>指定模型</div>
              </div>
              <div v-if="form.modelScope === 'custom'" style="margin-top:12px;">
                <div v-for="g in modelGroups" :key="g.title" style="margin-bottom:10px;">
                  <div class="mp-group-title">{{ g.title }}</div>
                  <div class="chips">
                    <div v-for="m in g.items" :key="m" class="chip model-chip"
                         :class="{ active: form.models.includes(m) }"
                         @click="toggleModel(m)">{{ m }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-row">
              <label class="form-label">限流与并发（留空 = 不限制）</label>
              <div class="org-grid">
                <div class="org-field"><div class="org-lbl">RPM（次/分钟）</div><input class="form-input" type="number" min="1" v-model="form.rpm" placeholder="如 3000" /></div>
                <div class="org-field"><div class="org-lbl">TPM（Token/分钟）</div><input class="form-input" type="number" min="1" v-model="form.tpm" placeholder="如 1000000" /></div>
                <div class="org-field"><div class="org-lbl">并发上限</div><input class="form-input" type="number" min="1" v-model="form.cc" placeholder="如 500" /></div>
              </div>
            </div>

            <div class="form-row" style="margin-bottom:0;">
              <label class="form-label">组织归属（公司 · 部门 · 业务）</label>
              <div class="org-grid">
                <div class="org-field"><div class="org-lbl">公司</div><input class="form-input" v-model="form.org.company" placeholder="输入或选择公司" /></div>
                <div class="org-field"><div class="org-lbl">部门</div><input class="form-input" v-model="form.org.dept" placeholder="输入或选择部门" /></div>
                <div class="org-field"><div class="org-lbl">业务</div><input class="form-input" v-model="form.org.business" placeholder="输入或选择业务线" /></div>
              </div>
              <div class="form-help">组织信息用于成本归属与按部门分摊。</div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="modalOpen = false">取消</button>
          <button class="btn btn-primary" @click="submit">{{ editId ? '更新' : '创建' }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api, getUser } from '../api'

const owner = getUser()?.username || 'admin'
const list = ref([])
const total = ref(0)
const filterField = ref('name')
const filterValue = ref('')
const modalOpen = ref(false)
const editId = ref(null)
const advOpen = ref(false)
const createdNotice = ref('')

const modelGroups = [
  { title: '文本生成', items: ['GLM-4.7', 'GLM-4.6', 'GLM-4.5-Air', 'DeepSeek-V3.2', 'DeepSeek-R1'] },
  { title: '多模态', items: ['GLM-4V', 'GLM-4V-Flash'] },
  { title: '向量 / 嵌入', items: ['GLM-Embedding-3', 'BGE-Large'] }
]

const emptyForm = () => ({
  name: '', expiryType: 'never', expiryDate: '', modelScope: 'all', models: [],
  rpm: '', tpm: '', cc: '', org: { company: '', dept: '', business: '' }
})
const form = ref(emptyForm())

onMounted(load)

async function load() {
  const res = await api('/api/apikeys?page=1&size=50')
  if (res.code === 0) {
    list.value = res.data.list || []
    total.value = res.data.total || 0
  }
}

function openCreate() {
  editId.value = null
  form.value = emptyForm()
  advOpen.value = false
  modalOpen.value = true
}

function openEdit(k) {
  editId.value = k.id
  form.value = {
    name: k.name,
    expiryType: k.expiryDate ? 'date' : 'never',
    expiryDate: k.expiryDate || '',
    modelScope: k.models && k.models.length ? 'custom' : 'all',
    models: k.models ? [...k.models] : [],
    rpm: k.rpm == null ? '' : k.rpm,
    tpm: k.tpm == null ? '' : k.tpm,
    cc: k.cc == null ? '' : k.cc,
    org: { ...k.org }
  }
  advOpen.value = true
  modalOpen.value = true
}

function toggleModel(m) {
  const i = form.value.models.indexOf(m)
  if (i >= 0) form.value.models.splice(i, 1)
  else form.value.models.push(m)
}

async function submit() {
  if (!form.value.name.trim()) return
  const body = {
    name: form.value.name.trim(),
    owner,
    expiryType: form.value.expiryType,
    expiryDate: form.value.expiryType === 'date' ? form.value.expiryDate : undefined,
    expiryNever: form.value.expiryType === 'never',
    models: form.value.modelScope === 'custom' ? form.value.models : null,
    rpm: form.value.rpm || null,
    tpm: form.value.tpm || null,
    cc: form.value.cc || null,
    org: form.value.org
  }
  let res
  if (editId.value) {
    res = await api('/api/apikeys/' + editId.value, { method: 'PUT', body: JSON.stringify(body) })
    if (res.code === 0) createdNotice.value = 'API Key「<b>' + body.name + '</b>」已更新，配置立即生效。'
  } else {
    res = await api('/api/apikeys', { method: 'POST', body: JSON.stringify(body) })
    if (res.code === 0) {
      createdNotice.value = 'API Key 创建成功，请立即复制保存（仅展示一次）：<span class="mono" style="font-weight:600;">' + res.data.apiKey + '</span>'
    }
  }
  if (res.code !== 0) { createdNotice.value = '操作失败：' + (res.message || ''); return }
  modalOpen.value = false
  load()
}

async function renew(k) {
  if (!k.expiryDate) { alert('该密钥永久有效，无需延期。'); return }
  await api('/api/apikeys/' + k.id + '/renew', { method: 'POST' })
  load()
}

async function remove(k) {
  if (!confirm('确认删除该 API Key？删除后立即失效且不可恢复。')) return
  await api('/api/apikeys/' + k.id, { method: 'DELETE' })
  load()
}

function fmtTime(s) { return s ? String(s).replace('T', ' ').slice(0, 19) : '' }
function fmtLimit(n) {
  if (n == null) return '∞'
  if (n >= 1000000) return (n / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
  return String(n)
}
function isExpired(k) { return k.expiryDate && new Date(k.expiryDate) < new Date() }
function isWarn(k) {
  if (!k.expiryDate || isExpired(k)) return false
  return (new Date(k.expiryDate) - new Date()) < 30 * 86400000
}
</script>

<style>
.adv-divider { display: flex; align-items: center; gap: 12px; margin: 22px 0; cursor: pointer; user-select: none; }
.adv-divider .line { flex: 1; height: 1px; background: var(--border-light); }
.adv-divider .cap { font-size: 12px; font-weight: 600; color: var(--text-tertiary); letter-spacing: 2px; flex-shrink: 0; }
.adv-divider:hover .cap { color: var(--text-secondary); }
.radio-group { display: flex; gap: 10px; flex-wrap: wrap; }
.radio-opt { display: inline-flex; align-items: center; gap: 6px; padding: 7px 14px; border: 1px solid var(--border); border-radius: 8px; font-size: 13px; cursor: pointer; user-select: none; }
.radio-opt.active { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }
.radio-dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.org-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.org-lbl { font-size: 12px; color: var(--text-secondary); margin-bottom: 6px; }
.mp-group-title { font-size: 12px; color: var(--text-tertiary); margin-bottom: 8px; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip { padding: 5px 12px; border: 1px solid var(--border); border-radius: 14px; font-size: 12.5px; cursor: pointer; user-select: none; }
.chip.model-chip.active { background: var(--accent); color: #fff; border-color: var(--accent); }
</style>
