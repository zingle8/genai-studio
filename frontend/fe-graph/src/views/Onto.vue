<template>
  <div class="onto-page">
    <div class="page-header">
      <div>
        <div class="page-title">本体图谱 Onto</div>
        <div class="page-subtitle">在唯一一份数据上定义多领域/个人本体视图 · 节点关系图 / 文本双模式 · 一致性检查防重复与冲突</div>
      </div>
      <div class="header-actions">
        <select class="form-select" v-model="dsId" style="width:180px;" @change="loadGraphData">
          <option v-for="d in datasources" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
        <button class="btn btn-primary" @click="openNewOnto">＋ 新建本体</button>
      </div>
    </div>

    <div class="onto-layout">
      <aside class="onto-side card">
        <div class="side-tabs">
          <button :class="{on: scopeFilter==='all'}" @click="scopeFilter='all'">全部</button>
          <button :class="{on: scopeFilter==='domain'}" @click="scopeFilter='domain'">领域</button>
          <button :class="{on: scopeFilter==='personal'}" @click="scopeFilter==='personal'">个人</button>
        </div>
        <div class="onto-list">
          <div v-for="o in filteredOntos" :key="o.id" class="onto-item" :class="{on: cur?.id===o.id}" @click="selectOnto(o)">
            <div class="onto-name"><span class="scope-dot" :class="o.scope"></span>{{ o.name }}</div>
            <div class="text-xs muted">{{ o.scope==='domain' ? '领域' : '个人' }} · {{ o.authority==='high' ? '高权威' : '普通' }} · {{ o.class_count }} 类 / {{ o.rel_count }} 规则</div>
          </div>
          <div v-if="!filteredOntos.length" class="empty" style="padding:32px 0;">暂无本体，点击右上角新建</div>
        </div>
      </aside>

      <section class="onto-main" v-if="cur">
        <div class="onto-toolbar">
          <div class="onto-cur"><b>{{ cur.name }}</b><span class="text-xs muted" style="margin-left:8px;">ns: {{ cur.namespace || '-' }}</span></div>
          <div class="tab-btns">
            <button :class="{on: tab==='graph'}" @click="tab='graph'">关系节点图</button>
            <button :class="{on: tab==='text'}" @click="tab='text'">文本定义</button>
            <button :class="{on: tab==='check'}" @click="tab='check'">一致性检查</button>
            <button :class="{on: tab==='data'}" @click="tab='data'">数据映射</button>
          </div>
          <button class="btn btn-secondary btn-sm" @click="delOnto">删除本体</button>
        </div>

        <div v-show="tab==='graph'" class="panel">
          <div class="svg-wrap">
            <svg :viewBox="svgBox" width="100%" height="100%">
              <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="26" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs>
              <g v-for="e in graphEdges" :key="'e'+e.id">
                <path :d="e.path" fill="none" stroke="#cbd5e1" stroke-width="1.8" marker-end="url(#arr)" style="cursor:pointer" @click="selEdge=e; selNode=null"/>
                <text :x="e.mx" :y="e.my" text-anchor="middle" class="edge-label" @click="selEdge=e; selNode=null">
                  {{ e.name }} · {{ e.cardinality==='one' ? (e.nullable ? '0..1' : '1..1') : 'N:M' }}{{ e.nullable ? '' : ' 必' }}
                </text>
              </g>
              <g v-for="n in nodes" :key="'n'+n.id">
                <rect :x="n.x-52" :y="n.y-22" width="104" height="44" rx="10" class="node-rect" :class="{sel: selNode?.id===n.id}" @click="selNode=n; selEdge=null"/>
                <text :x="n.x" :y="n.y+1" text-anchor="middle" class="node-name">{{ n.name }}</text>
                <text v-if="n.parent_name" :x="n.x" :y="n.y+14" text-anchor="middle" class="node-sub">⊂ {{ n.parent_name }}</text>
              </g>
            </svg>
            <div class="svg-hint">点击节点/边在右侧编辑 · "必" = 不允许为空</div>
          </div>

          <div class="edit-col">
            <button class="btn btn-secondary btn-sm full" @click="newClassOpen=!newClassOpen">{{ newClassOpen ? '收起' : '＋ 新建类' }}</button>
            <div v-if="newClassOpen" class="mini-form">
              <input class="form-input" v-model="clsForm.name" placeholder="类名，如 c0"/>
              <input class="form-input" v-model="clsForm.parentName" placeholder="父类（可空）"/>
              <input class="form-input" v-model="clsForm.comment" placeholder="说明（可空）"/>
              <button class="btn btn-primary btn-sm full" @click="createClass">创建类</button>
            </div>
            <button class="btn btn-secondary btn-sm full" @click="newRelOpen=!newRelOpen">{{ newRelOpen ? '收起' : '＋ 新建关系规则' }}</button>
            <div v-if="newRelOpen" class="mini-form">
              <input class="form-input" v-model="relForm.name" placeholder="关系名，如 belongs_to"/>
              <select class="form-select" v-model="relForm.subjClass"><option value="">主体类</option><option v-for="n in nodes" :key="n.id" :value="n.name">{{ n.name }}</option></select>
              <select class="form-select" v-model="relForm.objClass"><option value="">客体类</option><option v-for="n in nodes" :key="n.id" :value="n.name">{{ n.name }}</option></select>
              <select class="form-select" v-model="relForm.cardinality"><option value="many">多对多 many</option><option value="one">一对一 one</option></select>
              <label class="chk"><input type="checkbox" v-model="relForm.nullable"/> 允许为空</label>
              <input class="form-input" v-model="relForm.inheritsFrom" placeholder="继承关系名（可空）"/>
              <button class="btn btn-primary btn-sm full" @click="createRel">创建规则</button>
            </div>
            <div v-if="selNode" class="sel-card"><b>{{ selNode.name }}</b>
              <div class="text-xs muted" style="margin:4px 0 8px;">父类：{{ selNode.parent_name || '无' }} · {{ selNode.comment || '无说明' }}</div>
              <button class="btn btn-danger btn-sm full" @click="delClass(selNode)">删除该类</button></div>
            <div v-if="selEdge" class="sel-card"><b>{{ selEdge.name }}</b>
              <div class="text-xs mono muted" style="margin:4px 0;">{{ selEdge.subj_class }} → {{ selEdge.obj_class }}</div>
              <div class="text-xs" style="margin-bottom:8px;">基数：{{ selEdge.cardinality==='one' ? '一对一' : '多对多' }} · {{ selEdge.nullable ? '允许为空' : '不允许为空' }}
                <template v-if="selEdge.inherits_from"><br/>继承：{{ selEdge.inherits_from }}</template></div>
              <button class="btn btn-danger btn-sm full" @click="delRel(selEdge)">删除该规则</button></div>
            <div v-if="!selNode && !selEdge" class="text-xs muted" style="padding:6px 2px;">图上 {{ nodes.length }} 个类 · {{ graphEdges.length }} 条规则边</div>
          </div>
        </div>

        <div v-show="tab==='text'" class="panel">
          <div class="text-hint">Turtle 风格 DSL：<code>&lt;类名&gt; a :Class ; comment "…"</code> ／ <code>&lt;关系名&gt; a :Relation ; domain &lt;A&gt; ; range &lt;B&gt; ; cardinality "one|many" ; nullable true|false ; inherits &lt;关系&gt;</code></div>
          <textarea class="ttl-box" v-model="ttlText" spellcheck="false"></textarea>
          <div class="text-actions">
            <button class="btn btn-primary btn-sm" @click="importTtl">导入（解析并入库，自动检查）</button>
            <button class="btn btn-secondary btn-sm" @click="exportTtl">导出当前本体为文本</button>
            <span class="text-xs muted">导入时同名类/同规则自动跳过，不覆盖已有定义</span>
          </div>
        </div>

        <div v-show="tab==='check'" class="panel">
          <div class="check-bar">
            <button class="btn btn-primary btn-sm" @click="runCheck">▶ 运行一致性检查</button>
            <span class="text-xs muted">检测：同名类重复 · 关系规则重复定义 · 引用类缺失 · 继承放宽冲突 · 映射矛盾</span>
          </div>
          <div v-for="(i, idx) in issues" :key="idx" class="issue" :class="i.level">
            <b>{{ i.level==='error' ? '✗ 冲突' : i.level==='warn' ? '⚠ 提示' : '✓ 通过' }}</b>
            <span class="issue-code mono">{{ i.code }}</span>
            <span>{{ i.message }}</span>
          </div>
        </div>

        <div v-show="tab==='data'" class="panel">
          <div class="map-grid">
            <div>
              <div class="sec-t">物理数据（数据源：<b>{{ graphData.source || '-' }}</b>）</div>
              <div class="text-sm" style="margin:8px 0;">节点 {{ physNodes.length }} 个（{{ [...new Set(physNodes.map(n=>n.type))].join(', ') }}）<br/>边 {{ physEdges.length }} 条（{{ [...new Set(physEdges.map(e=>e.type))].join(', ') }}）</div>
              <div class="sec-t">新建映射</div>
              <div class="mini-form">
                <select class="form-select" v-model="mapForm.kind"><option value="node">节点类</option><option value="edge">关系边</option></select>
                <select class="form-select" v-model="mapForm.ontoType"><option value="">本体类型</option><option v-for="n in nodes" :key="n.id" :value="n.name">{{ n.name }}</option></select>
                <select class="form-select" v-model="mapForm.physicalType"><option value="">物理类型</option><option v-for="t in physTypes" :key="t" :value="t">{{ t }}</option></select>
                <button class="btn btn-primary btn-sm full" @click="addMap">绑定映射</button>
              </div>
            </div>
            <div>
              <div class="sec-t">映射列表（本体类型 → 物理类型）</div>
              <table class="map-table">
                <thead><tr><th>本体类型</th><th>物理类型</th><th>种类</th><th></th></tr></thead>
                <tbody>
                  <tr v-for="m in mappings" :key="m.id">
                    <td><span class="tag">{{ m.onto_type }}</span></td><td class="mono text-xs">{{ m.physical_type }}</td>
                    <td class="text-xs muted">{{ m.kind==='node' ? '节点' : '边' }}</td>
                    <td><button class="link-btn" @click="delMap(m)">删</button></td>
                  </tr>
                  <tr v-if="!mappings.length"><td colspan="4" class="text-xs muted">暂无映射——绑定后可按本体视角过滤查看数据</td></tr>
                </tbody>
              </table>
              <div v-if="mappings.length" class="text-sm" style="margin-top:8px;">
                本体视角投影：<b>{{ viewNodes.length }}</b> 节点 / <b>{{ viewEdges.length }}</b> 边
                <button class="link-btn" @click="loadView">按映射刷新</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-else class="onto-main card empty" style="display:flex;align-items:center;justify-content:center;">
        <div>← 选择或新建一个本体开始定义</div>
      </section>
    </div>

    <div v-if="newOpen" class="modal-mask" @click.self="newOpen=false">
      <div class="modal-card">
        <div class="modal-header"><div class="modal-title">新建本体</div><button class="modal-close" @click="newOpen=false">×</button></div>
        <div class="modal-body">
          <div class="form-row"><label class="form-label">名称</label><input class="form-input" v-model="ontoForm.name" placeholder="如 o1-组织管理"/></div>
          <div class="form-row"><label class="form-label">归属</label><select class="form-select" v-model="ontoForm.scope"><option value="domain">领域本体</option><option value="personal">个人本体</option></select></div>
          <div class="form-row"><label class="form-label">权威等级</label><select class="form-select" v-model="ontoForm.authority"><option value="normal">普通</option><option value="high">高权威（合并冲突时优先）</option></select></div>
          <div class="form-row"><label class="form-label">说明</label><input class="form-input" v-model="ontoForm.comment" placeholder="用途说明（可空）"/></div>
        </div>
        <div class="modal-footer"><button class="btn btn-secondary" @click="newOpen=false">取消</button><button class="btn btn-primary" @click="createOnto">创建</button></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'

