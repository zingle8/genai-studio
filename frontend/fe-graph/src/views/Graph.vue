<template>
  <div class="page-header">
    <div><div class="page-title">知识图谱</div><div class="page-subtitle">图谱（数据库概念）/ 实体类型 / 节点·属性·关系 / 版本（自动快照·可恢复）</div></div>
    <div class="page-actions">
      <button class="btn btn-ghost" @click="spaceOpen = true">＋ 新建空间</button>
      <button class="btn btn-ghost" @click="openNewGraph">＋ 新建图谱</button>
      <template v-if="curGraph">
        <button class="btn btn-ghost" @click="entityOpen = true">＋ 实体类型</button>
        <button class="btn btn-ghost" @click="nodeOpen = true">＋ 节点</button>
        <button class="btn btn-primary" @click="edgeOpen = true">＋ 关系</button>
      </template>
    </div>
  </div>

  <div class="graph-layout">
    <!-- 左：图谱空间 → 图谱 两级手风琴树 -->
    <div class="graph-side-left">
      <div class="acc-group" v-for="sp in tree" :key="sp.id" :class="{ open: sp.open }">
        <div class="acc-head" :class="{ active: selSpace === sp.id && !curGraph }" @click="toggleGroup(sp)" :title="sp.description || ''">
          <span class="acc-arrow">▶</span>
          <span class="tree-ico">📁</span>
          <span class="tree-name">{{ sp.name }}</span>
          <span class="tree-badge">{{ sp.children.length }} 图谱</span>
          <span class="tree-del" @click.stop="delSpace(sp)" title="删除空间">×</span>
        </div>
        <div class="acc-body"><div class="acc-body-inner">
          <div class="acc-item" v-for="g in sp.children" :key="g.id"
               :class="{ active: curGraph?.id === g.id }" @click="pickGraph(g)" :title="g.description || ''">
            <span class="db-icon" :class="g.db_type === 'neo4j' ? 'neo' : ''">{{ g.db_type === 'neo4j' ? 'N4' : 'SQL' }}</span>
            <span class="tree-name">{{ g.name }}</span>
            <span class="tree-badge">{{ g.nodeCount }} 节点</span>
            <span v-if="g.db_type === 'neo4j'" class="dot-mini" :class="g.dbOk ? 'green' : 'red'" :title="g.dbOk ? 'Neo4j 已连接' : 'Neo4j 连接失败'"></span>
            <span class="tree-del" @click.stop="delGraph(g)" title="删除图谱">×</span>
          </div>
          <div v-if="!sp.children.length" class="tree-empty text-xs muted">（无图谱）</div>
        </div></div>
      </div>
      <div v-if="!tree.length" class="text-center muted text-sm" style="padding:20px;">暂无图谱空间</div>
    </div>

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
            <b>{{ curGraph.name }}</b><span class="text-xs muted">{{ nodes.length }} 节点 · {{ edges.length }} 关系 · {{ curGraph.db_type === 'neo4j' ? 'Neo4j' : '内置存储' }} · 按关系聚簇（力导向布局）</span>
            <span style="flex:1"></span>
            <MultiNodeSelect v-model="focusIds" :options="allNodes.map(n => ({ value: n.id, label: n.name }))" placeholder="全图（可多选节点）" />
            <select class="form-input" v-model="depth" style="width:96px;" title="邻域展开级数">
              <option v-for="d in 7" :key="d" :value="d">{{ d }} 级</option>
            </select>
            <button class="btn btn-primary btn-sm" :disabled="searching" @click="loadGraph">{{ searching ? '查询中…' : '查询邻域' }}</button>
            <span class="zoom-ctl">
              <button class="zoom-btn" title="放大视图" @click="zoomIn">➕</button>
              <button class="zoom-btn" title="缩小视图" @click="zoomOut">➖</button>
              <button class="zoom-btn" title="重置视图比例" @click="zoomReset">⌂</button>
              <span class="text-xs muted zoom-val">{{ Math.round(scale * 100) }}%</span>
            </span>
          </div>
          <svg class="graph-svg" viewBox="0 0 1000 620">
            <g :transform="viewTransform">
              <g v-for="e in edges" :key="'e' + e.id" style="cursor:pointer;" @click="selEdge=e; selNode=null">
                <line :x1="pos(e.source_id).x + 32" :y1="pos(e.source_id).y + 18" :x2="pos(e.target_id).x + 32" :y2="pos(e.target_id).y + 18" class="edge-line" :class="{ sel: selEdge?.id === e.id }" />
                <text :x="(pos(e.source_id).x + pos(e.target_id).x) / 2 + 32" :y="(pos(e.source_id).y + pos(e.target_id).y) / 2 + 12" class="edge-label" :class="{ sel: selEdge?.id === e.id }">{{ e.rel_type }}</text>
              </g>
              <g v-for="n in nodes" :key="'n' + n.id" style="cursor:pointer;" @click="selNode=n; selEdge=null">
                <rect :x="pos(n.id).x" :y="pos(n.id).y" width="64" height="36" rx="8" class="node-box" :class="{ sel: selNode?.id === n.id }" :style="{ stroke: typeColor(n.entity_id) }" />
                <circle :cx="pos(n.id).x + 8" :cy="pos(n.id).y + 8" r="4" :fill="typeColor(n.entity_id)" />
                <text :x="pos(n.id).x + 34" :y="pos(n.id).y + 23" class="node-name">{{ n.name.length > 6 ? n.name.slice(0, 6) : n.name }}</text>
              </g>
            </g>
          </svg>

          <!-- 选中对象详情：属性 / 状态 / 版本 / 操作 -->
          <div class="graph-detail">
            <template v-if="selNode">
              <div class="detail-head">
                <b>{{ selNode.name }}</b>
                <span class="tag tag-success">节点 · {{ entityName(selNode.entity_id) }}</span>
                <span class="text-xs muted">ID {{ selNode.id }} · 创建 {{ selNode.created_at }}</span>
                <span style="flex:1"></span>
                <button class="btn btn-primary btn-sm" @click="editNode(selNode)">更新节点</button>
                <button class="btn btn-secondary btn-sm" @click="openEdgeFor(selNode)">＋ 关联关系</button>
                <button class="btn btn-secondary btn-sm" @click="nodeOpen = true">＋ 节点</button>
                <button class="btn btn-danger btn-sm" @click="delNode(selNode)">删除</button>
              </div>
              <div class="detail-grid">
                <div><div class="sec-t">属性（{{ nodeProps(selNode).length }}）</div>
                  <table class="detail-table"><tbody>
                    <tr v-for="p in nodeProps(selNode)" :key="p[0]"><td class="mono">{{ p[0] }}</td><td>{{ p[1] }}</td></tr>
                    <tr v-if="!nodeProps(selNode).length"><td colspan="2" class="muted">（无属性）</td></tr>
                  </tbody></table>
                  <div class="text-xs muted" style="margin-top:4px;">类型定义：{{ propsSchemaText(entitySchema(selNode.entity_id)) }}</div>
                </div>
                <div><div class="sec-t">关联关系（{{ relatedEdges(selNode).length }}）</div>
                  <div class="detail-list"><div v-for="e in relatedEdges(selNode)" :key="e.id" class="detail-item" @click="selEdge=e; selNode=null">
                    <b>{{ e.rel_type }}</b> {{ nodeName(e.source_id) === selNode.name ? '→ ' + nodeName(e.target_id) : '← ' + nodeName(e.source_id) }}
                  </div><div v-if="!relatedEdges(selNode).length" class="muted text-xs">（无关联）</div></div>
                </div>
                <div><div class="sec-t">版本 / 状态</div>
                  <div class="text-xs muted">当前图谱 {{ versions.length }} 个版本 · 最近操作：</div>
                  <div class="detail-list"><div v-for="v in versions.slice(0, 5)" :key="v.id" class="detail-item">
                    <span class="mono">v{{ v.version_no }}</span> {{ v.op }} · {{ v.note || v.created_at }}
                    <button class="link-btn" @click="viewVersion(v)">内容</button>
                  </div><div v-if="!versions.length" class="muted text-xs">（暂无版本快照）</div></div>
                  <button class="btn btn-ghost btn-sm" @click="tab='versions'; loadVersions()">全部版本 ›</button>
                </div>
              </div>
            </template>
            <template v-else-if="selEdge">
              <div class="detail-head">
                <b>{{ selEdge.rel_type }}</b><span class="tag">关系 #{{ selEdge.id }}</span>
                <span class="text-xs muted">创建 {{ selEdge.created_at }}</span>
                <span style="flex:1"></span>
                <button class="btn btn-primary btn-sm" @click="editEdge(selEdge)">更新关系</button>
                <button class="btn btn-secondary btn-sm" @click="nodeOpen = true">＋ 节点</button>
                <button class="btn btn-danger btn-sm" @click="delEdge(selEdge)">删除</button>
              </div>
              <div class="detail-grid">
                <div><div class="sec-t">关系信息</div>
                  <table class="detail-table"><tbody>
                    <tr><td>起点</td><td class="clickable" @click="selectNodeById(selEdge.source_id)">{{ nodeName(selEdge.source_id) }}</td></tr>
                    <tr><td>终点</td><td class="clickable" @click="selectNodeById(selEdge.target_id)">{{ nodeName(selEdge.target_id) }}</td></tr>
                    <tr><td>属性</td><td>{{ selEdge.props || '{}' }}</td></tr>
                  </tbody></table>
                </div>
                <div><div class="sec-t">版本 / 状态</div>
                  <div class="text-xs muted">当前图谱 {{ versions.length }} 个版本 · 最近操作：</div>
                  <div class="detail-list"><div v-for="v in versions.slice(0, 5)" :key="v.id" class="detail-item">
                    <span class="mono">v{{ v.version_no }}</span> {{ v.op }} · {{ v.note || v.created_at }}
                    <button class="link-btn" @click="viewVersion(v)">内容</button>
                  </div></div>
                </div>
              </div>
            </template>
            <div v-else class="text-xs muted">点击图中的节点或关系，查看属性、状态、版本并执行增删改操作</div>
          </div>
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

  <!-- 新建空间 -->
  <div class="modal-mask" v-if="spaceOpen" @click.self="spaceOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">新建图谱空间</div><button class="modal-close" @click="spaceOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">空间名 <span style="color:#ef4444;">*</span></label><input class="form-input" v-model="spaceForm.name" placeholder="如 风控图谱空间" /></div>
        <div class="form-row"><label class="form-label">描述</label><input class="form-input" v-model="spaceForm.description" /></div>
      </div>
      <div class="modal-footer"><button class="btn btn-ghost" @click="spaceOpen = false">取消</button><button class="btn btn-primary" @click="saveSpace">创建</button></div>
    </div>
  </div>

  <!-- 新建/编辑图谱 -->
  <div class="modal-mask" v-if="graphOpen" @click.self="graphOpen = false">
    <div class="modal">
      <div class="modal-header"><div class="modal-title">新建图谱</div><button class="modal-close" @click="graphOpen = false">×</button></div>
      <div class="modal-body">
        <div class="form-row"><label class="form-label">图谱空间 <span style="color:#ef4444;">*</span></label>
          <select class="form-input" v-model="graphForm.space_id">
            <option :value="0" disabled>— 请选择图谱空间（必选）—</option>
            <option v-for="s in spaces" :key="s.id" :value="s.id">{{ s.name }}</option>
          </select></div>
        <div class="form-row"><label class="form-label">图谱名</label><input class="form-input" v-model="graphForm.name" /></div>
        <div class="form-row"><label class="form-label">存储后端</label>
          <select class="form-input" v-model="graphForm.db_type" @change="onDbTypeChange">
            <option value="sqlite">内置存储（SQLite）</option>
            <option value="neo4j">Neo4j（图数据库）</option>
          </select></div>
        <template v-if="graphForm.db_type === 'neo4j'">
          <div class="text-xs muted" style="margin:0 0 8px 118px;">已从平台配置（graph.neo4j.*）带入默认值，可覆盖；密码在「平台配置」中统一维护</div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { api, withBase } from '../api'
