
/** qiankun 环境直连后端（独立访问走 vite 代理） */
const IS_QK = true  // 后端已开 CORS，统一直连后端端口
const GBASES = { '/api/graph': IS_QK ? 'http://localhost:38137' : '' }
export function withBase(path) {
  for (const p in GBASES) if (path.startsWith(p)) return GBASES[p] + path
  return path
}
/** 统一请求封装 */
export async function api(path, options = {}) {
  const token = localStorage.getItem('genai_token') || ''
  // 对象 body 自动序列化（字符串 body 保持原样，兼容已手动 JSON.stringify 的调用）
  const opts = options.body && typeof options.body === 'object' && !(options.body instanceof FormData)
    ? { ...options, body: JSON.stringify(options.body) }
    : options
  const res = await fetch(path, {
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: token } : {}) },
    ...opts
  })
  return res.json()
}
export function getUser() {
  try { return JSON.parse(localStorage.getItem('genai_user') || 'null') } catch { return null }
}
