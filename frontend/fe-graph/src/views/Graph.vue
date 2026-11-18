<template>
  <div class="page-header">
    <div><div class="page-title">知识图谱</div><div class="page-subtitle">图谱（数据库概念）/ 实体类型 / 节点·属性·关系 / 版本（自动快照·可恢复）</div></div>
    <div class="page-actions">
      <button class="btn btn-ghost" @click="graphOpen = true">＋ 新建图谱</button>
      <template v-if="curGraph">
        <button class="btn btn-ghost" @click="entityOpen = true">＋ 实体类型</button>
        <button class="btn btn-ghost" @click="nodeOpen = true">＋ 节点</button>
        <button class="btn btn-primary" @click="edgeOpen = true">＋ 关系</button>
      </template>
    </div>
  </div>

  <div class="graph-layout">
    <!-- 左：图谱列表（数据库概念） -->
    <div class="card graph-side-left"><div class="card-body no-pad">
      <div style="padding:10px 14px; border-bottom:1px solid var(--border-light);"><b class="text-sm">图谱库</b></div>
      <div class="side-row" v-for="g in graphs" :key="g.id" :class="{ active: curGraph?.id === g.id }" style="cursor:pointer;" @click="pickGraph(g)">
        <span class="db-icon" :class="g.db_type === 'neo4j' ? 'neo' : ''">{{ g.db_type === 'neo4j' ? 'N4' : 'SQL' }}</span>
        <div style="flex:1;">
          <b class="text-sm">{{ g.name }}</b>
          <div class="text-xs muted">{{ g.nodeCount }} 节点 · v{{ g.versionCount }}</div>
        </div>
        <span v-if="g.db_type === 'neo4j'" class="dot-mini" :class="g.dbOk ? 'green' : 'red'" :title="g.dbOk ? 'Neo4j 已连接' : 'Neo4j 连接失败'"></span>
        <button class="btn btn-ghost btn-sm" @click.stop="delGraph(g)">删</button>
      </div>
      <div v-if="!graphs.length" class="text-center muted text-sm" style="padding:20px;">暂无图谱</div>
    </div></div>

    <template v-if="curGraph">
      <!-- 主区：tab -->
      <div style="flex:1; min-width:0; display:flex; flex-direction:column; gap:12px;">
        <div class="mode-tabs">
          <button class="mode-tab" :class="{ active: tab === 'view' }" @click="tab = 'view'">图视图</button>
          <button class="mode-tab" :class="{ active: tab === 'entities' }" @click="tab = 'entities'">实体类型</button>
          <button class="mode-tab" :class="{ active: tab === 'nodes' }" @click="tab = 'nodes'">节点与属性</button>
          <button class="mode-tab" :class="{ active: tab === 'edges' }" @click="tab = 'edges'">关系</button>
          <button class="mode-tab" :class="{ active: tab === 'versions' }" @click="tab = 'versions'; loadVersions()">版本</button>
        </div>

        <!-- 图视图 -->
        <div class="card" v-if="tab === 'view'"><div class="card-body">
          <div class="row-head" style="margin-bottom:8px;">
            <b>{{ curGraph.name }}</b><span class="text-xs muted">{{ nodes.length }} 节点 · {{ edges.length }} 关系 · {{ curGraph.db_type === 'neo4j' ? 'Neo4j' : '内置存储' }}</span>
            <span style="flex:1"></span>
            <select class="form-input" v-model="focusId" style="width:170px;" @change="loadGraph">
              <option value="">全图</option>
              <option v-for="n in nodes" :key="n.id" :value="n.id">{{ n.name }} 邻域</option>
            </select>
            <select class="form-input" v-model="depth" style="width:90px;" @change="focusId && loadGraph()">
              <option :value="1">1 层</option><option :value="2">2 层</option><option :value="3">3 层</option>
            </select>
          </div>
          <svg class="graph-svg" viewBox="0 0 900 560">
            <g v-for="e in edges" :key="'e' + e.id">
              <line :x1="pos(e.source_id).x + 32" :y1="pos(e.source_id).y + 18" :x2="pos(e.target_id).x + 32" :y2="pos(e.target_id).y + 18" class="edge-line" />
              <text :x="(pos(e.source_id).x + pos(e.target_id).x) / 2 + 32" :y="(pos(e.source_id).y + pos(e.target_id).y) / 2 + 12" class="edge-label">{{ e.rel_type }}</text>
            </g>
            <g v-for="n in nodes" :key="'n' + n.id" style="cursor:pointer;">
              <rect :x="pos(n.id).x" :y="pos(n.id).y" width="64" height="36" rx="8" class="node-box" />
              <text :x="pos(n.id).x + 32" :y="pos(n.id).y + 23" class="node-name">{{ n.name.length > 6 ? n.name.slice(0, 6) : n.name }}</text>
            </g>
          </svg>
        </div></div>

        <!-- 实体类型 -->
        <div class="card" v-if="tab === 'entities'"><div class="card-body">
          <div class="table-wrap"><table>
            <thead><tr><th>实体类型</th><th>属性定义</th><th class="text-right">操作</th></tr></thead>
            <tbody>
              <tr v-for="e in entities" :key="e.id">
                <td><b>{{ e.name }}</b></td>
                <td class="text-xs muted">{{ propsSchemaText(e.props_schema) }}</td>
                <td class="text-right">
                  <button class="btn btn-ghost btn-sm" @click="editEntity(e)">改</button>
                  <button class="btn btn-ghost btn-sm" @click="delEntity(e)">删</button>
                </td>
              </tr>
              <tr v-if="!entities.length"><td colspan="3" class="text-center muted">暂无实体类型（如：部门/员工/项目）</td></tr>
            </tbody>
          </table></div>
        </div></div>

        <!-- 节点与属性 -->
        <div class="card" v-if="tab === 'nodes'"><div class="card-body">
          <div class="table-wrap"><table>
            <thead><tr><th>节点</th><th>实体类型</th><th>属性</th><th class="text-right">操作</th></tr></thead>
            <tbody>
              <tr v-for="n in nodes" :key="n.id">
                <td><b>{{ n.name }}</b></td>
                <td class="text-xs">{{ entityName(n.entity_id) }}</td>
                <td class="text-xs muted" style="max-width:320px;">{{ n.props && n.props !== '{}' ? n.props : '—' }}</td>
                <td class="text-right">
                  <button class="btn btn-ghost btn-sm" @click="editNode(n)">改</button>
                  <button class="btn btn-ghost btn-sm" @click="delNode(n)">删</button>
                </td>
              </tr>
              <tr v-if="!nodes.length"><td colspan="4" class="text-center muted">暂无节点</td></tr>
            </tbody>
          </table></div>
        </div></div>

        <!-- 关系 -->
        <div class="card" v-if="tab === 'edges'"><div class="card-body">
          <div class="table-wrap"><table>
            <thead><tr><th>起点</th><th>关系</th><th>终点</th><th class="text-right">操作</th></tr></thead>
            <tbody>
              <tr v-for="e in edges" :key="e.id">
                <td>{{ e.sourceName }}</td>
                <td><span class="tag" style="font-size:11px;">{{ e.rel_type }}</span></td>
                <td>{{ e.targetName }}</td>
                <td class="text-right">
                  <button class="btn btn-ghost btn-sm" @click="editEdge(e)" v-if="curGraph.db_type !== 'neo4j'">改</button>
                  <button class="btn btn-ghost btn-sm" @click="delEdge(e)">删</button>
                </td>
              </tr>
              <tr v-if="!edges.length"><td colspan="4" class="text-center muted">暂无关系</td></tr>
            </tbody>
          </table></div>
        </div></div>

        <!-- 版本 -->
        <div class="card" v-if="tab === 'versions'"><div class="card-body">
          <div class="text-xs muted" style="margin-bottom:8px;">每次新增/更新/删除操作自动生成版本快照；可查看指定版本内容，并一键恢复</div>
          <div class="table-wrap"><table>
            <thead><tr><th>版本</th><th>操作</th><th>备注</th><th>时间</th><th class="text-right">操作</th></tr></thead>
            <tbody>
              <tr v-for="v in versions" :key="v.version_no">
                <td><b>v{{ v.version_no }}</b></td>
                <td><span class="tag" style="font-size:11px;">{{ v.op }}</span></td>
                <td class="text-xs muted">{{ v.note || '—' }}</td>
                <td class="text-xs muted">{{ v.created_at }}</td>
                <td class="text-right">
                  <button class="btn btn-ghost btn-sm" @click="viewVersion(v)">内容</button>
                  <button class="btn btn-ghost btn-sm" @click="restoreVersion(v)">恢复此版本</button>
                </td>
              </tr>
              <tr v-if="!versions.length"><td colspan="5" class="text-center muted">暂无版本</td></tr>
            </tbody>
          </table></div>
        </div></div>
      </div>
    </template>
    <div v-else class="card" style="flex:1;"><div class="card-body text-center muted" style="padding:60px 0;">左侧选择图谱，或新建（可选 Neo4j 后端）</div></div>
  </div>

  <!-- 新建/编辑图谱 -->
  <div class="modal-mask" v-if="graphOpen" @click.self="graphOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">新建图谱</div><button class="modal-close" @click="graphOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">图谱名</label><input class="form-input" v-model="graphForm.name" /></div>
        <div class="form-row"><label class="form-label">存储后端</label>
          <select class="form-input" v-model="graphForm.db_type">
            <option value="sqlite">内置存储（SQLite）</option>
            <option value="neo4j">Neo4j（图数据库）</option>
          </select></div>
        <template v-if="graphForm.db_type === 'neo4j'">
          <div class="form-row"><label class="form-label">Neo4j HTTP 地址</label><input class="form-input" v-model="n4cfg.uri" placeholder="http://localhost:7474" /></div>
          <div class="form-row"><label class="form-label">用户 / 密码</label>
            <div class="row-head" style="flex:1; gap:6px;">
              <input class="form-input" v-model="n4cfg.user" placeholder="neo4j" style="flex:1;" />
              <input class="form-input" type="password" v-model="n4cfg.password" placeholder="密码" style="flex:1;" />
            </div></div>
        </template>
        <div class="form-row"><label class="form-label">描述</label><input class="form-input" v-model="graphForm.description" /></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="graphOpen = false">取消</button><button class="btn btn-primary" @click="saveGraph">创建</button></div>
    </div>
  </div>

  <!-- 实体类型 -->
  <div class="modal-mask" v-if="entityOpen" @click.self="entityOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">{{ entityForm.id ? '编辑实体类型' : '新建实体类型' }}</div><button class="modal-close" @click="entityOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">类型名</label><input class="form-input" v-model="entityForm.name" placeholder="如 部门 / 员工" /></div>
        <div class="form-row"><label class="form-label">属性定义（JSON 数组）</label>
          <textarea class="form-input" v-model="entityForm.props_schema" rows="4" placeholder='[{"name":"负责人","type":"string"},{"name":"人数","type":"number"}]'></textarea></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="entityOpen = false">取消</button><button class="btn btn-primary" @click="saveEntity">保存</button></div>
    </div>
  </div>

  <!-- 节点 -->
  <div class="modal-mask" v-if="nodeOpen" @click.self="nodeOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">{{ nodeForm.id ? '编辑节点' : '新建节点' }}</div><button class="modal-close" @click="nodeOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">实体类型</label>
          <select class="form-input" v-model="nodeForm.entity_id"><option :value="0">— 无类型 —</option><option v-for="e in entities" :key="e.id" :value="e.id">{{ e.name }}</option></select></div>
        <div class="form-row"><label class="form-label">节点名</label><input class="form-input" v-model="nodeForm.name" /></div>
        <div class="form-row"><label class="form-label">属性（JSON 对象）</label>
          <textarea class="form-input" v-model="nodeForm.props" rows="4" placeholder='{"负责人":"张三"}'></textarea></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="nodeOpen = false">取消</button><button class="btn btn-primary" @click="saveNode">保存</button></div>
    </div>
  </div>

  <!-- 关系 -->
  <div class="modal-mask" v-if="edgeOpen" @click.self="edgeOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">{{ edgeForm.id ? '编辑关系' : '新建关系' }}</div><button class="modal-close" @click="edgeOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">起点</label>
          <select class="form-input" v-model="edgeForm.source_id"><option v-for="n in nodes" :key="n.id" :value="n.id">{{ n.name }}</option></select></div>
        <div class="form-row"><label class="form-label">关系类型</label><input class="form-input" v-model="edgeForm.rel_type" placeholder="works_in / join_project" /></div>
        <div class="form-row"><label class="form-label">终点</label>
          <select class="form-input" v-model="edgeForm.target_id"><option v-for="n in nodes" :key="n.id" :value="n.id">{{ n.name }}</option></select></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="edgeOpen = false">取消</button><button class="btn btn-primary" @click="saveEdge">保存</button></div>
    </div>
  </div>

  <!-- 版本内容 -->
  <div class="modal-mask" v-if="verDetail" @click.self="verDetail = null">
    <div class="modal modal-lg">
      <div class="modal-header"><div class="modal-title">v{{ verDetail.version_no }} 快照（{{ verDetail.op }} · {{ verDetail.created_at }}）</div><button class="modal-close" @click="verDetail = null">×</button></div>
      <div class="modal-body">
        <div class="text-sm" style="margin-bottom:8px;">实体 {{ verDetail.snapshot.entities.length }} · 节点 {{ verDetail.snapshot.nodes.length }} · 关系 {{ verDetail.snapshot.edges.length }}</div>
        <pre class="ver-pre">{{ JSON.stringify(verDetail.snapshot, null, 2).slice(0, 3000) }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api, withBase } from '../api'