import MultiNodeSelect from '../components/MultiNodeSelect.vue'
const graphs = ref([]); const curGraph = ref(null); const tab = ref('view')
const entities = ref([]); const nodes = ref([]); const edges = ref([]); const versions = ref([])
const focusIds = ref([]); const allNodes = ref([]); const depth = ref(1); const searching = ref(false)
const selNode = ref(null); const selEdge = ref(null)
const graphOpen = ref(false); const graphForm = ref({ name: '', space_id: 0, db_type: 'sqlite', description: '' }); const n4cfg = ref({})
const entityOpen = ref(false); const entityForm = ref({ id: null, name: '', props_schema: '[]' })
const nodeOpen = ref(false); const nodeForm = ref({ id: null, entity_id: 0, name: '', props: '{}' })
const edgeOpen = ref(false); const edgeForm = ref({ id: null, source_id: '', rel_type: '', target_id: '' })
const verDetail = ref(null)
const pub = ref({})
// 图谱空间（对齐知识库 space 模型）
const spaces = ref([]); const selSpace = ref(0)
const spaceOpen = ref(false); const spaceForm = ref({ name: '', description: '' })
const tree = computed(() => {
  const groups = spaces.value.map(s => ({ id: s.id, name: s.name, description: s.description, open: s.open, children: [] }))
  for (const g of graphs.value) {
    const sp = groups.find(x => x.id === g.space_id)
    if (sp) sp.children.push(g)
  }
  return groups
})
function toggleGroup(sp) {
  const s = spaces.value.find(x => x.id === sp.id)
  if (s) s.open = !s.open
  selSpace.value = sp.id; curGraph.value = null
}
async function loadSpaces() {
  const r = await api(withBase('/api/graphs/spaces'))
  if (r.code === 0) {
    const prev = new Map(spaces.value.map(s => [s.id, s.open]))
    spaces.value = r.data.map(s => ({ ...s, open: prev.get(s.id) ?? true }))
  }
}
async function saveSpace() {
  if (!spaceForm.value.name.trim()) { alert('空间名不能为空'); return }
  const r = await api(withBase('/api/graphs/spaces'), { method: 'POST', body: JSON.stringify(spaceForm.value) })
  if (r.code === 0) { spaceOpen.value = false; spaceForm.value = { name: '', description: '' }; loadSpaces() }
  else alert(r.detail || '失败')
}
async function delSpace(sp) {
  if (!confirm(`删除图谱空间「${sp.name}」？（空间下需无图谱方可删除）`)) return
  const r = await api(withBase('/api/graphs/spaces/' + sp.id), { method: 'DELETE' })
  if (r.code === 0) { if (selSpace.value === sp.id) selSpace.value = 0; loadSpaces() } else alert(r.detail || '失败')
}
async function loadPub() {
  try {
    const res = await fetch('/api/configs?size=100').catch(() => fetch('http://localhost:38087/api/configs?size=100'))
    const r = await res.json()
    if (r.code === 0) { const m = {}; for (const it of (r.data.list || r.data || [])) m[it.configKey] = it.configValue; pub.value = m }
  } catch {}
}
onMounted(() => { loadPub(); loadGraphs(); loadSpaces() })

