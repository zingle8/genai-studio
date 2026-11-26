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
        <span class="db-icon" :class="curDsDbType === 'neo4j' ? 'neo' : ''" :title="curDsDbType === 'neo4j' ? 'Neo4j 数据源' : 'SQL/内置数据源'">{{ curDsDbType === 'neo4j' ? 'N4' : 'SQL' }}</span>
        <button class="btn btn-secondary" @click="spaceOpen=true">＋ 新建空间</button>
        <button class="btn btn-ghost" @click="openNewGraph">＋ 新建图谱</button>
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
              <div class="onto-name">
                <span class="db-icon" :class="ontoDbType(o) === 'neo4j' ? 'neo' : ''" :title="ontoDbType(o) === 'neo4j' ? 'Neo4j 数据源' : 'SQL/内置数据源'">{{ ontoDbType(o) === 'neo4j' ? 'N4' : 'SQL' }}</span>
                <span class="scope-dot" :class="o.scope"></span>{{ o.name }}
              </div>
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
            <button :class="{on: tab==='dataView'}" @click="tab='dataView'; onDataViewTab()">数据关系图</button>
            <button :class="{on: tab==='versions'}" @click="tab='versions'; loadOntoVersions()">版本</button>
            <button :class="{on: tab==='audit'}" @click="tab='audit'; loadAudit()">审计日志</button>
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
            <svg class="onto-svg" :class="{ panning }" viewBox="0 0 1400 900" width="100%" height="100%"
                 @mousedown="panStart($event, 'onto')" @mousemove="panMove" @mouseup="panEnd" @mouseleave="panEnd">
              <defs><marker id="arr" markerWidth="8" markerHeight="8" refX="26" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#94a3b8"/></marker></defs>
              <g :transform="ontoViewTransform">
                <g v-for="e in graphEdges" :key="'e'+e.id" style="cursor:pointer;" @click="selEdge=e; selNode=null" @mouseenter="showOntoTip($event,'rel',e)" @mousemove="moveTip" @mouseleave="hoverTip=null">
                  <line :x1="npos(e.subj_class).x+44" :y1="npos(e.subj_class).y+10" :x2="npos(e.obj_class).x-56" :y2="npos(e.obj_class).y+10" class="onto-edge-line" :class="{sel: selEdge?.id===e.id}" marker-end="url(#arr)"/>
                  <text :x="(npos(e.subj_class).x+npos(e.obj_class).x)/2 - 6" :y="(npos(e.subj_class).y+npos(e.obj_class).y)/2" class="onto-edge-label" :class="{sel: selEdge?.id===e.id}">
                    {{ e.name }} · {{ e.cardinality==='one' ? (e.nullable ? '0..1' : '1..1') : 'N:M' }}{{ e.nullable ? '' : ' 必' }}
                  </text>
                </g>
                <g v-for="n in nodes" :key="'n'+n.id" style="cursor:pointer;" @click="selNode=n; selEdge=null" @mouseenter="showOntoTip($event,'class',n)" @mousemove="moveTip" @mouseleave="hoverTip=null">
                  <rect :x="npos(n.name).x-70" :y="npos(n.name).y-28" width="140" height="56" rx="10" class="onto-node-rect" :class="{sel: selNode?.id===n.id}" :style="{stroke: typeColor(n.name)}"/>
                  <circle :cx="npos(n.name).x-56" :cy="npos(n.name).y-13" r="5" :fill="typeColor(n.name)"/>
                  <text :x="npos(n.name).x+2" :y="npos(n.name).y+2" text-anchor="middle" class="node-name">{{ n.name.length > 9 ? n.name.slice(0,9) : n.name }}</text>
                  <text v-if="n.parent_name" :x="npos(n.name).x+2" :y="npos(n.name).y+18" text-anchor="middle" class="node-sub">⊂ {{ n.parent_name }}</text>
                </g>
              </g>
            </svg>
            <div v-if="hoverTip && tab==='graph'" class="hover-tip" :style="{ left: hoverTip.x+'px', top: hoverTip.y+'px' }">
              <div class="ht-title">{{ hoverTip.title }}</div>
              <div class="ht-sub">{{ hoverTip.sub }}</div>
              <div v-for="r in hoverTip.rows" :key="r[0]" class="ht-row"><span class="ht-key">{{ r[0] }}</span><span class="ht-val">{{ r[1] }}</span></div>
            </div>
            <div class="zoom-ctl onto-zoom">
              <button class="zoom-btn" title="放大视图" @click="ontoZoomIn">➕</button>
              <button class="zoom-btn" title="缩小视图" @click="ontoZoomOut">➖</button>
              <button class="zoom-btn" title="重置视图比例" @click="ontoZoomReset">⌂</button>
              <span class="text-xs muted zoom-val">{{ Math.round(ontoScale*100) }}%</span>
            </div>
            <div class="svg-hint">点击节点/规则在右侧查看属性、状态、版本并操作 · "必" = 不允许为空</div>
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
              <select class="form-select" v-model="relForm.cardinality"><option v-for="c in dimOptions('cardinality')" :key="c.value" :value="c.value">{{ c.label }}</option></select>
              <label class="chk"><input type="checkbox" v-model="relForm.nullable"/> 允许为空</label>
              <input class="form-input" v-model="relForm.inheritsFrom" placeholder="继承关系名（可空）"/>
              <button class="btn btn-primary btn-sm full" @click="createRel">创建规则</button>
            </div>
            <Transition name="drawer">
            <aside v-if="selNode || selEdge" class="graph-detail-drawer">
              <div class="drawer-head">
                <b>本体详情</b>
                <button class="drawer-close" title="关闭" @click="closeOntoDetail">×</button>
              </div>
            <div v-if="selNode" class="sel-card">
              <div class="sel-title"><b>{{ selNode.name }}</b><span class="tag tag-success">类 #{{ selNode.id }}</span></div>
              <div class="sel-meta">本体：{{ cur.name }} · 状态：{{ cur.status || 'active' }} · 版本：{{ cur.version || 'v1' }}</div>
              <div class="sel-meta">父类：{{ selNode.parent_name || '无' }} · 说明：{{ selNode.comment || '无' }}</div>
              <div class="sel-meta">关联规则 {{ relsOfClass(selNode).length }} 条：{{ relsOfClass(selNode).map(r => r.name).join('、') || '无' }}</div>
              <div class="sel-meta">最近变更：{{ ontoVersions.slice(0, 3).map(v => 'v' + v.version_no + ' ' + v.op).join(' / ') || '暂无' }}</div>
              <div class="sel-actions">
                <button class="btn btn-primary btn-sm" @click="editSelClass">更新类</button>
                <button class="btn btn-secondary btn-sm" @click="delClass(selNode)">删除</button>
                <button class="btn btn-secondary btn-sm" @click="closeOntoDetail(); newClassOpen = true">＋ 类</button>
                <button class="btn btn-secondary btn-sm" @click="closeOntoDetail(); newRelOpen = true">＋ 规则</button>
              </div>
            </div>
            <div v-if="selEdge" class="sel-card">
              <div class="sel-title"><b>{{ selEdge.name }}</b><span class="tag">规则 #{{ selEdge.id }}</span></div>
              <div class="sel-meta">本体：{{ cur.name }} · 状态：{{ cur.status || 'active' }} · 版本：{{ cur.version || 'v1' }}</div>
              <div class="sel-meta mono">{{ selEdge.subj_class }} → {{ selEdge.obj_class }}</div>
              <div class="sel-meta">基数：{{ selEdge.cardinality==='one' ? '一对一' : '多对多' }} · {{ selEdge.nullable ? '允许为空' : '不允许为空' }}
                <template v-if="selEdge.inherits_from">· 继承：{{ selEdge.inherits_from }}</template></div>
              <div class="sel-meta">说明：{{ selEdge.comment || '无' }}</div>
              <div class="sel-meta">最近变更：{{ ontoVersions.slice(0, 3).map(v => 'v' + v.version_no + ' ' + v.op).join(' / ') || '暂无' }}</div>
              <div class="sel-actions">
                <button class="btn btn-primary btn-sm" @click="editSelRel">更新规则</button>
                <button class="btn btn-secondary btn-sm" @click="delRel(selEdge)">删除</button>
                <button class="btn btn-secondary btn-sm" @click="closeOntoDetail(); newClassOpen = true">＋ 类</button>
                <button class="btn btn-secondary btn-sm" @click="closeOntoDetail(); newRelOpen = true">＋ 规则</button>
              </div>
            </div>
            </aside>
            </Transition>
            <div v-if="!selNode && !selEdge" class="text-xs muted" style="padding:6px 2px;">点击图中节点或规则查看属性、状态、版本并操作 · 共 {{ nodes.length }} 类 / {{ graphEdges.length }} 规则</div>
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
                  <td><select class="form-select" v-model="r.cardinality"><option v-for="c in dimOptions('cardinality')" :key="c.value" :value="c.value">{{ c.label }}</option></select></td>
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
                  <td><select class="form-select" v-model="relForm.cardinality"><option v-for="c in dimOptions('cardinality')" :key="c.value" :value="c.value">{{ c.label }}</option></select></td>
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
                <select class="form-select" v-model="mapForm.kind"><option v-for="c in dimOptions('mapping')" :key="c.value" :value="c.value">{{ c.label }}</option></select>
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

        <!-- 数据关系图：数据源实例的关系节点视图（物理数据 / 本体视角投影） -->
        <div v-show="tab==='dataView'" class="panel">
          <div class="onto-toolbar" style="margin-top:2px;justify-content:flex-start;flex-wrap:wrap;">
            <span class="text-xs muted">数据源：<b>{{ (dataMode==='view' ? viewData?.source : graphData.source) || '-' }}</b> · <span class="mono">{{ dsSourceLabel }}</span></span>
            <span class="tag" style="font-size:10px;background:#eff6ff;color:#1d4ed8;" title="此处展示的是数据源的物理数据实例，非本体定义（类/规则）本身">数据实例</span>
            <div class="fmt-switch">
              <button :class="{on: dataMode==='physical'}" @click="switchDataMode('physical')">物理数据</button>
              <button :class="{on: dataMode==='view'}" @click="switchDataMode('view')">本体视角</button>
            </div>
            <MultiNodeSelect v-model="dataFocus" :options="dataAllNodes.map(n => ({ value: n.key, label: n.label }))" placeholder="全图（可多选节点）" />
            <select class="form-select" v-model="dataDepth" style="width:96px;" title="邻域展开级数">
              <option v-for="d in 7" :key="d" :value="d">{{ d }} 级</option>
            </select>
            <button class="btn btn-primary btn-sm" @click="runDataNeighborhood">查询邻域</button>
            <button class="btn btn-secondary btn-sm" @click="resetDataNeighborhood">全图</button>
            <span class="text-xs muted" v-if="dataVisibleKeys">显示 {{ dataNodes.length }} 节点 · {{ dataEdges.length }} 边（{{ dataFocus.length }} 起点 / {{ dataDepth }} 级）</span>
          </div>
          <div class="svg-wrap">
            <svg class="onto-svg" :class="{ panning }" viewBox="0 0 3000 2000" width="100%" height="100%"
                 @mousedown="panStart($event, 'data')" @mousemove="panMove" @mouseup="panEnd" @mouseleave="panEnd">
              <defs><marker id="darr" markerWidth="7" markerHeight="7" refX="22" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7 z" fill="#9aa6bd"/></marker></defs>
              <g :transform="dataViewTransform">
                <g v-for="e in dataEdges" :key="'de'+e.key" style="cursor:pointer;" @click="dataSelEdge=e; dataSelNode=null" @mouseenter="showDataTip($event,'edge',e)" @mousemove="moveTip" @mouseleave="hoverTip=null">
                  <line :x1="dpos(e.s).x" :y1="dpos(e.s).y" :x2="dpos(e.t).x" :y2="dpos(e.t).y" class="onto-edge-line" :class="{sel: dataSelEdge?.key===e.key}" marker-end="url(#darr)"/>
                </g>
                <g v-for="n in dataNodes" :key="'dn'+n.key" style="cursor:pointer;" @click="dataSelNode=n; dataSelEdge=null" @mouseenter="showDataTip($event,'node',n)" @mousemove="moveTip" @mouseleave="hoverTip=null">
                  <circle :cx="dpos(n.key).x" :cy="dpos(n.key).y" :r="dataHubKeys.has(n.key) ? 46 : 28" class="node-circle" :class="{sel: dataSelNode?.key===n.key, hub: dataHubKeys.has(n.key)}" :fill="dataGroupColor(dataGroupKeyOf(n))"/>
                  <text :x="dpos(n.key).x" :y="dpos(n.key).y+4" text-anchor="middle" class="node-circle-name">{{ n.label.length > (dataHubKeys.has(n.key)?5:4) ? n.label.slice(0, dataHubKeys.has(n.key)?5:4) : n.label }}</text>
                  <text v-if="nodeStatusOf(n)" :x="dpos(n.key).x" :y="dpos(n.key).y + (dataHubKeys.has(n.key)?62:42)" text-anchor="middle" class="node-status">{{ nodeStatusOf(n) }}</text>
                </g>
              </g>
            </svg>
            <div v-if="hoverTip && tab==='dataView'" class="hover-tip" :style="{ left: hoverTip.x+'px', top: hoverTip.y+'px' }">
              <div class="ht-title">{{ hoverTip.title }}</div>
              <div class="ht-sub">{{ hoverTip.sub }}</div>
              <div v-for="r in hoverTip.rows" :key="r[0]" class="ht-row"><span class="ht-key">{{ r[0] }}</span><span class="ht-val">{{ r[1] }}</span></div>
            </div>
            <div class="zoom-ctl onto-zoom">
              <button class="zoom-btn" title="放大视图" @click="dataZoomIn">➕</button>
              <button class="zoom-btn" title="缩小视图" @click="dataZoomOut">➖</button>
              <button class="zoom-btn" title="重置视图比例" @click="dataZoomReset">⌂</button>
              <span class="text-xs muted zoom-val">{{ Math.round(dataScale*100) }}%</span>
            </div>
            <div class="svg-hint">点击节点/边在右侧查看属性详情 · 可多选节点查询 1~7 级邻域</div>
          </div>
          <Transition name="drawer">
          <aside v-if="dataSelNode || dataSelEdge" class="graph-detail-drawer">
            <div class="drawer-head">
              <b>数据详情</b>
              <button class="drawer-close" title="关闭" @click="closeDataDetail">×</button>
            </div>
            <div class="data-detail">
            <template v-if="dataSelNode">
              <div class="detail-head">
                <b>{{ dataSelNode.label }}</b><span class="tag tag-success">节点 · {{ dataSelNode.type }}</span>
                <span class="text-xs muted">key {{ dataSelNode.key }}</span>
              </div>
              <div class="sec-t" style="margin-top:6px;">属性</div>
              <table class="detail-table"><tbody>
                <tr v-for="p in dataPropEntries(dataSelNode)" :key="p[0]"><td class="mono">{{ p[0] }}</td><td>{{ p[1] }}</td></tr>
                <tr v-if="!dataPropEntries(dataSelNode).length"><td colspan="2" class="muted">（无属性）</td></tr>
              </tbody></table>
            </template>
            <template v-else-if="dataSelEdge">
              <div class="detail-head">
                <b>{{ dataSelEdge.rel }}</b><span class="tag">关系边</span>
              </div>
              <div class="sec-t" style="margin-top:6px;">关系信息</div>
              <table class="detail-table"><tbody>
                <tr><td>起点</td><td class="clickable" @click="selectDataNode(dataSelEdge.s)">{{ dataNodeLabel(dataSelEdge.s) }}</td></tr>
                <tr><td>终点</td><td class="clickable" @click="selectDataNode(dataSelEdge.t)">{{ dataNodeLabel(dataSelEdge.t) }}</td></tr>
                <tr><td>属性</td><td>{{ dataSelEdge.propsText }}</td></tr>
              </tbody></table>
            </template>
            <div v-else class="text-xs muted">点击图中的节点或关系边，查看物理数据的属性详情</div>
            </div>
          </aside>
          </Transition>
        </div>

        <!-- 版本快照 -->
        <div v-show="tab==='versions'" class="panel">
          <div class="check-bar">
            <b>本体版本快照</b><span class="text-xs muted">类 / 关系 / 映射的每次写入自动生成版本</span>
            <span style="flex:1"></span><button class="btn btn-secondary btn-sm" @click="loadOntoVersions">刷新</button>
          </div>
          <div class="table-wrap"><table>
            <thead><tr><th>版本</th><th>操作</th><th>说明</th><th>时间</th><th class="text-right">操作</th></tr></thead>
            <tbody>
              <tr v-for="v in ontoVersions" :key="v.id">
                <td class="mono">v{{ v.version_no }}</td><td>{{ v.op }}</td><td>{{ v.note || '—' }}</td><td class="text-xs muted">{{ v.created_at }}</td>
                <td class="text-right">
                  <button class="btn btn-ghost btn-sm" @click="viewOntoVersion(v)">内容</button>
                  <button class="btn btn-ghost btn-sm" @click="restoreOntoVersion(v)">恢复此版本</button>
                </td>
              </tr>
              <tr v-if="!ontoVersions.length"><td colspan="5" class="text-center muted">暂无版本快照</td></tr>
            </tbody>
          </table></div>
        </div>

        <!-- 审计日志 -->
        <div v-show="tab==='audit'" class="panel">
          <div class="check-bar">
            <b>审计日志</b><span class="text-xs muted">本体及类/规则/映射/数据源等写操作记录（操作人取自登录令牌）</span>
            <span style="flex:1"></span><button class="btn btn-secondary btn-sm" @click="loadAudit">刷新</button>
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
        </div>
      </section>

      <section v-else class="onto-main card empty" style="display:flex;align-items:center;justify-content:center;">
        <div>← 选择或新建一个本体开始定义</div>
      </section>
    </div>

    <!-- 编辑选中类 / 关系规则 -->
    <div v-if="editSel" class="modal-mask" @click.self="editSel=null">
      <div class="modal-card">
        <div class="modal-header"><div class="modal-title">更新{{ editSel.kind === 'class' ? '类' : '关系规则' }}</div><button class="modal-close" @click="editSel=null">×</button></div>
        <div class="modal-body">
          <template v-if="editSel.kind === 'class'">
            <div class="form-row"><label class="form-label">类名</label><input class="form-input" v-model="editForm.name" /></div>
            <div class="form-row"><label class="form-label">父类</label><input class="form-input" v-model="editForm.parentName" placeholder="可空" /></div>
            <div class="form-row"><label class="form-label">说明</label><input class="form-input" v-model="editForm.comment" /></div>
          </template>
          <template v-else>
            <div class="form-row"><label class="form-label">关系名</label><input class="form-input" v-model="editForm.name" /></div>
            <div class="form-row"><label class="form-label">主体类</label><input class="form-input" v-model="editForm.subjClass" /></div>
            <div class="form-row"><label class="form-label">客体类</label><input class="form-input" v-model="editForm.objClass" /></div>
            <div class="form-row"><label class="form-label">基数</label><select class="form-select" v-model="editForm.cardinality"><option v-for="c in dimOptions('cardinality')" :key="c.value" :value="c.value">{{ c.label }}</option></select></div>
            <div class="form-row"><label class="form-label">可空</label><input type="checkbox" v-model="editForm.nullable" /></div>
            <div class="form-row"><label class="form-label">继承</label><input class="form-input" v-model="editForm.inheritsFrom" placeholder="可空" /></div>
            <div class="form-row"><label class="form-label">说明</label><input class="form-input" v-model="editForm.comment" /></div>
          </template>
        </div>
        <div class="modal-footer"><button class="btn btn-secondary" @click="editSel=null">取消</button><button class="btn btn-primary" @click="saveEditSel">保存</button></div>
      </div>
    </div>
    <!-- 版本快照内容 -->
    <div v-if="ontoVerDetail" class="modal-mask" @click.self="ontoVerDetail=null">
      <div class="modal-card modal-lg" style="width:640px;">
        <div class="modal-header"><div class="modal-title">v{{ ontoVerDetail.version_no }} 快照（{{ ontoVerDetail.op }} · {{ ontoVerDetail.created_at }}）</div><button class="modal-close" @click="ontoVerDetail=null">×</button></div>
        <div class="modal-body"><pre class="ver-pre">{{ JSON.stringify(ontoVerDetail.snapshot, null, 2).slice(0, 3000) }}</pre></div>
        <div class="modal-footer"><button class="btn btn-secondary" @click="ontoVerDetail=null">关闭</button><button class="btn btn-primary" @click="restoreOntoVersion(ontoVerDetail); ontoVerDetail=null">恢复此版本</button></div>
      </div>
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
          <div class="form-row"><label class="form-label">归属</label><select class="form-select" v-model="ontoForm.scope"><option v-for="c in dimOptions('scope')" :key="c.value" :value="c.value">{{ c.label }}</option></select></div>
          <div class="form-row"><label class="form-label">权威等级</label><select class="form-select" v-model="ontoForm.authority"><option v-for="c in dimOptions('authority')" :key="c.value" :value="c.value">{{ c.label }}</option></select></div>
          <div class="form-row"><label class="form-label">说明</label><input class="form-input" v-model="ontoForm.comment" placeholder="用途说明（可空）"/></div>
        </div>
        <div class="modal-footer"><button class="btn btn-secondary" @click="newOpen=false">取消</button><button class="btn btn-primary" @click="createOnto">创建</button></div>
      </div>
    </div>

    <div v-if="graphOpen" class="modal-mask" @click.self="graphOpen=false">
      <div class="modal-card">
        <div class="modal-header"><div class="modal-title">新建图谱（本体模块）</div><button class="modal-close" @click="graphOpen=false">×</button></div>
        <div class="modal-body">
          <div class="text-xs muted" style="margin-bottom:12px;">本模块创建的图谱可在知识图谱模块查看，但知识图谱模块无编辑权限。</div>
          <div class="form-row"><label class="form-label">图谱空间 <span style="color:#ef4444;">*</span></label>
            <select class="form-select" v-model="graphForm.space_id">
              <option :value="0" disabled>— 请选择图谱空间 —</option>
              <option v-for="s in graphSpaces" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select></div>
          <div class="form-row"><label class="form-label">图谱名</label><input class="form-input" v-model="graphForm.name" placeholder="如 万家家族族谱"/></div>
          <div class="form-row"><label class="form-label">描述</label><input class="form-input" v-model="graphForm.description" placeholder="用途说明（可空）"/></div>
        </div>
        <div class="modal-footer"><button class="btn btn-secondary" @click="graphOpen=false">取消</button><button class="btn btn-primary" @click="createGraph">创建</button></div>
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
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { api } from '../api'
import MultiNodeSelect from '../components/MultiNodeSelect.vue'

