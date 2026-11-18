
/** qiankun 环境直连后端（独立访问走 vite 代理） */
const IS_QK = true  // 后端已开 CORS，统一直连后端端口
const GBASES = { '/api/graph': IS_QK ? 'http://localhost:38117' : '' }
export function withBase(path) {
  for (const p in GBASES) if (path.startsWith(p)) return GBASES[p] + path
  return path
}
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
