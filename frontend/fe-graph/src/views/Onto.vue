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
        <button class="btn btn-secondary" @click="spaceOpen=true">＋ 新建空间</button>
        <button class="btn btn-primary" @click="openNewOnto">＋ 新建本体</button>
      </div>
    </div>

    <div class="onto-layout">
      <aside class="onto-side">
        <div class="acc-group" v-for="sp in tree" :key="sp.id" :class="{ open: sp.open }">
          <div class="acc-head" :class="{ active: selSpace === sp.id && !cur }" @click="toggleGroup(sp)" :title="sp.description || ''">
            <span class="acc-arrow">▶</span>
            <span class="tree-ico">📁</span>
            <span class="tree-name">{{ sp.name }}</span>
            <span class="tree-badge">{{ sp.children.length }} 本体</span>
            <span class="tree-del" @click.stop="delSpace(sp)" title="删除空间">×</span>
          </div>
          <div class="acc-body"><div class="acc-body-inner">
            <div v-for="o in sp.children" :key="o.id" class="onto-item" :class="{on: cur?.id===o.id}" @click="tab='graph'; selectOnto(o)">
              <div class="onto-name"><span class="scope-dot" :class="o.scope"></span>{{ o.name }}</div>
              <div class="text-xs muted">{{ o.scope==='domain' ? '领域' : '个人' }} · {{ o.class_count }} 类 / {{ o.rel_count }} 规则</div>
            </div>
            <div v-if="!sp.children.length" class="tree-empty text-xs muted">（无本体）</div>
          </div></div>
        </div>
        <div v-if="!tree.length" class="text-center muted text-sm" style="padding:24px 0;">暂无本体空间</div>
      </aside>

      <section class="onto-main" v-if="cur">
        <div class="onto-toolbar">
          <div class="onto-cur"><b>{{ cur.name }}</b><span class="text-xs muted" style="margin-left:8px;">ns: {{ cur.namespace || '-' }}</span></div>
          <div class="tab-btns">
            <button :class="{on: tab==='graph'}" @click="tab='graph'">关系节点图</button>
            <button :class="{on: tab==='text'}" @click="tab='text'; onTextTab()">文本定义</button>
            <button :class="{on: tab==='check'}" @click="tab='check'">一致性检查</button>
            <button :class="{on: tab==='data'}" @click="tab='data'">数据映射</button>
          </div>
          <button class="btn btn-secondary btn-sm" @click="delOnto">删除本体</button>
        </div>
        <!-- 关系节点图：多选起点 + 1~7 级邻域查询 -->
        <div v-if="tab==='graph'" class="onto-toolbar" style="margin-top:6px;">
          <MultiNodeSelect v-model="focusClasses" :options="classes.map(c => ({ value: c.name, label: c.name }))" placeholder="全图（可多选类节点）" />
          <select class="form-select" v-model="ontoDepth" style="width:96px;" title="邻域展开级数">
            <option v-for="d in 7" :key="d" :value="d">{{ d }} 级</option>
          </select>
          <button class="btn btn-primary btn-sm" @click="runNeighborhood">查询邻域</button>
          <button class="btn btn-secondary btn-sm" @click="resetNeighborhood">全图</button>
          <span class="text-xs muted" v-if="visibleNames">当前显示 {{ nodes.length }} 个类 · {{ graphEdges.length }} 条规则（{{ focusClasses.length }} 个起点 / {{ ontoDepth }} 级）</span>
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
          <div class="text-toolbar">
            <div class="fmt-switch">
              <button :class="{on: fmt==='form'}" @click="switchFmt('form')">表单</button>
              <button :class="{on: fmt==='yaml'}" @click="switchFmt('yaml')">YAML</button>
              <button :class="{on: fmt==='ttl'}" @click="switchFmt('ttl')">Turtle</button>
            </div>
            <span class="text-xs muted">
              <template v-if="fmt==='form'">表单模式：逐条增删改类与关系规则，保存后立即生效，无需导入</template>
              <template v-else-if="fmt==='yaml'">YAML 格式：classes/rels 列表，类含 name/comment/parent，关系含 name/subj/obj/cardinality/nullable/inherits</template>
              <template v-else>Turtle 风格 DSL：<code>&lt;类名&gt; a :Class ; comment "…"</code> ／ <code>&lt;关系名&gt; a :Relation ; domain &lt;A&gt; ; range &lt;B&gt; ; cardinality "one|many" ; nullable true|false ; inherits &lt;关系&gt;</code></template>
            </span>
          </div>

          <template v-if="fmt==='form'">
            <div class="sec-t">类定义（{{ classes.length }}）</div>
            <div class="form-table-wrap"><table class="form-def-table">
              <thead><tr><th>类名</th><th>父类</th><th>说明</th><th style="width:96px;">操作</th></tr></thead>
              <tbody>
                <tr v-for="c in classes" :key="c.id">
                  <td><input class="form-input" v-model="c.name" /></td>
                  <td><input class="form-input" v-model="c.parent_name" placeholder="可空" /></td>
                  <td><input class="form-input" v-model="c.comment" placeholder="可空" /></td>
                  <td class="text-right" style="white-space:nowrap;">
                    <button class="link-btn" @click="saveClass(c)">保存</button>
                    <button class="link-btn danger" @click="delClass(c)">删</button>
                  </td>
                </tr>
                <tr class="add-row">
                  <td><input class="form-input" v-model="clsForm.name" placeholder="新类名" /></td>
                  <td><input class="form-input" v-model="clsForm.parentName" placeholder="父类（可空）" /></td>
                  <td><input class="form-input" v-model="clsForm.comment" placeholder="说明（可空）" /></td>
                  <td><button class="btn btn-primary btn-sm" @click="createClass">＋ 新增</button></td>
                </tr>
              </tbody>
            </table></div>

            <div class="sec-t">关系规则（{{ (cur._rels || []).length }}）</div>
            <div class="form-table-wrap"><table class="form-def-table">
              <thead><tr><th>关系名</th><th>主体类</th><th>客体类</th><th>基数</th><th>可空</th><th>说明</th><th style="width:96px;">操作</th></tr></thead>
              <tbody>
                <tr v-for="r in (cur._rels || [])" :key="r.id">
                  <td><input class="form-input" v-model="r.name" /></td>
                  <td><input class="form-input" v-model="r.subj_class" /></td>
                  <td><input class="form-input" v-model="r.obj_class" /></td>
                  <td><select class="form-select" v-model="r.cardinality"><option value="many">many</option><option value="one">one</option></select></td>
                  <td><input type="checkbox" v-model="r.nullable" :true-value="1" :false-value="0" /></td>
                  <td><input class="form-input" v-model="r.comment" placeholder="可空" /></td>
                  <td style="white-space:nowrap;">
                    <button class="link-btn" @click="saveRel(r)">保存</button>
                    <button class="link-btn danger" @click="delRel(r)">删</button>
                  </td>
                </tr>
                <tr class="add-row">
                  <td><input class="form-input" v-model="relForm.name" placeholder="新关系名" /></td>
                  <td><select class="form-select" v-model="relForm.subjClass"><option value="">主体类</option><option v-for="n in nodes" :key="n.id" :value="n.name">{{ n.name }}</option></select></td>
                  <td><select class="form-select" v-model="relForm.objClass"><option value="">客体类</option><option v-for="n in nodes" :key="n.id" :value="n.name">{{ n.name }}</option></select></td>
                  <td><select class="form-select" v-model="relForm.cardinality"><option value="many">many</option><option value="one">one</option></select></td>
                  <td><input type="checkbox" v-model="relForm.nullable" /></td>
                  <td><input class="form-input" v-model="relForm.inheritsFrom" placeholder="继承（可空）" /></td>
                  <td><button class="btn btn-primary btn-sm" @click="createRel">＋ 新增</button></td>
                </tr>
              </tbody>
            </table></div>
          </template>

          <template v-else>
            <textarea class="ttl-box" v-model="ttlText" spellcheck="false"></textarea>
            <div class="text-actions">
              <button class="btn btn-primary btn-sm" @click="importText">导入（解析并入库，自动检查）</button>
              <button class="btn btn-secondary btn-sm" @click="exportText">导出当前本体为{{ fmt==='yaml' ? ' YAML' : ' Turtle' }}文本</button>
              <span class="text-xs muted">导入时同名类/同规则自动跳过，不覆盖已有定义；也可切换到「表单」逐条编辑</span>
            </div>
          </template>
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
          <div class="form-row"><label class="form-label">本体空间 <span style="color:#ef4444;">*</span></label>
            <select class="form-select" v-model="ontoForm.space_id">
              <option :value="0" disabled>— 请选择本体空间（必选）—</option>
              <option v-for="s in spaces" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select></div>
          <div class="form-row"><label class="form-label">名称</label><input class="form-input" v-model="ontoForm.name" placeholder="如 o1-组织管理"/></div>
          <div class="form-row"><label class="form-label">归属</label><select class="form-select" v-model="ontoForm.scope"><option value="domain">领域本体</option><option value="personal">个人本体</option></select></div>
          <div class="form-row"><label class="form-label">权威等级</label><select class="form-select" v-model="ontoForm.authority"><option value="normal">普通</option><option value="high">高权威（合并冲突时优先）</option></select></div>
          <div class="form-row"><label class="form-label">说明</label><input class="form-input" v-model="ontoForm.comment" placeholder="用途说明（可空）"/></div>
        </div>
        <div class="modal-footer"><button class="btn btn-secondary" @click="newOpen=false">取消</button><button class="btn btn-primary" @click="createOnto">创建</button></div>
      </div>
    </div>
    <div v-if="spaceOpen" class="modal-mask" @click.self="spaceOpen=false">
      <div class="modal-card">
        <div class="modal-header"><div class="modal-title">新建本体空间</div><button class="modal-close" @click="spaceOpen=false">×</button></div>
        <div class="modal-body">
          <div class="form-row"><label class="form-label">空间名 <span style="color:#ef4444;">*</span></label><input class="form-input" v-model="spaceForm.name" placeholder="如 风控本体空间"/></div>
          <div class="form-row"><label class="form-label">说明</label><input class="form-input" v-model="spaceForm.comment" placeholder="用途说明（可空）"/></div>
        </div>
        <div class="modal-footer"><button class="btn btn-secondary" @click="spaceOpen=false">取消</button><button class="btn btn-primary" @click="saveSpace">创建</button></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '../api'