const ontos = ref([])
const datasources = ref([])
const dsId = ref(null)
const kgGraphs = ref([])   // 知识图谱列表（用于解析 graph-ref 数据源的真实库类型）
const dims = ref({})       // 维度表：domain_code -> items[]（UI 下拉统一数据源）

/** 从维度表取下拉选项（只取后端已支持的项，保留 value=code / label=中文名）；未加载时返回空数组，由 :value 兜底当前值 */
function dimOptions(domain) {
  const items = dims.value[domain] || []
  return items.filter(x => x.supported === 1).map(x => ({ value: x.code, label: x.label }))
}
async function loadDims() {
  const r = await api('/api/onto/dims')
  if (r.code === 0) {
    const m = {}
    for (const d of r.data) m[d.code] = d.items || []
    dims.value = m
  }
}

async function loadKgGraphs() {
  const r = await api('/api/graphs')
  if (r.code === 0) kgGraphs.value = r.data
}
/** 数据源真实库类型：neo4j → N4，其余（内置示例/指向图谱的 graph-ref）→ SQL */
function dsDbType(ds) {
  if (!ds) return 'sql'
  if (ds.type === 'neo4j') return 'neo4j'
  if (ds.type === 'graph-ref') {
    let cfg = {}
    try { cfg = typeof ds.config === 'string' ? JSON.parse(ds.config) : (ds.config || {}) } catch {}
    const g = kgGraphs.value.find(x => x.id === Number(cfg.graphId))
    return g?.db_type === 'neo4j' ? 'neo4j' : 'sql'
  }
  return 'sql'
}
const curDsDbType = computed(() => dsDbType(datasources.value.find(d => d.id === dsId.value)))
function ontoDbType(o) {
  const ds = matchDatasource(o.name)
  return ds ? dsDbType(ds) : (kgGraphs.value.find(x => x.name === o.name)?.db_type === 'neo4j' ? 'neo4j' : 'sql')
}
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
// 本体模块创建图谱：来源标记 ontology，知识图谱侧只读展示
const graphOpen = ref(false)
const graphSpaces = ref([])
const graphForm = ref({ name: '', space_id: 0, description: '' })
async function openNewGraph() {
  const r = await api('/api/onto/graph-spaces')
  if (r.code === 0) graphSpaces.value = r.data
  graphForm.value = { name: '', space_id: graphSpaces.value[0]?.id || 0, description: '' }
  graphOpen.value = true
}
async function createGraph() {
  if (!graphForm.value.name.trim()) return alert('图谱名不能为空')
  const r = await api('/api/onto/graphs', { method: 'POST', body: graphForm.value })
  if (r.code !== 0) return alert(r.detail || r.message || '创建失败')
  graphOpen.value = false
  alert('创建成功：该图谱由本体模块创建，知识图谱模块仅可查看（无编辑权限）')
}
const clsForm = ref({ name: '', parentName: '', comment: '' })
const relForm = ref({ name: '', subjClass: '', objClass: '', cardinality: 'many', nullable: true, inheritsFrom: '' })
const mapForm = ref({ kind: 'node', ontoType: '', physicalType: '' })
const newClassOpen = ref(false)
const newRelOpen = ref(false)
const selNode = ref(null)
const ontoVersions = ref([]); const ontoVerDetail = ref(null)
const audits = ref([])
const editSel = ref(null); const editForm = ref({})
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
const nodes = computed(() => visibleClasses.value.map(c => ({ ...c })))
const graphEdges = computed(() => (cur.value?._rels || []).filter(r =>
  nodes.value.some(n => n.name === r.subj_class) && nodes.value.some(n => n.name === r.obj_class)))

