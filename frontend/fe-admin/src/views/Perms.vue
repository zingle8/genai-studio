<template>
  <div>
    <div class="page-header">
      <div><div class="page-title">权限管理</div><div class="page-subtitle">权限组与字典复用网关平台（/perm/groups、/perm/dictionary）</div></div>
      <div class="page-actions"><button class="btn btn-secondary" @click="load">刷新</button></div>
    </div>
    <div class="card" style="margin-bottom:16px;">
      <div class="card-header"><b>权限组</b></div>
      <div class="card-body no-pad"><div class="table-wrap">
        <table>
          <thead><tr><th>ID</th><th>名称</th><th>编码</th><th>描述</th></tr></thead>
          <tbody>
            <tr v-for="g in groups" :key="g.id">
              <td class="mono">{{ g.id }}</td>
              <td><b>{{ g.name || g.groupName }}</b></td>
              <td class="mono">{{ g.code || g.groupCode || '-' }}</td>
              <td class="muted">{{ g.description || g.remark || '-' }}</td>
            </tr>
            <tr v-if="!groups.length"><td colspan="4"><div class="empty" style="padding:32px 0;">{{ groupsTip }}</div></td></tr>
          </tbody>
        </table>
      </div></div>
    </div>
    <div class="card">
      <div class="card-header"><b>字典</b></div>
      <div class="card-body no-pad"><div class="table-wrap">
        <table>
          <thead><tr><th>类型</th><th>键</th><th>值</th></tr></thead>
          <tbody>
            <tr v-for="(d, i) in dicts" :key="i">
              <td>{{ d.type || d.dictType || '-' }}</td>
              <td class="mono">{{ d.key || d.dictKey || '-' }}</td>
              <td class="muted">{{ d.value || d.dictValue || '-' }}</td>
            </tr>
            <tr v-if="!dicts.length"><td colspan="3"><div class="empty" style="padding:32px 0;">{{ dictsTip }}</div></td></tr>
          </tbody>
        </table>
      </div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'
const groups = ref([]); const dicts = ref([])
const groupsTip = ref('加载中…'); const dictsTip = ref('加载中…')
onMounted(load)
function pickList(d) {
  if (Array.isArray(d)) return d
  return d?.list || d?.records || d?.content || []
}
async function load() {
  const g = await api('/api/perms/groups')
  if (g.code === 0) { groups.value = pickList(g.data); if (!groups.value.length) groupsTip.value = '网关返回为空或结构待适配' }
  else groupsTip.value = '加载失败：' + (g.message || '')
  const d = await api('/api/perms/dictionary')
  if (d.code === 0) { dicts.value = pickList(d.data); if (!dicts.value.length) dictsTip.value = '网关返回为空或结构待适配' }
  else dictsTip.value = '加载失败：' + (d.message || '')
  console.log('[perms] groups:', g, 'dictionary:', d)
}
</script>
