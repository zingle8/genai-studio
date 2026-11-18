<template>
  <div class="page-header">
    <div><div class="page-title">知识图谱</div><div class="page-subtitle">实体关系管理 / 可视化 / 邻域查询（py-genai-graph）</div></div>
    <div class="page-actions">
      <button class="btn btn-ghost" @click="nodeOpen = true">＋ 节点</button>
      <button class="btn btn-primary" @click="edgeOpen = true">＋ 关系</button>
    </div>
  </div>

  <div class="graph-layout">
    <!-- 左：图可视化 -->
    <div class="card" style="flex:1; min-width:0;"><div class="card-body">
      <div class="row-head" style="margin-bottom:8px;">
        <b>图视图</b><span class="text-xs muted">{{ nodes.length }} 节点 · {{ edges.length }} 关系</span>
        <span style="flex:1"></span>
        <select class="form-input" v-model="focusId" style="width:170px;" @change="loadGraph">
          <option value="">全图</option>
          <option v-for="n in nodes" :key="n.id" :value="n.id">{{ n.name }}（{{ n.label }}）邻域</option>
        </select>
        <select class="form-input" v-model="depth" style="width:100px;" @change="focusId && loadGraph()">
          <option :value="1">1 层</option><option :value="2">2 层</option><option :value="3">3 层</option>
        </select>
      </div>
      <svg class="graph-svg" :viewBox="`0 0 900 560`">
        <g v-for="e in viewEdges" :key="'e' + e.id">
          <line :x1="pos(e.source_id).x + 32" :y1="pos(e.source_id).y + 18" :x2="pos(e.target_id).x + 32" :y2="pos(e.target_id).y + 18"
                class="edge-line" @click="editEdge(e)" />
          <text :x="(pos(e.source_id).x + pos(e.target_id).x) / 2 + 32" :y="(pos(e.source_id).y + pos(e.target_id).y) / 2 + 12"
                class="edge-label" @click="editEdge(e)">{{ e.rel_type }}</text>
        </g>
        <g v-for="n in viewNodes" :key="'n' + n.id" @click="focusId = n.id; loadGraph()" style="cursor:pointer;">
          <rect :x="pos(n.id).x" :y="pos(n.id).y" width="64" height="36" rx="8"
                class="node-box" :class="'lb-' + safeLabel(n.label)" />
          <text :x="pos(n.id).x + 32" :y="pos(n.id).y + 23" class="node-name">{{ n.name.length > 6 ? n.name.slice(0, 6) : n.name }}</text>
        </g>
      </svg>
      <div class="legend">
        <span v-for="l in labels" :key="l" class="legend-item"><span class="legend-dot" :class="'lb-' + safeLabel(l)"></span>{{ l }}</span>
      </div>
    </div></div>

    <!-- 右：节点/关系管理 -->
    <div class="graph-side">
      <div class="card"><div class="card-body no-pad">
        <div style="padding:12px 14px; border-bottom:1px solid var(--border-light);" class="row-head"><b>节点</b>
          <span style="flex:1"></span><input class="form-input" v-model="q" placeholder="搜索" style="width:120px;" @input="loadGraph" /></div>
        <div class="side-list">
          <div class="side-row" v-for="n in nodes" :key="n.id">
            <span class="legend-dot" :class="'lb-' + safeLabel(n.label)"></span>
            <div style="flex:1;"><b class="text-sm">{{ n.name }}</b><div class="text-xs muted">{{ n.label }}</div></div>
            <button class="btn btn-ghost btn-sm" @click="editNode(n)">改</button>
            <button class="btn btn-ghost btn-sm" @click="delNode(n)">删</button>
          </div>
        </div>
      </div></div>
      <div class="card"><div class="card-body no-pad">
        <div style="padding:12px 14px; border-bottom:1px solid var(--border-light);"><b>关系</b></div>
        <div class="side-list">
          <div class="side-row" v-for="e in edges" :key="e.id">
            <div style="flex:1;" class="text-sm">{{ e.sourceName }} <span class="tag" style="font-size:11px;">{{ e.rel_type }}</span> {{ e.targetName }}</div>
            <button class="btn btn-ghost btn-sm" @click="editEdge(e)">改</button>
            <button class="btn btn-ghost btn-sm" @click="delEdge(e)">删</button>
          </div>
        </div>
      </div></div>
    </div>
  </div>

  <!-- 节点编辑 -->
  <div class="modal-mask" v-if="nodeOpen" @click.self="nodeOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">{{ nodeForm.id ? '编辑节点' : '新建节点' }}</div><button class="modal-close" @click="nodeOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">类型（label）</label><input class="form-input" v-model="nodeForm.label" placeholder="如 部门/员工/项目" /></div>
        <div class="form-row"><label class="form-label">名称</label><input class="form-input" v-model="nodeForm.name" /></div>
        <div class="form-row"><label class="form-label">属性（可选 JSON）</label><input class="form-input" v-model="nodeForm.props" placeholder='{"title":"工程师"}' /></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="nodeOpen = false">取消</button><button class="btn btn-primary" @click="saveNode">保存</button></div>
    </div>
  </div>

  <!-- 关系编辑 -->
  <div class="modal-mask" v-if="edgeOpen" @click.self="edgeOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">{{ edgeForm.id ? '编辑关系' : '新建关系' }}</div><button class="modal-close" @click="edgeOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">起点</label>
          <select class="form-input" v-model="edgeForm.source_id"><option v-for="n in nodes" :key="n.id" :value="n.id">{{ n.name }}（{{ n.label }}）</option></select></div>
        <div class="form-row"><label class="form-label">关系类型</label><input class="form-input" v-model="edgeForm.rel_type" placeholder="如 works_in / join_project" /></div>
        <div class="form-row"><label class="form-label">终点</label>
          <select class="form-input" v-model="edgeForm.target_id"><option v-for="n in nodes" :key="n.id" :value="n.id">{{ n.name }}（{{ n.label }}）</option></select></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="edgeOpen = false">取消</button><button class="btn btn-primary" @click="saveEdge">保存</button></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api, withBase } from '../api'