/* ===== 关系节点图：力导向簇群布局 + 缩放（对齐知识图谱图视图） ===== */
const nodePositions = ref({})   // name -> {x,y}
const ontoScale = ref(1)
const TYPE_COLORS = ['#4d6bfe', '#e5484d', '#12b76a', '#f79009', '#7a5af8', '#06aed4', '#d444f1', '#6b7280']
function typeColor(name) {
  const i = classes.value.findIndex(c => c.name === name)
  return TYPE_COLORS[(i < 0 ? 0 : i) % TYPE_COLORS.length]
}
function npos(name) { return nodePositions.value[name] || { x: 700, y: 450 } }

/** 力导向模拟：按父类分簇 + 规则边弹簧 + 斥力 + 中心引力 */
function ontologyLayout() {
  const list = nodes.value
  const P = {}
  if (!list.length) { nodePositions.value = P; return }
  const W = 1400, H = 900, PAD = 90, cx = W / 2, cy = H / 2
  const buckets = {}
  for (const n of list) (buckets[n.parent_name || ''] = buckets[n.parent_name || ''] || []).push(n)
  const keys = Object.keys(buckets)
  let bi = 0
  for (const k of keys) {
    const a = (bi / keys.length) * Math.PI * 2
    const br = 220 + 45 * keys.length
    const bx = cx + br * Math.cos(a), by = cy + br * 0.8 * Math.sin(a)
    buckets[k].forEach((n, j) => {
      const ja = j / buckets[k].length * Math.PI * 2
      P[n.name] = { x: bx + 40 * Math.cos(ja) + (Math.random() - 0.5) * 24, y: by + 34 * Math.sin(ja) + (Math.random() - 0.5) * 24 }
    })
    bi++
  }
  const rels = graphEdges.value
  const names = list.map(n => n.name)
  const k = Math.sqrt((W * H) / Math.max(1, list.length)) * 5.2
  const spring = 0.008, ideal = Math.max(150, Math.min(210, 1600 / Math.sqrt(list.length)))
  for (let it = 0; it < 220; it++) {
    const temp = Math.max(2, 70 * (1 - it / 220))
    const F = {}
    for (const nm of names) F[nm] = { x: 0, y: 0 }
    for (let i = 0; i < names.length; i++) {
      for (let j = i + 1; j < names.length; j++) {
        const a = P[names[i]], b = P[names[j]]
        const dx = a.x - b.x, dy = a.y - b.y
        const d2 = dx * dx + dy * dy || 1, d = Math.sqrt(d2)
        const f = k / d2, fx = dx / d * f, fy = dy / d * f
        F[names[i]].x += fx; F[names[i]].y += fy
        F[names[j]].x -= fx; F[names[j]].y -= fy
        if (Math.abs(dx) < 170 && Math.abs(dy) < 100) {
          const sx = Math.sign(dx) || (Math.random() < 0.5 ? -1 : 1)
          const sy = Math.sign(dy) || (Math.random() < 0.5 ? -1 : 1)
          F[names[i]].x += sx * 18; F[names[i]].y += sy * 14
          F[names[j]].x -= sx * 18; F[names[j]].y -= sy * 14
        }
      }
    }
    for (const r of rels) {
      const a = P[r.subj_class], b = P[r.obj_class]
      if (!a || !b) continue
      const dx = b.x - a.x, dy = b.y - a.y, d = Math.sqrt(dx * dx + dy * dy) || 1
      const f = spring * (d - ideal), fx = dx / d * f, fy = dy / d * f
      F[r.subj_class].x += fx; F[r.subj_class].y += fy
      F[r.obj_class].x -= fx; F[r.obj_class].y -= fy
    }
    for (const nm of names) {
      const p = P[nm]
      F[nm].x += (cx - p.x) * 0.0008; F[nm].y += (cy - p.y) * 0.0008
      const d = Math.sqrt(F[nm].x ** 2 + F[nm].y ** 2) || 1
      const lim = Math.min(d, temp)
      p.x += F[nm].x / d * lim; p.y += F[nm].y / d * lim
      p.x = Math.max(PAD, Math.min(W - PAD, p.x))
      p.y = Math.max(PAD, Math.min(H - PAD, p.y))
    }
  }
  // 确定性去重叠：类节点框约 140x56（含间距用 165x80）
  for (let pass = 0; pass < 120; pass++) {
    let moved = false
    for (let i = 0; i < names.length; i++) {
      for (let j = i + 1; j < names.length; j++) {
        const a = P[names[i]], b = P[names[j]]
        const dx = a.x - b.x, dy = a.y - b.y
        if (Math.abs(dx) < 165 && Math.abs(dy) < 80) {
          const ox = (165 - Math.abs(dx)) / 2 + 1, oy = (80 - Math.abs(dy)) / 2 + 1
          const sx = dx >= 0 ? 1 : -1, sy = dy >= 0 ? 1 : -1
          if (Math.abs(dx) / 165 > Math.abs(dy) / 80) { a.x += sx * ox; b.x -= sx * ox }
          else { a.y += sy * oy; b.y -= sy * oy }
          moved = true
        }
      }
    }
    for (const nm of names) { P[nm].x = Math.max(PAD, Math.min(W - PAD, P[nm].x)); P[nm].y = Math.max(PAD, Math.min(H - PAD, P[nm].y)) }
    if (!moved) break
  }
  nodePositions.value = P
}
watch([nodes, graphEdges], ontologyLayout)