async function loadGraphs() {
  const r = await api(withBase('/api/graphs'))
  if (r.code === 0) graphs.value = r.data
}
function pickGraph(g) {
  curGraph.value = g
  entities.value = []; nodes.value = []; edges.value = []; allNodes.value = []; focusIds.value = []
  selNode.value = null; selEdge.value = null
  loadGraph(); loadVersions()
}
async function loadGraph() {
  if (!curGraph.value) return
  const gid = curGraph.value.id
  const ids = focusIds.value || []
  selNode.value = null; selEdge.value = null
  searching.value = true
  try {
    const path = ids.length
      ? withBase(`/api/graphs/${gid}/neighborhood?nids=${ids.join(',')}&depth=${depth.value}`)
      : withBase(`/api/graphs/${gid}/nodes`)
    const r = await api(path)
    if (r.code === 0) {
      nodes.value = r.data.nodes
      if (!ids.length) allNodes.value = r.data.nodes            // 全量节点作为多选选项
      if (r.data.entities) entities.value = r.data.entities
    }
    const re = await api(withBase(`/api/graphs/${gid}/edges`))
    if (re.code === 0) edges.value = ids.length ? (r.data?.edges || []) : re.data
    const rn = await api(withBase(`/api/graphs/${gid}/entities`))
    if (rn.code === 0) entities.value = rn.data
  } finally { searching.value = false }
}
async function loadVersions() {
  const r = await api(withBase(`/api/graphs/${curGraph.value.id}/versions`))
  if (r.code === 0) versions.value = r.data
}

