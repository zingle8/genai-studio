<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">成本统计</div>
        <div class="page-subtitle">成本归集查询（jv-genai-costs · 数据来源 usage_log T+1 聚合）</div>
      </div>
      <div class="page-actions">
        <div class="date-filter">
          <input class="form-input date-input" type="date" v-model="from" :max="today" />
          <span class="date-sep">至</span>
          <input class="form-input date-input" type="date" v-model="to" :max="today" />
          <button class="btn btn-primary btn-sm" @click="applyRange">查询统计</button>
          <button v-for="q in quickRanges" :key="q.label" class="btn btn-secondary btn-sm" :class="{ active: quickActive === q.label }" @click="applyQuick(q)">{{ q.label }}</button>
        </div>
      </div>
    </div>

    <!-- 区间统计 -->
    <div class="stat-grid">
      <div class="stat-card"><div><div class="stat-label">区间成本</div><div class="stat-value">¥{{ num(summary.cost) }}</div><div class="stat-trend">{{ summary.from }} ~ {{ summary.to }}</div></div></div>
      <div class="stat-card"><div><div class="stat-label">区间请求</div><div class="stat-value">{{ fmtNum(summary.requests) }}</div><div class="stat-trend">覆盖 {{ summary.activeDays || 0 }} 个有效天</div></div></div>
      <div class="stat-card"><div><div class="stat-label">区间 Token</div><div class="stat-value">{{ fmtNum(summary.tokens) }}</div><div class="stat-trend">日均 ¥{{ avgDaily }}</div></div></div>
      <div class="stat-card"><div><div class="stat-label">今日成本</div><div class="stat-value">¥{{ num(today.cost) }}</div><div class="stat-trend">{{ num(today.requests) }} 次调用</div></div></div>
    </div>

    <div class="card mb-16">
      <div class="card-header"><b>按日成本趋势（{{ summary.from }} ~ {{ summary.to }}）</b></div>
      <div class="card-body">
        <div v-if="daily.length" class="bars">
          <div v-for="d in daily" :key="d.statDate" class="bar-item" :title="d.statDate + ' ¥' + d.cost + ' · ' + d.requests + ' 次'">
            <div class="bar" :style="{ height: barHeight(d.cost) }"></div>
            <div class="bar-label">{{ String(d.statDate).slice(5) }}</div>
          </div>
        </div>
        <div v-else class="empty">所选区间暂无数据</div>
      </div>
    </div>

    <div class="card">
      <div class="card-header"><b>按模型成本分布（{{ summary.from }} ~ {{ summary.to }}）</b></div>
      <div class="card-body no-pad">
        <div class="table-wrap">
          <table>
            <thead><tr><th>模型</th><th>成本</th><th>请求次数</th><th>Token</th><th>占比</th></tr></thead>
            <tbody>
              <tr v-for="m in byModel" :key="m.model">
                <td><b>{{ m.model }}</b></td>
                <td class="mono">¥{{ m.cost }}</td>
                <td class="muted">{{ m.requests }}</td>
                <td class="muted">{{ fmtNum(m.tokens) }}</td>
                <td style="min-width:160px;">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <div style="flex:1; height:6px; background:var(--bg-soft); border-radius:3px; overflow:hidden;">
                      <div :style="{ width: pct(m.cost) + '%', height: '100%', background: 'var(--accent)' }"></div>
                    </div>
                    <span class="text-sm muted">{{ pct(m.cost) }}%</span>
                  </div>
                </td>
              </tr>
              <tr v-if="!byModel.length"><td colspan="5"><div class="empty" style="padding:48px 0;">所选区间暂无数据</div></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

const today = new Date().toISOString().slice(0, 10)
const from = ref(addDays(today, -29))
const to = ref(today)
const quickActive = ref('近30天')
const todayStat = ref({})
const summary = ref({ from: from.value, to: to.value })
const daily = ref([])
const byModel = ref([])
const maxCost = computed(() => Math.max(0.01, ...daily.value.map(d => Number(d.cost))))
const totalCost = computed(() => byModel.value.reduce((s, m) => s + Number(m.cost), 0) || 1)
const avgDaily = computed(() => {
  const d = Number(summary.value.activeDays) || 0
  return d ? (Number(summary.value.cost) / d).toFixed(2) : '0.00'
})

const quickRanges = [
  { label: '近7天', days: 6 }, { label: '近30天', days: 29 },
  { label: '近90天', days: 89 }, { label: '本月', month: true }
]

function addDays(dateStr, n) {
  const d = new Date(dateStr + 'T00:00:00')
  d.setDate(d.getDate() + n)
  return d.toISOString().slice(0, 10)
}

function applyQuick(q) {
  quickActive.value = q.label
  to.value = today
  from.value = q.month ? today.slice(0, 8) + '01' : addDays(today, -q.days)
  load()
}

function applyRange() {
  if (!from.value || !to.value) return
  if (from.value > to.value) { alert('开始日期不能晚于结束日期'); return }
  quickActive.value = ''
  load()
}

onMounted(load)

async function load() {
  summary.value = { from: from.value, to: to.value, cost: 0, requests: 0, tokens: 0, activeDays: 0 }
  const qs = 'from=' + from.value + '&to=' + to.value
  const [ov, sm, dl, bm] = await Promise.all([
    api('/api/costs/overview'),
    api('/api/costs/summary?' + qs),
    api('/api/costs/daily?' + qs),
    api('/api/costs/by-model?' + qs)
  ])
  if (ov.code === 0) todayStat.value = ov.data.today || {}
  if (sm.code === 0) summary.value = { ...summary.value, ...sm.data }
  if (dl.code === 0) daily.value = dl.data || []
  if (bm.code === 0) byModel.value = bm.data || []
}

function barHeight(cost) { return Math.max(4, Math.round(Number(cost) / maxCost.value * 120)) + 'px' }
function pct(cost) { return (Number(cost) / totalCost.value * 100).toFixed(1) }
function num(v) { return v == null ? '0.00' : Number(v).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }
function fmtNum(n) {
  n = Number(n) || 0
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return String(n)
}
</script>

<style>
.bars { display: flex; align-items: flex-end; gap: 8px; height: 160px; padding: 8px 4px 0; }
.bar-item { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 6px; height: 100%; justify-content: flex-end; }
.bar { width: 100%; max-width: 42px; background: linear-gradient(180deg, var(--accent), #7B8FF8); border-radius: 4px 4px 0 0; }
.bar-label { font-size: 10.5px; color: var(--text-tertiary); white-space: nowrap; }
.card-header { padding: 14px 20px; border-bottom: 1px solid var(--border-light); }

/* 日期筛选 */
.date-filter { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.date-input { width: 138px; padding: 7px 10px; font-size: 13px; }
.date-sep { color: var(--text-tertiary); font-size: 13px; }
.date-filter .btn.active { border-color: var(--accent); color: var(--accent); font-weight: 600; }
</style>