function ontoZoomIn() { ontoScale.value = Math.min(2.5, +(ontoScale.value * 1.25).toFixed(3)) }
function ontoZoomOut() { ontoScale.value = Math.max(0.35, +(ontoScale.value / 1.25).toFixed(3)) }
function ontoZoomReset() { ontoScale.value = 1; pan.value = { x: 0, y: 0 } }
const ontoViewTransform = computed(() => `translate(${500 * (1 - ontoScale.value) + pan.value.x} ${310 * (1 - ontoScale.value) + pan.value.y}) scale(${ontoScale.value})`)
const physNodes = computed(() => graphData.value.nodes || [])
const physEdges = computed(() => graphData.value.edges || [])
const physTypes = computed(() => [...new Set([...physNodes.value.map(n => n.type), ...physEdges.value.map(e => e.type)])])
const viewNodes = computed(() => viewData.value?.nodes || [])
const viewEdges = computed(() => viewData.value?.edges || [])

/* ===== 数据关系图：把数据源实例（物理数据 / 本体投影）画成关系节点图 ===== */
const dataMode = ref('physical')
const dataFocus = ref([])
const dataDepth = ref(1)
const dataVisibleKeys = ref(null)   // null=全图；Set=邻域
const dataSelNode = ref(null)
const dataSelEdge = ref(null)
const dataPositions = ref({})
const dataScale = ref(1)