import MultiNodeSelect from '../components/MultiNodeSelect.vue'

const ontos = ref([])
const datasources = ref([])
const dsId = ref(null)
const cur = ref(null)
const tab = ref('graph')
// 本体空间（对齐知识库 space 模型）
const spaces = ref([]); const selSpace = ref(0)
const spaceOpen = ref(false); const spaceForm = ref({ name: '', comment: '' })
const tree = computed(() => {
  const groups = spaces.value.map(s => ({ id: s.id, name: s.name, description: s.comment, open: s.open, children: [] }))
  for (const o of ontos.value) {
    const sp = groups.find(x => x.id === o.space_id)
    if (sp) sp.children.push(o)
  }
  return groups
})
function toggleGroup(sp) {
  const s = spaces.value.find(x => x.id === sp.id)
  if (s) s.open = !s.open
  selSpace.value = sp.id; cur.value = null
}
async function loadSpaces() {
  const r = await api('/api/onto/spaces')
  if (r.code === 0) {
    const prev = new Map(spaces.value.map(s => [s.id, s.open]))
    spaces.value = r.data.map(s => ({ ...s, open: prev.get(s.id) ?? true }))
  }
}
async function saveSpace() {
  if (!spaceForm.value.name.trim()) return alert('空间名不能为空')
  const r = await api('/api/onto/spaces', { method: 'POST', body: spaceForm.value })
  if (r.code !== 0) return alert(r.message || '创建失败')
  spaceOpen.value = false; spaceForm.value = { name: '', comment: '' }; await loadSpaces()
}
async function delSpace(sp) {
  if (!confirm(`删除本体空间「${sp.name}」？（空间下需无本体方可删除）`)) return
  const r = await api(`/api/onto/spaces/${sp.id}`, { method: 'DELETE' })
  if (r.code !== 0) return alert(r.message || r.detail || '失败')
  if (selSpace.value === sp.id) selSpace.value = 0
  await loadSpaces()
}
const newOpen = ref(false)
const ontoForm = ref({ name: '', space_id: 0, scope: 'domain', authority: 'normal', comment: '' })
const clsForm = ref({ name: '', parentName: '', comment: '' })
const relForm = ref({ name: '', subjClass: '', objClass: '', cardinality: 'many', nullable: true, inheritsFrom: '' })
const mapForm = ref({ kind: 'node', ontoType: '', physicalType: '' })
const newClassOpen = ref(false)
const newRelOpen = ref(false)
const selNode = ref(null)
const selEdge = ref(null)
const ttlText = ref('')
const fmt = ref('form')   // 本体定义方式：form=表单 / yaml / ttl
function switchFmt(f) {
  fmt.value = f
  if (f === 'form') return
  ttlText.value = ''
  if (cur.value) exportText()
}
function onTextTab() {
  if (cur.value && fmt.value !== 'form' && !ttlText.value.trim()) exportText()
}
const issues = ref([])
const mappings = ref([])
const graphData = ref({})
const viewData = ref(null)