const ontos = ref([])
const datasources = ref([])
const dsId = ref(null)
const cur = ref(null)
const tab = ref('graph')
const scopeFilter = ref('all')
const newOpen = ref(false)
const ontoForm = ref({ name: '', scope: 'domain', authority: 'normal', comment: '' })
const clsForm = ref({ name: '', parentName: '', comment: '' })
const relForm = ref({ name: '', subjClass: '', objClass: '', cardinality: 'many', nullable: true, inheritsFrom: '' })
const mapForm = ref({ kind: 'node', ontoType: '', physicalType: '' })
const newClassOpen = ref(false)
const newRelOpen = ref(false)
const selNode = ref(null)
const selEdge = ref(null)
const ttlText = ref('')
const issues = ref([])
const mappings = ref([])
const graphData = ref({})
const viewData = ref(null)

const filteredOntos = computed(() => ontos.value.filter(o => scopeFilter.value === 'all' || o.scope === scopeFilter.value))
const classes = computed(() => cur.value?._classes || [])
const nodes = computed(() => classes.value.map((c, i) => ({ ...c, x: 130 + (i % 3) * 170, y: 80 + Math.floor(i / 3) * 110 })))
const graphEdges = computed(() => (cur.value?._rels || []).map(r => {
  const s = nodes.value.find(n => n.name === r.subj_class), o = nodes.value.find(n => n.name === r.obj_class)
  if (!s || !o) return null
  const mx = (s.x + o.x) / 2, my = (s.y + o.y) / 2 - 8
  return { ...r, path: `M ${s.x} ${s.y} L ${o.x} ${o.y}`, mx, my }
}).filter(Boolean))
const svgBox = computed(() => {
  const ys = nodes.value.map(n => n.y)
  return `10 10 570 ${Math.max(200, Math.max(...ys, 0) + 80)}`
})
const physNodes = computed(() => graphData.value.nodes || [])
const physEdges = computed(() => graphData.value.edges || [])
const physTypes = computed(() => [...new Set([...physNodes.value.map(n => n.type), ...physEdges.value.map(e => e.type)])])
const viewNodes = computed(() => viewData.value?.nodes || [])
const viewEdges = computed(() => viewData.value?.edges || [])