const graphs = ref([]); const curGraph = ref(null); const tab = ref('view')
const entities = ref([]); const nodes = ref([]); const edges = ref([]); const versions = ref([])
const focusId = ref(''); const depth = ref(1)
const graphOpen = ref(false); const graphForm = ref({ name: '', db_type: 'sqlite', description: '' }); const n4cfg = ref({})
const entityOpen = ref(false); const entityForm = ref({ id: null, name: '', props_schema: '[]' })
const nodeOpen = ref(false); const nodeForm = ref({ id: null, entity_id: 0, name: '', props: '{}' })
const edgeOpen = ref(false); const edgeForm = ref({ id: null, source_id: '', rel_type: '', target_id: '' })
const verDetail = ref(null)
onMounted(loadGraphs)

async function loadGraphs() {
  const r = await api(withBase('/api/graphs'))
  if (r.code === 0) graphs.value = r.data
}
function pickGraph(g) {
  curGraph.value = g
  entities.value = []; nodes.value = []; edges.value = []
  loadGraph()
}
async function loadGraph() {
  if (!curGraph.value) return
  const gid = curGraph.value.id
  const path = focusId.value
    ? withBase(`/api/graphs/${gid}/neighborhood?nid=${focusId.value}&depth=${depth.value}`)
    : withBase(`/api/graphs/${gid}/nodes`)
  const r = await api(path)
  if (r.code === 0) {
    nodes.value = r.data.nodes
    if (r.data.entities) entities.value = r.data.entities
  }
  const re = await api(withBase(`/api/graphs/${gid}/edges`))
  if (re.code === 0) edges.value = re.data
  const rn = await api(withBase(`/api/graphs/${gid}/entities`))
  if (rn.code === 0) entities.value = rn.data
}
async function loadVersions() {
  const r = await api(withBase(`/api/graphs/${curGraph.value.id}/versions`))
  if (r.code === 0) versions.value = r.data
}

