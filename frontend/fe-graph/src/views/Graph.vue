<template>
  <div class="page-header">
    <div><div class="page-title">知识图谱</div><div class="page-subtitle">图谱（数据库概念）/ 实体类型 / 节点·属性·关系 / 版本（自动快照·可恢复）</div></div>
    <div class="page-actions">
      <button class="btn btn-ghost" @click="spaceOpen = true">＋ 新建空间</button>
      <button class="btn btn-ghost" @click="openNewGraph">＋ 新建图谱</button>
      <template v-if="curGraph && !isReadonly">
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
            <span v-if="g.editable === false" class="tag" style="font-size:10px;background:#fff7ed;color:#c2410c;" title="本体图谱模块创建的图谱，知识图谱模块只读">只读</span>
            <span class="tree-badge">{{ g.nodeCount }} 节点</span>
            <span v-if="g.db_type === 'neo4j'" class="dot-mini" :class="g.dbOk ? 'green' : 'red'" :title="g.dbOk ? 'Neo4j 已连接' : 'Neo4j 连接失败'"></span>
            <span v-if="g.editable !== false" class="tree-del" @click.stop="delGraph(g)" title="删除图谱">×</span>
          </div>
          <div v-if="!sp.children.length" class="tree-empty text-xs muted">（无图谱）</div>
        </div></div>
      </div>
      <div v-if="!tree.length" class="text-center muted text-sm" style="padding:20px;">暂无图谱空间</div>
    </div>

    <template v-if="curGraph">
      <!-- 主区：tab -->
      <div class="graph-view-main">
        <div class="mode-tabs">
          <button class="mode-tab" :class="{ active: tab === 'view' }" @click="tab = 'view'">图视图</button>
          <button class="mode-tab" :class="{ active: tab === 'entities' }" @click="tab = 'entities'">实体类型</button>
          <button class="mode-tab" :class="{ active: tab === 'nodes' }" @click="tab = 'nodes'">节点与属性</button>
          <button class="mode-tab" :class="{ active: tab === 'edges' }" @click="tab = 'edges'">关系</button>
          <button class="mode-tab" :class="{ active: tab === 'versions' }" @click="tab = 'versions'; loadVersions()">版本</button>
          <button class="mode-tab" :class="{ active: tab === 'audit' }" @click="tab = 'audit'; loadAudit()">审计日志</button>
        </div>

        <!-- 图视图 -->
        <div class="card graph-view-card" v-if="tab === 'view'"><div class="card-body graph-view-body">
          <div class="row-head" style="margin-bottom:8px;">
            <b>{{ curGraph.name }}</b><span class="tag" style="font-size:11px;">{{ curGraph.version || 'v1' }}</span><span class="text-xs muted">{{ nodes.length }} 节点 · {{ edges.length }} 关系 · {{ curGraph.db_type === 'neo4j' ? 'Neo4j' : '内置存储' }} · 按关系聚簇（力导向布局）</span>
            <span v-if="isReadonly" class="tag" style="background:#fff7ed;color:#c2410c;" title="该图谱由本体图谱模块创建，知识图谱模块仅可查看">只读图谱 · 无编辑权限</span>
            <span style="flex:1"></span>
            <MultiNodeSelect v-model="focusIds" :options="allNodes.map(n => ({ value: n.id, label: n.name }))" placeholder="全图（可多选节点）" />
            <select class="form-input" v-model="depth" style="width:96px;" title="邻域展开级数">
              <option v-for="d in 7" :key="d" :value="d">{{ d }} 级</option>
            </select>
            <button class="btn btn-primary btn-sm" :disabled="searching" @click="loadGraph">{{ searching ? '查询中…' : '查询邻域' }}</button>
          </div>
          <div class="svg-box">
            <div class="zoom-ctl graph-zoom">
              <button class="zoom-btn" title="放大视图" @click="zoomIn">➕</button>
              <button class="zoom-btn" title="缩小视图" @click="zoomOut">➖</button>
              <button class="zoom-btn" title="重置视图" @click="zoomReset">⌂</button>
              <span class="text-xs muted zoom-val">{{ Math.round(scale * 100) }}%</span>
            </div>
            <svg class="graph-svg" :class="{ panning }" :viewBox="`0 0 ${canvas.w} ${canvas.h}`"
                 @mousedown="panStart" @mousemove="panMove" @mouseup="panEnd" @mouseleave="panEnd" @wheel.prevent="onWheel">
            <g :transform="viewTransform">
              <defs><marker id="garr" markerWidth="7" markerHeight="7" refX="22" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z" fill="#9aa6bd"/></marker></defs>
              <g v-for="e in edges" :key="'e' + e.id" style="cursor:pointer;" @click="selEdge=e; selNode=null" @mouseenter="showNodeTip($event, 'edge', e)" @mousemove="moveTip" @mouseleave="hoverTip=null">
                <line :x1="pos(e.source_id).x" :y1="pos(e.source_id).y" :x2="pos(e.target_id).x" :y2="pos(e.target_id).y" class="edge-line" :class="{ sel: selEdge?.id === e.id }" marker-end="url(#garr)" />
              </g>
              <g v-for="n in nodes" :key="'n' + n.id" style="cursor:pointer;" @click="selNode=n; selEdge=null" @mouseenter="showNodeTip($event, 'node', n)" @mousemove="moveTip" @mouseleave="hoverTip=null">
                <circle :cx="pos(n.id).x" :cy="pos(n.id).y" :r="(hubIds.has(n.id) ? 42 : 26) * nodeScale" class="node-circle" :class="{ sel: selNode?.id === n.id, hub: hubIds.has(n.id) }" :fill="groupColor(groupKeyOf(n))" />
                <text :x="pos(n.id).x" :y="pos(n.id).y + 4" text-anchor="middle" class="node-circle-name" :style="{ fontSize: 12 * nodeScale + 'px' }">{{ n.name.length > (hubIds.has(n.id)?5:4) ? n.name.slice(0, hubIds.has(n.id)?5:4) : n.name }}</text>
                <text v-if="nodeStatus(n)" :x="pos(n.id).x" :y="pos(n.id).y + (hubIds.has(n.id)?58:40) * nodeScale" text-anchor="middle" class="node-status" :style="{ fontSize: 11 * nodeScale + 'px' }">{{ nodeStatus(n) }}</text>
              </g>
            </g>
            </svg>
          </div>
          <div v-if="hoverTip" class="hover-tip" :style="{ left: hoverTip.x + 'px', top: hoverTip.y + 'px' }">
            <div class="ht-title">{{ hoverTip.title }}</div>
            <div class="ht-sub">{{ hoverTip.sub }}</div>
            <div v-for="r in hoverTip.rows" :key="r[0]" class="ht-row"><span class="ht-key">{{ r[0] }}</span><span class="ht-val">{{ r[1] }}</span></div>
          </div>

          <!-- 选中对象详情：右侧滑出抽屉 -->
          <Transition name="drawer">
          <aside v-if="selNode || selEdge" class="graph-detail-drawer">
            <div class="drawer-head">
              <b>详情与操作</b>
              <button class="drawer-close" title="关闭" @click="closeDetail">×</button>
            </div>
            <div class="graph-detail">
            <template v-if="selNode">
              <div class="detail-head">
                <b>{{ selNode.name }}</b>
                <span class="tag tag-success">节点 · {{ entityName(selNode.entity_id) }}</span>
                <span class="text-xs muted">ID {{ selNode.id }} · 创建 {{ selNode.created_at }}</span>
                <span class="detail-spacer"></span>
                <button v-if="!isReadonly" class="btn btn-primary btn-sm" @click="editNode(selNode)">更新节点</button>
                <button v-if="!isReadonly" class="btn btn-secondary btn-sm" @click="openEdgeFor(selNode)">＋ 关联关系</button>
                <button v-if="!isReadonly" class="btn btn-secondary btn-sm" @click="nodeOpen = true">＋ 节点</button>
                <button v-if="!isReadonly" class="btn btn-danger btn-sm" @click="delNode(selNode)">删除</button>
                <span v-if="isReadonly" class="text-xs muted">该图谱由本体模块创建，仅可查看</span>
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
                <span class="detail-spacer"></span>
                <button v-if="!isReadonly" class="btn btn-primary btn-sm" @click="editEdge(selEdge)">更新关系</button>
                <button v-if="!isReadonly" class="btn btn-secondary btn-sm" @click="nodeOpen = true">＋ 节点</button>
                <button v-if="!isReadonly" class="btn btn-danger btn-sm" @click="delEdge(selEdge)">删除</button>
                <span v-if="isReadonly" class="text-xs muted">该图谱由本体模块创建，仅可查看</span>
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
          </aside>
          </Transition>
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
                  <button v-if="!isReadonly" class="btn btn-ghost btn-sm" @click="editEntity(e)">改</button>
                  <button v-if="!isReadonly" class="btn btn-ghost btn-sm" @click="delEntity(e)">删</button>
                  <span v-if="isReadonly" class="text-xs muted">只读</span>
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
                  <button v-if="!isReadonly" class="btn btn-ghost btn-sm" @click="editNode(n)">改</button>
                  <button v-if="!isReadonly" class="btn btn-ghost btn-sm" @click="delNode(n)">删</button>
                  <span v-if="isReadonly" class="text-xs muted">只读</span>
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
                  <button class="btn btn-ghost btn-sm" @click="editEdge(e)" v-if="!isReadonly && curGraph.db_type !== 'neo4j'">改</button>
                  <button v-if="!isReadonly" class="btn btn-ghost btn-sm" @click="delEdge(e)">删</button>
                  <span v-if="isReadonly" class="text-xs muted">只读</span>
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
                  <button v-if="!isReadonly" class="btn btn-ghost btn-sm" @click="restoreVersion(v)">恢复此版本</button>
                </td>
              </tr>
              <tr v-if="!versions.length"><td colspan="5" class="text-center muted">暂无版本</td></tr>
            </tbody>
          </table></div>
        </div></div>

        <!-- 审计日志 -->
        <div class="card" v-if="tab === 'audit'"><div class="card-body">
          <div class="row-head" style="margin-bottom:8px;">
            <div class="text-xs muted">当前图谱及本模块所有写操作记录（操作人取自登录令牌）；每次增删改自动记录</div>
            <span style="flex:1"></span>
            <button class="btn btn-ghost btn-sm" @click="loadAudit">刷新</button>
          </div>
          <div class="table-wrap"><table>
            <thead><tr><th>时间</th><th>操作人</th><th>操作</th><th>对象</th><th>详情</th></tr></thead>
            <tbody>
              <tr v-for="a in audits" :key="a.id">
                <td class="text-xs muted">{{ a.created_at }}</td>
                <td class="text-xs">{{ a.operator }}</td>
                <td><span class="tag" style="font-size:11px;">{{ a.op }}</span></td>
                <td class="text-xs">{{ a.target_type }} #{{ a.target_id }} {{ a.target_name }}</td>
                <td class="text-xs muted">{{ a.detail || '—' }}</td>
              </tr>
              <tr v-if="!audits.length"><td colspan="5" class="text-center muted">暂无操作记录</td></tr>
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
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { api, withBase } from '../api'
import MultiNodeSelect from '../components/MultiNodeSelect.vue'
const graphs = ref([]); const curGraph = ref(null); const tab = ref('view')
const entities = ref([]); const nodes = ref([]); const edges = ref([]); const versions = ref([]); const audits = ref([])
const focusIds = ref([]); const allNodes = ref([]); const depth = ref(1); const searching = ref(false)
const selNode = ref(null); const selEdge = ref(null)
// 来源非知识图谱模块（如本体图谱模块创建）的图谱只读：前端隐藏写入口，后端强制校验
const isReadonly = computed(() => !!curGraph.value && curGraph.value.editable === false)
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
onMounted(() => { loadPub(); loadGraphs(); loadSpaces(); document.addEventListener('mousedown', onDocClick) })
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocClick))