const nodes = ref([]); const edges = ref([]); const labels = ref([])
const q = ref(''); const focusId = ref(''); const depth = ref(1)
const nodeOpen = ref(false); const nodeForm = ref({ id: null, label: '', name: '', props: '' })
const edgeOpen = ref(false); const edgeForm = ref({ id: null, source_id: '', rel_type: '', target_id: '' })
onMounted(loadGraph)

async function loadGraph() {
  const path = focusId.value
    ? `/api/graph/neighborhood?nid=${focusId.value}&depth=${depth.value}`
    : '/api/graph/view'
  const r = await api(withBase(path))
  if (r.code !== 0) return
  nodes.value = r.data.nodes
  edges.value = r.data.edges?.length ? r.data.edges : (r.data.edges === undefined ? edges.value : r.data.edges)
  if (r.data.labels) labels.value = r.data.labels
  if (!focusId.value && r.data.edges) edges.value = r.data.edges
  // 邻域接口只返回子图边，节点/关系管理区仍拉全量
  const all = await api(withBase('/api/graph/edges'))
  if (all.code === 0) edges.value = all.data
  const nl = await api(withBase('/api/graph/nodes' + (q.value ? '?q=' + encodeURIComponent(q.value) : '')))
  if (nl.code === 0) nodes.value = nl.data
}
const viewNodes = computed(() => nodes.value)
const viewEdges = computed(() => edges.value)

// 圆形布局
function pos(id) {
  const list = nodes.value
  const i = list.findIndex(n => n.id === id)
  if (i < 0) return { x: 20, y: 20 }
  if (list.length === 1) return { x: 400, y: 250 }
  const cx = 440, cy = 268, r = Math.min(210, 90 + list.length * 14)
  const a = (i / list.length) * Math.PI * 2 - Math.PI / 2
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) }
}
function safeLabel(l) { return String(l || 'x').replace(/\W/g, '') }

