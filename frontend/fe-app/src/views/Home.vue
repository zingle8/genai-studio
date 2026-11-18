<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">首页</div>
        <div class="page-subtitle">{{ todayText }} · {{ greetText }}，{{ user?.name || user?.username || '用户' }} 👋</div>
      </div>
      <div class="page-actions">
        <router-link class="btn btn-secondary" to="/fe-docs/api-docs">接口文档</router-link>
        <router-link class="btn btn-primary" to="/fe-chats/playground">打开体验中心 →</router-link>
      </div>
    </div>

    <!-- 核心指标 -->
    <div class="stat-grid">
      <div class="stat-card">
        <div>
          <div class="stat-label">总调用量（今日）</div>
          <div class="stat-value">{{ fmtNum(overview.today.requests) }}</div>
          <div class="stat-trend">{{ monthReqTrend }}</div>
        </div>
        <div class="stat-icon primary"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg></div>
      </div>
      <div class="stat-card">
        <div>
          <div class="stat-label">Token 消耗（本月）</div>
          <div class="stat-value">{{ fmtTokens(overview.month.tokens) }}</div>
          <div class="stat-trend">{{ fmtNum(overview.month.requests) }} 次请求</div>
        </div>
        <div class="stat-icon cyan"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7V4h16v3M9 20h6M12 4v16"/></svg></div>
      </div>
      <div class="stat-card">
        <div>
          <div class="stat-label">成本（本月）</div>
          <div class="stat-value">¥{{ fmtMoney(overview.month.cost) }}</div>
          <div class="stat-trend">今日 ¥{{ fmtMoney(overview.today.cost) }}</div>
        </div>
        <div class="stat-icon warning"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div>
      </div>
      <div class="stat-card">
        <div>
          <div class="stat-label">在线模型</div>
          <div class="stat-value">{{ modelTotal }} / {{ modelTotal }}</div>
          <div class="stat-trend up">▲ 服务健康运行中</div>
        </div>
        <div class="stat-icon success"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/></svg></div>
      </div>
    </div>

    <!-- 账户余额条 -->
    <div class="card mb-16">
      <div class="card-body home-balance">
        <div>
          <div class="stat-label">账户余额</div>
          <div class="stat-value" style="font-size:22px;">¥{{ fmtMoney(billing.balance) }}
            <span class="tag" :class="billing.balance < 50 ? 'tag-danger' : 'tag-success'" style="margin-left:4px;">{{ billing.balance < 50 ? '余额偏低' : '余额充足' }}</span>
          </div>
        </div>
        <div class="home-balance-item"><div class="stat-label">今日消费</div><b>¥{{ fmtMoney(billing.todayConsume) }}</b></div>
        <div class="home-balance-item"><div class="stat-label">本月消费</div><b>¥{{ fmtMoney(billing.monthConsume) }}</b></div>
        <div class="home-balance-item"><div class="stat-label">本月充值</div><b>¥{{ fmtMoney(billing.monthTopup) }}</b></div>
        <router-link class="btn btn-primary btn-sm" to="/fe-admin/billing">充值 / 账单 →</router-link>
      </div>
    </div>

    <!-- 趋势 + 快捷入口 -->
    <div class="dash-grid">
      <div>
        <div class="card mb-16">
          <div class="card-header"><div class="card-title">调用量趋势（近 14 天）</div><span class="text-sm muted">请求次数 / 成本</span></div>
          <div class="card-body">
            <svg v-if="daily.length" class="trend-svg" viewBox="0 0 560 180" preserveAspectRatio="none">
              <polygon :points="areaPoints" fill="rgba(77,107,254,0.12)"/>
              <polyline :points="linePoints" fill="none" stroke="#4D6BFE" stroke-width="2.5" stroke-linejoin="round"/>
              <g v-for="(d, i) in daily" :key="i">
                <circle :cx="x(i)" :cy="yReq(d.requests)" r="3.5" fill="#fff" stroke="#4D6BFE" stroke-width="2"/>
                <text :x="x(i)" :y="176" text-anchor="middle" class="trend-x">{{ d.statDate.slice(5) }}</text>
              </g>
            </svg>
            <div v-else class="text-sm muted" style="padding:30px; text-align:center;">暂无趋势数据</div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title">模型调用排行 TOP5（近 14 天）</div>
            <router-link class="text-sm" style="color:var(--primary); text-decoration:none;" to="/fe-dashboard/costs">成本统计 →</router-link>
          </div>
          <div class="table-wrap">
            <table>
              <thead><tr><th>模型</th><th>请求数</th><th>Token</th><th>成本</th><th>占比</th></tr></thead>
              <tbody>
                <tr v-for="m in topModels" :key="m.model">
                  <td><b>{{ m.model }}</b></td>
                  <td>{{ fmtNum(m.requests) }}</td>
                  <td>{{ fmtTokens(m.tokens) }}</td>
                  <td>¥{{ fmtMoney(m.cost) }}</td>
                  <td style="min-width:120px;">
                    <div class="ratio-bar"><i :style="{ width: ratioPct(m.cost) + '%' }"></i></div>
                    <span class="text-sm muted">{{ ratioPct(m.cost) }}%</span>
                  </td>
                </tr>
                <tr v-if="!topModels.length"><td colspan="5" class="text-sm muted" style="text-align:center;">暂无数据</td></tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div>
        <div class="card mb-16">
          <div class="card-header"><div class="card-title">成本分布（近 14 天）</div></div>
          <div class="card-body">
            <div v-for="m in topModels" :key="'d' + m.model" class="dist-row">
              <span class="dist-name">{{ m.model }}</span>
              <div class="ratio-bar"><i :style="{ width: ratioPct(m.cost) + '%', background: distColor(m.model) }"></i></div>
              <span class="dist-val">¥{{ fmtMoney(m.cost) }}</span>
            </div>
            <div v-if="!topModels.length" class="text-sm muted">暂无数据</div>
          </div>
        </div>

        <div class="card mb-16">
          <div class="card-header"><div class="card-title">快捷入口</div></div>
          <div class="card-body quick-grid">
            <router-link v-for="q in quicks" :key="q.to" :to="q.to" class="quick-item">
              <span class="quick-ico" v-html="q.icon"></span>
              <div><b class="text-sm">{{ q.title }}</b><div class="text-xs muted">{{ q.desc }}</div></div>
            </router-link>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <div class="card-title">最近请求</div>
            <router-link class="text-sm" style="color:var(--primary); text-decoration:none;" to="/fe-dashboard/usage-logs">全部日志 →</router-link>
          </div>
          <div class="card-body recent-list">
            <div v-for="l in recentLogs" :key="l.id" class="recent-row">
              <span class="tag" :class="l.status === 'success' ? 'tag-success' : 'tag-danger'">{{ l.status }}</span>
              <b class="text-sm">{{ l.model }}</b>
              <span class="text-xs muted">{{ l.serviceId }}</span>
              <span class="text-xs muted" style="margin-left:auto;">{{ fmtTokens(l.totalTokens) }} tok · ¥{{ fmtMoney(l.cost) }}</span>
            </div>
            <div v-if="!recentLogs.length" class="text-sm muted">暂无请求记录</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getUser } from '../api'

