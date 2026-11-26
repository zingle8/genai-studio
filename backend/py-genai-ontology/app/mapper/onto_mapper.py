
# -*- coding: utf-8 -*-
"""本体知识服务存储层（SQLite：本体空间/本体/类/关系规则/映射/数据源）

迁移自 app/storage.py；目录层级对齐 py-genai-rag-reranker 分层结构。
"""
import base64
import sqlite3, json, time, os
from contextvars import ContextVar

DB_PATH = os.environ.get("ONTO_DB", os.path.join(os.path.dirname(__file__), "..", "..", "onto.db"))

# ===== 审计上下文：从请求头 Authorization(JWT) 解析操作人 =====
_operator_ctx = ContextVar("onto_operator", default="system")


def current_operator():
    return _operator_ctx.get()


def _jwt_sub(auth: str) -> str:
    try:
        token = auth.split()[-1]
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        sub = json.loads(base64.urlsafe_b64decode(payload)).get("sub")
        return sub or "system"
    except Exception:
        return "system"


class AuditContextMiddleware:
    """纯 ASGI 中间件：在同一 task 内设置/清理操作人上下文"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            headers = dict(scope.get("headers", []))
            auth = headers.get(b"authorization", b"").decode("utf-8", "ignore")
            token = _operator_ctx.set(_jwt_sub(auth))
            try:
                await self.app(scope, receive, send)
            finally:
                _operator_ctx.reset(token)
        else:
            await self.app(scope, receive, send)


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


# ===== 维度表种子数据：领域分类 + 枚举值（UI 下拉与后端校验共用唯一数据源） =====
DIM_DOMAINS = [
    ("structural",      "结构关系",   "类与类之间的结构关系，保存于 tb_onto_rel.rel_kind", "tb_onto_rel.rel_kind"),
    ("semantic",        "业务语义关系", "关系在业务上的语义分类，用于图展示与检索", "tb_onto_rel.semantic_kind"),
    ("mapping",         "映射关系",   "本体到物理数据的映射类型，保存于 tb_onto_mapping.kind", "tb_onto_mapping.kind"),
    ("event_flow",      "事件流关系", "事件类型之间的时序/因果/触发关系", "tb_onto_event_flow.rel_type"),
    ("dependency",      "依赖与规则关系", "规则、版本、对象之间的依赖与约束关系", "tb_onto_link.rel_kind"),
    ("cardinality",     "基数",       "关系两端允许的实例数量，保存于 tb_onto_rel.cardinality", "tb_onto_rel.cardinality"),
    ("version_relation", "版本谱系关系", "本体版本之间的分支/取代/兼容关系", "tb_onto_version_link.rel_kind"),
    ("status",          "生命周期状态", "本体及各对象的发布状态", "各对象 status"),
]

DIM_ITEMS = [
    # structural
    ("structural", "inheritance", "继承", "is-a，子类继承父类的属性与关系，对应存量 parent_name", "子类→父类", 1, ""),
    ("structural", "association", "关联", "普通结构连接，无生命周期依赖", "双向/单向", 1, ""),
    ("structural", "composition", "组合", "强拥有，部分随整体创建与销毁", "整体→部分", 1, ""),
    ("structural", "aggregation", "聚合", "弱拥有，部分可独立存在", "整体→部分", 1, ""),
    ("structural", "dependency",  "依赖", "源的变更会影响目标", "依赖方→被依赖方", 1, ""),
    ("structural", "realization", "实现", "类实现接口或契约规则", "实现方→契约", 1, ""),
    # semantic
    ("semantic", "kinship",     "亲属",    "父子/配偶等亲属语义，如 father_of、spouse_of", "主体→客体", 1, ""),
    ("semantic", "part_of",     "组成",    "部分属于整体", "部分→整体", 1, ""),
    ("semantic", "ownership",   "归属",    "拥有者与被拥有物", "拥有者→物", 1, ""),
    ("semantic", "membership",  "成员",    "个体属于组织或群体", "成员→组织", 1, ""),
    ("semantic", "location",    "位置",    "对象或事件位于某地", "对象→地点", 1, ""),
    ("semantic", "causal",      "因果",    "原因导致结果", "因→果", 1, ""),
    ("semantic", "temporal",    "时序",    "时间先后关系", "先→后", 1, ""),
    ("semantic", "provenance",  "来源派生", "结论派生自证据或数据", "派生→来源", 1, ""),
    ("semantic", "reference",   "引用",    "弱语义引用，不蕴含生命周期依赖", "引用方→被引用方", 1, ""),
    # mapping
    ("mapping", "node",     "实体映射",  "本体类映射到物理表/图节点", "本体→物理", 1, "存量值"),
    ("mapping", "edge",     "关系映射",  "关系映射到外键或边表", "本体→物理", 1, "存量值"),
    ("mapping", "property", "属性映射",  "属性映射到字段", "本体→物理", 0, "待开放"),
    ("mapping", "event",    "事件映射",  "事件类型映射到事件表", "本体→物理", 0, "待开放"),
    ("mapping", "rule",     "规则映射",  "规则映射到校验逻辑或触发器", "本体→物理", 0, "待开放"),
    ("mapping", "alias",    "别名映射",  "同名异义消歧", "本体→物理", 0, "待开放"),
    # event_flow
    ("event_flow", "before",    "早于",       "事件严格先于另一事件",    "前→后", 1, ""),
    ("event_flow", "after",     "晚于",       "事件严格晚于另一事件",    "后→前", 1, ""),
    ("event_flow", "overlaps",  "时间重叠",   "两事件区间部分交叉",      "双向", 1, ""),
    ("event_flow", "during",    "期间",       "事件发生在另一事件期间",  "子→父", 1, ""),
    ("event_flow", "contains",  "包含",       "事件包含另一事件",        "父→子", 1, ""),
    ("event_flow", "meets",     "紧接",       "前事件结束即后事件开始",  "前→后", 1, ""),
    ("event_flow", "causes",    "导致",       "因果驱动，前事件是原因",  "因→果", 1, ""),
    ("event_flow", "triggers",  "触发",       "条件满足后触发事件",      "条件→事件", 1, ""),
    ("event_flow", "enables",   "允许",       "前置事件使后置事件可执行", "允许方→被执行方", 1, ""),
    ("event_flow", "prevents",  "阻止",       "前置事件阻止后置事件",    "阻止方→被阻止方", 1, ""),
    ("event_flow", "part_of",   "子事件",     "组合事件中的子步骤",      "子→父", 1, ""),
    # dependency
    ("dependency", "depends_on",    "依赖于",   "当前对象生效依赖另一对象",   "依赖方→被依赖方", 1, ""),
    ("dependency", "derives_from",  "派生自",   "结论或数据来源于另一对象",   "派生→来源", 1, ""),
    ("dependency", "conflicts_with","冲突",    "两个对象语义互斥，不能同时生效", "双向", 1, ""),
    ("dependency", "supersedes",    "取代",     "新版本覆盖旧版本",           "新→旧", 1, ""),
    ("dependency", "replaces",      "替换",     "等价替换，语义不变",         "替代→原", 1, ""),
    ("dependency", "validates",     "校验",     "规则校验某类或属性",         "规则→被校验对象", 1, ""),
    ("dependency", "references",    "引用",     "弱依赖，仅引用不约束",       "引用方→被引用方", 1, ""),
    ("dependency", "blocks",        "阻断",     "不满足则流程不能继续",       "阻断方→被阻断方", 1, ""),
    ("dependency", "enables",       "启用",     "满足后启用另一对象",         "启用方→被启用方", 1, ""),
    # cardinality
    ("cardinality", "one",          "1..1",     "一对一，存量 one",             "—", 1, "存量值"),
    ("cardinality", "many",         "1..N",     "一对多，存量 many",            "—", 1, "存量值"),
    ("cardinality", "zero_or_one",  "0..1",     "零或一，等价于 one 且 nullable=1", "—", 0, "用 one+nullable 表达"),
    ("cardinality", "zero_or_many", "0..N",     "零或多，等价于 many 且 nullable=1", "—", 0, "用 many+nullable 表达"),
    # version_relation
    ("version_relation", "based_on",        "基于",     "当前版本基于某版本创建",   "新→旧", 1, ""),
    ("version_relation", "supersedes",      "取代",     "当前版本取代前一版本",     "新→旧", 1, ""),
    ("version_relation", "forked_from",     "分叉自",   "从某版本分出独立分支",     "分支→主干", 1, ""),
    ("version_relation", "merges",          "合并自",   "由多个分支合并而来",       "合并→分支", 1, ""),
    ("version_relation", "compatible_with", "兼容",     "跨版本可互操作",           "双向", 1, ""),
    # status
    ("status", "draft",      "草稿",     "编辑中，不对外生效",           "—", 1, ""),
    ("status", "active",     "生效",     "正常可用，默认状态",           "—", 1, "存量值"),
    ("status", "frozen",     "冻结",     "只读锁定，不可编辑",           "—", 1, ""),
    ("status", "deprecated", "废弃",     "不推荐新引用，检查时告警",     "—", 1, ""),
    ("status", "archived",   "归档",     "历史保留，不参与查询",         "—", 1, ""),
    ("status", "disabled",   "停用",     "规则保留定义但不执行",         "—", 1, ""),
    ("status", "broken",     "失效",     "映射指向的物理对象已不存在",   "—", 1, ""),
]


def _seed_dims(c):
    """维度种子：INSERT OR IGNORE，升级不覆盖用户改过的 label/description"""
    for i, (code, name, desc, applies) in enumerate(DIM_DOMAINS):
        c.execute("INSERT OR IGNORE INTO tb_dim_domain(code,name,description,applies_to,sort_order) VALUES(?,?,?,?,?)",
                  (code, name, desc, applies, i))
    for i, (domain, code, label, desc, direction, supported, extra) in enumerate(DIM_ITEMS):
        c.execute("INSERT OR IGNORE INTO tb_dim_item(domain_code,code,label,description,direction,supported,extra,sort_order) "
                  "VALUES(?,?,?,?,?,?,?,?)",
                  (domain, code, label, desc, direction, supported, extra or '{}', i))


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tb_onto_space(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          description TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_ontology(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, scope TEXT DEFAULT 'domain',
          namespace TEXT DEFAULT '', authority TEXT DEFAULT 'normal', version TEXT DEFAULT 'v1',
          status TEXT DEFAULT 'active', comment TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_onto_class(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL,
          name TEXT NOT NULL, parent_name TEXT DEFAULT '', comment TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS tb_onto_rel(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL,
          name TEXT NOT NULL, subj_class TEXT NOT NULL, obj_class TEXT NOT NULL,
          cardinality TEXT DEFAULT 'many' CHECK(cardinality IN ('one','many')),
          nullable INTEGER DEFAULT 1, inherits_from TEXT DEFAULT '', comment TEXT DEFAULT '');
        CREATE TABLE IF NOT EXISTS tb_onto_mapping(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL,
          onto_type TEXT NOT NULL, physical_type TEXT NOT NULL, kind TEXT DEFAULT 'node' CHECK(kind IN ('node','edge')));
        CREATE TABLE IF NOT EXISTS tb_data_source(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, type TEXT DEFAULT 'builtin-demo',
          config TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_onto_version(
          id INTEGER PRIMARY KEY AUTOINCREMENT, ontology_id INTEGER NOT NULL, version_no INTEGER NOT NULL,
          op TEXT NOT NULL, note TEXT DEFAULT '', snapshot TEXT DEFAULT '{}',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_audit_log(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          module TEXT NOT NULL DEFAULT 'ontology',       -- graph | ontology
          target_type TEXT NOT NULL,                     -- ontology/space/class/rel/mapping/version/datasource/graph
          target_id INTEGER DEFAULT 0,
          target_name TEXT DEFAULT '',
          op TEXT NOT NULL,
          detail TEXT DEFAULT '',
          operator TEXT DEFAULT 'system',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE INDEX IF NOT EXISTS idx_audit_target ON tb_audit_log(module, target_id, id DESC);
        CREATE TABLE IF NOT EXISTS tb_dim_domain(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          code TEXT NOT NULL UNIQUE, name TEXT NOT NULL,
          description TEXT DEFAULT '', applies_to TEXT DEFAULT '',
          sort_order INTEGER DEFAULT 0, enabled INTEGER DEFAULT 1,
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_dim_item(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          domain_code TEXT NOT NULL, code TEXT NOT NULL, label TEXT NOT NULL,
          description TEXT DEFAULT '', direction TEXT DEFAULT '',
          supported INTEGER DEFAULT 1, extra TEXT DEFAULT '{}',
          sort_order INTEGER DEFAULT 0, enabled INTEGER DEFAULT 1,
          created_at TEXT DEFAULT (datetime('now','localtime')),
          UNIQUE(domain_code, code));
        CREATE INDEX IF NOT EXISTS idx_dim_item_domain ON tb_dim_item(domain_code, sort_order);
        """)
        _seed_dims(c)
        try:
            c.execute("ALTER TABLE tb_dim_domain ADD COLUMN enabled INTEGER DEFAULT 1")
            c.commit()
        except Exception:
            pass
        # 本体归属空间（对齐知识库 space 模型）
        try:
            c.execute("ALTER TABLE tb_ontology ADD COLUMN space_id INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass


def migrate_ensure_space():
    """本体必须归属本体空间：保证至少一个空间存在，并把未归属的存量本体归入默认空间"""
    if not one("SELECT id FROM tb_onto_space LIMIT 1"):
        run("INSERT INTO tb_onto_space(name, description) VALUES('默认空间','系统自动创建')")
    d = one("SELECT id FROM tb_onto_space ORDER BY id LIMIT 1")
    run("UPDATE tb_ontology SET space_id=? WHERE space_id IS NULL OR space_id=0", (d["id"],))


def rows(sql, args=()):
    with conn() as c:
        return [dict(r) for r in c.execute(sql, args).fetchall()]


def run(sql, args=()):
    with conn() as c:
        cur = c.execute(sql, args)
        c.commit()
        return cur.lastrowid


def one(sql, args=()):
    with conn() as c:
        r = c.execute(sql, args).fetchone()
        return dict(r) if r else None


def exec_many(sql_list):
    with conn() as c:
        for s, a in sql_list:
            c.execute(s, a)
        c.commit()


# ===== 版本快照（对齐图谱模块 tb_graph_version） =====
def snapshot(oid):
    """本体全量快照：本体定义 + 类 + 关系规则 + 映射"""
    return {
        "ontology": one("SELECT * FROM tb_ontology WHERE id=?", (oid,)),
        "classes": rows("SELECT * FROM tb_onto_class WHERE ontology_id=? ORDER BY id", (oid,)),
        "rels": rows("SELECT * FROM tb_onto_rel WHERE ontology_id=? ORDER BY id", (oid,)),
        "mappings": rows("SELECT * FROM tb_onto_mapping WHERE ontology_id=? ORDER BY id", (oid,)),
    }


def bump_version(oid):
    """本体写操作后递增版本号 v1->v2..."""
    o = one("SELECT version FROM tb_ontology WHERE id=?", (oid,))
    cur = o["version"] if o and o["version"] else "v1"
    try:
        n = int(str(cur).lstrip("v")) + 1
    except Exception:
        n = 2
    new = f"v{n}"
    run("UPDATE tb_ontology SET version=? WHERE id=?", (new, oid))
    return new


def audit(target_type, target_id, target_name, op, detail="", module="ontology"):
    run("INSERT INTO tb_audit_log(module, target_type, target_id, target_name, op, detail, operator) VALUES(?,?,?,?,?,?,?)",
        (module, target_type, target_id or 0, target_name or "", op, detail or "", current_operator()))


def audit_list(target_id=None, limit=200):
    if target_id:
        return rows("SELECT * FROM tb_audit_log WHERE target_id=? ORDER BY id DESC LIMIT ?", (target_id, limit))
    return rows("SELECT * FROM tb_audit_log ORDER BY id DESC LIMIT ?", (limit,))


def save_version(oid, op, note=""):
    """写操作后自动快照（version_no 自增），并同步递增本体版本号、记录审计日志"""
    last = one("SELECT MAX(version_no) m FROM tb_onto_version WHERE ontology_id=?", (oid,))
    no = (last["m"] or 0) + 1
    run("INSERT INTO tb_onto_version(ontology_id, version_no, op, note, snapshot) VALUES(?,?,?,?,?)",
        (oid, no, op, note, json.dumps(snapshot(oid), ensure_ascii=False)))
    bump_version(oid)
    tmap = {"ontology": "ontology", "class": "class", "rel": "rel", "mapping": "mapping"}
    target = next((v for k, v in tmap.items() if k in op), "ontology")
    o = one("SELECT name FROM tb_ontology WHERE id=?", (oid,))
    audit(target, oid, (o or {}).get("name", ""), op, f"v{no} {note}" if note else f"v{no}")
    return no


init_db()
migrate_ensure_space()