/** 归一化节点/边：兼容 graph-ref（id/name/props字符串/source_id/target_id/rel_type）与 builtin-demo（id/type/props对象/from/to） */
function normalizeData(nodesRaw, edgesRaw) {
  const ns = (nodesRaw || []).map((n, i) => {
    const key = String(n.id ?? i)
    const props = n.props && typeof n.props === 'object' ? n.props : parseProps(n.props)
    const label = n.name || props['姓名'] || props['名称'] || props.name || key
    return { key, label, type: n.type || '节点', props }
  })
  const keys = new Set(ns.map(n => n.key))
  const es = (edgesRaw || []).map((e, i) => {
    const s = String(e.source_id ?? e.from ?? '')
    const t = String(e.target_id ?? e.to ?? '')
    const rel = e.rel_type || e.type || '关系'
    const props = e.props && typeof e.props === 'object' ? e.props : parseProps(e.props)
    return { key: String(e.id ?? i), s, t, rel, props, propsText: JSON.stringify(props) }
  }).filter(e => keys.has(e.s) && keys.has(e.t))
  return { nodes: ns, edges: es }
}
function parseProps(s) {
  try { const o = JSON.parse(s || '{}'); return o && typeof o === 'object' ? o : {} } catch { return {} }
}
const dataAll = computed(() => dataMode.value === 'view'
  ? normalizeData(viewNodes.value, viewEdges.value)
  : normalizeData(physNodes.value, physEdges.value))