onMounted(async () => { loadOntos(); const d = await api('/api/onto/datasources'); if (d.code === 0) { datasources.value = d.data; dsId.value = d.data[0]?.id; loadGraphData() } })

async function loadOntos() {
  const r = await api('/api/onto/ontologies')
  if (r.code === 0) ontos.value = r.data
}
async function loadGraphData() {
  if (!dsId.value) return
  const r = await api('/api/onto/graph-data?ds=' + dsId.value)
  if (r.code === 0) graphData.value = r.data
}
async function selectOnto(o) {
  const r = await api(`/api/onto/${o.id}/full`)
  if (r.code === 0) { cur.value = { ...r.data.ontology, _classes: r.data.classes, _rels: r.data.rels }; selNode.value = null; selEdge.value = null; tab.value = 'graph'; issues.value = []; await loadMappings() }
}
function openNewOnto() { ontoForm.value = { name: '', scope: 'domain', authority: 'normal', comment: '' }; newOpen.value = true }
async function createOnto() {
  if (!ontoForm.value.name.trim()) return alert('请输入本体名称')
  const r = await api('/api/onto/ontologies', { method: 'POST', body: ontoForm.value })
  if (r.code !== 0) return alert(r.message || '创建失败')
  newOpen.value = false; await loadOntos()
  const created = ontos.value.find(x => x.name === ontoForm.value.name.trim())
  if (created) selectOnto(created)
}
async function delOnto() {
  if (!confirm(`确认删除本体「${cur.value.name}」及其全部类与规则？`)) return
  await api(`/api/onto/ontologies/${cur.value.id}`, { method: 'DELETE' })
  cur.value = null; await loadOntos()
}
async function createClass() {
  if (!clsForm.value.name.trim()) return alert('请输入类名')
  const r = await api('/api/onto/classes', { method: 'POST', body: { ontologyId: cur.value.id, ...clsForm.value } })
  if (r.code !== 0) return alert(r.message || '创建失败')
  clsForm.value = { name: '', parentName: '', comment: '' }; newClassOpen.value = false; await selectOnto(cur.value)
}
async function delClass(n) {
  if (!confirm(`删除类「${n.name}」？`)) return
  await api(`/api/onto/classes/${n.id}`, { method: 'DELETE' }); await selectOnto(cur.value)
}
async function createRel() {
  if (!relForm.value.name.trim() || !relForm.value.subjClass || !relForm.value.objClass) return alert('请补全关系名与主体/客体类')
  const r = await api('/api/onto/rels', { method: 'POST', body: { ontologyId: cur.value.id, ...relForm.value } })
  if (r.code !== 0) return alert(r.message || '创建失败')
  relForm.value = { name: '', subjClass: '', objClass: '', cardinality: 'many', nullable: true, inheritsFrom: '' }
  newRelOpen.value = false; await selectOnto(cur.value)
}
async function delRel(e) { if (!confirm(`删除规则「${e.name}」？`)) return; await api(`/api/onto/rels/${e.id}`, { method: 'DELETE' }); await selectOnto(cur.value) }
async function runCheck() { const r = await api(`/api/onto/${cur.value.id}/check`); if (r.code === 0) issues.value = r.data }
async function importTtl() {
  const r = await api('/api/onto/import', { method: 'POST', body: { ontologyId: cur.value.id, text: ttlText.value } })
  if (r.code !== 0) return alert('解析失败：' + (r.message || r.detail || ''))
  alert(`导入完成：新增类 ${r.data.classes} 个 / 规则 ${r.data.rels} 条`)
  issues.value = r.data.issues; await selectOnto(cur.value)
}
async function exportTtl() { const r = await api(`/api/onto/${cur.value.id}/export`); if (r.code === 0) ttlText.value = r.data.text }
async function loadMappings() { const r = await api(`/api/onto/${cur.value.id}/full`); if (r.code === 0) mappings.value = r.data.mappings }
async function addMap() {
  if (!mapForm.value.ontoType || !mapForm.value.physicalType) return alert('请选择本体类型与物理类型')
  await api('/api/onto/mappings', { method: 'POST', body: { ontologyId: cur.value.id, ...mapForm.value } })
  mapForm.value = { kind: 'node', ontoType: '', physicalType: '' }; await loadMappings()
}
async function delMap(m) { await api(`/api/onto/mappings/${m.id}`, { method: 'DELETE' }); await loadMappings() }
async function loadView() { const r = await api(`/api/onto/${cur.value.id}/view-graph?ds=${dsId.value}`); if (r.code === 0) viewData.value = r.data }
</script>