function pos(id) {
  const list = nodes.value
  const i = list.findIndex(n => n.id === id)
  if (i < 0) return { x: 20, y: 20 }
  if (list.length === 1) return { x: 400, y: 250 }
  const cx = 440, cy = 268, r = Math.min(210, 90 + list.length * 14)
  const a = (i / list.length) * Math.PI * 2 - Math.PI / 2
  return { x: cx + r * Math.cos(a), y: cy + r * Math.sin(a) }
}
function entityName(eid) { const e = entities.value.find(x => x.id === eid); return e ? e.name : '—' }
function propsSchemaText(s) {
  try { const a = JSON.parse(s || '[]'); return a.length ? a.map(x => x.name + ':' + x.type).join('、') : '（无属性定义）' } catch { return '—' }
}

async function saveGraph() {
  const body = { ...graphForm.value, db_config: graphForm.value.db_type === 'neo4j' ? JSON.stringify(n4cfg.value) : '' }
  const r = await api(withBase('/api/graphs'), { method: 'POST', body: JSON.stringify(body) })
  if (r.code === 0) { graphOpen.value = false; graphForm.value = { name: '', db_type: 'sqlite', description: '' }; loadGraphs(); curGraph.value = r.data; loadGraph() }
  else alert(r.detail || '失败（Neo4j 连接失败请检查地址/凭据）')
}
async function delGraph(g) {
  if (!confirm(`删除图谱「${g.name}」及其全部数据${g.db_type === 'neo4j' ? '（含 Neo4j 节点）' : ''}？`)) return
  await api(withBase('/api/graphs/' + g.id), { method: 'DELETE' })
  if (curGraph.value?.id === g.id) curGraph.value = null
  loadGraphs()
}
function editEntity(e) { entityForm.value = { id: e.id, name: e.name, props_schema: e.props_schema || '[]' }; entityOpen.value = true }
async function saveEntity() {
  const body = JSON.stringify({ name: entityForm.value.name, props_schema: entityForm.value.props_schema })
  const r = entityForm.value.id
    ? await api(withBase(`/api/graphs/${curGraph.value.id}/entities/${entityForm.value.id}`), { method: 'PUT', body })
    : await api(withBase(`/api/graphs/${curGraph.value.id}/entities`), { method: 'POST', body })
  if (r.code === 0) { entityOpen.value = false; entityForm.value = { id: null, name: '', props_schema: '[]' }; loadGraph() } else alert(r.detail || '失败')
}
async function delEntity(e) {
  if (!confirm(`删除实体类型「${e.name}」？`)) return
  await api(withBase(`/api/graphs/${curGraph.value.id}/entities/${e.id}`), { method: 'DELETE' })
  loadGraph()
}
function editNode(n) { nodeForm.value = { id: n.id, entity_id: n.entity_id || 0, name: n.name, props: n.props || '{}' }; nodeOpen.value = true }
async function saveNode() {
  const body = JSON.stringify({ entity_id: nodeForm.value.entity_id, name: nodeForm.value.name, props: nodeForm.value.props })
  const r = nodeForm.value.id
    ? await api(withBase(`/api/graphs/${curGraph.value.id}/nodes/${nodeForm.value.id}`), { method: 'PUT', body })
    : await api(withBase(`/api/graphs/${curGraph.value.id}/nodes`), { method: 'POST', body })
  if (r.code === 0) { nodeOpen.value = false; loadGraph(); loadGraphs() } else alert(r.detail || '失败')
}
async function delNode(n) {
  if (!confirm(`删除节点「${n.name}」及其关系？`)) return
  await api(withBase(`/api/graphs/${curGraph.value.id}/nodes/${n.id}`), { method: 'DELETE' })
  loadGraph(); loadGraphs()
}
function editEdge(e) { edgeForm.value = { id: e.id, source_id: e.source_id, rel_type: e.rel_type, target_id: e.target_id }; edgeOpen.value = true }
async function saveEdge() {
  const body = JSON.stringify({ source_id: edgeForm.value.source_id, rel_type: edgeForm.value.rel_type, target_id: edgeForm.value.target_id, props: '{}' })
  const r = edgeForm.value.id
    ? await api(withBase(`/api/graphs/${curGraph.value.id}/edges/${edgeForm.value.id}`), { method: 'PUT', body })
    : await api(withBase(`/api/graphs/${curGraph.value.id}/edges`), { method: 'POST', body })
  if (r.code === 0) { edgeOpen.value = false; loadGraph() } else alert(r.detail || '失败')
}
async function delEdge(e) {
  await api(withBase(`/api/graphs/${curGraph.value.id}/edges/${e.id}`), { method: 'DELETE' })
  loadGraph()
}
async function viewVersion(v) {
  const r = await api(withBase(`/api/graphs/${curGraph.value.id}/versions/${v.version_no}`))
  if (r.code === 0) verDetail.value = r.data
}
async function restoreVersion(v) {
  if (!confirm(`恢复到 v${v.version_no}？当前数据会先自动保存为新版本。`)) return
  const r = await api(withBase(`/api/graphs/${curGraph.value.id}/versions/${v.version_no}/restore`), { method: 'POST' })
  if (r.code === 0) { loadGraph(); loadGraphs(); loadVersions() } else alert(r.detail || '失败')
}
</script>