const dataAllNodes = computed(() => dataAll.value.nodes)
const dataNodes = computed(() => dataVisibleKeys.value
  ? dataAll.value.nodes.filter(n => dataVisibleKeys.value.has(n.key))
  : dataAll.value.nodes)
const dataEdges = computed(() => {
  if (!dataVisibleKeys.value) return dataAll.value.edges
  return dataAll.value.edges.filter(e => dataVisibleKeys.value.has(e.s) && dataVisibleKeys.value.has(e.t))
})
const TYPE_COLORS_D = ['#4d6bfe', '#e5484d', '#12b76a', '#f79009', '#7a5af8', '#06aed4', '#d444f1', '#6b7280']
function dColor(type) {
  const types = [...new Set(dataAll.value.nodes.map(n => n.type))]
  const i = types.indexOf(type)
  return TYPE_COLORS_D[(i < 0 ? 0 : i) % TYPE_COLORS_D.length]
}
function dataPropEntries(n) { return Object.entries(n?.props || {}) }
function nodeStatusOf(n) { const p = n?.props || {}; return p['状态'] || p.status || '' }
/* 鼠标悬浮提示 */
const hoverTip = ref(null)
function moveTip(ev) { if (hoverTip.value) { hoverTip.value.x = ev.clientX + 14; hoverTip.value.y = ev.clientY + 14 } }
function showOntoTip(ev, kind, item) {
  if (kind === 'class') {
    hoverTip.value = { x: ev.clientX + 14, y: ev.clientY + 14, title: item.name,
      sub: `本体类 · ${item.parent_name ? '父类 ' + item.parent_name : '根类'}`,
      rows: [['权威等级', item.authority || item.scope || '—'], ['说明', item.comment || '—']].filter(r => r[1] !== '—') }
  } else {
    hoverTip.value = { x: ev.clientX + 14, y: ev.clientY + 14, title: item.name,
      sub: `规则 · ${item.subj_class} → ${item.obj_class}`,
      rows: [['基数', item.cardinality === 'one' ? (item.nullable ? '0..1' : '1..1') : 'N:M'], ['可空', item.nullable ? '是' : '否'], ['说明', item.comment || '—']].slice(0, 8) }
  }
}
function showDataTip(ev, kind, item) {
  if (kind === 'node') {
    hoverTip.value = { x: ev.clientX + 14, y: ev.clientY + 14, title: item.label,
      sub: `节点 · ${item.type} · ${item.key}`,
      rows: dataPropEntries(item).slice(0, 8) }
  } else {
    hoverTip.value = { x: ev.clientX + 14, y: ev.clientY + 14, title: item.rel,
      sub: `关系 · ${dataNodeLabel(item.s)} → ${dataNodeLabel(item.t)}`,
      rows: [['起点', dataNodeLabel(item.s)], ['终点', dataNodeLabel(item.t)], ['属性', item.propsText || '—']].slice(0, 8) }
  }
}
function dataNodeLabel(key) { return dataAll.value.nodes.find(n => n.key === key)?.label || '#' + key }
function selectDataNode(key) { const n = dataNodes.value.find(x => x.key === key); if (n) { dataSelEdge.value = null; dataSelNode.value = n } }
function runDataNeighborhood() {
  const starts = dataFocus.value || []
  if (!starts.length) { dataVisibleKeys.value = null; return }
  let front = new Set(starts), seen = new Set(starts)
  for (let i = 0; i < Math.max(1, Math.min(7, dataDepth.value)); i++) {
    const nxt = new Set()
    for (const e of dataAll.value.edges) {
      if (front.has(e.s)) nxt.add(e.t)
      if (front.has(e.t)) nxt.add(e.s)
    }
    seen = new Set([...seen, ...nxt])
    front = new Set([...nxt].filter(x => !front.has(x)))
  }
  dataVisibleKeys.value = seen
  dataSelNode.value = null; dataSelEdge.value = null
}
function resetDataNeighborhood() { dataFocus.value = []; dataVisibleKeys.value = null; dataDepth.value = 1; dataSelNode.value = null; dataSelEdge.value = null }
function closeDataDetail() { dataSelNode.value = null; dataSelEdge.value = null }
function closeOntoDetail() { selNode.value = null; selEdge.value = null }
function switchDataMode(m) {
  dataMode.value = m
  dataFocus.value = []; dataVisibleKeys.value = null
  dataSelNode.value = null; dataSelEdge.value = null
  if (m === 'view' && !viewData.value) loadView()
}
function onDataViewTab() { if (dataMode.value === 'view' && !viewData.value) loadView() }

/** 族群放射布局：按辈分/类型分群，hub 居中 + 卫星同心环 */
function dataGroupKeyOf(n) {
  const p = n?.props || {}
  return p['辈分'] || p['实体类型'] || n.type || '其他'
}
function dataLayout() {
  const list = dataNodes.value, rels = dataEdges.value
  const P = {}
  if (!list.length) { dataPositions.value = P; dataHubKeys.value = new Set(); return }
  dataHubKeys.value = new Set()
  const W = 3000, H = 2000, PAD = 140
  const buckets = {}
  for (const n of list) { const k = dataGroupKeyOf(n); (buckets[k] = buckets[k] || []).push(n) }
  const keys = Object.keys(buckets).sort((a, b) => buckets[b].length - buckets[a].length)
  const G = keys.length, centers = []
  if (G === 1) centers.push({ x: W / 2, y: H / 2 })
  else {
    const R = Math.min(W, H) * 0.36
    for (let i = 0; i < G; i++) {
      const a = i * 2.399963
      const r = i === 0 ? 0 : R * Math.sqrt(i / (G - 1)) * 1.15
      centers.push({ x: W / 2 + r * Math.cos(a), y: H / 2 + r * Math.sin(a) * 0.82 })
    }
  }
  const deg = {}
  for (const e of rels) { deg[e.s] = (deg[e.s] || 0) + 1; deg[e.t] = (deg[e.t] || 0) + 1 }
  keys.forEach((k, gi) => {
    const members = buckets[k].slice()
    const c = centers[gi]
    members.sort((a, b) => (deg[b.key] || 0) - (deg[a.key] || 0))
    const hub = members.shift()
    P[hub.key] = { x: c.x, y: c.y }
    dataHubKeys.value.add(hub.key)
    const rest = members
    if (!rest.length) return
    const cap = Math.max(6, Math.floor(2 * Math.PI * 170 / 90))
    let idx = 0, ring = 1
    while (idx < rest.length) {
      const cnt = Math.min(cap * ring, rest.length - idx)
      const radius = 170 * ring
      for (let j = 0; j < cnt; j++) {
        const ang = (j / cnt) * Math.PI * 2 + (ring % 2) * 0.3
        const n = rest[idx++]
        P[n.key] = { x: c.x + radius * Math.cos(ang), y: c.y + radius * Math.sin(ang) * 0.82 }
      }
      ring++
    }
  })
  for (const id in P) { P[id].x = Math.max(PAD, Math.min(W - PAD, P[id].x)); P[id].y = Math.max(PAD, Math.min(H - PAD, P[id].y)) }
  dataPositions.value = P
}
watch([dataNodes, dataEdges], dataLayout)
function dpos(key) { return dataPositions.value[key] || { x: 1500, y: 1000 } }
const dataHubKeys = ref(new Set())
const DATA_GROUP_COLORS = ['#4d6bfe', '#12b76a', '#e5484d', '#7a5af8', '#06aed4', '#f79009', '#d444f1', '#0d9488', '#db2777', '#65a30d']
function dataGroupColor(key) {
  const keys = [...new Set(dataNodes.value.map(dataGroupKeyOf))]
  const i = keys.indexOf(key)
  return DATA_GROUP_COLORS[(i < 0 ? 0 : i) % DATA_GROUP_COLORS.length]
}
function dataZoomIn() { dataScale.value = Math.min(2.5, +(dataScale.value * 1.25).toFixed(3)) }
function dataZoomOut() { dataScale.value = Math.max(0.35, +(dataScale.value / 1.25).toFixed(3)) }
function dataZoomReset() { dataScale.value = 1; pan.value = { x: 0, y: 0 } }
const dataViewTransform = computed(() => `translate(${1500 * (1 - dataScale.value) + pan.value.x} ${1000 * (1 - dataScale.value) + pan.value.y}) scale(${dataScale.value})`)