const filteredOntos = computed(() => ontos.value)
const classes = computed(() => cur.value?._classes || [])
/* 关系节点图邻域查询：多选起点类 + 1~7 级 BFS（visibleNames=null 表示全图） */
const focusClasses = ref([])
const ontoDepth = ref(1)
const visibleNames = ref(null)
const visibleClasses = computed(() => visibleNames.value ? classes.value.filter(c => visibleNames.value.has(c.name)) : classes.value)
function runNeighborhood() {
  const starts = focusClasses.value || []
  if (!starts.length) { visibleNames.value = null; return }
  let front = new Set(starts), seen = new Set(starts)
  for (let i = 0; i < Math.max(1, Math.min(7, ontoDepth.value)); i++) {
    const nxt = new Set()
    for (const r of (cur.value?._rels || [])) {
      if (front.has(r.subj_class)) nxt.add(r.obj_class)
      if (front.has(r.obj_class)) nxt.add(r.subj_class)
    }
    seen = new Set([...seen, ...nxt])
    front = new Set([...nxt].filter(x => !front.has(x)))
  }
  visibleNames.value = seen
}
function resetNeighborhood() { focusClasses.value = []; visibleNames.value = null; ontoDepth.value = 1 }
const nodes = computed(() => visibleClasses.value.map((c, i) => ({ ...c, x: 130 + (i % 3) * 170, y: 80 + Math.floor(i / 3) * 110 })))
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

