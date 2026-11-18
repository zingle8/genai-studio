<template>
  <div>
    <div class="page-header">
      <div><div class="page-title">运维中心</div><div class="page-subtitle">平台服务清单与健康探测（jv-genai-dashboard）</div></div>
      <div class="page-actions">
        <button class="btn btn-secondary" @click="checkAll" :disabled="checking">{{ checking ? '探测中…' : '一键探测' }}</button>
      </div>
    </div>
    <div class="card"><div class="card-body no-pad"><div class="table-wrap">
      <table>
        <thead><tr><th>服务 ID</th><th>服务名</th><th>模块</th><th>端口</th><th>健康状态</th><th>最近探测</th><th class="text-right">操作</th></tr></thead>
        <tbody>
          <tr v-for="s in list" :key="s.id">
            <td class="mono">{{ s.service_id }}</td>
            <td><b>{{ s.service_name }}</b></td>
            <td class="muted mono">{{ s.module }}</td>
            <td class="mono">{{ s.port }}</td>
            <td><span class="tag" :class="statusCls(s.status)">{{ statusText(s.status) }}</span></td>
            <td class="muted">{{ fmtTime(s.checked_at) }}</td>
            <td class="text-right"><span class="link" style="cursor:pointer;" @click="checkOne(s)">探测</span></td>
          </tr>
          <tr v-if="!list.length"><td colspan="7"><div class="empty" style="padding:48px 0;">暂无数据</div></td></tr>
        </tbody>
      </table>
    </div></div></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
const list = ref([]); const checking = ref(false)
onMounted(load)
async function load() {
  const res = await api('/api/ops/services')
  if (res.code === 0) list.value = res.data || []
}
async function checkOne(s) {
  const res = await api('/api/ops/services/' + s.id + '/check', { method: 'POST' })
  if (res.code === 0) s.status = res.data.status
  load()
}
async function checkAll() {
  checking.value = true
  for (const s of list.value) await checkOne(s)
  checking.value = false
}
function statusCls(s) { return s === 'up' ? 'tag-success' : s === 'down' ? 'tag-danger' : '' }
function statusText(s) { return s === 'up' ? '正常' : s === 'down' ? '异常' : '未知' }
function fmtTime(t) { return t ? String(t).replace('T', ' ').slice(0, 19) : '-' }
</script>