/* ===== 图视图：力导向簇群布局 + 缩放 ===== */
const positions = ref({})        // nodeId -> {x,y}
const scale = ref(1)
const TYPE_COLORS = ['#4d6bfe', '#e5484d', '#12b76a', '#f79009', '#7a5af8', '#06aed4', '#d444f1', '#6b7280']
function typeColor(eid) {
  const i = entities.value.findIndex(x => x.id === eid)
  return TYPE_COLORS[(i < 0 ? 0 : i) % TYPE_COLORS.length]
}
function pos(id) { return positions.value[id] || { x: 20, y: 20 } }

/** 力导向模拟：同类节点初始按扇区聚集（簇群），斥力 + 边弹簧 + 中心引力 */
function layout() {
  const list = nodes.value
  const P = {}
  if (!list.length) { positions.value = P; return }
  const W = 1000, H = 620, PAD = 50
  const cx = W / 2, cy = H / 2
  // 初始位置：按实体类型分簇放到圆环扇区
  const buckets = {}
  for (const n of list) (buckets[n.entity_id] = buckets[n.entity_id] || []).push(n)
  const keys = Object.keys(buckets)
  let bi = 0
  for (const k of keys) {
    const a = (bi / keys.length) * Math.PI * 2
    const br = 150 + 30 * keys.length
    const bx = cx + br * Math.cos(a), by = cy + br * 0.8 * Math.sin(a)
    buckets[k].forEach((n, j) => {
      const ja = j / buckets[k].length * Math.PI * 2
      P[n.id] = { x: bx + 24 * Math.cos(ja) + (Math.random() - 0.5) * 20, y: by + 20 * Math.sin(ja) + (Math.random() - 0.5) * 20 }
    })
    bi++
  }
  // 邻接表
  const adj = {}
  for (const e of edges.value) {
    if (P[e.source_id] && P[e.target_id]) (adj[e.source_id] = adj[e.source_id] || []).push(e.target_id)
    if (P[e.source_id] && P[e.target_id]) (adj[e.target_id] = adj[e.target_id] || []).push(e.source_id)
  }
  const ids = list.map(n => n.id)
  const k = Math.sqrt((W * H) / Math.max(1, list.length)) * 3.2   // 斥力系数
  const spring = 0.012, ideal = Math.max(120, Math.min(180, 1100 / Math.sqrt(list.length)))
  for (let it = 0; it < 220; it++) {
    const temp = Math.max(2, 70 * (1 - it / 220))
    const F = {}
    for (const id of ids) F[id] = { x: 0, y: 0 }
    // 节点间斥力
    for (let i = 0; i < ids.length; i++) {
      for (let j = i + 1; j < ids.length; j++) {
        const a = P[ids[i]], b = P[ids[j]]
        let dx = a.x - b.x, dy = a.y - b.y
        let d2 = dx * dx + dy * dy || 1
        const f = k / d2, d = Math.sqrt(d2)
        const fx = dx / d * f, fy = dy / d * f
        F[ids[i]].x += fx; F[ids[i]].y += fy
        F[ids[j]].x -= fx; F[ids[j]].y -= fy
        // 矩形碰撞排斥：节点框(64x36)+间距，避免叠在一起
        if (Math.abs(dx) < 80 && Math.abs(dy) < 52) {
          const sx = Math.sign(dx) || (Math.random() < 0.5 ? -1 : 1)
          const sy = Math.sign(dy) || (Math.random() < 0.5 ? -1 : 1)
          F[ids[i]].x += sx * 12; F[ids[i]].y += sy * 8
          F[ids[j]].x -= sx * 12; F[ids[j]].y -= sy * 8
        }
      }
    }
    // 边弹簧 + 中心引力
    for (const e of edges.value) {
      const a = P[e.source_id], b = P[e.target_id]
      if (!a || !b) continue
      const dx = b.x - a.x, dy = b.y - a.y
      const d = Math.sqrt(dx * dx + dy * dy) || 1
      const f = spring * (d - ideal)
      const fx = dx / d * f, fy = dy / d * f
      F[e.source_id].x += fx; F[e.source_id].y += fy
      F[e.target_id].x -= fx; F[e.target_id].y -= fy
    }
    for (const id of ids) {
      const p = P[id]
      F[id].x += (cx - p.x) * 0.002; F[id].y += (cy - p.y) * 0.002
      const d = Math.sqrt(F[id].x ** 2 + F[id].y ** 2) || 1
      const lim = Math.min(d, temp)
      p.x += F[id].x / d * lim; p.y += F[id].y / d * lim
      p.x = Math.max(PAD, Math.min(W - PAD, p.x))
      p.y = Math.max(PAD, Math.min(H - PAD, p.y))
    }
  }
  positions.value = P
}
watch([nodes, edges], layout)