// 点击抽屉外部关闭详情；点击图中节点/边交给其自身处理，用于切换选中
function onDocClick(e) {
  if (e.target.closest?.('.graph-detail-drawer')) return
  if (selNode.value || selEdge.value) closeDetail()
}

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
async function loadAudit() {
  const r = await api(withBase(`/api/graphs/audit?gid=${curGraph.value?.id || 0}&limit=1000`))
  if (r.code === 0) audits.value = r.data
}

/* ===== 图视图：力导向簇群布局 + 缩放 ===== */
const positions = ref({})        // nodeId -> {x,y}
const canvas = ref({ w: 2600, h: 1800 })
const nodeScale = ref(1)
const scale = ref(1)
const TYPE_COLORS = ['#4d6bfe', '#e5484d', '#12b76a', '#f79009', '#7a5af8', '#06aed4', '#d444f1', '#6b7280']
function typeColor(eid) {
  const i = entities.value.findIndex(x => x.id === eid)
  return TYPE_COLORS[(i < 0 ? 0 : i) % TYPE_COLORS.length]
}
function pos(id) { return positions.value[id] || { x: canvas.value.w / 2, y: canvas.value.h / 2 } }
const hubIds = ref(new Set())
const GROUP_COLORS = ['#4d6bfe', '#12b76a', '#e5484d', '#7a5af8', '#06aed4', '#f79009', '#d444f1', '#0d9488', '#db2777', '#65a30d']
function groupColor(key) {
  const keys = [...new Set(nodes.value.map(groupKeyOf))]
  const i = keys.indexOf(key)
  return GROUP_COLORS[(i < 0 ? 0 : i) % GROUP_COLORS.length]
}

