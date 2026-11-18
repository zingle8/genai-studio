/** 统一请求封装（qiankun 环境下直连后端端口，独立访问走 vite 代理） */
const IS_QK = true  // 后端已开 CORS，统一直连后端端口（独立/嵌入环境均可用）
const BASES = {
  '/api/kb': IS_QK ? 'http://localhost:38126' : '',
  '/api/rag': IS_QK ? 'http://localhost:38109' : '',
  '/api/ocr': IS_QK ? 'http://localhost:38128' : ''
}
export function withBase(path) {
  for (const p in BASES) if (path.startsWith(p)) return BASES[p] + path
  return path
}
export async function api(path, options = {}) {
  const token = localStorage.getItem('genai_token') || ''
  const res = await fetch(withBase(path), {
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: token } : {}) },
    ...options
  })
  return res.json()
}
export function getUser() {
  try { return JSON.parse(localStorage.getItem('genai_user') || 'null') } catch { return null }
}
