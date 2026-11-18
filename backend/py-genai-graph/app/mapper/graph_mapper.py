# -*- coding: utf-8 -*-
"""知识图谱服务存储层
- 元数据/版本快照：SQLite
- 图数据（节点/关系）：按图谱配置存 Neo4j（HTTP API）或内置 SQLite
- 版本：每次写操作自动快照（自动递增），可查看/恢复指定版本
"""
import sqlite3, os, json, requests

from app.config.settings import settings

DB_PATH = settings.db_path


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.executescript("""
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
        """)


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
    """写操作后自动快照（version_no 自增）"""
    last = one("SELECT MAX(version_no) m FROM tb_graph_version WHERE graph_id=?", (gid,))
    no = (last["m"] or 0) + 1
    run("INSERT INTO tb_graph_version(graph_id, version_no, op, note, snapshot) VALUES(?,?,?,?,?)",
        (gid, no, op, note, json.dumps(snapshot(gid), ensure_ascii=False)))
    return no


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
seed_demo()