function editNode(n) { nodeForm.value = { id: n.id, label: n.label, name: n.name, props: n.props || '' }; nodeOpen.value = true }
async function saveNode() {
  const body = JSON.stringify({ label: nodeForm.value.label, name: nodeForm.value.name, props: nodeForm.value.props })
  const r = nodeForm.value.id
    ? await api(withBase('/api/graph/nodes/' + nodeForm.value.id), { method: 'PUT', body })
    : await api(withBase('/api/graph/nodes'), { method: 'POST', body })
  if (r.code === 0) { nodeOpen.value = false; loadGraph() } else alert(r.detail || '失败')
}
async function delNode(n) {
  if (!confirm(`删除节点「${n.name}」及其全部关系？`)) return
  await api(withBase('/api/graph/nodes/' + n.id), { method: 'DELETE' }); loadGraph()
}
function editEdge(e) { edgeForm.value = { id: e.id, source_id: e.source_id, rel_type: e.rel_type, target_id: e.target_id }; edgeOpen.value = true }
async function saveEdge() {
  const body = JSON.stringify({ source_id: edgeForm.value.source_id, rel_type: edgeForm.value.rel_type, target_id: edgeForm.value.target_id, props: '' })
  const r = edgeForm.value.id
    ? await api(withBase('/api/graph/edges/' + edgeForm.value.id), { method: 'PUT', body })
    : await api(withBase('/api/graph/edges'), { method: 'POST', body })
  if (r.code === 0) { edgeOpen.value = false; loadGraph() } else alert(r.detail || '失败')
}
async function delEdge(e) { await api(withBase('/api/graph/edges/' + e.id), { method: 'DELETE' }); loadGraph() }
</script>

<style>
.graph-layout { display: flex; gap: 12px; flex: 1; min-height: 0; align-items: flex-start; }
.graph-side { width: 280px; flex-shrink: 0; display: flex; flex-direction: column; gap: 12px; max-height: 620px; }
.side-list { max-height: 240px; overflow-y: auto; }
.side-row { display: flex; align-items: center; gap: 8px; padding: 8px 14px; border-bottom: 1px solid var(--border-light); }
.graph-svg { width: 100%; height: 560px; background: var(--bg-soft); border-radius: 10px; }
.node-box { fill: #fff; stroke: #4d6bfe; stroke-width: 1.5; }
.node-name { text-anchor: middle; font-size: 13px; fill: #1f2430; font-weight: 600; pointer-events: none; }
.edge-line { stroke: #b9c2d4; stroke-width: 1.5; cursor: pointer; }
.edge-line:hover { stroke: #4d6bfe; }
.edge-label { text-anchor: middle; font-size: 11px; fill: #6b7280; cursor: pointer; }
.legend { display: flex; gap: 14px; margin-top: 8px; flex-wrap: wrap; }
.legend-item { font-size: 12px; color: var(--text-secondary); display: inline-flex; align-items: center; gap: 5px; }
.legend-dot { width: 10px; height: 10px; border-radius: 3px; display: inline-block; background: #4d6bfe; }
.lb-公司 { background: #4d6bfe; } .node-box.lb-公司 { stroke: #4d6bfe; fill: #eef2ff; }
.lb-部门 { background: #22c55e; } .node-box.lb-部门 { stroke: #22c55e; fill: #f0fdf4; }
.lb-员工 { background: #f59e0b; } .node-box.lb-员工 { stroke: #f59e0b; fill: #fffbeb; }
.lb-项目 { background: #a855f7; } .node-box.lb-项目 { stroke: #a855f7; fill: #faf5ff; }
.row-head { display: flex; align-items: center; gap: 10px; }
.modal { min-width: 420px; }
</style>