<style>
.graph-layout { display: flex; gap: 12px; flex: 1; min-height: 0; align-items: flex-start; }
.graph-side-left { width: 220px; flex-shrink: 0; overflow-y: auto; max-height: 620px; }
.side-row { display: flex; align-items: center; gap: 8px; padding: 10px 14px; border-bottom: 1px solid var(--border-light); }
.side-row.active { background: var(--bg-soft); }
.db-icon { width: 30px; height: 22px; border-radius: 5px; background: #6b7280; color: #fff; font-size: 10px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.db-icon.neo { background: #018bff; }
.dot-mini { display: inline-block; width: 8px; height: 8px; border-radius: 50%; }
.dot-mini.green { background: #22c55e; }
.dot-mini.red { background: #ef4444; }
.graph-svg { width: 100%; height: 560px; background: var(--bg-soft); border-radius: 10px; }
.node-box { fill: #fff; stroke: #4d6bfe; stroke-width: 1.5; }
.node-name { text-anchor: middle; font-size: 13px; fill: #1f2430; font-weight: 600; pointer-events: none; }
.edge-line { stroke: #b9c2d4; stroke-width: 1.5; }
.edge-label { text-anchor: middle; font-size: 11px; fill: #6b7280; }
.row-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.ver-pre { background: var(--bg-soft); border: 1px solid var(--border-light); border-radius: 8px; padding: 12px; font-size: 12px; max-height: 50vh; overflow: auto; line-height: 1.5; }
.modal { min-width: 440px; }
</style>
