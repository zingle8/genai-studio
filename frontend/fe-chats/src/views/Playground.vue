<template>
  <div class="pg">
    <div class="page-header">
      <div>
        <div class="page-title">体验中心</div>
        <div class="page-subtitle">直连模型路由 jv-genai-router，真实推理 · 轮次自动保存</div>
      </div>
      <div class="page-actions mode-tabs">
        <button class="mode-tab" :class="{ active: mode === 'chat' }" @click="switchMode('chat')">聊天模式</button>
        <button class="mode-tab" :class="{ active: mode === 'debug' }" @click="switchMode('debug')">调试模式</button>
        <button class="mode-tab" :class="{ active: mode === 'special' }" @click="switchMode('special')">特殊模式</button>
      </div>
    </div>

    <div class="chat-layout">
      <!-- ===== 左侧：会话 + 配置 ===== -->
      <aside class="chat-side">
        <div class="chat-side-block">
          <button class="new-chat-btn" @click="newChat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
            新建对话
          </button>
          <div class="session-list">
            <div v-for="ses in sessions" :key="ses.id" class="session-item2" :class="{ active: currentId === ses.id }" @click="pick(ses)">
              <span class="session-title">{{ ses.title }}</span>
              <span class="session-del" title="删除会话" @click.stop="removeSession(ses)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg>
              </span>
            </div>
            <div v-if="!sessions.length" class="side-empty">暂无历史 · 发送后自动保存</div>
          </div>
        </div>

      </aside>

      <!-- ===== 主区 ===== -->
      <div class="chat-main">
        <!-- 特殊模式：与聊天/调试一致——上方响应区，下方输入区 -->
        <template v-if="mode === 'special'">
          <div class="special-wrap">
            <div class="special-resp">
              <div v-if="specialResp" class="special-resp-head">
                <span class="tag" :class="specialStatus === 'OK' ? 'tag-success' : 'tag-danger'">{{ specialStatus }}</span>
                <span class="text-xs muted">响应</span>
              </div>
              <pre v-if="specialResp" class="special-json">{{ specialResp }}</pre>
              <div v-else class="chat-welcome special-empty">
                <div class="welcome-badge">GenAI Studio</div>
                <h3>特殊模型请求</h3>
                <p class="muted">选择模型与接口路径，编辑请求体后发送</p>
              </div>
            </div>
            <div class="special-input">
              <div class="input-toolbar">
                <GwSelect v-model="selSpecialModel" class="model-select" :options="specialModelOptions" searchable fixed drop-up placeholder="选择特殊模型" />
                <label class="stream-toggle" title="请求体注入 stream:true，SSE 帧聚合后展示（仅 chat/completions 类接口支持）">
                  <input type="checkbox" v-model="streamOn"/> 流式返回
                </label>
                <span class="text-xs muted toolbar-hint">特殊接口 · 自定义请求体</span>
                <button class="key-fab" :class="{ open: keyPanelOpen, ok: !!currentKey }" :title="keyPanelOpen ? '收起配置面板' : '打开配置面板'" @click.stop="togglePanel($event.currentTarget)">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3m-3.6-6.4-2.1 2.1m-8.6 8.6-2.1 2.1m0-12.8 2.1 2.1m8.6 8.6 2.1 2.1"/></svg>
                  <span v-if="!keyPanelOpen && currentKeyName" class="key-fab-name">{{ currentKeyName }}</span>
                </button>
              </div>
              <div class="special-head">
                向 <b>{{ selSpecialModel || '（未选模型）' }}</b> 的 <code>{{ specialPath || '—' }}</code> 发送请求
              </div>
              <div class="input-row">
                <textarea class="special-editor" v-model="specialBody" rows="3" spellcheck="false" placeholder="编辑请求体 JSON…"></textarea>
                <button class="send-btn" :disabled="sending || !selSpecialModel || !specialPath" @click="sendSpecial" title="发送请求">
                  <svg v-if="!sending" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                  <span v-else class="spinner"></span>
                </button>
              </div>
              <div class="input-foot">{{ sending ? '请求中…' : '编辑请求体后发送 · 响应展示在上方' }}</div>
            </div>
          </div>
        </template>

        <!-- 聊天 / 调试模式 -->
        <template v-else>
          <div class="chat-msgs" ref="msgsEl">
            <!-- 空状态：欢迎 + 建议 -->
            <div v-if="!messages.length" class="chat-welcome">
              <div class="welcome-badge">GenAI Studio</div>
              <h3>{{ mode === 'debug' ? '调试模式' : '今天想聊点什么？' }}</h3>
              <p class="muted">{{ mode === 'debug' ? '配置系统提示词与模型参数后开始调试对话' : '在输入框上方选择一个模型，开始对话' }}</p>
              <div class="suggest-row">
                <button v-for="s in suggestions" :key="s" class="suggest-card" @click="quickSend(s)">{{ s }}</button>
              </div>
            </div>

            <div v-for="(m, i) in messages" :key="i" class="chat-msg" :class="m.role">
              <!-- assistant：头像 + 气泡 -->
              <div v-if="m.role === 'assistant'" class="msg-avatar">
                {{ (m.model || 'AI').slice(0, 2).toUpperCase() }}
              </div>
              <div class="msg-col">
                <div v-if="m.role === 'assistant' && m.model" class="msg-meta">
                  {{ m.model }}
                  <span v-if="m.completionTokens" class="msg-stat">{{ m.promptTokens }}+{{ m.completionTokens }} tok<template v-if="m.durationMs"> · {{ (m.durationMs / 1000).toFixed(1) }}s</template></span>
                </div>
                <div class="chat-bubble">
                  <template v-if="m.role === 'user' && m.images && m.images.length">
                    <img v-for="(img, j) in m.images" :key="j" :src="img" class="msg-img" />
                  </template>
                  <span class="msg-text">{{ m.content }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="chat-input">
            <!-- 输入框上方工具条：模型选择 + 流式开关 + 配置面板触发（向上弹出） -->
            <div class="input-toolbar">
              <GwSelect v-model="selModel" class="model-select" :options="chatModelOptions" searchable fixed drop-up placeholder="选择模型" />
              <label class="stream-toggle" title="开启后模型逐字返回（SSE 流式）">
                <input type="checkbox" v-model="streamOn"/> 流式返回
              </label>
              <span class="text-xs muted toolbar-hint">{{ mode === 'debug' ? '调试模式 · 支持系统提示词' : '单模型对话' }}</span>
              <button class="key-fab" :class="{ open: keyPanelOpen, ok: !!currentKey }" :title="keyPanelOpen ? '收起配置面板' : '打开配置面板'" @click.stop="togglePanel($event.currentTarget)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3m-3.6-6.4-2.1 2.1m-8.6 8.6-2.1 2.1m0-12.8 2.1 2.1m8.6 8.6 2.1 2.1"/></svg>
                <span v-if="!keyPanelOpen && currentKeyName" class="key-fab-name">{{ currentKeyName }}</span>
              </button>
            </div>
            <!-- 待发送图片预览 -->
            <div v-if="pendingImages.length" class="img-previews">
              <div v-for="(img, j) in pendingImages" :key="j" class="img-chip">
                <img :src="img.data" />
                <button class="img-chip-del" @click="pendingImages.splice(j, 1)">×</button>
              </div>
            </div>
            <div class="input-row">
              <label v-if="hasMultimodal" class="upload-btn" title="上传图片（多模态模型）">
                <input type="file" accept="image/*" multiple style="display:none;" @change="onFiles" />
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.4 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.2-9.19a4 4 0 0 1 5.65 5.66l-9.2 9.19a2 2 0 0 1-2.82-2.83l8.49-8.48"/></svg>
              </label>
              <textarea ref="inputEl" class="chat-textarea" rows="1" v-model="draft" :placeholder="inputHint"
                        :disabled="sending" @input="autoGrow" @keydown.enter.exact.prevent="onEnter" @keydown.shift.enter="autoGrow"></textarea>
              <button class="send-btn" :disabled="sending || !draft.trim() || !selModel" @click="send" :title="sendTitle">
                <svg v-if="!sending" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                <span v-else class="spinner"></span>
              </button>
            </div>
            <div class="input-foot">Enter 发送 · Shift+Enter 换行 · 内容自动保存</div>
          </div>
        </template>

        <!-- ===== 配置面板（单份，fixed 定位锚定触发按钮，向上弹出） ===== -->
        <transition name="gw-pop">
          <aside v-if="keyPanelOpen" class="config-pop" :style="popStyle" @click.stop>
            <div class="key-drawer-head">
              <span class="side-title" style="margin:0;">{{ panelTitle }}</span>
              <button class="key-drawer-close" title="收起" @click="keyPanelOpen = false">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/></svg>
              </button>
            </div>
            <div class="drawer-section">
              <div class="drawer-section-title">API Key</div>
              <GwSelect v-model="keyValue" :options="keyOptions" creatable searchable fixed placeholder="选择 Key 或直接粘贴新密钥" style="margin-bottom:8px;" @create="onKeyCreate" />
              <div class="side-note" style="margin-bottom:6px;">可下拉选择已保存的 Key，也可直接粘贴 sk-... 新密钥（自动保存）。</div>
              <div v-if="keyError" class="key-error">⚠ {{ keyError }}</div>
              <div v-if="meInfo" class="key-meta">
                <div class="key-meta-row">
                  <span class="tag tag-success">{{ meInfo.name }}</span>
                  <span class="key-limits">RPM {{ meInfo.rpm ?? '∞' }} · TPM {{ meInfo.tpm ?? '∞' }} · CC {{ meInfo.cc ?? '∞' }}</span>
                </div>
                <div class="key-meta-row muted">{{ meInfo.models?.length ? '白名单：' + meInfo.models.join('、') : '模型不限' }}</div>
              </div>
              <button v-if="currentKey" class="side-link" @click="delKey">删除当前 Key</button>
            </div>
            <template v-if="mode === 'debug'">
              <div class="drawer-section bordered">
                <div class="drawer-section-title">系统提示词</div>
                <GwSelect v-model="selPrompt" :options="promptOptions" fixed placeholder="选择模板…" style="margin-bottom:8px;" @update:model-value="applyPrompt" />
                <textarea class="form-input" v-model="systemPrompt" rows="5" placeholder="输入 System 提示词…"></textarea>
              </div>
              <div class="drawer-section bordered">
                <div class="drawer-section-title">知识库</div>
                <GwSelect v-model="kbId" :options="[]" placeholder="不使用知识库" disabled />
                <div class="side-note">知识库服务建设中，当前仅占位。</div>
              </div>
            </template>
            <template v-if="mode === 'special'">
              <div class="drawer-section bordered">
                <div class="drawer-section-title">接口路径</div>
                <GwSelect v-model="specialPath" :options="pathOptions" fixed placeholder="选择接口路径" style="margin-bottom:8px;" />
                <button class="btn btn-secondary btn-sm btn-block" @click="resetTemplate">重置请求模板</button>
              </div>
            </template>
          </aside>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { api, routerApi, routerStream, getUser } from '../api'
import GwSelect from '../components/GwSelect.vue'

/* ===== 常量 ===== */
const SPECIAL_RE = /向量|Embedding|重排|Rerank|判断|Judge/i
const MULTIMODAL_RE = /多模态|视觉|语音|OCR/i
const SUGGESTIONS = ['用一句话介绍你自己', '帮我写一段 SQL：查询近 7 天每日调用费用 Top10 模型', '解释一下什么是 RAG 检索增强']

/* ===== 状态 ===== */
const sessions = ref([]); const currentId = ref(null)
const mode = ref('chat')
const savedKeys = ref(JSON.parse(localStorage.getItem('pfx_keys') || '[]'))
const keyValue = ref('')  // 当前使用的 API Key 字符串（平台拉取 / 本地保存 / 直接粘贴）
const platformKeys = ref([])  // 从账号拉取的可用 Key（jv-genai-apikey /usable）
const keyError = ref('')      // Key 校验错误信息（面板内显示，不打断操作）
const meInfo = ref(null)
const allModels = ref([])
const selModel = ref('')
const selSpecialModel = ref('')
const messages = ref([])
const draft = ref('')
const streamOn = ref(false)
const sending = ref(false)
const msgsEl = ref(null)
const inputEl = ref(null)
const prompts = ref([])
const selPrompt = ref('')
const systemPrompt = ref('')
const kbId = ref('')
const specialPath = ref('')
const specialBody = ref('')
const specialResp = ref('')
const specialStatus = ref('')
const pendingImages = ref([])

/* ===== 计算属性 ===== */
const currentKey = computed(() => keyValue.value)
/** 平台 Key 优先（标记来源），其次本地保存的，按 value 去重 */
const keyOptions = computed(() => {
  const seen = new Set(); const out = []
  for (const k of platformKeys.value) {
    if (seen.has(k.apiKey)) continue
    seen.add(k.apiKey)
    out.push({ value: k.apiKey, label: k.name || '平台 Key', desc: '平台预置 · ' + (k.remark || k.apiKey.slice(0, 10) + '…'), tag: '平台' })
  }
  for (const k of savedKeys.value) {
    if (seen.has(k.key)) continue
    seen.add(k.key)
    out.push({ value: k.key, label: k.name || '未命名 Key', desc: k.key.slice(0, 10) + '…' + k.key.slice(-4) })
  }
  return out
})
const keyModels = computed(() => meInfo.value?.models || [])
/** 聊天/调试：非特殊类别；特殊模式：仅特殊类别；再按 Key 白名单过滤 */
const availModels = computed(() => {
  const base = mode.value === 'special'
    ? allModels.value.filter(m => SPECIAL_RE.test(m['jv-category'] || ''))
    : allModels.value.filter(m => !SPECIAL_RE.test(m['jv-category'] || ''))
  if (mode.value === 'special') return base
  if (!keyModels.value.length) return base
  return base.filter(m => keyModels.value.includes(m.id))
})
const chatModelOptions = computed(() => availModels.value.map(m => ({
  value: m.id, label: m.id, desc: m['jv-real-model'] || '', tag: m['jv-tier'] || '标准',
  tagCls: m['jv-tier'] === '旗舰' ? 'tag-danger' : m['jv-tier'] === '免费' ? 'tag-success' : ''
})))
const specialModelOptions = computed(() => availModels.value.map(m => ({
  value: m.id, label: m.id, desc: m['jv-real-model'] || '', tag: m['jv-tier'] || '标准',
  tagCls: m['jv-tier'] === '旗舰' ? 'tag-danger' : m['jv-tier'] === '免费' ? 'tag-success' : ''
})))
const promptOptions = computed(() => prompts.value.map(p => ({ value: p.id, label: p.name })))
const pathOptions = computed(() => specialPaths.value.map(p => ({ value: p, label: p })))
const specialModel = computed(() => allModels.value.find(m => m.id === selSpecialModel.value))
const specialPaths = computed(() => specialModel.value?.['jv-url-paths']?.map(p => p.path) || [])
const hasMultimodal = computed(() => {
  const m = allModels.value.find(x => x.id === selModel.value)
  return m && MULTIMODAL_RE.test(m['jv-category'] || '')
})
const inputHint = computed(() => {
  if (!selModel.value) return '先在输入框上方选择模型…'
  return `发送至 ${selModel.value}${hasMultimodal.value ? '（可附图片）' : ''}`
})
const sendTitle = computed(() => sending.value ? '发送中' : (!selModel.value ? '请先选择模型' : '发送 (Enter)'))
const currentKeyName = computed(() => keyOptions.value.find(o => o.value === keyValue.value)?.label || '')
const panelTitle = computed(() => mode.value === 'debug' ? '调试参数' : mode.value === 'special' ? '特殊请求配置' : 'API Key')

/* ===== 配置面板：fixed 定位锚定触发按钮，向上弹出，点击外部关闭 ===== */
const keyPanelOpen = ref(false)
const popStyle = ref({})

function togglePanel(anchorEl) {
  if (keyPanelOpen.value) { keyPanelOpen.value = false; return }
  const r = anchorEl.getBoundingClientRect()
  popStyle.value = {
    right: Math.max(8, Math.round(window.innerWidth - r.right)) + 'px',
    bottom: Math.round(window.innerHeight - r.top + 8) + 'px',
  }
  keyPanelOpen.value = true
  nextTick(() => {})
}

function onDocClickPanel(e) {
  if (!keyPanelOpen.value) return
  if (e.target.closest?.('.config-pop') || e.target.closest?.('.key-fab')) return
  keyPanelOpen.value = false
}
onMounted(() => document.addEventListener('click', onDocClickPanel))
onBeforeUnmount(() => document.removeEventListener('click', onDocClickPanel))

/* ===== 初始化 ===== */
onMounted(async () => {
  await loadPlatformKeys()
  if (!keyValue.value) {
    const first = platformKeys.value[0]?.apiKey || savedKeys.value[0]?.key || ''
    if (first) { keyValue.value = first; verifyKey() }
  }
  await loadModels()
  await loadPrompts()
  await loadSessions()
  // 切走页面再回来时自动恢复最近会话（含进行中轮次已落库的内容），避免"对话丢失"的观感
  if (sessions.value.length && !messages.value.length) pick(sessions.value[0])
})

/* Key 变化（选历史/输入新值）自动校验 */
watch(keyValue, v => {
  // 同步到平台统一存储（routerApi 默认从这里取 Key；聊天发送不显式传头）
  if (v) { localStorage.setItem('genai_model_api_key', v); verifyKey() }
  else { localStorage.removeItem('genai_model_api_key'); meInfo.value = null }
})

/** 拉取当前登录账号的可用 Key（jv-genai-apikey，owner=登录用户名，未登录回落 admin 演示账号） */
async function loadPlatformKeys() {
  try {
    const u = getUser()
    const owner = encodeURIComponent(u?.username || 'admin')
    const res = await api('/api/apikeys/usable?owner=' + owner)
    if (res.code === 0) platformKeys.value = res.data || []
  } catch (e) { /* apikey 服务未启动时忽略 */ }
}

/* 可用模型变化后：自动补选默认模型（保证进入页面即可直接发送） */
watch(availModels, list => {
  if (mode.value === 'special') return
  if (selModel.value && !list.some(m => m.id === selModel.value)) selModel.value = ''
  if (!selModel.value && list.length) {
    // 默认优先本地 Ollama 模型（保证可用），无本地模型才选第一个
    const local = list.find(m => /Ollama|本地/i.test(m.owned_by || ''))
    selModel.value = local?.id || list[0].id
  }
}, { immediate: true })

/* 特殊模式：切换模型自动重置请求模板与路径 */
watch(selSpecialModel, () => { if (mode.value === 'special') resetTemplate() })

/* ===== 会话 ===== */
async function loadSessions() {
  try {
    const res = await api('/api/chats?size=50')
    if (res.code === 0) sessions.value = res.data.list || []
  } catch (e) { /* chats 服务未启动时忽略 */ }
}

function newChat() { currentId.value = null; messages.value = []; pendingImages.value = [] }

async function ensureSession(firstText) {
  if (currentId.value) return currentId.value
  const title = (firstText || '新对话').slice(0, 20)
  const res = await api('/api/chats', { method: 'POST', body: JSON.stringify({ title }) })
  if (res.code === 0) { await loadSessions(); currentId.value = res.data.id }
  return currentId.value
}

async function pick(ses) {
  currentId.value = ses.id
  try {
    const res = await api('/api/chats/' + ses.id + '/messages')
    if (res.code === 0) {
      messages.value = (res.data || []).map(m => ({
        role: m.role, content: m.content, model: m.model || '', traceId: m.traceId || '',
        images: [], promptTokens: m.promptTokens, completionTokens: m.completionTokens, durationMs: m.durationMs || 0, cost: m.cost
      }))
    }
  } catch (e) { /* 服务未启动 */ }
  scrollBottom()
}

async function removeSession(ses) {
  if (!confirm('删除会话「' + ses.title + '」及其全部消息？')) return
  await api('/api/chats/' + ses.id, { method: 'DELETE' })
  if (currentId.value === ses.id) newChat()
  loadSessions()
}

/** 批量落库一轮消息（user + N 个模型回复，同 traceId） */
async function saveRound(traceId, round, sid0) {
  try {
    // 会话锁定：优先用发送时锁定的会话，防止切换会话/页面后消息串到当前会话
    let sid = sid0 ?? currentId.value
    if (!sid) {
      const title = (round[0]?.content || '新对话').slice(0, 20)
      const res = await api('/api/chats', { method: 'POST', body: JSON.stringify({ title }) })
      if (res.code !== 0) return
      sid = res.data.id
      currentId.value = sid
      loadSessions()
    }
    if (!sid) return
    await api('/api/chats/' + sid + '/messages/batch', {
      method: 'POST',
      body: JSON.stringify({ messages: round.map(m => ({
        role: m.role, content: m.content, model: m.model || '', traceId,
        promptTokens: m.promptTokens || 0, completionTokens: m.completionTokens || 0,
        durationMs: m.durationMs || 0, cost: m.cost || 0
      })) })
    })
    loadSessions()
  } catch (e) { /* 落库失败不影响对话 */ }
}

async function loadModels(attempt = 0) {
  const res = await routerApi('/v1/models').catch(() => null)
  if (res?.data?.length) { allModels.value = res.data; return }
  // 失败或空结果自动重试（router 冷启动/代理抖动自愈），最多 2 次
  if (attempt < 2) {
    await new Promise(r => setTimeout(r, 1200))
    return loadModels(attempt + 1)
  }
  allModels.value = res?.data || []
}

async function loadPrompts() {
  try {
    const res = await api('/api/prompts?size=50')
    if (res.code === 0) prompts.value = (res.data.list || []).map(p => ({ id: p.id, name: p.name, content: p.content }))
  } catch (e) { /* 提示词服务未启动时忽略 */ }
}

/* ===== Key 管理（单一下拉框：选历史 Key 或直接粘贴新 Key 自动保存） ===== */
function persistKeys() { localStorage.setItem('pfx_keys', JSON.stringify(savedKeys.value)) }

/** 下拉框输入新 Key 并确认 → 自动存入列表（备注 = Key 尾号） */
function onKeyCreate(key) {
  if (!savedKeys.value.some(k => k.key === key)) {
    savedKeys.value.push({ name: 'Key·' + key.slice(-4), key })
    persistKeys()
  }
}

let verifySeq = 0  // 竞态守卫：只接受最后一次校验结果（快速切换 Key 时旧响应作废）

async function verifyKey(attempt = 0) {
  const seq = ++verifySeq
  meInfo.value = null
  keyError.value = ''
  const key = keyValue.value
  if (!key) return
  let res = null
  try {
    res = await routerApi('/v1/me', { headers: { Authorization: 'Bearer ' + key } })
  } catch (e) {
    res = null
  }
  if (seq !== verifySeq) return  // 期间 Key 又被切换，丢弃过期结果
  if (res && res.object === 'me') {
    meInfo.value = res
    return
  }
  if (res && res.code === 401) {
    keyError.value = 'Key 无效或已被删除，请重新选择或粘贴有效密钥'
    return
  }
  // 网络/未知失败：自动重试一次（router 冷启动/代理抖动自愈）
  if (attempt < 1) {
    await new Promise(r => setTimeout(r, 1000))
    if (seq !== verifySeq) return
    return verifyKey(attempt + 1)
  }
  keyError.value = (res && res.message) || '无法连接模型路由（router:38100），请确认服务已启动'
}

function delKey() {
  const idx = savedKeys.value.findIndex(k => k.key === keyValue.value)
  if (idx < 0) return
  if (!confirm('删除 Key「' + (savedKeys.value[idx].name || '未命名') + '」？')) return
  savedKeys.value.splice(idx, 1)
  persistKeys()
  keyValue.value = ''
  meInfo.value = null
}

/* ===== 模式切换 ===== */
function switchMode(m) {
  mode.value = m
  messages.value = []
  currentId.value = null
  selSpecialModel.value = ''
  specialResp.value = ''
  specialStatus.value = ''
  specialPath.value = ''
  if (m !== 'debug') { selPrompt.value = '' }
}

/* ===== 调试模式辅助 ===== */
function applyPrompt() {
  const p = prompts.value.find(x => x.id === selPrompt.value)
  if (p) systemPrompt.value = p.content || ''
}

/* ===== 输入框自适应高度 ===== */
function autoGrow() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

/* ===== 聊天 / 调试：发送（单模型） ===== */
async function send() {
  if (!draft.value.trim() && !pendingImages.value.length) return
  if (!selModel.value) {
    // 自愈：可用模型有值则自动补选本地模型继续发送；确实无模型则刷新模型列表并提示
    const list = availModels.value
    if (list.length) {
      const local = list.find(m => /Ollama|本地/i.test(m.owned_by || ''))
      selModel.value = local?.id || list[0].id
    } else {
      loadModels().then(() => {
        if (availModels.value.length) selModel.value = availModels.value[0].id
      })
      alert('可用模型列表为空，正在重新加载模型列表，请稍后再试（或确认 router:38100 已启动）')
      return
    }
  }
  if (!currentKey.value) { alert('请先点击输入框上方的钥匙图标，保存 API Key'); return }
  sending.value = true
  const sid0 = currentId.value          // 锁定本轮会话（期间切换会话不影响落库归属）
  const t0 = Date.now()                 // 请求→回复总耗时起点
  const text = draft.value.trim()
  const images = pendingImages.value.map(x => x.data)
  const traceId = 'tr-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8)
  const round = [{ role: 'user', content: text, images }]
  messages.value.push({ role: 'user', content: text, images })
  draft.value = ''
  pendingImages.value = []
  resetInput()
  // 防御：nextTick 强制清空 DOM value，防止输入法/浏览器在 keydown 后把 pending 文本以 input 事件写回（残留已发送内容）
  nextTick(() => { if (inputEl.value && inputEl.value.value !== '') { inputEl.value.value = ''; draft.value = '' } })
  scrollBottom()

  const sys = mode.value === 'debug' && systemPrompt.value.trim()
    ? [{ role: 'system', content: systemPrompt.value.trim() }] : []
  const userContent = images.length
    ? [{ type: 'text', text }, ...images.map(u => ({ type: 'image_url', image_url: { url: u } }))]
    : text
  const history = messages.value
    .filter(m => m.role === 'user' || (m.role === 'assistant' && m.model === selModel.value))
    .map(m => ({ role: m.role, content: m.images?.length ? userContentOf(m) : m.content }))

  {
    const model = selModel.value
    const body = { model, messages: [...sys, ...history.slice(0, -1), { role: 'user', content: userContent }] }
    if (streamOn.value) { body.stream = true; body.stream_options = { include_usage: true } }
    const reply = { role: 'assistant', model, content: '', traceId, promptTokens: 0, completionTokens: 0 }
    messages.value.push(reply)
    round.push(reply)
    const live = messages.value[messages.value.length - 1]
    scrollBottom()
    const res = streamOn.value
      ? await routerStream('/v1/chat/completions', body, (_d, all) => { live.content = all; scrollBottom() }).catch(() => null)
      : await routerApi('/v1/chat/completions', { method: 'POST', body: JSON.stringify(body) }).catch(() => null)
    const usage = res?.usage || {}
    live.promptTokens = usage.prompt_tokens || 0
    live.completionTokens = usage.completion_tokens || 0
    live.durationMs = Date.now() - t0
    if (res && res.choices && res.choices[0]) {
      if (!streamOn.value) live.content = res.choices[0].message.content
    } else {
      live.content = '⚠ ' + (res && res.error ? res.error.message : (res?.message || '调用失败（router 未启动？）'))
    }
    scrollBottom()
  }
  sending.value = false
  saveRound(traceId, round, sid0)
  scrollBottom()
}

/* 空状态建议卡片一键发送 */
function quickSend(s) { draft.value = s; nextTick(() => { autoGrow(); send() }) }

/** Enter 发送：输入法组合期间（选词确认）不触发发送 */
function onEnter(e) {
  if (e.isComposing || e.keyCode === 229) return
  send()
}

function resetInput() { nextTick(() => { if (inputEl.value) { inputEl.value.style.height = 'auto' } }) }

function userContentOf(m) {
  return [{ type: 'text', text: m.content }, ...(m.images || []).map(u => ({ type: 'image_url', image_url: { url: u } }))]
}

/* ===== 多模态上传 ===== */
function onFiles(ev) {
  for (const f of ev.target.files || []) {
    if (!f.type.startsWith('image/')) continue
    const reader = new FileReader()
    reader.onload = () => pendingImages.value.push({ name: f.name, data: reader.result })
    reader.readAsDataURL(f)
  }
  ev.target.value = ''
}

/* ===== 特殊模式 ===== */
const TEMPLATES = {
  embedding: { model: '', input: ['在这里输入需要向量化的文本'] },
  rerank: { model: '', query: '查询语句', documents: ['文档一……', '文档二……', '文档三……'] },
  laya: { model: 'laya', state: '待判断的状态文本或结构化对象', questions: { q1: { type: 'choice', candidates: ['选项A', '选项B'] } } },
  nanojev: { model: 'nanojev', states: [{ state: '状态文本', questions: { q1: { type: 'boolean' } } }] }
}

function resetTemplate() {
  const m = specialModel.value
  if (!m) return
  const cat = m['jv-category'] || ''
  const tplKey = /向量|Embedding/i.test(cat) ? 'embedding'
    : /重排|Rerank/i.test(cat) ? 'rerank'
    : /nanojev/i.test(m.id) ? 'nanojev' : 'laya'
  const tpl = JSON.parse(JSON.stringify(TEMPLATES[tplKey]))
  tpl.model = m.id
  specialBody.value = JSON.stringify(tpl, null, 2)
  specialPath.value = specialPaths.value[0] || ''
}

async function sendSpecial() {
  if (!selSpecialModel.value || !specialPath.value) return
  if (!currentKey.value) { alert('请先点击输入框上方的钥匙图标，保存 API Key'); return }
  let body
  try { body = JSON.parse(specialBody.value) } catch (e) { alert('请求体不是合法 JSON：' + e.message); return }
  sending.value = true
  specialResp.value = ''
  if (streamOn.value) body.stream = true
  const res = streamOn.value
    ? await routerStream(specialPath.value, body).catch(() => null)
    : await routerApi(specialPath.value, { method: 'POST', body: JSON.stringify(body) }).catch(() => null)
  sending.value = false
  if (res === null) { specialResp.value = '请求失败（router 未启动？）'; specialStatus.value = 'ERROR'; return }
  specialStatus.value = res.error ? 'ERROR' : 'OK'
  specialResp.value = JSON.stringify(res, null, 2)
}

/* ===== 工具 ===== */
function scrollBottom() { nextTick(() => { if (msgsEl.value) msgsEl.value.scrollTop = msgsEl.value.scrollHeight }) }
</script>

<style>
/* ============================================================
   体验中心 · 聊天 UI（DeepSeek Platform 风格：白底 / 气泡 / 大输入框）
   ============================================================ */
.pg { height: calc(100vh - var(--header-h, 49px) - 24px); display: flex; flex-direction: column; }
.pg .page-header { flex-shrink: 0; }

/* ===== 模式 tabs ===== */
.mode-tabs { display: flex; gap: 6px; background: var(--bg-soft); padding: 3px; border-radius: 10px; }
.mode-tab {
  padding: 6px 14px; border: none; border-radius: 8px; background: transparent;
  font-size: 13px; color: var(--text-secondary); cursor: pointer; transition: all .15s;
}
.mode-tab:hover { color: var(--text-primary); }
.mode-tab.active { background: #fff; color: var(--text-primary); font-weight: 600; box-shadow: var(--shadow-xs); }

/* 流式开关 */
.stream-toggle {
  display: inline-flex; align-items: center; gap: 5px; flex-shrink: 0;
  font-size: 12.5px; color: var(--text-secondary); cursor: pointer; user-select: none;
  padding: 4px 10px; border: 1px solid var(--border); border-radius: 8px; background: #fff;
  transition: border-color .15s;
}
.stream-toggle:hover { border-color: var(--text-quaternary); }
.stream-toggle input { accent-color: var(--accent, #4d6bfe); cursor: pointer; }

/* ===== 布局 ===== */
.chat-layout { display: flex; gap: 12px; flex: 1; min-height: 0; }
.chat-side {
  width: 264px; flex-shrink: 0; display: flex; flex-direction: column;
  background: #fff; border: 1px solid var(--border); border-radius: var(--radius-lg);
  overflow-y: auto;
}
.chat-side-block { padding: 12px 12px 14px; }
.chat-side-block.bordered { border-top: 1px solid var(--border-light); }
.chat-main {
  flex: 1; min-width: 0; display: flex; flex-direction: column;
  background: #fff; border: 1px solid var(--border); border-radius: var(--radius-lg);
  overflow: hidden; position: relative;
}

/* ===== 配置面板触发按钮（输入框上方工具条内） ===== */
.key-fab {
  margin-left: auto; flex-shrink: 0;
  display: flex; align-items: center; gap: 6px; max-width: 180px;
  height: 32px; padding: 0 10px; border: 1px solid var(--border); border-radius: 999px;
  background: #fff; color: var(--text-secondary); font-size: 12px; cursor: pointer;
  transition: all .15s; box-shadow: var(--shadow-xs);
}
.key-fab:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-soft-2); }
.key-fab.ok { color: var(--success); }
.key-fab.open { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }
.key-fab svg { width: 14px; height: 14px; flex-shrink: 0; }
.key-fab-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

/* ===== 配置面板（fixed 锚定触发按钮，向上弹出） ===== */
.config-pop {
  position: fixed; z-index: 90;
  width: 320px; max-height: min(480px, 62vh); overflow-y: auto;
  background: #fff; border: 1px solid var(--border); border-radius: 12px;
  box-shadow: 0 12px 36px rgba(0,0,0,0.16); padding: 14px;
  transform-origin: bottom right;
}
.gw-pop-enter-active, .gw-pop-leave-active { transition: opacity .18s ease, transform .2s ease; }
.gw-pop-enter-from, .gw-pop-leave-to { opacity: 0; transform: translateY(10px) scale(.97); }
.key-drawer-head {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;
}
.config-pop .key-drawer-head { margin-bottom: 10px; }
.key-drawer-close {
  width: 26px; height: 26px; border: none; background: none; border-radius: 6px;
  color: var(--text-tertiary); cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.key-drawer-close:hover { background: var(--bg-soft); color: var(--text-primary); }
.key-drawer-close svg { width: 15px; height: 15px; }
.key-error {
  font-size: 12px; color: var(--danger, #e5484d); background: rgba(229,72,77,0.08);
  border: 1px solid rgba(229,72,77,0.25); border-radius: 8px; padding: 6px 10px; margin-bottom: 8px;
}
.drawer-section { padding-bottom: 12px; }
.drawer-section.bordered { border-top: 1px solid var(--border-light); padding-top: 12px; }
.drawer-section-title { font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px; }

/* ===== 左侧 ===== */
.new-chat-btn {
  display: flex; align-items: center; justify-content: center; gap: 7px; width: 100%;
  height: 34px; margin-bottom: 10px; border: 1px solid var(--border); border-radius: var(--radius);
  background: #fff; font-size: 13px; color: var(--text-primary); cursor: pointer;
  transition: background .15s, border-color .15s;
}
.new-chat-btn:hover { background: var(--bg-soft); border-color: var(--text-quaternary); }
.new-chat-btn svg { width: 14px; height: 14px; color: var(--accent); }
.session-list { max-height: none; flex: 1; min-height: 120px; overflow-y: auto; display: flex; flex-direction: column; gap: 2px; }
.session-item2 {
  display: flex; align-items: center; padding: 6px 8px; cursor: pointer;
  font-size: 12.5px; color: var(--text-secondary); border-radius: var(--radius-sm);
  transition: background .12s;
}
.session-item2:hover { background: var(--bg-soft); }
.session-item2:hover .session-del { opacity: 1; }
.session-item2.active { background: var(--accent-soft); color: var(--accent); font-weight: 500; }
.session-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.session-del { opacity: 0; color: var(--text-tertiary); padding: 2px; border-radius: 4px; transition: opacity .15s; flex-shrink: 0; display: flex; }
.session-del:hover { color: var(--danger); background: var(--danger-soft); }
.session-del svg { width: 12px; height: 12px; }
.side-empty { padding: 14px 0; font-size: 12px; color: var(--text-tertiary); text-align: center; }
.side-note { font-size: 11.5px; color: var(--text-tertiary); margin-top: 6px; line-height: 1.5; }
.side-title { font-size: 12px; font-weight: 600; color: var(--text-secondary); margin-bottom: 8px; }
.side-link { background: none; border: none; font-size: 12px; color: var(--text-tertiary); cursor: pointer; margin-top: 6px; padding: 0; }
.side-link:hover { color: var(--danger); }
.key-meta { margin-top: 8px; display: flex; flex-direction: column; gap: 4px; }
.key-meta-row { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; font-size: 11.5px; }
.key-limits { color: var(--text-tertiary); }
.key-meta-row.muted { color: var(--text-tertiary); }

/* ===== 输入框上方工具条：模型选择 + 流式 + 配置触发 ===== */
.input-toolbar {
  position: relative; display: flex; align-items: center; gap: 10px;
  margin-bottom: 10px;
}
/* 独立 class：避开全局 .model-picker 的 max-height / overflow 裁剪 */
.model-select { width: 300px; overflow: visible; max-height: none; }
.toolbar-hint { flex-shrink: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.chat-input .input-toolbar { margin-bottom: 10px; }

/* ===== 消息区 ===== */
.chat-msgs { flex: 1; min-height: 0; overflow-y: auto; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.chat-msg { display: flex; gap: 10px; max-width: 860px; }
.chat-msg.user { align-self: flex-end; flex-direction: row-reverse; max-width: 70%; }
.chat-msg.assistant { align-self: flex-start; }
.msg-avatar {
  width: 30px; height: 30px; flex-shrink: 0; border-radius: 8px;
  background: linear-gradient(135deg, #1A1A1A, #3A3A3A); color: #fff;
  font-size: 10px; font-weight: 700; display: flex; align-items: center; justify-content: center;
  margin-top: 2px;
}
.msg-col { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.chat-msg.user .msg-col { align-items: flex-end; }
.msg-meta { font-size: 11px; color: var(--text-tertiary); display: flex; align-items: center; gap: 6px; padding-left: 2px; }
.msg-stat { font-size: 10px; background: var(--bg-soft); border-radius: 4px; padding: 0 5px; }
.chat-bubble {
  padding: 10px 14px; border-radius: var(--radius-lg); font-size: 13.5px; line-height: 1.7;
  white-space: pre-wrap; word-break: break-word; box-shadow: var(--shadow-xs);
}
.chat-msg.user .chat-bubble { background: var(--accent); color: #fff; border-bottom-right-radius: 4px; }
.chat-msg.assistant .chat-bubble { background: #fff; border: 1px solid var(--border); color: var(--text-primary); border-top-left-radius: 4px; }
.msg-text { white-space: pre-wrap; }
.msg-img { max-width: 200px; border-radius: 8px; display: block; margin-bottom: 6px; border: 1px solid rgba(255,255,255,.3); }

/* ===== 空状态（欢迎 + 建议） ===== */
.chat-welcome { margin: auto; text-align: center; max-width: 560px; }
.welcome-badge {
  display: inline-block; padding: 5px 14px; margin-bottom: 16px; border-radius: 999px;
  background: var(--accent-soft); color: var(--accent); font-size: 12px; font-weight: 600; letter-spacing: 1px;
}
.chat-welcome h3 { font-size: 22px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px; }
.chat-welcome p { font-size: 13px; color: var(--text-secondary); margin-bottom: 22px; }
.suggest-row { display: flex; flex-direction: column; gap: 8px; }
.suggest-card {
  padding: 11px 16px; border: 1px solid var(--border); border-radius: var(--radius-md);
  background: #fff; font-size: 13px; color: var(--text-secondary); cursor: pointer; text-align: left;
  transition: all .15s;
}
.suggest-card:hover { border-color: var(--accent); color: var(--accent); background: var(--accent-soft-2); transform: translateY(-1px); box-shadow: var(--shadow-sm); }

/* ===== 输入区 ===== */
.chat-input { flex-shrink: 0; padding: 12px 16px 10px; border-top: 1px solid var(--border-light); background: #fff; }
.img-previews { display: flex; gap: 8px; margin-bottom: 8px; }
.img-chip { position: relative; width: 56px; height: 56px; border-radius: 8px; overflow: hidden; border: 1px solid var(--border); }
.img-chip img { width: 100%; height: 100%; object-fit: cover; }
.img-chip-del {
  position: absolute; right: 2px; top: 2px; width: 16px; height: 16px; border-radius: 50%;
  background: rgba(0,0,0,.55); color: #fff; border: none; font-size: 11px; line-height: 1; cursor: pointer;
}
.input-row {
  display: flex; align-items: flex-end; gap: 10px;
  border: 1px solid var(--border); border-radius: var(--radius-xl); background: var(--bg-page);
  padding: 8px 8px 8px 12px; transition: border-color .15s, box-shadow .15s;
}
.input-row:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); background: #fff; }
.upload-btn {
  display: flex; align-items: center; justify-content: center; width: 32px; height: 32px; flex-shrink: 0;
  border-radius: var(--radius); cursor: pointer; color: var(--text-tertiary); transition: all .15s;
}
.upload-btn:hover { background: var(--bg-soft); color: var(--accent); }
.upload-btn svg { width: 17px; height: 17px; }
.chat-textarea {
  flex: 1; border: none; outline: none; background: none; resize: none;
  font-size: 13.5px; line-height: 1.6; color: var(--text-primary);
  max-height: 160px; padding: 5px 0; font-family: inherit;
}
.chat-textarea::placeholder { color: var(--text-quaternary); }
.send-btn {
  width: 34px; height: 34px; flex-shrink: 0; border-radius: 50%; border: none;
  background: var(--primary); color: #fff; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: opacity .15s, background .15s;
}
.send-btn:hover { background: var(--primary-hover); }
.send-btn:disabled { opacity: .3; cursor: not-allowed; }
.send-btn svg { width: 15px; height: 15px; }
.spinner {
  width: 14px; height: 14px; border: 2px solid rgba(255,255,255,.3);
  border-top-color: #fff; border-radius: 50%; animation: gw-spin .7s linear infinite;
}
@keyframes gw-spin { to { transform: rotate(360deg); } }
.input-foot { text-align: center; font-size: 11px; color: var(--text-quaternary); margin-top: 6px; }

/* ===== 特殊模式：复用聊天模式的上下分区（响应在上、输入在下） ===== */
.special-wrap { display: flex; flex-direction: column; flex: 1; min-height: 0; }
.special-resp { flex: 1; min-height: 0; overflow-y: auto; padding: 20px 24px; display: flex; flex-direction: column; gap: 16px; }
.special-empty { padding-top: 24px; }
.special-resp-head { display: flex; align-items: center; gap: 8px; }
.special-json { margin: 0; font-family: ui-monospace, Menlo, monospace; font-size: 12px; white-space: pre-wrap; word-break: break-all; color: var(--text-primary); }
.special-input { flex-shrink: 0; padding: 12px 16px 10px; border-top: 1px solid var(--border-light); background: #fff; }
.special-wrap .input-toolbar { margin-bottom: 10px; }
.special-head { font-size: 13px; color: var(--text-secondary); margin-bottom: 8px; }
.special-head b { color: var(--text-primary); }
.special-head code { background: var(--bg-soft); padding: 1px 6px; border-radius: 4px; font-size: 12px; }
.special-editor {
  flex: 1; border: none; outline: none; background: none; resize: none;
  font-size: 12.5px; line-height: 1.6; color: var(--text-primary);
  min-height: 60px; max-height: 200px; padding: 5px 0; font-family: ui-monospace, Menlo, monospace;
}
.special-editor::placeholder { color: var(--text-quaternary); }

/* ===== 响应式 ===== */
@media (max-width: 960px) {
  .chat-layout { flex-direction: column; }
  .chat-side { width: 100%; max-height: 240px; }
  .model-select { width: 100%; }
  .topbar-hint, .toolbar-hint { display: none; }
  .chat-msg.user { max-width: 88%; }
}
</style>
