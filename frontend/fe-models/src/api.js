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
