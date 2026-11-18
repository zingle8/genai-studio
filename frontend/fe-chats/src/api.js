/** 统一请求封装 */
export async function api(path, options = {}) {
  const token = localStorage.getItem('genai_token') || ''
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: token } : {}) },
    ...options
  })
  return res.json()
}
export function getUser() {
  try { return JSON.parse(localStorage.getItem('genai_user') || 'null') } catch { return null }
}

/**
 * 模型路由统一调用封装（jv-genai-router，OpenAI 兼容）
 * 自动注入平台 API Key（localStorage.genai_model_api_key，管理面 ApiKey 页创建后复制）。
 * 平台内所有直连模型的调用（对话/向量/重排等）统一走此封装，避免 401。
 */
export const ROUTER_BASE = '' // 走 vite 代理 /v1 → http://localhost:38100（避免浏览器 CORS）

/** 流式调用（SSE）：逐帧回调 onDelta(增量, 累计)，返回聚合后的 OpenAI 兼容结构 */
export async function routerStream(path, body, onDelta) {
  const key = getModelApiKey()
  const headers = { 'Content-Type': 'application/json' }
  if (key) headers['Authorization'] = key.startsWith('Bearer ') ? key : 'Bearer ' + key
  const res = await fetch(ROUTER_BASE + path, { headers, method: 'POST', body: JSON.stringify(body) })
  if (!res.ok || !res.body) {
    const err = await res.json().catch(() => ({}))
    return { code: res.status, error: err.error || { message: err.message || '模型调用失败' } }
  }
  const reader = res.body.getReader()
  const dec = new TextDecoder()
  let buf = '', content = '', usage = null, finish = null, model = body.model || ''
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += dec.decode(value, { stream: true })
    const lines = buf.split('\n')
    buf = lines.pop()
    for (const line of lines) {
      const s = line.trim()
      if (!s.startsWith('data:')) continue
      const data = s.slice(5).trim()
      if (!data || data === '[DONE]') continue
      try {
        const j = JSON.parse(data)
        if (j.usage) usage = j.usage
        if (j.model) model = j.model
        const ch = j.choices && j.choices[0]
        if (ch) {
          if (ch.finish_reason) finish = ch.finish_reason
          const delta = (ch.delta && ch.delta.content) || (ch.message && ch.message.content) || ''
          if (delta) { content += delta; if (onDelta) onDelta(delta, content) }
        }
      } catch (e) { /* 跳过不完整帧 */ }
    }
  }
  return { model, choices: [{ message: { role: 'assistant', content }, finish_reason: finish || 'stop' }], usage: usage || {}, _stream: true }
}

export function getModelApiKey() {
  return localStorage.getItem('genai_model_api_key') || ''
}

export async function routerApi(path, options = {}) {
  const key = getModelApiKey()
  const headers = { 'Content-Type': 'application/json' }
  if (key) headers['Authorization'] = key.startsWith('Bearer ') ? key : 'Bearer ' + key
  const res = await fetch(ROUTER_BASE + path, { headers, ...options })
  const body = await res.json().catch(() => ({}))
  if (!res.ok && body.error) return { code: res.status, message: body.error.message || '模型调用失败' }
  return body
}