function zoomIn() { scale.value = Math.min(2.5, +(scale.value * 1.25).toFixed(3)) }
function zoomOut() { scale.value = Math.max(0.35, +(scale.value / 1.25).toFixed(3)) }
function zoomReset() { scale.value = 1 }
const viewTransform = computed(() => `translate(${500 * (1 - scale.value)} ${310 * (1 - scale.value)}) scale(${scale.value})`)
function entityName(eid) { const e = entities.value.find(x => x.id === eid); return e ? e.name : '—' }
function entitySchema(eid) { return entities.value.find(x => x.id === eid)?.props_schema || '[]' }
function nodeProps(n) {
  try {
    const o = JSON.parse(n?.props || '{}')
    return o && typeof o === 'object' && !Array.isArray(o) ? Object.entries(o) : []
  } catch { return [] }
}
function relatedEdges(n) { return edges.value.filter(e => e.source_id === n.id || e.target_id === n.id) }
function nodeName(id) { return nodes.value.find(n => n.id === id)?.name || '#' + id }
function selectNodeById(id) { const n = nodes.value.find(x => x.id === id); if (n) { selEdge.value = null; selNode.value = n } }
function openEdgeFor(n) { edgeForm.value = { id: null, source_id: n.id, rel_type: '', target_id: '' }; edgeOpen.value = true }
function propsSchemaText(s) {
  try { const a = JSON.parse(s || '[]'); return a.length ? a.map(x => x.name + ':' + x.type).join('、') : '（无属性定义）' } catch { return '—' }
}