/** 族群放射布局：按辈分/实体类型分群，族群中心 hub + 卫星节点同心环放射，族群在画布上网格分区 */
function groupKeyOf(n) {
  const p = Object.fromEntries(nodeProps(n))
  return p['辈分'] || p['实体类型'] || entityName(n.entity_id) || '其他'
}
function layout() {
  const list = nodes.value
  const P = {}
  if (!list.length) { positions.value = P; hubIds.value = new Set(); return }
  hubIds.value = new Set()
  // 画布随节点规模成比例放大，保证大图谱每个族群有足够放射空间
  const scaleFactor = Math.max(1, Math.min(3.6, Math.sqrt(list.length / 60)))
  const W = Math.round(2600 * scaleFactor), H = Math.round(1800 * scaleFactor), PAD = Math.round(140 * scaleFactor)
  canvas.value = { w: W, h: H }
  nodeScale.value = Math.min(1.5, Math.sqrt(scaleFactor))
  // 1) 按族群分组，族群按节点数降序（大族优先占中间区域）
  const buckets = {}
  for (const n of list) { const k = groupKeyOf(n); (buckets[k] = buckets[k] || []).push(n) }
  const keys = Object.keys(buckets).sort((a, b) => buckets[b].length - buckets[a].length)
  // 2) 族群中心：围绕画布中心按黄金角螺旋散布，避免规则网格的僵硬感
  const G = keys.length
  const centers = []
  if (G === 1) centers.push({ x: W / 2, y: H / 2 })
  else {
    const R = Math.min(W, H) * 0.42
    for (let i = 0; i < G; i++) {
      const a = i * 2.399963; // 黄金角
      const r = i === 0 ? 0 : R * Math.sqrt(i / (G - 1)) * 1.15
      centers.push({ x: W / 2 + r * Math.cos(a), y: H / 2 + r * Math.sin(a) * 0.82 })
    }
  }
  // 度数（用于选 hub）
  const deg = {}
  for (const e of edges.value) { deg[e.source_id] = (deg[e.source_id] || 0) + 1; deg[e.target_id] = (deg[e.target_id] || 0) + 1 }
  // 3) 每族：选度数最高为 hub 置中心，其余按同心环放射排布
  keys.forEach((k, gi) => {
    const members = buckets[k].slice()
    const c = centers[gi]
    members.sort((a, b) => (deg[b.id] || 0) - (deg[a.id] || 0))
    const hub = members.shift()
    P[hub.id] = { x: c.x, y: c.y }
    hubIds.value.add(hub.id)
    const rest = members
    if (!rest.length) return
    // 同心环：环距按画布比例放大，保证大图谱节点不重叠
    const step = 165 * scaleFactor
    const cap = Math.max(6, Math.floor(2 * Math.PI * step / 78))
    let idx = 0, ring = 1
    while (idx < rest.length) {
      const ringCount = Math.min(cap * ring, rest.length - idx)
      const radius = step * ring
      for (let j = 0; j < ringCount; j++) {
        const ang = (j / ringCount) * Math.PI * 2 + (ring % 2) * 0.3
        const n = rest[idx++]
        P[n.id] = { x: c.x + radius * Math.cos(ang), y: c.y + radius * Math.sin(ang) * 0.82 }
      }
      ring++
    }
  })
  // 4) 全局边界钳制
  for (const id in P) { P[id].x = Math.max(PAD, Math.min(W - PAD, P[id].x)); P[id].y = Math.max(PAD, Math.min(H - PAD, P[id].y)) }
  positions.value = P
}
watch([nodes, edges], layout)