/* ===== 画布拖拽平移：按住空白处拖动整体移动节点 ===== */
const pan = ref({ x: 0, y: 0 })
const panning = ref(false)
const panState = ref(null)
function panStart(e, key) {
  if (e.button !== 0) return
  panState.value = { svg: e.currentTarget, key, sx: e.clientX, sy: e.clientY, ox: pan.value.x, oy: pan.value.y }
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

/* 数据源随本体自动匹配：本体名与数据源名互相包含则优先（如 万家家族族谱 ⊂ 万家家族族谱·实例数据），否则取内置示例 */
function matchDatasource(ontoName) {
  const list = datasources.value || []
  if (!list.length) return null
  return list.find(d => d.name.includes(ontoName) || ontoName.includes(d.name.split('·')[0])) || list[0]
}
const currentDs = computed(() => datasources.value.find(d => d.id === dsId.value) || null)
const dsSourceLabel = computed(() => {
  const d = currentDs.value
  if (!d) return '—'
  if (d.type === 'graph-ref') {
    let cfg = {}; try { cfg = JSON.parse(d.config || '{}') } catch {}
    return `图谱模块 graph.db · 图谱 #${cfg.graphId || cfg.graph_id || '?'}`
  }
  if (d.type === 'builtin-demo') return '内置示例数据（非真实图谱）'
  return d.type
})

onMounted(async () => {
  loadSpaces(); loadOntos(); loadKgGraphs(); loadDims()
  document.addEventListener('mousedown', onDocClick)
  const d = await api('/api/onto/datasources')
  if (d.code === 0) { datasources.value = d.data; dsId.value = d.data[0]?.id }
})
onBeforeUnmount(() => document.removeEventListener('mousedown', onDocClick))

// 点击抽屉外部关闭详情；点击图中节点/边交给其自身处理，用于切换选中
function onDocClick(e) {
  if (e.target.closest?.('.graph-detail-drawer')) return
  if (selNode.value || selEdge.value) closeOntoDetail()
  if (dataSelNode.value || dataSelEdge.value) closeDataDetail()
}

// 数据源切换（自动匹配或手动选择）时联动刷新图数据与本体投影
watch(dsId, async () => {
  viewData.value = null
  await loadGraphData()
  if (tab.value === 'dataView' && dataMode.value === 'view' && cur.value) loadView()
})

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
    resetNeighborhood(); resetDataNeighborhood()
    // 自动切换到与该本体匹配的数据源（如 万家家族族谱 → 万家家族族谱·实例数据 graph-ref）
    const ds = matchDatasource(o.name)
    if (ds && ds.id !== dsId.value) dsId.value = ds.id
    await loadMappings(); await loadOntoVersions()
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
/* ===== 选中对象：关系列表 / 更新弹窗 / 版本快照 ===== */
function relsOfClass(n) { return (cur.value?._rels || []).filter(r => r.subj_class === n.name || r.obj_class === n.name) }
function editSelClass() {
  editForm.value = { name: selNode.value.name, parentName: selNode.value.parent_name || '', comment: selNode.value.comment || '' }
  editSel.value = { kind: 'class' }
}
function editSelRel() {
  const r = selEdge.value
  editForm.value = { name: r.name, subjClass: r.subj_class, objClass: r.obj_class, cardinality: r.cardinality,
    nullable: !!r.nullable, inheritsFrom: r.inherits_from || '', comment: r.comment || '' }
  editSel.value = { kind: 'rel' }
}
async function saveEditSel() {
  if (!editForm.value.name?.trim()) return alert('名称不能为空')
  if (editSel.value.kind === 'class') {
    await saveClass({ id: selNode.value.id, name: editForm.value.name, parent_name: editForm.value.parentName, comment: editForm.value.comment })
  } else {
    await saveRel({ id: selEdge.value.id, name: editForm.value.name, subj_class: editForm.value.subjClass,
      obj_class: editForm.value.objClass, cardinality: editForm.value.cardinality,
      nullable: editForm.value.nullable, inherits_from: editForm.value.inheritsFrom, comment: editForm.value.comment })
  }
  editSel.value = null
}
async function loadOntoVersions() {
  if (!cur.value) return
  const r = await api(`/api/onto/${cur.value.id}/versions`)
  if (r.code === 0) ontoVersions.value = r.data
}
async function loadAudit() {
  const r = await api(`/api/onto/audit?oid=${cur.value?.id || 0}&limit=1000`)
  if (r.code === 0) audits.value = r.data
}
async function viewOntoVersion(v) {
  const r = await api(`/api/onto/${cur.value.id}/versions/${v.version_no}`)
  if (r.code === 0) ontoVerDetail.value = r.data
}
async function restoreOntoVersion(v) {
  if (!confirm(`恢复到 v${v.version_no}？当前数据会先自动保存为新版本。`)) return
  const r = await api(`/api/onto/${cur.value.id}/versions/${v.version_no}/restore`, { method: 'POST' })
  if (r.code === 0) { alert(`已恢复到 v${v.version_no}`); selNode.value = null; selEdge.value = null; await selectOnto(cur.value) }
  else alert(r.message || r.detail || '恢复失败')
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
  mapForm.value = { kind: 'node', ontoType: '', physicalType: '' }; await loadMappings(); await loadOntoVersions()
}
async function delMap(m) { await api(`/api/onto/mappings/${m.id}`, { method: 'DELETE' }); await loadMappings(); await loadOntoVersions() }
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
.db-icon { width: 30px; height: 22px; border-radius: 5px; background: #6b7280; color: #fff; font-size: 10px; font-weight: 700; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0; }
.db-icon.neo { background: #018bff; }
.header-actions .db-icon { margin-left: -6px; }
.onto-svg { cursor: grab; user-select: none; }
.onto-svg.panning { cursor: grabbing; }
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

/* 关系节点图（对齐知识图谱图视图） */
.svg-wrap { position: relative; border: 1px solid var(--border-light, #e9ebf0); border-radius: 10px; background: var(--bg-soft, #f0f2f7); min-height: 340px; flex: 1; overflow: hidden; }
.svg-hint { position: absolute; left: 10px; bottom: 8px; font-size: 11.5px; color: var(--text-muted, #9ca3af); }
.onto-node-rect { fill: #fff; stroke: #4d6bfe; stroke-width: 1.5; }
.onto-node-rect.sel { stroke: #e5484d !important; stroke-width: 3; filter: drop-shadow(0 0 5px rgba(229,72,77,.4)); }
.node-name { font-size: 13px; font-weight: 600; fill: #1f2430; pointer-events: none; }
.node-sub { font-size: 10.5px; fill: #9ca3af; pointer-events: none; }
.onto-edge-line { stroke: #b9c2d4; stroke-width: 1.5; }
.onto-edge-line.sel { stroke: #e5484d; stroke-width: 3; }
.onto-edge-label { font-size: 11px; fill: #6b7280; pointer-events: none; }
.onto-edge-label.sel { fill: #e5484d; font-weight: 700; }
.zoom-ctl { position: absolute; right: 10px; top: 10px; display: inline-flex; align-items: center; gap: 4px; background: #fff; border: 1px solid var(--border-light, #e9ebf0); border-radius: 8px; padding: 2px 6px 2px 2px; z-index: 2; }
.zoom-btn { width: 28px; height: 26px; border: none; background: none; border-radius: 6px; font-size: 13px; line-height: 1; cursor: pointer; color: var(--text-secondary, #4b5563); transition: background .15s, color .15s; }
.zoom-btn:hover { background: var(--bg-soft, #f0f2f7); color: var(--primary, #4d6bfe); }
.zoom-val { min-width: 36px; text-align: center; }
.node-status { font-size: 11px; fill: #e07b39; pointer-events: none; }
.node-circle { stroke: #fff; stroke-width: 2; opacity: .92; transition: opacity .15s; }
.node-circle:hover { opacity: 1; }
.node-circle.hub { stroke-width: 3; stroke: rgba(255,255,255,.9); }
.node-circle.sel { stroke: #e5484d !important; stroke-width: 4; filter: drop-shadow(0 0 6px rgba(229,72,77,.5)); }
.node-circle-name { font-size: 12px; fill: #fff; font-weight: 600; pointer-events: none; }
.hover-tip { position: fixed; z-index: 9999; pointer-events: none; min-width: 150px; max-width: 280px; background: #1f2430; color: #fff; border-radius: 8px; padding: 8px 10px; box-shadow: 0 6px 20px rgba(0,0,0,.25); font-size: 12px; }
.hover-tip .ht-title { font-weight: 700; font-size: 13px; }
.hover-tip .ht-sub { color: #aab4c8; font-size: 11px; margin: 2px 0 6px; }
.hover-tip .ht-row { display: flex; gap: 8px; padding: 2px 0; border-top: 1px solid rgba(255,255,255,.08); }
.hover-tip .ht-key { color: #9fb3d9; min-width: 48px; flex-shrink: 0; }
.hover-tip .ht-val { word-break: break-all; }
/* 操作区置于全图之前：横向工具条，展开表单/详情时换行到下一行 */
.edit-col { order: -1; width: 100%; flex-shrink: 0; display: flex; flex-direction: row; flex-wrap: wrap; align-items: center; gap: 8px; }
.edit-col > .btn.full { width: auto; flex: 0 0 auto; }
.edit-col > .text-xs.muted { flex: 1 1 auto; text-align: right; }
.full { width: 100%; }
.mini-form { flex: 1 1 100%; display: flex; flex-direction: row; flex-wrap: wrap; align-items: center; gap: 6px; padding: 8px; background: var(--bg-soft, #f7f8fa); border-radius: 8px; }
.mini-form .form-input, .mini-form .form-select { flex: 1 1 160px; width: auto; font-size: 12.5px; padding: 6px 8px; }
.mini-form .btn { flex: 0 0 auto; }
.mini-form .btn.full { width: auto; }
.edit-col .sel-card { flex: 1 1 100%; }
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

<style>
/* 本体选中详情卡 */
.sel-card { padding: 10px !important; }
.sel-title { display: flex; align-items: center; gap: 8px; margin-bottom: 6px; }
.sel-meta { font-size: 11.5px; color: #6b7280; line-height: 1.6; word-break: break-all; }
.sel-actions { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 8px; }

/* 数据关系图详情 */
.data-detail { border: 1px solid var(--border-light, #e9ebf0); border-radius: 10px; padding: 8px 12px; background: #fff; max-height: 200px; overflow-y: auto; }
.detail-head { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.detail-head b { font-size: 14px; }
.detail-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.detail-table td { padding: 4px 6px; border-bottom: 1px solid #f4f5f8; text-align: left; word-break: break-all; }
.detail-table td:first-child { width: 30%; color: #6b7280; }
.clickable { cursor: pointer; color: #4d6bfe; }

/* 数据详情：右侧滑出抽屉（与知识图谱一致） */
.graph-detail-drawer {
  position: fixed; top: 0; right: 0; height: 100vh; width: 480px; max-width: 92vw;
  z-index: 900; background: #fff; border-left: 1px solid var(--border-light, #e9ebf0);
  box-shadow: -10px 0 32px rgba(0,0,0,.14); overflow-y: auto; padding: 16px 20px 28px;
}
.drawer-head { position: sticky; top: -16px; background: #fff; z-index: 1; display: flex; align-items: center; justify-content: space-between; padding: 4px 0 10px; margin-bottom: 8px; border-bottom: 1px solid var(--border-light, #e9ebf0); }
.drawer-head b { font-size: 15px; }
.drawer-close { width: 30px; height: 30px; border-radius: 6px; font-size: 20px; line-height: 1; color: var(--text-secondary, #6b7280); background: var(--bg-soft, #f7f8fa); }
.drawer-close:hover { background: #e9ebf0; color: #111; }
.graph-detail-drawer .data-detail { max-height: none; border: none; border-radius: 0; padding: 0; background: transparent; overflow: visible; }
.graph-detail-drawer .sel-card { border: none; padding: 0 !important; background: transparent; }
.graph-detail-drawer .sel-actions { margin-top: 14px; }
.drawer-enter-active, .drawer-leave-active { transition: transform .26s ease, opacity .26s ease; }
.drawer-enter-from, .drawer-leave-to { transform: translateX(100%); opacity: .7; }
</style>