function onDbTypeChange() {
  if (graphForm.value.db_type === 'neo4j' && !n4cfg.value.uri) {
    const p = pub.value
    n4cfg.value = { uri: p['graph.neo4j.url'] || 'http://localhost:7474', user: p['graph.neo4j.user'] || 'neo4j', password: p['graph.neo4j.password'] || '' }
  }
}
function openNewGraph() {
  const p = pub.value
  // 图谱必须归属空间：默认当前空间，否则取第一个空间
  const sid = selSpace.value || (spaces.value[0]?.id ?? 0)
  graphForm.value = { name: '', space_id: sid, db_type: 'sqlite', description: '' }
  n4cfg.value = { uri: p['graph.neo4j.url'] || 'http://localhost:7474', user: p['graph.neo4j.user'] || 'neo4j', password: p['graph.neo4j.password'] || '' }
  graphOpen.value = true
}
async function saveGraph() {
  if (!graphForm.value.space_id) { alert('图谱必须归属图谱空间，请先选择空间'); return }
  const body = { ...graphForm.value, db_config: graphForm.value.db_type === 'neo4j' ? JSON.stringify(n4cfg.value) : '' }
  const r = await api(withBase('/api/graphs'), { method: 'POST', body: JSON.stringify(body) })
  if (r.code === 0) { graphOpen.value = false; loadGraphs(); loadSpaces(); curGraph.value = r.data; loadGraph() }
  else alert(r.detail || '失败（Neo4j 连接失败请检查地址/凭据）')
}
async function delGraph(g) {
  if (!confirm(`删除图谱「${g.name}」及其全部数据${g.db_type === 'neo4j' ? '（含 Neo4j 节点）' : ''}？`)) return
  await api(withBase('/api/graphs/' + g.id), { method: 'DELETE' })
  if (curGraph.value?.id === g.id) curGraph.value = null
  loadGraphs(); loadSpaces()
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
.graph-side-left { width: 280px; flex-shrink: 0; overflow-y: auto; max-height: calc(100vh - 160px); position: sticky; top: 12px; }
/* 手风琴（对齐知识库 Kb.vue） */
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
.acc-item { display: flex; align-items: center; gap: 7px; padding: 8px 10px; border-radius: 8px; cursor: pointer; font-size: 13px; }
.acc-item:hover { background: #f5f6fa; }
.acc-item.active { background: rgba(77, 107, 254, .09); color: #4d6bfe; font-weight: 600; }
.tree-ico { font-size: 13px; }
.tree-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.tree-badge { font-size: 11px; color: #6b7280; background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 1px 8px; white-space: nowrap; }
.tree-del { color: #c3cad8; font-size: 14px; padding: 0 3px; visibility: hidden; }
.acc-head:hover .tree-del, .acc-item:hover .tree-del { visibility: visible; }
.tree-del:hover { color: #ef4444; }
.tree-empty { padding: 6px 12px 6px 34px; }
.db-icon { width: 30px; height: 22px; border-radius: 5px; background: #6b7280; color: #fff; font-size: 10px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.db-icon.neo { background: #018bff; }
.dot-mini { display: inline-block; width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-mini.green { background: #22c55e; }
.dot-mini.red { background: #ef4444; }
.graph-svg { width: 100%; height: 560px; background: var(--bg-soft); border-radius: 10px; }
.zoom-ctl { display: inline-flex; align-items: center; gap: 4px; background: #fff; border: 1px solid var(--border-light, #e9ebf0); border-radius: 8px; padding: 2px 6px 2px 2px; }
.zoom-btn { width: 28px; height: 26px; border: none; background: none; border-radius: 6px; font-size: 13px; line-height: 1; cursor: pointer; color: var(--text-secondary, #4b5563); transition: background .15s, color .15s; }
.zoom-btn:hover { background: var(--bg-soft, #f0f2f7); color: var(--primary, #4d6bfe); }
.zoom-val { min-width: 36px; text-align: center; }
.node-box { fill: #fff; stroke: #4d6bfe; stroke-width: 1.5; }
.node-name { text-anchor: middle; font-size: 13px; fill: #1f2430; font-weight: 600; pointer-events: none; }
.edge-line { stroke: #b9c2d4; stroke-width: 1.5; }
.edge-label { text-anchor: middle; font-size: 11px; fill: #6b7280; }
.row-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.ver-pre { background: var(--bg-soft); border: 1px solid var(--border-light); border-radius: 8px; padding: 12px; font-size: 12px; max-height: 50vh; overflow: auto; line-height: 1.5; }
.modal { min-width: 440px; }
</style>

/* ===== 图视图选中详情：属性 / 关系 / 版本 / 操作 ===== */
.graph-detail { margin-top: 10px; padding: 10px 12px; border: 1px solid var(--border-light, #e9ebf0); border-radius: 10px; background: #fff; }
.detail-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; padding-bottom: 8px; border-bottom: 1px solid #f0f1f5; }
.detail-head b { font-size: 14px; }
.detail-grid { display: grid; grid-template-columns: 1.1fr 1fr 1.2fr; gap: 18px; margin-top: 9px; }
.sec-t { font-size: 12px; font-weight: 600; color: #4b5563; margin-bottom: 6px; }
.detail-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.detail-table td { padding: 4px 6px; border-bottom: 1px solid #f4f5f8; text-align: left; word-break: break-all; }
.detail-table td:first-child { width: 38%; color: #6b7280; }
.detail-list { max-height: 140px; overflow-y: auto; }
.detail-item { padding: 4px 6px; border-radius: 5px; font-size: 12px; color: #374151; cursor: pointer; }
.detail-item:hover { background: #f4f6fb; }
.detail-item .link-btn { margin-left: 6px; }
.clickable { cursor: pointer; color: #4d6bfe; }
.node-box.sel { stroke: #e5484d !important; stroke-width: 3; filter: drop-shadow(0 0 5px rgba(229,72,77,.4)); }
.edge-line.sel { stroke: #e5484d; stroke-width: 3; }
.edge-label.sel { fill: #e5484d; font-weight: 700; }