onMounted(async () => { loadSpaces(); loadOntos(); const d = await api('/api/onto/datasources'); if (d.code === 0) { datasources.value = d.data; dsId.value = d.data[0]?.id; loadGraphData() } })

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
  if (r.code === 0) {
    cur.value = { ...r.data.ontology, _classes: r.data.classes, _rels: r.data.rels }
    selNode.value = null; selEdge.value = null; issues.value = []
    resetNeighborhood()
    await loadMappings()
  }
}
function openNewOnto() {
  // 本体必须归属空间：默认当前空间，否则取第一个空间
  const sid = selSpace.value || (spaces.value[0]?.id ?? 0)
  ontoForm.value = { name: '', space_id: sid, scope: 'domain', authority: 'normal', comment: '' }
  newOpen.value = true
}
async function createOnto() {
  if (!ontoForm.value.name.trim()) return alert('请输入本体名称')
  if (!ontoForm.value.space_id) return alert('本体必须归属本体空间，请先选择空间')
  const r = await api('/api/onto/ontologies', { method: 'POST', body: ontoForm.value })
  if (r.code !== 0) return alert(r.message || r.detail || '创建失败')
  newOpen.value = false; await loadOntos(); await loadSpaces()
  const created = ontos.value.find(x => x.name === ontoForm.value.name.trim())
  if (created) selectOnto(created)
}
async function delOnto() {
  if (!confirm(`确认删除本体「${cur.value.name}」及其全部类与规则？`)) return
  await api(`/api/onto/ontologies/${cur.value.id}`, { method: 'DELETE' })
  cur.value = null; await loadOntos(); await loadSpaces()
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
// ===== 表单模式：逐条保存类 / 关系规则 =====
async function saveClass(c) {
  const r = await api(`/api/onto/classes/${c.id}`, { method: 'PUT', body: {
    ontologyId: cur.value.id, name: c.name, parentName: c.parent_name || '', comment: c.comment || '' } })
  if (r.code !== 0) return alert(r.message || r.detail || '保存失败')
  await selectOnto(cur.value)
}
async function saveRel(r0) {
  const r = await api(`/api/onto/rels/${r0.id}`, { method: 'PUT', body: {
    ontologyId: cur.value.id, name: r0.name, subjClass: r0.subj_class, objClass: r0.obj_class,
    cardinality: r0.cardinality, nullable: !!r0.nullable, inheritsFrom: r0.inherits_from || '', comment: r0.comment || '' } })
  if (r.code !== 0) return alert(r.message || r.detail || '保存失败')
  await selectOnto(cur.value)
}
async function runCheck() { const r = await api(`/api/onto/${cur.value.id}/check`); if (r.code === 0) issues.value = r.data }
async function importText() {
  const r = await api('/api/onto/import', { method: 'POST', body: { ontologyId: cur.value.id, text: ttlText.value, format: fmt.value } })
  if (r.code !== 0) return alert('解析失败：' + (r.message || r.detail || ''))
  alert(`导入完成：新增类 ${r.data.classes} 个 / 规则 ${r.data.rels} 条`)
  issues.value = r.data.issues; await selectOnto(cur.value); await loadSpaces()
}
async function exportText() {
  const r = await api(`/api/onto/${cur.value.id}/export?format=${fmt.value}`)
  if (r.code === 0) ttlText.value = r.data.text
}
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
.onto-side { width: 260px; flex-shrink: 0; display: flex; flex-direction: column; padding: 10px; overflow-y: auto; max-height: calc(100vh - 160px); position: sticky; top: 12px; }
/* 手风琴（对齐知识库 Kb.vue / Graph.vue） */
.acc-group { border: 1px solid #e9ebf0; border-radius: 10px; margin-bottom: 8px; overflow: hidden; background: #fff; transition: border-color .18s, box-shadow .18s; }
.acc-group:hover { border-color: #c9d3ee; }
.acc-group.open { box-shadow: 0 1px 6px rgba(77, 107, 254, .07); }
.acc-head { padding: 9px 12px; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 8px; background: #f8f9fb; user-select: none; }
.acc-group.open .acc-head { background: #f3f5fd; }
.acc-head.active { background: rgba(77, 107, 254, .12); color: #4d6bfe; font-weight: 600; }
.acc-arrow { color: #9aa3b5; font-size: 9px; transition: transform .22s ease; width: 12px; text-align: center; }
.acc-group.open .acc-arrow { transform: rotate(90deg); color: #4d6bfe; }
.acc-body { display: grid; grid-template-rows: 0fr; opacity: 0; transition: grid-template-rows .24s ease, opacity .18s ease; }
.acc-group.open .acc-body { grid-template-rows: 1fr; opacity: 1; }
.acc-body-inner { overflow: hidden; min-height: 0; padding: 0 4px; }
.acc-group.open .acc-body-inner { padding: 4px; }
.tree-ico { font-size: 13px; }
.tree-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.tree-badge { font-size: 11px; color: #6b7280; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 1px 8px; white-space: nowrap; }
.tree-del { color: #c3cad8; font-size: 14px; padding: 0 3px; visibility: hidden; }
.acc-head:hover .tree-del { visibility: visible; }
.tree-del:hover { color: #ef4444; }
.tree-empty { padding: 6px 12px 6px 34px; }
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
.form-table-wrap { overflow-x: auto; }
.form-def-table { width: 100%; border-collapse: collapse; font-size: 12.5px; }
.form-def-table th, .form-def-table td { text-align: left; padding: 5px 6px; border-bottom: 1px solid var(--border-light, #eef0f5); }
.form-def-table th { color: var(--text-muted, #6b7280); font-weight: 600; }
.form-def-table .form-input, .form-def-table .form-select { font-size: 12.5px; padding: 5px 7px; min-width: 80px; width: 100%; }
.form-def-table .add-row { background: var(--bg-soft, #f7f8fa); }
.link-btn.danger { color: #ef4444; margin-left: 8px; }
.text-toolbar { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.fmt-switch { display: flex; gap: 2px; background: var(--bg-soft, #f0f2f7); border-radius: 8px; padding: 3px; flex-shrink: 0; }
.fmt-switch button { border: none; background: transparent; padding: 4px 14px; border-radius: 6px; font-size: 12.5px; color: var(--text-muted, #6b7280); cursor: pointer; }
.fmt-switch button.on { background: #fff; color: var(--primary, #4d6bfe); font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
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