const user = getUser()

const overview = ref({ today: {}, month: {} })
const billing = ref({})
const modelTotal = ref(0)
const daily = ref([])
const topModels = ref([])
const recentLogs = ref([])

const fmtNum = n => Number(n || 0).toLocaleString('en-US')
const fmtMoney = n => Number(n || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
const fmtTokens = n => { n = Number(n || 0); return n >= 1000000 ? (n / 1000000).toFixed(1) + 'M' : n >= 1000 ? (n / 1000).toFixed(1) + 'K' : n }

const now = new Date()
const week = '日一二三四五六'[now.getDay()]
const todayText = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')} 星期${week}`
const greetText = now.getHours() < 6 ? '凌晨好' : now.getHours() < 12 ? '上午好' : now.getHours() < 14 ? '中午好' : now.getHours() < 18 ? '下午好' : '晚上好'
const monthReqTrend = computed(() => `本月累计 ${fmtNum(overview.value.month.requests)} 次`)

async function getJson(url) {
  try { const r = await fetch(url).then(res => res.json()); return r?.code === 0 ? r.data : null } catch { return null }
}

onMounted(async () => {
  const [ov, bl, md, dl, bm, lg] = await Promise.all([
    getJson('/api/costs/overview'),
    getJson('/api/billing/summary'),
    getJson('/api/models?size=1'),
    getJson('/api/costs/daily?days=14'),
    getJson('/api/costs/by-model?days=14'),
    getJson('/api/logs?size=5')
  ])
  if (ov) overview.value = ov
  if (bl) billing.value = bl
  if (md) modelTotal.value = Number(md.total ?? (Array.isArray(md) ? md.length : 0)) || 0
  if (dl) daily.value = [...dl].reverse() // 升序，便于折线从左到右
  if (bm) topModels.value = bm.slice(0, 5)
  if (lg) recentLogs.value = lg.list || []
})

/* 趋势图坐标（viewBox 560x180） */
const W = 560, H = 160, PAD = 24
const x = i => daily.value.length <= 1 ? W / 2 : PAD + (i * (W - PAD * 2)) / (daily.value.length - 1)
const maxReq = computed(() => Math.max(...daily.value.map(d => Number(d.requests) || 1), 1))
const yReq = v => H - (Number(v) / maxReq.value) * (H - 30) - 10
const linePoints = computed(() => daily.value.map((d, i) => `${x(i)},${yReq(d.requests)}`).join(' '))
const areaPoints = computed(() => daily.value.length ? `${PAD},${H} ${linePoints.value} ${x(daily.value.length - 1)},${H}` : '')

/* 成本占比 */
const totalCost = computed(() => topModels.value.reduce((s, m) => s + Number(m.cost || 0), 0) || 1)
const ratioPct = c => Math.round((Number(c || 0) / totalCost.value) * 1000) / 10
const DIST_COLORS = ['#4D6BFE', '#22C55E', '#F59E0B', '#06B6D4', '#A855F7']
const distColor = model => DIST_COLORS[topModels.value.findIndex(m => m.model === model) % DIST_COLORS.length]

const quicks = [
  { to: '/fe-admin/apikey', title: 'API Key', desc: '密钥创建与轮转', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="7.5" cy="15.5" r="4.5"/><path d="M11 12l9-9m-3 3 2.5 2.5M15 9l2 2"/></svg>' },
  { to: '/fe-chats/playground', title: '体验中心', desc: '在线对话调试', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a8 8 0 0 1-8 8H4l2-3a8 8 0 1 1 15-5z"/></svg>' },
  { to: '/fe-admin/billing', title: '账单充值', desc: '余额与消费明细', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/></svg>' },
  { to: '/fe-docs/api-docs', title: '接口文档', desc: 'API 接入手册', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V2H6.5A2.5 2.5 0 0 0 4 4.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/></svg>' },
  { to: '/fe-dashboard/costs', title: '成本统计', desc: '按日/按模型分析', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v18h18"/><path d="M7 14l4-4 4 3 5-6"/></svg>' },
  { to: '/fe-models/models', title: '模型广场', desc: '可用模型一览', icon: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/></svg>' }
]
</script>

<style>
/* ===== 首页（对齐 demo index.html 布局） ===== */
.page-actions { display: flex; gap: 10px; align-items: center; }
.stat-card { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.stat-icon { width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-icon svg { width: 20px; height: 20px; }
.stat-icon.primary { background: rgba(77,107,254,0.12); color: #4D6BFE; }
.stat-icon.success { background: rgba(34,197,94,0.12); color: #22C55E; }
.stat-icon.warning { background: rgba(245,158,11,0.14); color: #F59E0B; }
.stat-icon.cyan { background: rgba(6,182,212,0.12); color: #06B6D4; }

.home-balance { display: flex; gap: 36px; align-items: center; flex-wrap: wrap; }
.home-balance-item .stat-label { margin-bottom: 4px; }

.dash-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 16px; align-items: start; }
@media (max-width: 1100px) { .dash-grid { grid-template-columns: 1fr; } }

.trend-svg { width: 100%; height: 180px; }
.trend-x { font-size: 10px; fill: var(--text-tertiary); }

.ratio-bar { display: inline-block; vertical-align: middle; width: 84px; height: 7px; border-radius: 4px; background: var(--border-light); overflow: hidden; margin-right: 6px; }
.ratio-bar i { display: block; height: 100%; border-radius: 4px; background: #4D6BFE; }
.dist-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; }
.dist-name { font-size: 12.5px; min-width: 108px; }
.dist-row .ratio-bar { flex: 1; width: auto; margin: 0; }
.dist-val { font-size: 12px; color: var(--text-secondary); min-width: 64px; text-align: right; }

.quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.quick-item { display: flex; gap: 10px; align-items: center; padding: 10px; border: 1px solid var(--border-light); border-radius: 10px; text-decoration: none; color: inherit; transition: border-color 0.15s, box-shadow 0.15s; }
.quick-item:hover { border-color: #4D6BFE; box-shadow: 0 2px 10px rgba(77,107,254,0.12); }
.quick-ico { width: 34px; height: 34px; border-radius: 9px; background: rgba(77,107,254,0.1); color: #4D6BFE; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.quick-ico svg { width: 17px; height: 17px; }

.recent-list { display: flex; flex-direction: column; gap: 4px; }
.recent-row { display: flex; align-items: center; gap: 8px; padding: 6px 0; }
</style>