<style>
.onto-page { padding: 20px 24px; }
.onto-layout { display: flex; gap: 16px; height: calc(100vh - 170px); min-height: 480px; }
.onto-side { width: 240px; flex-shrink: 0; display: flex; flex-direction: column; padding: 10px; overflow: hidden; }
.side-tabs { display: flex; gap: 4px; margin-bottom: 8px; }
.side-tabs button { flex: 1; border: none; background: transparent; padding: 5px 0; border-radius: 6px; font-size: 12.5px; color: var(--text-muted, #6b7280); cursor: pointer; }
.side-tabs button.on { background: var(--bg-soft, #f0f2f7); color: var(--primary, #4d6bfe); font-weight: 600; }
.onto-list { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
.onto-item { padding: 9px 10px; border-radius: 8px; cursor: pointer; border: 1px solid transparent; }
.onto-item:hover { background: var(--bg-soft, #f7f8fa); }
.onto-item.on { background: #eef1fe; border-color: var(--primary, #4d6bfe); }
.onto-name { font-size: 13.5px; font-weight: 600; display: flex; align-items: center; gap: 6px; }
.scope-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.scope-dot.domain { background: #4d6bfe; }
.scope-dot.personal { background: #22c55e; }

.onto-main { flex: 1; min-width: 0; display: flex; flex-direction: column; background: #fff; border-radius: 12px; border: 1px solid var(--border-light, #e5e8ef); overflow: hidden; }
.onto-toolbar { display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 10px 16px; border-bottom: 1px solid var(--border-light, #e5e8ef); }
.onto-cur b { font-size: 15px; }
.tab-btns { display: flex; gap: 2px; background: var(--bg-soft, #f0f2f7); border-radius: 8px; padding: 3px; }
.tab-btns button { border: none; background: transparent; padding: 5px 14px; border-radius: 6px; font-size: 12.5px; color: var(--text-muted, #6b7280); cursor: pointer; }
.tab-btns button.on { background: #fff; color: var(--primary, #4d6bfe); font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
.panel { flex: 1; overflow-y: auto; padding: 14px 16px; display: flex; flex-direction: column; gap: 10px; }

/* 关系节点图 */
.svg-wrap { position: relative; border: 1px solid var(--border-light, #e5e8ef); border-radius: 10px; background: #fafbfe; min-height: 300px; flex: 1; }
.svg-hint { position: absolute; left: 10px; bottom: 8px; font-size: 11.5px; color: var(--text-muted, #9ca3af); }
.node-rect { fill: #fff; stroke: #c7d0e6; stroke-width: 1.5; cursor: pointer; }
.node-rect.sel { stroke: var(--primary, #4d6bfe); stroke-width: 2.5; fill: #eef1fe; }
.node-name { font-size: 14px; font-weight: 600; fill: #1f2430; cursor: pointer; }
.node-sub { font-size: 10.5px; fill: #9ca3af; }
.edge-label { font-size: 11px; fill: #64748b; cursor: pointer; }
.edit-col { width: 230px; flex-shrink: 0; display: flex; flex-direction: column; gap: 8px; overflow-y: auto; }
.full { width: 100%; }
.mini-form { display: flex; flex-direction: column; gap: 6px; padding: 8px; background: var(--bg-soft, #f7f8fa); border-radius: 8px; }
.mini-form .form-input, .mini-form .form-select { font-size: 12.5px; padding: 6px 8px; }
.chk { font-size: 12.5px; color: var(--text-muted, #6b7280); display: flex; align-items: center; gap: 6px; }
.sel-card { border: 1px solid var(--border-light, #e5e8ef); border-radius: 8px; padding: 10px; font-size: 13.5px; background: #fff; }

/* 文本 */
.text-hint { font-size: 12px; color: var(--text-muted, #6b7280); line-height: 1.6; }
.text-hint code { background: var(--bg-soft, #f0f2f7); border-radius: 4px; padding: 1px 5px; font-size: 11px; }
.ttl-box { flex: 1; min-height: 260px; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 12.5px; line-height: 1.6; border: 1px solid var(--border-light, #e5e8ef); border-radius: 10px; padding: 12px; resize: none; background: #fdfdfe; }
.text-actions { display: flex; align-items: center; gap: 10px; }

/* 检查 */
.check-bar { display: flex; align-items: center; gap: 12px; }
.issue { display: flex; align-items: flex-start; gap: 10px; padding: 9px 12px; border-radius: 8px; font-size: 13px; line-height: 1.5; }
.issue.ok { background: #f0fdf4; color: #15803d; }
.issue.warn { background: #fffbeb; color: #b45309; }
.issue.error { background: #fef2f2; color: #dc2626; }
.issue-code { font-size: 11px; opacity: .7; flex-shrink: 0; padding-top: 2px; }

/* 数据映射 */
.map-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 20px; }
.sec-t { font-size: 12.5px; font-weight: 600; color: var(--text-muted, #6b7280); margin-top: 6px; padding-left: 8px; border-left: 3px solid var(--primary, #4d6bfe); }
.map-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.map-table th, .map-table td { text-align: left; padding: 6px 8px; border-bottom: 1px solid var(--border-light, #eef0f5); }
.link-btn { border: none; background: transparent; color: var(--primary, #4d6bfe); cursor: pointer; font-size: 12px; padding: 0; }

.modal-mask { position: fixed; inset: 0; background: rgba(15,23,42,.4); z-index: 900; display: flex; align-items: center; justify-content: center; }
.modal-card { width: 420px; background: #fff; border-radius: 14px; box-shadow: 0 20px 50px rgba(0,0,0,.2); }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 14px 18px; border-bottom: 1px solid var(--border-light, #eef0f5); }
.modal-title { font-size: 15px; font-weight: 700; }
.modal-close { border: none; background: transparent; font-size: 20px; color: #9ca3af; cursor: pointer; }
.modal-body { padding: 14px 18px; display: flex; flex-direction: column; gap: 10px; }
.form-row { display: flex; align-items: center; gap: 10px; }
.form-label { width: 70px; flex-shrink: 0; font-size: 13px; color: var(--text-muted, #6b7280); }
.modal-footer { padding: 12px 18px; border-top: 1px solid var(--border-light, #eef0f5); display: flex; justify-content: flex-end; gap: 8px; }
</style>