function zoomIn() { scale.value = Math.min(2.5, +(scale.value * 1.25).toFixed(3)) }
function zoomOut() { scale.value = Math.max(0.35, +(scale.value / 1.25).toFixed(3)) }
function zoomReset() { scale.value = 1; pan.value = { x: 0, y: 0 } }

/* ===== 画布拖拽平移：按住空白处拖动整体移动节点 ===== */
const pan = ref({ x: 0, y: 0 })
const panning = ref(false)
const panState = ref(null)
function panStart(e) {
  if (e.button !== 0) return
  panState.value = { svg: e.currentTarget, sx: e.clientX, sy: e.clientY, ox: pan.value.x, oy: pan.value.y }
  panning.value = true
  window.addEventListener('mouseup', panEnd, { once: true })
}
function panMove(e) {
  const st = panState.value
  if (!st) return
  const ctm = st.svg.getScreenCTM()
  if (!ctm) return
  pan.value = { x: st.ox + (e.clientX - st.sx) / ctm.a, y: st.oy + (e.clientY - st.sy) / ctm.d }
}
function panEnd() { panState.value = null; panning.value = false }
/** 滚轮缩放：向上滚放大、向下滚缩小 */
function onWheel(e) {
  const f = e.deltaY < 0 ? 1.12 : 1 / 1.12
  scale.value = Math.min(2.5, Math.max(0.35, +(scale.value * f).toFixed(3)))
}
function closeDetail() { selNode.value = null; selEdge.value = null }
const viewTransform = computed(() => `translate(${canvas.value.w / 2 * (1 - scale.value) + pan.value.x} ${canvas.value.h / 2 * (1 - scale.value) + pan.value.y}) scale(${scale.value})`)
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
function nodeStatus(n) {
  const p = Object.fromEntries(nodeProps(n))
  return p['状态'] || p['status'] || ''
}
/* 鼠标悬浮提示：展示属性/状态/关系详情 */
const hoverTip = ref(null)
function showNodeTip(ev, kind, item) {
  if (kind === 'node') {
    hoverTip.value = {
      x: ev.clientX + 14, y: ev.clientY + 14,
      title: item.name, sub: `节点 · ${entityName(item.entity_id)} · ID ${item.id}`,
      rows: nodeProps(item).slice(0, 8)
    }
  } else {
    let ep = []
    try { const o = JSON.parse(item.props || '{}'); ep = o && typeof o === 'object' ? Object.entries(o) : [] } catch {}
    hoverTip.value = {
      x: ev.clientX + 14, y: ev.clientY + 14,
      title: item.rel_type, sub: `关系 · ${nodeName(item.source_id)} → ${nodeName(item.target_id)}`,
      rows: [['起点', nodeName(item.source_id)], ['终点', nodeName(item.target_id)], ...ep].slice(0, 8)
    }
  }
}
function moveTip(ev) { if (hoverTip.value) { hoverTip.value.x = ev.clientX + 14; hoverTip.value.y = ev.clientY + 14 } }
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
/* 图视图主区：视口内动态铺满，避免整页滚动 */
.graph-view-main { flex: 1; min-width: 0; min-height: 0; display: flex; flex-direction: column; gap: 12px; height: calc(100vh - 108px); }
/* 顶部视图 tab：分段按钮，避免文字粘连 */
.graph-view-main > .mode-tabs { display: flex; align-items: center; gap: 4px; flex-wrap: wrap; width: fit-content; max-width: 100%; background: var(--bg-soft, #f5f6fa); border: 1px solid var(--border-light, #e5e7eb); border-radius: 10px; padding: 4px; flex-shrink: 0; }
.graph-view-main > .mode-tabs .mode-tab { border: 1px solid transparent; background: transparent; padding: 7px 18px; border-radius: 8px; cursor: pointer; font-size: 13px; line-height: 1.2; white-space: nowrap; color: var(--text-secondary, #6b7280); transition: background .15s, color .15s, box-shadow .15s; }
.graph-view-main > .mode-tabs .mode-tab:hover { color: var(--text-primary, #111827); background: rgba(255,255,255,.55); }
.graph-view-main > .mode-tabs .mode-tab.active { background: #fff; color: var(--text-primary, #111827); font-weight: 600; box-shadow: 0 1px 3px rgba(0,0,0,.08); border-color: var(--border-light, #e5e7eb); }
.graph-view-card { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.graph-view-body { flex: 1; min-height: 0; display: flex; flex-direction: column; }
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
.graph-svg { width: 100%; flex: 1 1 auto; min-height: 160px; height: auto; background: var(--bg-soft); border-radius: 10px; display: block; cursor: grab; user-select: none; }
.graph-svg.panning { cursor: grabbing; }
.graph-view-body .row-head { flex-shrink: 0; }
/* 选中详情：右侧滑出抽屉 */
.graph-detail-drawer {
  position: fixed; top: 0; right: 0; height: 100vh; width: 480px; max-width: 92vw;
  z-index: 900; background: #fff; border-left: 1px solid var(--border-light, #e9ebf0);
  box-shadow: -10px 0 32px rgba(0,0,0,.14); overflow-y: auto; padding: 16px 20px 28px;
}
.drawer-head { position: sticky; top: -16px; background: #fff; z-index: 1; display: flex; align-items: center; justify-content: space-between; padding: 4px 0 10px; margin-bottom: 8px; border-bottom: 1px solid var(--border-light, #e9ebf0); }
.drawer-head b { font-size: 15px; }
.drawer-close { width: 30px; height: 30px; border-radius: 6px; font-size: 20px; line-height: 1; color: var(--text-secondary, #6b7280); background: var(--bg-soft, #f7f8fa); }
.drawer-close:hover { background: #e9ebf0; color: #111; }
.graph-detail-drawer .graph-detail { margin-top: 0; padding: 0; border: none; border-radius: 0; background: transparent; }
.detail-spacer { flex: 1; }
.graph-detail-drawer .detail-spacer { display: none; }
.graph-detail-drawer .detail-head > .text-xs.muted { flex: 0 0 100%; order: 3; }
.graph-detail-drawer .detail-head .btn { order: 2; flex: 0 0 auto; }
.graph-detail-drawer .detail-grid { grid-template-columns: 1fr; gap: 14px; }
.drawer-enter-active, .drawer-leave-active { transition: transform .26s ease, opacity .26s ease; }
.drawer-enter-from, .drawer-leave-to { transform: translateX(100%); opacity: .7; }
.node-status { font-size: 11px; fill: #e07b39; pointer-events: none; }
.hover-tip { position: fixed; z-index: 9999; pointer-events: none; min-width: 150px; max-width: 280px; background: #1f2430; color: #fff; border-radius: 8px; padding: 8px 10px; box-shadow: 0 6px 20px rgba(0,0,0,.25); font-size: 12px; }
.hover-tip .ht-title { font-weight: 700; font-size: 13px; }
.hover-tip .ht-sub { color: #aab4c8; font-size: 11px; margin: 2px 0 6px; }
.hover-tip .ht-row { display: flex; gap: 8px; padding: 2px 0; border-top: 1px solid rgba(255,255,255,.08); }
.hover-tip .ht-key { color: #9fb3d9; min-width: 48px; flex-shrink: 0; }
.hover-tip .ht-val { word-break: break-all; }
.svg-box { position: relative; flex: 1 1 auto; min-height: 0; display: flex; }
.zoom-ctl { display: inline-flex; align-items: center; gap: 4px; background: #fff; border: 1px solid var(--border-light, #e9ebf0); border-radius: 8px; padding: 2px 6px 2px 2px; }
.graph-zoom { position: absolute; right: 10px; top: 10px; z-index: 2; box-shadow: 0 2px 8px rgba(0,0,0,.08); }
.zoom-btn { width: 28px; height: 26px; border: none; background: none; border-radius: 6px; font-size: 13px; line-height: 1; cursor: pointer; color: var(--text-secondary, #4b5563); transition: background .15s, color .15s; }
.zoom-btn:hover { background: var(--bg-soft, #f0f2f7); color: var(--primary, #4d6bfe); }
.zoom-val { min-width: 36px; text-align: center; }
.node-circle { stroke: #fff; stroke-width: 2; opacity: .92; transition: opacity .15s; }
.node-circle:hover { opacity: 1; }
.node-circle.hub { stroke-width: 3; stroke: rgba(255,255,255,.9); }
.node-circle-name { font-size: 12px; fill: #fff; font-weight: 600; pointer-events: none; }
.node-name { text-anchor: middle; font-size: 13px; fill: #1f2430; font-weight: 600; pointer-events: none; }
.edge-line { stroke: #b9c2d4; stroke-width: 1.4; }
.edge-label { text-anchor: middle; font-size: 11px; fill: #6b7280; }
.row-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.ver-pre { background: var(--bg-soft); border: 1px solid var(--border-light); border-radius: 8px; padding: 12px; font-size: 12px; max-height: 50vh; overflow: auto; line-height: 1.5; }
.modal { min-width: 440px; }

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
.node-circle.sel { stroke: #e5484d !important; stroke-width: 4; filter: drop-shadow(0 0 6px rgba(229,72,77,.5)); }
.edge-line.sel { stroke: #e5484d; stroke-width: 3; }
.edge-label.sel { fill: #e5484d; font-weight: 700; }
</style>
