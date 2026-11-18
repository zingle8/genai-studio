<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">接口文档</div>
        <div class="page-subtitle">平台开放 API 清单（jv-genai-docs）</div>
      </div>
    </div>
    <div class="card" v-for="(items, mod) in grouped" :key="mod" style="margin-bottom:16px;">
      <div class="card-header"><b>{{ mod }}</b></div>
      <div class="card-body no-pad"><div class="table-wrap">
        <table>
          <thead><tr><th style="width:90px;">方法</th><th>路径</th><th>说明</th></tr></thead>
          <tbody>
            <tr v-for="d in items" :key="d.id">
              <td><span class="tag" :class="methodCls(d.method)">{{ d.method }}</span></td>
              <td class="mono">{{ d.path }}</td>
              <td class="muted">{{ d.description }}</td>
            </tr>
          </tbody>
        </table>
      </div></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
const list = ref([])
onMounted(async () => { const res = await api('/api/docs'); if (res.code === 0) list.value = res.data || [] })
const grouped = computed(() => {
  const g = {}
  for (const d of list.value) (g[d.module] = g[d.module] || []).push(d)
  return g
})
function methodCls(m) {
  return { GET: 'tag-success', POST: 'tag-accent', PUT: 'tag-warning', DELETE: 'tag-danger' }[m] || ''
}
</script>
