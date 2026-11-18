<template>
  <div>
    <div class="page-header">
      <div><div class="page-title">用户管理</div><div class="page-subtitle">账号体系复用网关平台 jv-api-gateway-user（/users）</div></div>
      <div class="page-actions"><button class="btn btn-secondary" @click="load">刷新</button></div>
    </div>
    <div class="card"><div class="card-body no-pad"><div class="table-wrap">
      <table>
        <thead><tr><th>ID</th><th>用户名</th><th>昵称</th><th>邮箱</th><th>手机号</th><th>状态</th><th>创建时间</th></tr></thead>
        <tbody>
          <tr v-for="u in list" :key="u.id">
            <td class="mono">{{ u.id }}</td>
            <td><b>{{ u.username }}</b></td>
            <td>{{ u.nickname || u.nickName || '-' }}</td>
            <td class="muted">{{ u.email || '-' }}</td>
            <td class="muted">{{ u.phone || '-' }}</td>
            <td><span class="tag" :class="String(u.status) === '0' || u.status === 'DISABLED' ? 'tag-danger' : 'tag-success'">{{ fmtStatus(u.status) }}</span></td>
            <td class="muted">{{ fmtTime(u.createdAt || u.createTime) }}</td>
          </tr>
          <tr v-if="!list.length"><td colspan="7"><div class="empty" style="padding:48px 0;">{{ emptyTip }}</div></td></tr>
        </tbody>
      </table>
    </div></div></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
const list = ref([]); const emptyTip = ref('暂无数据')
onMounted(load)
async function load() {
  const res = await api('/api/users')
  if (res.code === 0) {
    const d = res.data
    list.value = Array.isArray(d) ? d : (d.list || d.records || d.content || [])
    if (!list.value.length) emptyTip.value = '网关返回为空或结构待适配（响应结构见控制台）'
  } else {
    emptyTip.value = '加载失败：' + (res.message || '')
  }
  console.log('[users] 网关响应：', res)
}
function fmtStatus(s) { return String(s) === '0' || s === 'DISABLED' ? '禁用' : '正常' }
function fmtTime(t) { return t ? String(t).replace('T', ' ').slice(0, 19) : '-' }
</script>
