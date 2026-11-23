<template>
  <div>
    <div class="page-header">
      <div>
        <div class="page-title">账单中心</div>
        <div class="page-subtitle">余额 / 充值 / 消费账单（jv-genai-billing）</div>
      </div>
      <div class="page-actions">
        <button class="btn btn-primary" @click="topupOpen = true">充值</button>
      </div>
    </div>

    <div class="stat-grid">
      <div class="stat-card">
        <div>
          <div class="stat-label">账户余额</div>
          <div class="stat-value">¥{{ summary.balance != null ? summary.balance : '-' }}</div>
          <div v-if="Number(summary.balance) < 50" class="tag tag-danger">余额偏低</div>
        </div>
      </div>
      <div class="stat-card"><div><div class="stat-label">本月消费</div><div class="stat-value">¥{{ summary.monthConsume != null ? summary.monthConsume : '-' }}</div></div></div>
      <div class="stat-card"><div><div class="stat-label">本月充值</div><div class="stat-value">¥{{ summary.monthTopup != null ? summary.monthTopup : '-' }}</div></div></div>
      <div class="stat-card"><div><div class="stat-label">今日消费</div><div class="stat-value">¥{{ summary.todayConsume != null ? summary.todayConsume : '-' }}</div></div></div>
    </div>

    <div class="filter-bar">
      <div class="segmented">
        <div class="seg" :class="{ active: type === '' }" @click="setType('')">全部</div>
        <div class="seg" :class="{ active: type === 'topup' }" @click="setType('topup')">充值</div>
        <div class="seg" :class="{ active: type === 'consume' }" @click="setType('consume')">消费</div>
      </div>
      <div class="spacer"></div>
      <span class="text-sm muted">共 {{ total }} 条</span>
    </div>

    <div class="card">
      <div class="card-body no-pad">
        <div class="table-wrap">
          <table>
            <thead><tr><th>订单号</th><th>类型</th><th>金额</th><th>交易后余额</th><th>渠道</th><th>时间</th><th>备注</th></tr></thead>
            <tbody>
              <tr v-for="o in orders" :key="o.id">
                <td class="mono">{{ o.orderNo }}</td>
                <td><span class="tag" :class="o.type === 'topup' ? 'tag-success' : ''">{{ o.type === 'topup' ? '充值' : '消费' }}</span></td>
                <td :style="{ color: o.type === 'topup' ? 'var(--success)' : 'var(--danger)' }">{{ o.type === 'topup' ? '+' : '-' }}¥{{ o.amount }}</td>
                <td class="mono">¥{{ o.balanceAfter }}</td>
                <td class="muted">{{ o.channel }}</td>
                <td class="muted">{{ fmtTime(o.createdAt) }}</td>
                <td class="muted">{{ o.remark }}</td>
              </tr>
              <tr v-if="!orders.length"><td colspan="7"><div class="empty" style="padding:48px 0;">暂无数据</div></td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- 分页：每页条数 + 上一页 / 下一页 -->
    <div class="pager">
      <span class="text-sm muted">共 {{ total }} 条 · 第 {{ page }} / {{ totalPages }} 页</span>
      <div class="pager-ctrl">
        <select class="form-select" style="width:110px;" :value="size" @change="changeSize($event.target.value)">
          <option v-for="s in [10, 20, 50, 100]" :key="s" :value="s">{{ s }} 条/页</option>
        </select>
        <button class="btn btn-secondary btn-sm" :disabled="page <= 1" @click="changePage(page - 1)">上一页</button>
        <button class="btn btn-secondary btn-sm" :disabled="page >= totalPages" @click="changePage(page + 1)">下一页</button>
      </div>
    </div>

    <div v-if="topupOpen" class="modal-mask show" style="display:flex" @click.self="topupOpen = false">
      <div class="modal">
        <div class="modal-header">
          <div class="modal-title">账户充值</div>
          <button class="modal-close" @click="topupOpen = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-row">
            <label class="form-label">充值金额（元）<span class="required">*</span></label>
            <input class="form-input" type="number" min="1" v-model="amount" placeholder="如 100" />
          </div>
          <div class="form-row" style="margin-bottom:0;">
            <label class="form-label">支付渠道</label>
            <select class="form-select" v-model="channel">
              <option value="alipay">支付宝</option>
              <option value="wechat">微信支付</option>
              <option value="bank_card">银行卡</option>
              <option value="balance">对公转账</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="topupOpen = false">取消</button>
          <button class="btn btn-primary" @click="doTopup">确认充值</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

const summary = ref({})
const orders = ref([])
const total = ref(0)
const type = ref('')
const page = ref(1)
const size = ref(10)
const topupOpen = ref(false)
const amount = ref('')
const channel = ref('balance')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / size.value)))

onMounted(() => { loadSummary(); loadOrders() })

async function loadSummary() {
  const res = await api('/api/billing/summary')
  if (res.code === 0) summary.value = res.data
}
async function loadOrders() {
  const res = await api('/api/billing/orders?type=' + type.value + '&page=' + page.value + '&size=' + size.value)
  if (res.code === 0) { orders.value = res.data.list || []; total.value = res.data.total || 0 }
}
function setType(t) { type.value = t; page.value = 1; loadOrders() }
function changePage(p) { page.value = Math.min(Math.max(p, 1), totalPages.value); loadOrders() }
function changeSize(v) { size.value = Number(v); page.value = 1; loadOrders() }
async function doTopup() {
  const n = Number(amount.value)
  if (!n || n <= 0) { alert('请输入有效的充值金额'); return }
  const res = await api('/api/billing/topup', { method: 'POST', body: JSON.stringify({ amount: n, channel: channel.value }) })
  if (res.code === 0) { topupOpen.value = false; amount.value = ''; loadSummary(); loadOrders() }
  else alert(res.message || '充值失败')
}
function fmtTime(s) { return s ? String(s).replace('T', ' ').slice(0, 19) : '' }
</script>

<style>
/* 分页条 */
.pager {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  margin-top: 12px;
}
.pager-ctrl { display: flex; align-items: center; gap: 8px; }
.pager-ctrl .btn:disabled { opacity: 0.45; cursor: not-allowed; }
</style>
