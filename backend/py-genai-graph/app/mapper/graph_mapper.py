# -*- coding: utf-8 -*-
"""知识图谱服务存储层
- 元数据/版本快照：SQLite
- 图数据（节点/关系）：按图谱配置存 Neo4j（HTTP API）或内置 SQLite
- 版本：每次写操作自动快照（自动递增），可查看/恢复指定版本
"""
import base64
import sqlite3, os, json, requests
from contextvars import ContextVar

from app.config.settings import settings

DB_PATH = settings.db_path

# ===== 审计上下文：从请求头 Authorization(JWT) 解析操作人，供写操作埋点记录 =====
_operator_ctx = ContextVar("graph_operator", default="system")


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
    """纯 ASGI 中间件：在同一 task 内设置/清理操作人上下文，避免 BaseHTTPMiddleware 的 contextvar 丢失"""

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


def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS tb_graph_space(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
          description TEXT DEFAULT '', created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_graph(
          id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE,
          db_type TEXT DEFAULT 'sqlite',           -- sqlite | neo4j | postgresql
          db_config TEXT DEFAULT '',               -- {"uri":"bolt://localhost:7687","user":"neo4j","password":"..."} 等
          description TEXT DEFAULT '',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_graph_entity(
          id INTEGER PRIMARY KEY AUTOINCREMENT, graph_id INTEGER NOT NULL,
          name TEXT NOT NULL,                      -- 实体类型名（如 部门/员工）
          props_schema TEXT DEFAULT '[]',          -- [{"name":"标题","type":"string"},...]
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_graph_node(
          id INTEGER PRIMARY KEY AUTOINCREMENT, graph_id INTEGER NOT NULL,
          entity_id INTEGER DEFAULT 0,             -- 实体类型
          name TEXT NOT NULL, props TEXT DEFAULT '{}',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_graph_edge(
          id INTEGER PRIMARY KEY AUTOINCREMENT, graph_id INTEGER NOT NULL,
          source_id INTEGER NOT NULL, target_id INTEGER NOT NULL, rel_type TEXT NOT NULL,
          props TEXT DEFAULT '{}',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_graph_version(
          id INTEGER PRIMARY KEY AUTOINCREMENT, graph_id INTEGER NOT NULL,
          version_no INTEGER NOT NULL, op TEXT DEFAULT '', note TEXT DEFAULT '',
          snapshot TEXT DEFAULT '{}',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE TABLE IF NOT EXISTS tb_audit_log(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          module TEXT NOT NULL DEFAULT 'graph',        -- graph | ontology
          target_type TEXT NOT NULL,                   -- graph/space/entity/node/edge/version
          target_id INTEGER DEFAULT 0,
          target_name TEXT DEFAULT '',
          op TEXT NOT NULL,                            -- create/update/delete/restore
          detail TEXT DEFAULT '',
          operator TEXT DEFAULT 'system',
          created_at TEXT DEFAULT (datetime('now','localtime')));
        CREATE INDEX IF NOT EXISTS idx_audit_target ON tb_audit_log(module, target_id, id DESC);
        """)
        # 图谱归属空间（对齐知识库 space 模型）
        try:
            c.execute("ALTER TABLE tb_graph ADD COLUMN space_id INTEGER DEFAULT 0")
            c.commit()
        except Exception:
            pass
        # 图谱来源模块：graph=知识图谱模块创建（可编辑）；ontology=本体图谱模块创建（知识图谱侧只读）
        try:
            c.execute("ALTER TABLE tb_graph ADD COLUMN source_module TEXT DEFAULT 'graph'")
            c.commit()
        except Exception:
            pass
        # 图谱版本号（写操作递增 v1/v2/...）
        try:
            c.execute("ALTER TABLE tb_graph ADD COLUMN version TEXT DEFAULT 'v1'")
            c.commit()
        except Exception:
            pass


def migrate_source_module():
    """把本体族谱图谱标记为 ontology 来源（一次性数据修正，幂等）"""
    run("UPDATE tb_graph SET source_module='ontology' WHERE name=? AND (source_module IS NULL OR source_module='graph')",
        ("万家家族族谱",))


def migrate_ensure_space():
    """图谱必须归属图谱空间：保证至少一个空间存在，并把未归属的存量图谱归入默认空间"""
    if not one("SELECT id FROM tb_graph_space LIMIT 1"):
        run("INSERT INTO tb_graph_space(name, description) VALUES('默认空间','系统自动创建')")
    d = one("SELECT id FROM tb_graph_space ORDER BY id LIMIT 1")
    run("UPDATE tb_graph SET space_id=? WHERE space_id IS NULL OR space_id=0", (d["id"],))


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


# ===== Neo4j（HTTP API，免驱动） =====
def neo4j_exec(cfg, cypher, params=None):
    """执行 Cypher（经 7474 HTTP 事务端点）"""
    uri = (cfg.get("uri") or "http://localhost:7474").replace("bolt://", "http://").replace("7687", "7474")
    auth = (cfg.get("user") or "neo4j", cfg.get("password") or "")
    payload = {"statements": [{"statement": cypher, "parameters": params or {}}]}
    r = requests.post(f"{uri}/db/neo4j/tx/commit", json=payload, auth=auth, timeout=10)
    j = r.json()
    if j.get("errors"):
        raise RuntimeError(j["errors"][0].get("message", "Neo4j 错误"))
    return j


def neo4j_ping(cfg):
    try:
        neo4j_exec(cfg, "RETURN 1 AS ok")
        return True
    except Exception:
        return False


# ===== 版本快照 =====
def snapshot(gid):
    """全量快照（SQLite 数据）"""
    return {
        "entities": rows("SELECT * FROM tb_graph_entity WHERE graph_id=?", (gid,)),
        "nodes": rows("SELECT * FROM tb_graph_node WHERE graph_id=?", (gid,)),
        "edges": rows("SELECT * FROM tb_graph_edge WHERE graph_id=?", (gid,)),
    }


def save_version(gid, op, note=""):
    """写操作后自动快照（version_no 自增），并同步递增图谱版本号、记录审计日志"""
    last = one("SELECT MAX(version_no) m FROM tb_graph_version WHERE graph_id=?", (gid,))
    no = (last["m"] or 0) + 1
    run("INSERT INTO tb_graph_version(graph_id, version_no, op, note, snapshot) VALUES(?,?,?,?,?)",
        (gid, no, op, note, json.dumps(snapshot(gid), ensure_ascii=False)))
    bump_version(gid)
    tmap = {"graph": "graph", "entity": "entity", "node": "node", "edge": "edge"}
    target = next((v for k, v in tmap.items() if k in op), "graph")
    g = one("SELECT name FROM tb_graph WHERE id=?", (gid,))
    audit(target, gid, (g or {}).get("name", ""), op, f"v{no} {note}" if note else f"v{no}")
    return no


def bump_version(gid):
    """写操作后递增图谱版本号 v1->v2...，返回新版本号"""
    g = one("SELECT version FROM tb_graph WHERE id=?", (gid,))
    cur = g["version"] if g and g["version"] else "v1"
    try:
        n = int(str(cur).lstrip("v")) + 1
    except Exception:
        n = 2
    new = f"v{n}"
    run("UPDATE tb_graph SET version=? WHERE id=?", (new, gid))
    return new


# ===== 审计日志 =====
def audit(target_type, target_id, target_name, op, detail="", module="graph"):
    run("INSERT INTO tb_audit_log(module, target_type, target_id, target_name, op, detail, operator) VALUES(?,?,?,?,?,?,?)",
        (module, target_type, target_id or 0, target_name or "", op, detail or "", current_operator()))


def audit_list(target_id=None, limit=200):
    if target_id:
        return rows("SELECT * FROM tb_audit_log WHERE target_id=? ORDER BY id DESC LIMIT ?", (target_id, limit))
    return rows("SELECT * FROM tb_audit_log ORDER BY id DESC LIMIT ?", (limit,))


def seed_demo():
    if one("SELECT id FROM tb_graph LIMIT 1"):
        return
    gid = run("INSERT INTO tb_graph(name, db_type, description) VALUES(?,?,?)",
              ("公司组织图谱", "sqlite", "示例：部门/员工/项目"))
    ents = {}
    for en in ["公司", "部门", "员工", "项目"]:
        ents[en] = run("INSERT INTO tb_graph_entity(graph_id, name) VALUES(?,?)", (gid, en))
    nodes = [("公司", "GenAI 科技"), ("部门", "研发部"), ("部门", "市场部"),
             ("员工", "张三"), ("员工", "李四"), ("项目", "Studio 平台")]
    ids = {}
    for en, name in nodes:
        ids[name] = run("INSERT INTO tb_graph_node(graph_id, entity_id, name) VALUES(?,?,?)",
                        (gid, ents[en], name))
    for s, t, rel in [("张三", "研发部", "works_in"), ("李四", "市场部", "works_in"),
                      ("研发部", "GenAI 科技", "belongs_to"), ("张三", "Studio 平台", "join_project")]:
        run("INSERT INTO tb_graph_edge(graph_id, source_id, target_id, rel_type) VALUES(?,?,?,?)",
            (gid, ids[s], ids[t], rel))
    save_version(gid, "seed", "内置示例数据")


init_db()
migrate_source_module()
migrate_ensure_space()
seed_demo()
